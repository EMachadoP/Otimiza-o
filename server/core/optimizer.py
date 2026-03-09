"""
RF-04: Backtest vetorizado de milhares de combinações de parâmetros com Grid e Random Search.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from concurrent.futures import ProcessPoolExecutor, as_completed
from itertools import product
import logging
from dataclasses import dataclass, asdict

import hashlib
import json
from functools import lru_cache
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)
# Cache simples em memória (pode ser Redis em produção)
_optimization_cache = {}

def _get_cache_key(df, strategy_type, param_ranges, criteria):
    """Gera chave de cache única."""
    param_hash = hashlib.md5(
        json.dumps(param_ranges, sort_keys=True).encode()
    ).hexdigest()[:16]
    
    return f"{strategy_type}_{param_hash}_{criteria}"

# Variáveis globais para workers
_GLOBAL_DF = None
_GLOBAL_SYMBOL = None
_GLOBAL_ENGINE = None

def _init_worker(df: pd.DataFrame, symbol, engine: Any):
    """Inicializa worker com dados pré-carregados."""
    global _GLOBAL_DF, _GLOBAL_SYMBOL, _GLOBAL_ENGINE
    _GLOBAL_DF = df
    _GLOBAL_SYMBOL = symbol
    _GLOBAL_ENGINE = engine

def _sanitize_metrics(metrics: Dict) -> Dict:
    """Replace NaN and Inf with 0 for JSON compatibility."""
    sanitized = {}
    for k, v in metrics.items():
        if isinstance(v, float) and (np.isnan(v) or np.isinf(v)):
            sanitized[k] = 0
        else:
            sanitized[k] = v
    return sanitized

def _evaluate_params_worker(args):
    """Avalia parâmetros usando dados globais para evitar serialização repetida."""
    global _GLOBAL_DF, _GLOBAL_SYMBOL, _GLOBAL_ENGINE
    params, strategy_type, fast = args
    
    try:
        if fast:
            metrics = _GLOBAL_ENGINE.run_backtest(_GLOBAL_DF, strategy_type, params, _GLOBAL_SYMBOL, fast=True)
            # Filtros rápidos para o estágio 1
            if metrics.get('sharpeIS', 0) < -0.5: return None
            if metrics.get('maxDrawdown', 100) > 60: return None
            return {'parameters': params, 'metrics': metrics}
        else:
            # Full backtest
            bt = _GLOBAL_ENGINE.run_backtest(_GLOBAL_DF, strategy_type, params, _GLOBAL_SYMBOL)
            # WFA
            wfa = _GLOBAL_ENGINE.run_wfa(_GLOBAL_DF, strategy_type, params, _GLOBAL_SYMBOL)
            # Monte Carlo
            mc = _GLOBAL_ENGINE.run_monte_carlo(_GLOBAL_DF, strategy_type, params, _GLOBAL_SYMBOL)
            
            bt['metrics'].update({
                'wfe': wfa['efficiency'],
                'sharpeOOS': wfa['oosSharpe'],
                'maxDrawdownMC': mc['maxDrawdownP95']
            })
            
            return {
                "parameters": params,
                "metrics": bt['metrics'],
                "equityCurve": bt['equityCurve'],
                "wfa": wfa,
                "mc": mc
            }
    except Exception:
        return None


@dataclass
class OptimizationResult:
    """Resultado de uma combinação de parâmetros."""
    parameters: Dict[str, Any]
    metrics: Dict[str, Any]
    rank: int = 0
    validation: Optional[Dict] = None
    stage: int = 1


class ParameterOptimizer:
    """Otimizador de parâmetros de estratégias com suporte a paralelismo."""
    
    def __init__(self, backtest_engine: Any, max_workers: int = 4, progress_callback: Optional[Any] = None):
        self.backtest_engine = backtest_engine
        self.max_workers = max_workers
        self.progress_callback = progress_callback
        self.symbol = "EURUSD"
        
    def _generate_grid_from_ranges(self, param_ranges: Dict[str, Dict]) -> Dict[str, List[float]]:
        """Converte formato {min, max, step} em listas para o produtor."""
        expanded = {}
        for key, r in param_ranges.items():
            if isinstance(r, dict) and "min" in r and "max" in r:
                mn, mx, step = r["min"], r["max"], r.get("step", 1)
                if mn > mx:
                    expanded[key] = [mn]
                    continue
                values = []
                v = mn
                while v <= mx + 1e-9:
                    values.append(round(v, 4))
                    v += step
                expanded[key] = values
            elif isinstance(r, list):
                expanded[key] = r
            else:
                expanded[key] = [r]
        return expanded

    def optimize(
        self,
        df: pd.DataFrame,
        strategy_type: str,
        param_ranges: Dict[str, Dict[str, float]],
        criteria: str = 'sharpe',
        n_top: int = 20,
        symbol_name: str = "EURUSD"
    ) -> Dict:
        """
        3-Stage Optimization Funnel with Caching and Improved Parallelization.
        """
        self.symbol = symbol_name
        
        # Verificar cache
        cache_key = _get_cache_key(df, strategy_type, param_ranges, criteria)
        if cache_key in _optimization_cache:
            logger.info("Usando resultado em cache")
            return _optimization_cache[cache_key]

        expanded_ranges = self._generate_grid_from_ranges(param_ranges)
            
        MAX_GRID_COMBOS = 5000 
        
        # Generator for combinations to save memory
        def get_combinations():
            keys = expanded_ranges.keys()
            for values in product(*expanded_ranges.values()):
                yield dict(zip(keys, values))

        total_combos = 1
        for vals in expanded_ranges.values():
            total_combos *= len(vals)
            
        is_random = total_combos > MAX_GRID_COMBOS
        n_trials = 500 if is_random else total_combos
        
        logger.info(f"Otimizador: Estágio 1 (Triagem) - {n_trials} candidatos.")
        
        # Stage 1: Fast Screening using initializer to avoid repeated df serialization
        candidates = []
        with ProcessPoolExecutor(
            max_workers=self.max_workers, 
            initializer=_init_worker, 
            initargs=(df, symbol_name, self.backtest_engine)
        ) as executor:
            
            if is_random:
                import random
                # Memory efficient sampling from product without creating the full list
                keys = expanded_ranges.keys()
                vals = list(expanded_ranges.values())
                combinations = []
                # Simple random selection from coordinates
                indices = set()
                while len(indices) < n_trials:
                    idx = tuple(random.randint(0, len(v) - 1) for v in vals)
                    if idx not in indices:
                        indices.add(idx)
                        combinations.append(dict(zip(keys, [vals[i][idx[i]] for i in range(len(vals))])))
            else:
                combinations = list(get_combinations())
            
            args = [(combo, strategy_type, True) for combo in combinations]
            
            for i, result in enumerate(executor.map(_evaluate_params_worker, args)):
                if result:
                    candidates.append(result)
                else:
                    logger.debug(f"Stage 1: Candidate failed filter.")

        # Sort and take top candidates for Stage 3
        candidates.sort(key=lambda x: x['metrics'].get('sharpeIS', 0), reverse=True)
        top_candidates = candidates[:30]
        
        logger.info(f"Otimizador: Estágio 3 (Validação Full) - {len(top_candidates)} candidatos.")
        
        # Stage 3: Full Validation
        final_results = []
        with ProcessPoolExecutor(
            max_workers=self.max_workers, 
            initializer=_init_worker, 
            initargs=(df, symbol_name, self.backtest_engine)
        ) as executor:
            args = [(c['parameters'], strategy_type, False) for c in top_candidates]
            
            for i, res in enumerate(executor.map(_evaluate_params_worker, args)):
                if res:
                    final_results.append(OptimizationResult(
                        parameters=res['parameters'],
                        metrics=res['metrics'],
                        validation={
                            "wfa": res.get('wfa'),
                            "mc": res.get('mc')
                        }
                    ))
                else:
                    logger.warning(f"Stage 3: Candidate failed full validation.")
        
        # Final ranking
        final_results.sort(key=lambda x: x.metrics.get(criteria, 0), reverse=True)
        for i, res in enumerate(final_results):
            res.rank = i + 1
            res.metrics = _sanitize_metrics(res.metrics)
            
        output = {
            "totalSearchSpace": total_combos,
            "totalTested": n_trials,
            "bestConfig": asdict(final_results[0]) if final_results else None,
            "results": [asdict(r) for r in final_results[:n_top]]
        }
        
        # Salvar no cache
        _optimization_cache[cache_key] = output
        
        return output
        
    optimize_strategy = optimize # Alias for compatibility

    def grid_search(
        self,
        df: pd.DataFrame,
        strategy_type: str,
        param_ranges: Dict[str, List[float]],
        criteria: str = 'sharpe',
        n_top: int = 20,
        symbol_name: str = "EURUSD"
    ) -> List[OptimizationResult]:
        """Executa grid search completo em paralelo."""
        param_names = list(param_ranges.keys())
        param_values = list(param_ranges.values())
        combinations = list(product(*param_values))
        
        results = []
        
        # Uso de ProcessPoolExecutor para CPU-bound backtests
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            for combo in combinations:
                params = dict(zip(param_names, combo))
                future = executor.submit(
                    self._evaluate_params,
                    df, strategy_type, params, symbol_name
                )
                futures[future] = params
            
            for future in as_completed(futures):
                try:
                    eval_result = future.result()
                    if eval_result and self._is_viable(eval_result['metrics']):
                        results.append(OptimizationResult(
                            parameters=futures[future],
                            metrics=eval_result['metrics'],
                            validation=eval_result['validation']
                        ))
                except Exception as e:
                    logger.error(f"Erro em grid_search: {e}")

        # Ordenar e rankear
        results = self._sort_by_criteria(results, criteria)
        for i, r in enumerate(results[:n_top]):
            r.rank = i + 1
            
        return results[:n_top]

    def random_search(
        self,
        df: pd.DataFrame,
        strategy_type: str,
        param_ranges: Dict[str, Any],
        n_iterations: int = 500,
        criteria: str = 'sharpe',
        n_top: int = 20,
        symbol_name: str = "EURUSD"
    ) -> List[OptimizationResult]:
        """Busca aleatória para espaços de parâmetros gigantescos."""
        results = []
        
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            for _ in range(n_iterations):
                params = {}
                for name, r in param_ranges.items():
                    if isinstance(r, dict) and "min" in r:
                        mn, mx = r["min"], r["max"]
                        if isinstance(mn, int) and isinstance(mx, int):
                            params[name] = np.random.randint(mn, mx + 1)
                        else:
                            params[name] = round(np.random.uniform(mn, mx), 4)
                    elif isinstance(r, list):
                        params[name] = np.random.choice(r)
                    else:
                        params[name] = r
                        
                future = executor.submit(self._evaluate_params, df, strategy_type, params, symbol_name)
                futures[future] = params

            for future in as_completed(futures):
                try:
                    eval_result = future.result()
                    if eval_result and self._is_viable(eval_result['metrics']):
                        results.append(OptimizationResult(
                            parameters=futures[future],
                            metrics=eval_result['metrics'],
                            validation=eval_result['validation']
                        ))
                except Exception as e:
                    logger.error(f"Erro em random_search: {e}")

        results = self._sort_by_criteria(results, criteria)
        for i, r in enumerate(results[:n_top]):
            r.rank = i + 1
            
        return results[:n_top]

    def _evaluate_params(
        self,
        df: pd.DataFrame,
        strategy_type: str,
        params: Dict[str, Any],
        symbol_name: str
    ) -> Optional[Dict]:
        """Avalia uma única combinação de parâmetros com validação completa."""
        try:
            # 1. Backtest Vetorizado
            result = self.backtest_engine.run_backtest(df, strategy_type, params, symbol_name=symbol_name)
            if 'error' in result:
                return None
            
            metrics = result['metrics']
            
            # 2. Validação Walk-Forward (3 janelas para velocidade na otimização)
            wfa = self.backtest_engine.run_wfa(df, strategy_type, params, symbol_name=symbol_name, n_windows=3)
            metrics['wfe'] = wfa['efficiency']
            metrics['sharpeOOS'] = wfa.get('oosSharpe', 0)
            
            # 3. Monte Carlo Rápido (200 simulações)
            mc = self.backtest_engine.run_monte_carlo(df, strategy_type, params, symbol_name=symbol_name, n_simulations=200)
            metrics['maxDrawdownMC'] = mc['maxDrawdownP95']
            
            # 4. Cálculo de PBO (baseado na eficiência do WFA)
            pbo = min(float((1 - wfa['efficiency']) * 100), 100)
            
            return {
                "metrics": metrics,
                "validation": {
                    "wfa": wfa,
                    "pbo": pbo
                }
            }
        except Exception:
            return None

    def _is_viable(self, metrics: Dict) -> bool:
        """Filtro de viabilidade para descartar resultados mediocres."""
        if metrics.get('sharpeIS', 0) < -0.5: return False
        if metrics.get('totalTrades', 0) < 3: return False
        if metrics.get('maxDrawdown', 100) > 60: return False
        return True

    def _sort_by_criteria(
        self,
        results: List[OptimizationResult],
        criteria: str
    ) -> List[OptimizationResult]:
        """Ordena os resultados baseados no critério escolhido."""
        def get_score(r: OptimizationResult) -> float:
            m = r.metrics
            if criteria == 'sharpe':
                return m.get('sharpeOOS', 0) or m.get('sharpeIS', 0)
            elif criteria == 'profit_factor' or criteria == 'profitFactor':
                return m.get('profitFactor', 0)
            elif criteria == 'win_rate' or criteria == 'winRate':
                return m.get('winRate', 0)
            elif criteria == 'wfe':
                return m.get('wfe', 0)
            return m.get('sharpeIS', 0)
            
        return sorted(results, key=get_score, reverse=True)


# Instância será configurada no main.py
parameter_optimizer = None
