import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class BacktestEngine:
    """Vectorized backtesting engine with real WFA, CPCV, and Monte Carlo validation."""

    STRATEGY_CONFIGS = [
        {
            "id": "strat_ema_cross",
            "name": "EMA Crossover",
            "type": "trend",
            "parameters": {"fastEMA": 9, "slowEMA": 21, "stopLoss": 50, "takeProfit": 100},
            "indicators": ["EMA(9)", "EMA(21)"],
        },
        {
            "id": "strat_rsi_reversal",
            "name": "RSI Reversal",
            "type": "reversal",
            "parameters": {"rsiPeriod": 14, "overbought": 70, "oversold": 30, "stopLoss": 40, "takeProfit": 80},
            "indicators": ["RSI(14)"],
        },
        {
            "id": "strat_bb_breakout",
            "name": "Bollinger Breakout",
            "type": "breakout",
            "parameters": {"bbPeriod": 20, "bbStd": 2.0, "stopLoss": 60, "takeProfit": 120},
            "indicators": ["BB(20,2)"],
        },
        {
            "id": "strat_macd_trend",
            "name": "MACD Trend",
            "type": "trend",
            "parameters": {"fastEMA": 12, "slowEMA": 26, "signalEMA": 9, "stopLoss": 50, "takeProfit": 150},
            "indicators": ["MACD(12,26,9)"],
        },
        {
            "id": "strat_scalper",
            "name": "Scalper Momentum",
            "type": "scalping",
            "parameters": {"fastEMA": 5, "slowEMA": 13, "rsiPeriod": 7, "stopLoss": 20, "takeProfit": 40},
            "indicators": ["EMA(5)", "EMA(13)", "RSI(7)"],
        },
        {
            "id": "strat_mean_reversion",
            "name": "Mean Reversion %B",
            "type": "mean_reversion",
            "parameters": {"period": 20, "std": 2.0, "stopLoss": 30, "takeProfit": 60},
            "indicators": ["BB %B (20, 2)"],
        },
        {
            "id": "strat_donchian",
            "name": "Donchian Breakout",
            "type": "donchian",
            "parameters": {"period": 20, "stopLoss": 50, "takeProfit": 150},
            "indicators": ["Donchian Channel(20)"],
        },
    ]

    def _generate_signals(self, df: pd.DataFrame, strategy_type: str, params: Dict) -> pd.Series:
        """Generate buy/sell signals based on strategy type using real data."""
        close = df['close']

        if strategy_type == "trend":
            fast = close.ewm(span=params.get('fastEMA', 9), adjust=False).mean()
            slow = close.ewm(span=params.get('slowEMA', 21), adjust=False).mean()
            signals = np.where(fast > slow, 1, -1)

        elif strategy_type == "reversal":
            period = params.get('rsiPeriod', 14)
            delta = close.diff()
            gain = delta.clip(lower=0).rolling(window=period).mean()
            loss = (-delta.clip(upper=0)).rolling(window=period).mean()
            rs = gain / (loss + 1e-10)
            rsi = 100 - (100 / (1 + rs))
            ob = params.get('overbought', 70)
            os_val = params.get('oversold', 30)
            signals = np.where(rsi < os_val, 1, np.where(rsi > ob, -1, 0))

        elif strategy_type == "breakout":
            period = params.get('bbPeriod', 20)
            std_dev = params.get('bbStd', 2.0)
            sma = close.rolling(window=period).mean()
            std = close.rolling(window=period).std()
            upper = sma + std_dev * std
            lower = sma - std_dev * std
            signals = np.where(close > upper, 1, np.where(close < lower, -1, 0))

        elif strategy_type == "scalping":
            fast = close.ewm(span=params.get('fastEMA', 5), adjust=False).mean()
            slow = close.ewm(span=params.get('slowEMA', 13), adjust=False).mean()
            period = params.get('rsiPeriod', 7)
            delta = close.diff()
            gain = delta.clip(lower=0).rolling(window=period).mean()
            loss = (-delta.clip(upper=0)).rolling(window=period).mean()
            rs = gain / (loss + 1e-10)
            rsi = 100 - (100 / (1 + rs))
            trend = np.where(fast > slow, 1, -1)
            momentum = np.where((rsi > 50) & (rsi < 80), 1, np.where((rsi < 50) & (rsi > 20), -1, 0))
            signals = np.where(trend == momentum, trend, 0)

        elif strategy_type == "mean_reversion":
            period = params.get('period', 20)
            std_dev = params.get('std', 2.0)
            sma = close.rolling(window=period).mean()
            std = close.rolling(window=period).std()
            upper = sma + std_dev * std
            lower = sma - std_dev * std
            # Sell at upper, buy at lower
            signals = np.where(close > upper, -1, np.where(close < lower, 1, 0))

        elif strategy_type == "donchian":
            period = params.get('period', 20)
            upper = close.rolling(window=period).max().shift(1)
            lower = close.rolling(window=period).min().shift(1)
            signals = np.where(close > upper, 1, np.where(close < lower, -1, 0))

        else:  # Default: EMA crossover
            fast = close.ewm(span=9, adjust=False).mean()
            slow = close.ewm(span=21, adjust=False).mean()
            signals = np.where(fast > slow, 1, -1)

        return pd.Series(signals, index=df.index)

    def _compute_metrics(self, equity_curve: pd.Series, signals: pd.Series, initial_balance: float = 10000) -> Dict:
        """Compute real strategy metrics from equity curve."""
        returns = equity_curve.pct_change().dropna()

        total_return = (equity_curve.iloc[-1] / initial_balance) - 1
        drawdown = (equity_curve.cummax() - equity_curve) / equity_curve.cummax()
        max_dd = float(drawdown.max())

        # Sharpe (annualized)
        sharpe = float(returns.mean() / (returns.std() + 1e-10) * np.sqrt(252))

        # Sortino
        downside = returns[returns < 0]
        sortino = float(returns.mean() / (downside.std() + 1e-10) * np.sqrt(252))

        # Profit Factor
        gains = returns[returns > 0].sum()
        losses = abs(returns[returns < 0].sum())
        pf = float(gains / (losses + 1e-10))

        # Win Rate
        signal_changes = signals.diff().abs()
        trades_count = int(signal_changes.sum() / 2)
        profitable_returns = returns[returns > 0]
        win_rate = float(len(profitable_returns) / (len(returns) + 1e-10) * 100)

        # Calmar
        cagr = float(((equity_curve.iloc[-1] / initial_balance) ** (252 / len(equity_curve)) - 1) * 100)
        calmar = float(cagr / (max_dd * 100 + 1e-10))

        return {
            "wfe": 0,  # Filled by WFA
            "sharpeIS": round(sharpe, 2),
            "sharpeOOS": 0,  # Filled by WFA
            "profitFactor": round(pf, 2),
            "winRate": round(win_rate, 1),
            "maxDrawdown": round(max_dd * 100, 2),
            "maxDrawdownMC": 0,  # Filled by Monte Carlo
            "totalTrades": trades_count,
            "avgTrade": round(float(total_return / (trades_count + 1e-10) * 100), 2),
            "expectancy": round(float(returns.mean() * 10000), 2),
            "calmarRatio": round(calmar, 2),
            "sortinoRatio": round(sortino, 2),
        }

    def run_backtest(self, df: pd.DataFrame, strategy_type: str, params: Dict) -> Dict:
        """Run a full vectorized backtest with validation."""
        try:
            signals = self._generate_signals(df, strategy_type, params)
            initial_balance = 10000
            # Vectorized Returns calculation
            close = df['close']
            returns = close.pct_change()
            
            # SL/TP Logic (Pips/Points)
            # Assuming 1 pip = 0.0001 (or 0.01 for JPY/BTC) - simplified for now
            # Better: use symbol digits from MT5 if available
            pip_size = 0.0001 if symbol_name and ("JPY" not in symbol_name and "BTC" not in symbol_name and "XAU" not in symbol_name) else 0.01
            if "XAU" in symbol_name: pip_size = 0.1 # Gold
            if "BTC" in symbol_name: pip_size = 1.0 # Crypto
            
            sl_pips = params.get('stopLoss', 0)
            tp_pips = params.get('takeProfit', 0)
            
            strategy_returns = signals.shift(1) * returns
            
            # Simplified SL/TP hit detection using vectorized logic
            # This is a bit complex in pure vectorization but we can approximate:
            if sl_pips > 0 or tp_pips > 0:
                high = df['high']
                low = df['low']
                
                # SL/TP prices for each potential trade entry
                # (Only valid on bars where sign changes)
                entry_prices = close.where(signals.diff().abs() > 0).ffill()
                
                if sl_pips > 0:
                    sl_dist = sl_pips * pip_size
                    # Long SL hit: Low < Entry - Dist
                    # Short SL hit: High > Entry + Dist
                    long_sl_hit = (signals.shift(1) == 1) & (low < (entry_prices - sl_dist))
                    short_sl_hit = (signals.shift(1) == -1) & (high > (entry_prices + sl_dist))
                    
                    # Cap returns at -SL dist %
                    # (Approximate: assuming we hit SL at exactly the price)
                    sl_hit = long_sl_hit | short_sl_hit
                    strategy_returns[sl_hit] = - (sl_dist / entry_prices)
                
                if tp_pips > 0:
                    tp_dist = tp_pips * pip_size
                    long_tp_hit = (signals.shift(1) == 1) & (high > (entry_prices + tp_dist))
                    short_tp_hit = (signals.shift(1) == -1) & (low < (entry_prices - tp_dist))
                    
                    tp_hit = long_tp_hit | short_tp_hit
                    strategy_returns[tp_hit] = (tp_dist / entry_prices)

            equity_curve = (1 + strategy_returns).cumprod() * initial_balance
            equity_curve = equity_curve.ffill().fillna(initial_balance)

            metrics = self._compute_metrics(equity_curve, signals, initial_balance)
            drawdown = (equity_curve.cummax() - equity_curve) / equity_curve.cummax()

            # Format equity curve for UI
            formatted_curve = []
            step = max(1, len(equity_curve) // 100)
            for i in range(0, len(equity_curve), step):
                formatted_curve.append({
                    "timestamp": int(df.iloc[i]['time'].timestamp() * 1000),
                    "equity": round(float(equity_curve.iloc[i]), 2),
                    "drawdown": round(float(drawdown.iloc[i] * 100), 2),
                    "trades": int(signals.iloc[:i].diff().abs().sum() / 2),
                })

            return {
                "id": f"bt_{int(pd.Timestamp.now().timestamp())}",
                "metrics": metrics,
                "equityCurve": formatted_curve,
            }
        except Exception as e:
            logger.error(f"Error in run_backtest: {e}")
            return {"error": str(e)}

    # ──────────────────────────────────────────
    # Walk-Forward Analysis (WFA)
    # ──────────────────────────────────────────
    def run_wfa(self, df: pd.DataFrame, strategy_type: str, params: Dict, n_windows: int = 5) -> Dict:
        """Real Walk-Forward Analysis on historical data."""
        total = len(df)
        # Adaptive: reduce windows if data is short
        effective_windows = n_windows
        while effective_windows > 2 and total // effective_windows < 20:
            effective_windows -= 1

        window_size = total // effective_windows
        train_ratio = 0.7
        windows = []
        oos_sharpes = []

        for i in range(effective_windows):
            start = i * window_size
            end = min(start + window_size, total)
            split = start + int((end - start) * train_ratio)

            train_df = df.iloc[start:split].copy()
            test_df = df.iloc[split:end].copy()

            if len(train_df) < 10 or len(test_df) < 5:
                continue

            train_signals = self._generate_signals(train_df, strategy_type, params)
            test_signals = self._generate_signals(test_df, strategy_type, params)

            train_ret = (train_df['close'].pct_change() * train_signals.shift(1)).sum()
            test_ret = (test_df['close'].pct_change() * test_signals.shift(1)).sum()

            # Compute OOS Sharpe for this window
            oos_returns = test_df['close'].pct_change() * test_signals.shift(1)
            oos_returns = oos_returns.dropna()
            if len(oos_returns) > 2:
                oos_sharpe = float(oos_returns.mean() / (oos_returns.std() + 1e-10) * np.sqrt(252))
                oos_sharpes.append(oos_sharpe)

            eff = test_ret / (train_ret + 1e-10) if train_ret > 0 else 0

            train_start_date = str(train_df.iloc[0]['time'].date()) if hasattr(train_df.iloc[0]['time'], 'date') else str(train_df.iloc[0]['time'])[:10]
            train_end_date = str(train_df.iloc[-1]['time'].date()) if hasattr(train_df.iloc[-1]['time'], 'date') else str(train_df.iloc[-1]['time'])[:10]
            test_start_date = str(test_df.iloc[0]['time'].date()) if hasattr(test_df.iloc[0]['time'], 'date') else str(test_df.iloc[0]['time'])[:10]
            test_end_date = str(test_df.iloc[-1]['time'].date()) if hasattr(test_df.iloc[-1]['time'], 'date') else str(test_df.iloc[-1]['time'])[:10]

            windows.append({
                "trainStart": train_start_date,
                "trainEnd": train_end_date,
                "testStart": test_start_date,
                "testEnd": test_end_date,
                "trainReturn": round(float(train_ret * 100), 1),
                "testReturn": round(float(test_ret * 100), 1),
                "efficiency": round(float(min(max(eff, 0), 2)), 2),
            })

        avg_eff = np.mean([w['efficiency'] for w in windows]) if windows else 0
        is_cagr = np.mean([w['trainReturn'] for w in windows]) if windows else 0
        oos_cagr = np.mean([w['testReturn'] for w in windows]) if windows else 0
        avg_oos_sharpe = round(float(np.mean(oos_sharpes)), 2) if oos_sharpes else 0

        return {
            "efficiency": round(float(avg_eff), 2),
            "isCAGR": round(float(is_cagr), 1),
            "oosCAGR": round(float(oos_cagr), 1),
            "oosSharpe": avg_oos_sharpe,
            "windows": windows,
        }

    # ──────────────────────────────────────────
    # Combinatorial Purged Cross-Validation (CPCV)
    # ──────────────────────────────────────────
    def run_cpcv(self, df: pd.DataFrame, strategy_type: str, params: Dict, n_folds: int = 6, embargo: int = 5) -> Dict:
        """Real CPCV on historical data."""
        total = len(df)
        fold_size = total // n_folds
        folds = []
        sharpes = []

        for i in range(n_folds):
            test_start = i * fold_size
            test_end = min(test_start + fold_size, total)

            train_indices = list(range(0, max(0, test_start - embargo))) + list(range(min(total, test_end + embargo), total))
            test_indices = list(range(test_start, test_end))

            if len(train_indices) < 30 or len(test_indices) < 10:
                continue

            train_df = df.iloc[train_indices].copy()
            test_df = df.iloc[test_indices].copy()

            test_signals = self._generate_signals(test_df, strategy_type, params)
            test_returns = test_df['close'].pct_change() * test_signals.shift(1)
            test_returns = test_returns.dropna()

            sharpe = float(test_returns.mean() / (test_returns.std() + 1e-10) * np.sqrt(252))
            signal_changes = test_signals.diff().abs()
            trades = int(signal_changes.sum() / 2)

            sharpes.append(sharpe)
            folds.append({
                "fold": i + 1,
                "trainSize": len(train_indices),
                "testSize": len(test_indices),
                "sharpe": round(sharpe, 2),
                "trades": trades,
            })

        return {
            "avgSharpe": round(float(np.mean(sharpes)), 2) if sharpes else 0,
            "sharpeStd": round(float(np.std(sharpes)), 2) if sharpes else 0,
            "purgedSplits": n_folds,
            "embargoSize": embargo,
            "foldResults": folds,
        }

    # ──────────────────────────────────────────
    # Monte Carlo Simulation
    # ──────────────────────────────────────────
    def run_monte_carlo(self, df: pd.DataFrame, strategy_type: str, params: Dict, n_simulations: int = 10000) -> Dict:
        """Real Monte Carlo simulation on strategy returns."""
        signals = self._generate_signals(df, strategy_type, params)
        returns = df['close'].pct_change() * signals.shift(1)
        returns = returns.dropna().values

        initial = 10000
        final_equities = []
        max_drawdowns = []

        for _ in range(n_simulations):
            shuffled = np.random.choice(returns, size=len(returns), replace=True)
            equity = initial * np.cumprod(1 + shuffled)
            final_equities.append(equity[-1])

            peak = np.maximum.accumulate(equity)
            dd = (peak - equity) / peak
            max_drawdowns.append(dd.max())

        final_equities = np.array(final_equities)
        max_drawdowns = np.array(max_drawdowns)

        return {
            "simulations": n_simulations,
            "profitablePct": round(float((final_equities > initial).mean() * 100), 1),
            "maxDrawdownP95": round(float(np.percentile(max_drawdowns, 95) * 100), 1),
            "maxDrawdownP99": round(float(np.percentile(max_drawdowns, 99) * 100), 1),
            "worstCaseEquity": round(float(np.percentile(final_equities, 5)), 0),
            "bestCaseEquity": round(float(np.percentile(final_equities, 95)), 0),
            "medianEquity": round(float(np.median(final_equities)), 0),
        }

    # ──────────────────────────────────────────
    # Strategy Discovery
    # ──────────────────────────────────────────
    def discover_strategies(self, df: pd.DataFrame) -> List[Dict]:
        """Run all built-in strategies on the data and rank them."""
        results = []

        for config in self.STRATEGY_CONFIGS:
            try:
                signals = self._generate_signals(df, config['type'], config['parameters'])
                returns = df['close'].pct_change()
                strategy_returns = signals.shift(1) * returns
                equity_curve = (1 + strategy_returns).cumprod() * 10000
                equity_curve = equity_curve.ffill().fillna(10000)

                metrics = self._compute_metrics(equity_curve, signals)

                # Quick WFA for efficiency + real OOS Sharpe
                wfa = self.run_wfa(df, config['type'], config['parameters'], n_windows=3)
                metrics['wfe'] = wfa['efficiency']
                metrics['sharpeOOS'] = wfa.get('oosSharpe', 0)

                # Quick Monte Carlo for Max DD P95 (500 sims for speed)
                strategy_returns_clean = strategy_returns.dropna()
                if len(strategy_returns_clean) > 10:
                    mc_dds = []
                    for _ in range(500):
                        sampled = np.random.choice(strategy_returns_clean.values, size=len(strategy_returns_clean), replace=True)
                        cum = np.cumprod(1 + sampled) * 10000
                        peak = np.maximum.accumulate(cum)
                        dd = (peak - cum) / (peak + 1e-10)
                        mc_dds.append(dd.max())
                    metrics['maxDrawdownMC'] = round(float(np.percentile(mc_dds, 95)) * 100, 1)

                results.append({
                    "id": config['id'],
                    "name": config['name'],
                    "type": config['type'],
                    "parameters": config['parameters'],
                    "indicators": config['indicators'],
                    "metrics": metrics,
                    "status": "approved" if wfa['efficiency'] >= 0.5 else "testing",
                    "createdAt": int(pd.Timestamp.now().timestamp() * 1000),
                })
            except Exception as e:
                logger.error(f"Error discovering strategy {config['name']}: {e}")

        # Sort by WFE descending
        results.sort(key=lambda x: x['metrics']['wfe'], reverse=True)
        return results

    # ──────────────────────────────────────────
    # Heatmap: Recurrence by Hour/Day
    # ──────────────────────────────────────────
    def compute_heatmap(self, df: pd.DataFrame) -> List[List[float]]:
        """Compute win rate heatmap by hour of day and day of week from real data."""
        df_copy = df.copy()
        df_copy['returns'] = df_copy['close'].pct_change()
        df_copy['hour'] = df_copy['time'].dt.hour
        df_copy['dayofweek'] = df_copy['time'].dt.dayofweek  # 0=Mon, 4=Fri

        hours = list(range(9, 18))
        days = list(range(5))

        heatmap = []
        for h in hours:
            row = []
            for d in days:
                subset = df_copy[(df_copy['hour'] == h) & (df_copy['dayofweek'] == d)]
                if len(subset) > 0:
                    win_rate = float((subset['returns'] > 0).mean() * 100)
                else:
                    win_rate = 50.0
                row.append(round(win_rate, 1))
            heatmap.append(row)

        return heatmap

    # ──────────────────────────────────────────
    # ML Feature Importance
    # ──────────────────────────────────────────
    def compute_feature_importance(self, df: pd.DataFrame) -> Dict:
        """Compute real feature importance using correlation analysis."""
        df_copy = df.copy()
        close = df_copy['close']

        # Compute features
        df_copy['returns'] = close.pct_change()
        df_copy['future_returns'] = df_copy['returns'].shift(-1)

        # RSI
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rs = gain / (loss + 1e-10)
        df_copy['rsi'] = 100 - (100 / (1 + rs))

        # ATR
        high_low = df_copy['high'] - df_copy['low']
        high_close = abs(df_copy['high'] - close.shift(1))
        low_close = abs(df_copy['low'] - close.shift(1))
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df_copy['atr'] = tr.rolling(14).mean()

        # Volume normalized
        df_copy['vol_norm'] = df_copy['tick_volume'] / df_copy['tick_volume'].rolling(20).mean() if 'tick_volume' in df_copy.columns else close * 0

        # EMA
        df_copy['ema50'] = close.ewm(span=50, adjust=False).mean()
        df_copy['ema_diff'] = (close - df_copy['ema50']) / df_copy['ema50'] * 100

        # MACD
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        df_copy['macd'] = ema12 - ema26

        # Drop NaN and compute correlations
        feature_cols = ['rsi', 'atr', 'vol_norm', 'ema_diff', 'macd']
        df_clean = df_copy[feature_cols + ['future_returns']].dropna()

        if len(df_clean) < 20:
            return {"features": [], "successProbability": 50, "explanation": "Dados insuficientes."}

        correlations = df_clean[feature_cols].corrwith(df_clean['future_returns']).abs()
        total_corr = correlations.sum()
        importances = (correlations / (total_corr + 1e-10) * 100).clip(0, 100)

        feature_names = {
            'rsi': ('RSI (14)', 'Índice de Força Relativa'),
            'atr': ('ATR (14)', 'Average True Range - Volatilidade'),
            'vol_norm': ('Volume', 'Volume normalizado de negociação'),
            'ema_diff': ('EMA (50)', 'Distância da Média Móvel Exponencial'),
            'macd': ('MACD', 'Convergência/Divergência de Médias'),
        }

        features = []
        for col in feature_cols:
            name, desc = feature_names.get(col, (col, col))
            features.append({
                "feature": name,
                "importance": round(float(importances.get(col, 0)), 1),
                "description": desc,
            })

        features.sort(key=lambda x: x['importance'], reverse=True)

        # Success probability based on recent trend consistency
        recent = df_copy['returns'].tail(20).dropna()
        consistency = float((recent > 0).mean() * 100)
        prob = round(min(max(consistency, 30), 95), 1)

        # Explanation
        trend = "alta" if df_copy['returns'].tail(5).mean() > 0 else "baixa"
        top_feat = features[0]['feature'] if features else "N/A"
        explanation = (
            f"O mercado está em uma tendência de {trend}. "
            f"O indicador mais relevante é {top_feat} com {features[0]['importance']:.0f}% de importância. "
            f"Baseado em {len(df_clean)} amostras históricas, a probabilidade de continuação é de {prob}%."
        )

        return {
            "features": features,
            "successProbability": prob,
            "explanation": explanation,
        }


backtest_engine = BacktestEngine()
