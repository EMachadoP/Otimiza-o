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
import optuna
import asyncio
import time
from functools import lru_cache

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
    except Exception as e:
        logger.error(f"Error in _evaluate_params_worker: {e}")
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

    async def optimize_stream(
        self,
        df: pd.DataFrame,
        strategy_type: str,
        param_ranges: Dict[str, Dict[str, float]],
        criteria: str = 'sharpe',
        n_top: int = 20,
        symbol_name: str = "EURUSD"
    ):
        """
        Streaming version of the multi-stage optimization funnel.
        Yields JSON status updates.
        """
        self.symbol = symbol_name
        
        yield json.dumps({"progress": 5, "phase": "Explorando espaço de parâmetros..."})
        
        expanded_ranges = self._generate_grid_from_ranges(param_ranges)
        total_combos = 1
        for vals in expanded_ranges.values():
            total_combos *= len(vals)
        
        MAX_GRID_COMBOS = 10000
        is_optuna = total_combos > MAX_GRID_COMBOS
        
        if is_optuna:
            yield json.dumps({"progress": 10, "phase": f"Espaço gigante ({total_combos:,}). Ativando Motor Bayesiano Optuna...", "totalCombinations": total_combos})
            
            # Optuna Bayesian Optimization
            def objective(trial):
                params = {}
                for key, r in param_ranges.items():
                    if isinstance(r, dict) and "min" in r and "max" in r:
                        mn, mx, step = r["min"], r["max"], r.get("step", 1)
                        if isinstance(mn, int) and isinstance(mx, int) and isinstance(step, int) and step >= 1:
                            params[key] = trial.suggest_int(key, mn, mx, step=step)
                        else:
                            params[key] = round(trial.suggest_float(key, mn, mx, step=step), 4)
                
                # Para o Optuna, fazemos apenas o backtest rápido inicialmente
                metrics = self.backtest_engine.run_backtest(df, strategy_type, params, symbol_name=symbol_name, fast=True)
                score = metrics.get(criteria, 0)
                if np.isnan(score) or np.isinf(score): return -1e9
                return score

            study = optuna.create_study(direction="maximize")
            n_trials = 500 # Cap para velocidade no streaming
            
            candidates = []
            for i in range(n_trials):
                trial = study.ask()
                value = objective(trial)
                study.tell(trial, value)
                
                if i % 50 == 0:
                    prog = 10 + int((i / n_trials) * 60)
                    yield json.dumps({"progress": prog, "phase": f"Busca Bayesiana: {i}/{n_trials} trials..."})
                
                params = trial.params
                candidates.append({"parameters": params, "metrics": {"sharpeIS": value}})

            candidates.sort(key=lambda x: x['metrics'].get('sharpeIS', -1e9), reverse=True)
            top_candidates = candidates[:30]
            
        else:
            yield json.dumps({"progress": 10, "phase": f"Iniciando Grid Search Vectorizado ({total_combos} combinações)...", "totalCombinations": total_combos})
            
            def get_combinations():
                keys = expanded_ranges.keys()
                for values in product(*expanded_ranges.values()):
                    yield dict(zip(keys, values))

            combinations = list(get_combinations())
            candidates = []
            
            with ProcessPoolExecutor(
                max_workers=self.max_workers, 
                initializer=_init_worker, 
                initargs=(df, symbol_name, self.backtest_engine)
            ) as executor:
                args = [(combo, strategy_type, True) for combo in combinations]
                
                # Usar submit e iterar os futures de forma a permitir await asyncio.sleep(0)
                futures = {executor.submit(_evaluate_params_worker, arg): arg for arg in args}
                i = 0
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        if result and "error" not in result.get("metrics", {}):
                            candidates.append(result)
                    except Exception as e:
                        logger.error(f"Worker crashed during initial screening: {e}")

                    i += 1
                    if i % 100 == 0 or i == len(args):
                        prog = 10 + int((i / len(args)) * 60)
                        yield json.dumps({"progress": prog, "phase": f"Triagem Inicial: {i}/{len(args)}..."})
                        await asyncio.sleep(0.01) # Cede controle para o event loop e evita hang do SSE

            candidates.sort(key=lambda x: x['metrics'].get('sharpeIS', -0.5), reverse=True)
            top_candidates = candidates[:30]

        yield json.dumps({"progress": 75, "phase": f"Validando Top {len(top_candidates)} com WFA + Monte Carlo..."})
        
        final_results = []
        with ProcessPoolExecutor(
            max_workers=self.max_workers, 
            initializer=_init_worker, 
            initargs=(df, symbol_name, self.backtest_engine)
        ) as executor:
            args = [(c['parameters'], strategy_type, False) for c in top_candidates]
            
            futures = {executor.submit(_evaluate_params_worker, arg): arg for arg in args}
            i = 0
            for future in as_completed(futures):
                try:
                    res = future.result()
                    if res and "error" not in res.get("metrics", {}):
                        final_results.append(OptimizationResult(
                            parameters=res['parameters'],
                            metrics=res['metrics'],
                            validation={
                                "wfa": res.get('wfa'),
                                "mc": res.get('mc')
                            }
                        ))
                except Exception as e:
                    logger.error(f"Worker crashed during robust validation: {e}")
                
                i += 1
                prog = 75 + int((i / len(args)) * 20)
                yield json.dumps({"progress": prog, "phase": f"Validação Robusta: {i}/{len(args)}..."})
                await asyncio.sleep(0.01)

        final_results.sort(key=lambda x: x.metrics.get(criteria, -1e9), reverse=True)
        for i, res in enumerate(final_results):
            res.rank = i + 1
            res.metrics = _sanitize_metrics(res.metrics)
            
        output = {
            "progress": 100,
            "phase": "Concluído!",
            "totalSearchSpace": total_combos,
            "totalTested": 500 if is_optuna else total_combos,
            "results": [asdict(r) for r in final_results[:n_top]]
        }
        
        yield json.dumps(output)

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
        Original block for backwards compatibility.
        """
        async def run_sync():
            res = None
            async for update in self.optimize_stream(df, strategy_type, param_ranges, criteria, n_top, symbol_name):
                res = json.loads(update)
            return res
        
        return asyncio.run(run_sync())
        
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
            result = self.backtest_engine.run_backtest(df, strategy_type, params, symbol_name=symbol_name)
            if 'error' in result:
                return None
            
            metrics = result['metrics']
            wfa = self.backtest_engine.run_wfa(df, strategy_type, params, symbol_name=symbol_name, n_windows=3)
            metrics['wfe'] = wfa['efficiency']
            metrics['sharpeOOS'] = wfa.get('oosSharpe', 0)
            mc = self.backtest_engine.run_monte_carlo(df, strategy_type, params, symbol_name=symbol_name, n_simulations=200)
            metrics['maxDrawdownMC'] = mc['maxDrawdownP95']
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
