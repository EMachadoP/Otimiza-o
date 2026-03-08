import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging
from itertools import product

logger = logging.getLogger(__name__)


class ParameterOptimizer:
    """Grid-search parameter optimizer with real WFA validation."""

    def __init__(self, backtest_engine):
        self.engine = backtest_engine

    def _generate_grid(
        self,
        param_ranges: Dict[str, Dict],
    ) -> List[Dict[str, float]]:
        """Generate all parameter combinations from ranges."""
        keys = list(param_ranges.keys())
        value_lists = []

        for key in keys:
            r = param_ranges[key]
            mn, mx, step = r["min"], r["max"], r["step"]
            values = []
            v = mn
            while v <= mx + 1e-9:
                values.append(round(v, 4))
                v += step
            value_lists.append(values)

        combinations = []
        for combo in product(*value_lists):
            combinations.append(dict(zip(keys, combo)))

        return combinations

    def optimize_strategy(
        self,
        df: pd.DataFrame,
        strategy_type: str,
        param_ranges: Dict[str, Dict],
        criteria: str = "sharpe",
        max_combinations: int = 2000,
    ) -> Dict:
        """
        Run grid-search optimization with real backtests and WFA validation.

        Returns top 20 parameter sets ranked by the chosen criteria.
        """
        combinations = self._generate_grid(param_ranges)
        total = len(combinations)

        if total > max_combinations:
            # Subsample evenly
            step = total / max_combinations
            indices = [int(i * step) for i in range(max_combinations)]
            combinations = [combinations[i] for i in indices]

        logger.info(f"Optimizer: testing {len(combinations)} combinations for {strategy_type} (Vectorized Engine)")

        results = []

        for i, params in enumerate(combinations):
            try:
                # 1) Run vectorized backtest
                signals = self.engine._generate_signals(df, strategy_type, params)
                returns = df["close"].pct_change()
                strategy_returns = signals.shift(1) * returns
                equity = (1 + strategy_returns).cumprod() * 10000
                equity = equity.ffill().fillna(10000)

                metrics = self.engine._compute_metrics(equity, signals)

                # Quick filter: skip terrible results
                if metrics["maxDrawdown"] > 50 or metrics["totalTrades"] < 5:
                    continue

                # 2) Quick WFA (3 windows for speed)
                wfa = self.engine.run_wfa(df, strategy_type, params, n_windows=3)
                metrics["wfe"] = wfa["efficiency"]
                metrics["sharpeOOS"] = wfa.get("oosSharpe", 0)

                # 3) Quick Monte Carlo (300 sims for speed)
                strat_ret = strategy_returns.dropna().values
                if len(strat_ret) > 10:
                    mc_dds = []
                    for _ in range(300):
                        sampled = np.random.choice(strat_ret, size=len(strat_ret), replace=True)
                        cum = np.cumprod(1 + sampled) * 10000
                        peak = np.maximum.accumulate(cum)
                        dd = (peak - cum) / (peak + 1e-10)
                        mc_dds.append(dd.max())
                    metrics["maxDrawdownMC"] = round(float(np.percentile(mc_dds, 95)) * 100, 1)

                # 4) PBO approximation
                pbo = min(float(wfa.get("efficiency", 0.5)), 1.0)
                pbo_pct = round((1 - pbo) * 100, 1)  # lower efficiency = higher PBO

                results.append({
                    "parameters": params,
                    "metrics": metrics,
                    "validation": {
                        "wfa": wfa,
                        "pbo": pbo_pct,
                    },
                    "rank": 0,
                })

            except Exception as e:
                logger.warning(f"Optimizer: combo {i} failed: {e}")
                continue

        # Sort by criteria
        sort_key = {
            "sharpe": lambda r: r["metrics"].get("sharpeOOS", 0),
            "profitFactor": lambda r: r["metrics"].get("profitFactor", 0),
            "winRate": lambda r: r["metrics"].get("winRate", 0),
            "wfe": lambda r: r["metrics"].get("wfe", 0),
        }.get(criteria, lambda r: r["metrics"].get("sharpeOOS", 0))

        results.sort(key=sort_key, reverse=True)

        # Assign ranks and trim to top 20
        for idx, r in enumerate(results[:20]):
            r["rank"] = idx + 1

        top_results = results[:20]

        return {
            "totalTested": len(combinations),
            "totalPassed": len(results),
            "results": top_results,
            "bestConfig": top_results[0] if top_results else None,
        }


# Factory: will be initialized in main.py after backtest_engine is imported
parameter_optimizer = None
