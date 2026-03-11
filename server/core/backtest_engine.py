import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class BacktestEngine:
    """Vectorized backtesting engine with real WFA, CPCV, and Monte Carlo validation."""

    STRATEGY_TEMPLATES = [
        {"family": "ema_trend", "name": "EMA Trend", "type": "trend"},
        {"family": "rsi_reversal", "name": "RSI Reversal", "type": "reversal"},
        {"family": "bb_breakout", "name": "Bollinger Breakout", "type": "breakout"},
        {"family": "momentum_scalper", "name": "Momentum Scalper", "type": "scalping"},
        {"family": "mean_reversion", "name": "Mean Reversion %B", "type": "mean_reversion"},
        {"family": "donchian_breakout", "name": "Donchian Breakout", "type": "donchian"},
    ]

    def _extract_microstructure(self, market_context: Optional[Dict]) -> Dict:
        if not market_context:
            return {}
        if isinstance(market_context, dict) and isinstance(market_context.get('microstructure'), dict):
            return market_context['microstructure']
        return market_context if isinstance(market_context, dict) else {}

    def _apply_microstructure_timing(self, df: pd.DataFrame, signals: pd.Series, strategy_type: str, market_context: Optional[Dict] = None) -> pd.Series:
        """Filter entries when current tick pressure/spread and active hours disagree with the setup."""
        micro = self._extract_microstructure(market_context)
        if not micro:
            return signals

        adjusted = signals.astype(float).copy()
        pressure_bias = str(micro.get('pressureBias', 'indefinido'))
        spread_state = str(micro.get('spreadState', 'normal'))
        active_bursts = micro.get('activeBursts', []) or []

        if 'time' in df.columns and active_bursts:
            preferred_hours = set()
            for burst in active_bursts[:2]:
                label = str(burst.get('label', ''))
                try:
                    preferred_hours.add(int(label.split(':')[0]))
                except Exception:
                    continue
            if preferred_hours:
                active_hours = df['time'].dt.hour.isin(preferred_hours)
                if strategy_type in ('scalping', 'breakout', 'donchian'):
                    adjusted = adjusted.where(active_hours, 0)
                elif strategy_type == 'trend':
                    adjusted = adjusted.where(active_hours | (adjusted == 0), adjusted * 0.5)

        if pressure_bias == 'compradora':
            if strategy_type in ('trend', 'breakout', 'donchian', 'scalping'):
                adjusted = adjusted.where(adjusted >= 0, 0)
            elif strategy_type in ('reversal', 'mean_reversion'):
                adjusted = adjusted.where(adjusted <= 0, adjusted)
                adjusted = adjusted.where(adjusted >= 0, adjusted * 0.5)
        elif pressure_bias == 'vendedora':
            if strategy_type in ('trend', 'breakout', 'donchian', 'scalping'):
                adjusted = adjusted.where(adjusted <= 0, 0)
            elif strategy_type in ('reversal', 'mean_reversion'):
                adjusted = adjusted.where(adjusted >= 0, adjusted)
                adjusted = adjusted.where(adjusted <= 0, adjusted * 0.5)
        elif pressure_bias == 'balanceada' and strategy_type in ('trend', 'breakout', 'donchian'):
            adjusted = adjusted.where(adjusted == 0, adjusted * 0.75)

        if spread_state == 'alargado':
            if strategy_type == 'scalping':
                adjusted[:] = 0
            elif strategy_type in ('breakout', 'donchian'):
                adjusted = adjusted * 0.5
        elif spread_state == 'apertado' and strategy_type == 'scalping':
            adjusted = adjusted.where(adjusted == 0, adjusted * 1.0)

        return adjusted.fillna(0).clip(-1, 1)

    def _generate_signals(self, df: pd.DataFrame, strategy_type: str, params: Dict, market_context: Optional[Dict] = None) -> pd.Series:
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

        base_signals = pd.Series(signals, index=df.index)
        return self._apply_microstructure_timing(df, base_signals, strategy_type, market_context=market_context)

    def _compute_metrics(self, equity_curve: pd.Series, signals: pd.Series, initial_balance: float = 10000, fast: bool = False) -> Dict:
        """Compute real strategy metrics from equity curve."""
        returns = equity_curve.pct_change().dropna()
        if returns.empty:
            return {"sharpeIS": -1, "profitFactor": 0, "winRate": 0, "maxDrawdown": 100}

        total_return = (equity_curve.iloc[-1] / initial_balance) - 1
        drawdown = (equity_curve.cummax() - equity_curve) / equity_curve.cummax()
        max_dd = float(drawdown.max())

        # Sharpe (annualized)
        sharpe = float(returns.mean() / (returns.std() + 1e-10) * np.sqrt(252))

        if fast:
            return {
                "sharpeIS": round(sharpe, 2),
                "maxDrawdown": round(max_dd * 100, 2),
                "totalReturn": round(total_return * 100, 1)
            }

        # Sortino
        downside = returns[returns < 0]
        if len(downside) > 2:
            sortino = float(returns.mean() / (downside.std() + 1e-10) * np.sqrt(252))
        else:
            sortino = 0.0

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

    def run_backtest(self, df: pd.DataFrame, strategy_type: str, params: Dict, symbol_name: str = "EURUSD", fast: bool = False, market_context: Optional[Dict] = None) -> Dict:
        """Run a vectorized backtest. If fast=True, skip curve formatting and return minimal metrics."""
        try:
            signals = self._generate_signals(df, strategy_type, params, market_context=market_context)
            initial_balance = 10000
            close = df['close']
            returns = close.pct_change()
            
            pip_size = 0.0001 if symbol_name and ("JPY" not in symbol_name and "BTC" not in symbol_name and "XAU" not in symbol_name) else 0.01
            if "XAU" in symbol_name: pip_size = 0.1 
            if "BTC" in symbol_name: pip_size = 1.0 
            
            sl_pips = params.get('stopLoss', 0)
            tp_pips = params.get('takeProfit', 0)
            
            strategy_returns = signals.shift(1) * returns
            
            if sl_pips > 0 or tp_pips > 0:
                high = df['high']
                low = df['low']
                entry_prices = close.where(signals.diff().abs() > 0).ffill()
                
                if sl_pips > 0:
                    sl_dist = sl_pips * pip_size
                    long_sl_hit = (signals.shift(1) == 1) & (low < (entry_prices - sl_dist))
                    short_sl_hit = (signals.shift(1) == -1) & (high > (entry_prices + sl_dist))
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

            metrics = self._compute_metrics(equity_curve, signals, initial_balance, fast=fast)
            
            if fast:
                return metrics

            drawdown = (equity_curve.cummax() - equity_curve) / equity_curve.cummax()
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
    def run_wfa(self, df: pd.DataFrame, strategy_type: str, params: Dict, symbol_name: str = "EURUSD", n_windows: int = 5) -> Dict:
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
    def run_cpcv(self, df: pd.DataFrame, strategy_type: str, params: Dict, symbol_name: str = "EURUSD", n_folds: int = 6, embargo: int = 5) -> Dict:
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
    def run_monte_carlo(self, df: pd.DataFrame, strategy_type: str, params: Dict, symbol_name: str = "EURUSD", n_simulations: int = 10000) -> Dict:
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
    def _compute_pbo(self, cpcv: Dict) -> float:
        """Approximate probability of overfitting from CPCV dispersion."""
        avg_sharpe = float(cpcv.get('avgSharpe', 0) or 0)
        sharpe_std = float(cpcv.get('sharpeStd', 0) or 0)
        if avg_sharpe == 0 and sharpe_std == 0:
            return 100.0
        return round(float(min((sharpe_std / (abs(avg_sharpe) + 1e-10)) * 100, 100)), 1)

    def _microstructure_validation_adjustment(self, market_context: Optional[Dict], strategy_type: str) -> Dict:
        """Adjust validation score when tick pressure/spread supports or weakens the setup."""
        if not market_context:
            return {'score': 0, 'reason': 'Sem ajuste microestrutural'}

        pressure_bias = str(market_context.get('pressureBias', 'indefinido'))
        spread_state = str(market_context.get('spreadState', 'normal'))
        score = 0
        reasons = []

        if strategy_type in ('trend', 'breakout', 'donchian') and pressure_bias in ('compradora', 'vendedora'):
            score += 1
            reasons.append('Ticks confirmam direcionalidade')
        if strategy_type in ('reversal', 'mean_reversion') and pressure_bias == 'balanceada':
            score += 1
            reasons.append('Fluxo equilibrado favorece reversao')
        if strategy_type == 'scalping' and spread_state == 'apertado':
            score += 1
            reasons.append('Spread apertado favorece scalp')
        if strategy_type == 'scalping' and spread_state == 'alargado':
            score -= 1
            reasons.append('Spread alargado penaliza scalp')
        if strategy_type in ('trend', 'breakout', 'donchian') and spread_state == 'alargado':
            score -= 1
            reasons.append('Spread largo aumenta friccao de entrada')

        return {'score': score, 'reason': '; '.join(reasons) if reasons else 'Ajuste neutro'}

    def _classify_strategy_status(self, wfa: Dict, cpcv: Dict, mc: Dict, pbo: float, strategy_type: str = "trend", market_context: Optional[Dict] = None) -> str:
        """Apply PRD-aligned robustness gates for approved/testing/rejected."""
        oos_cagr = float(wfa.get('oosCAGR', 0) or 0)
        is_cagr = float(wfa.get('isCAGR', 0) or 0)
        avg_sharpe = float(cpcv.get('avgSharpe', 0) or 0)
        profitable_pct = float(mc.get('profitablePct', 0) or 0)

        min_checks = [
            oos_cagr > 0,
            avg_sharpe > 1.0,
            profitable_pct >= 95.0,
            pbo < 50.0,
        ]

        ideal_checks = [
            is_cagr > 0 and oos_cagr >= (0.7 * is_cagr),
            avg_sharpe > 1.5,
            profitable_pct >= 99.0,
            pbo < 20.0,
        ]

        min_score = sum(1 for check in min_checks if check)
        ideal_score = sum(1 for check in ideal_checks if check)
        micro_adj = self._microstructure_validation_adjustment(market_context, strategy_type)
        min_score += max(-1, min(1, int(micro_adj['score'])))

        if min_score >= len(min_checks):
            return 'approved'
        if min_score >= 2 or ideal_score >= 1:
            return 'testing'
        return 'rejected'

    def _estimate_pip_size(self, symbol_name: str = "EURUSD") -> float:
        symbol = (symbol_name or "").upper()
        if "BTC" in symbol or "ETH" in symbol:
            return 1.0
        if "XAU" in symbol or "GOLD" in symbol:
            return 0.1
        if "JPY" in symbol:
            return 0.01
        return 0.0001

    def _infer_market_context(self, df: pd.DataFrame, symbol_name: str = "EURUSD", microstructure: Optional[Dict] = None) -> Dict:
        """Summarize the current market so discovery can propose context-aware candidates."""
        tail = df.tail(min(len(df), 250)).copy()
        close = tail['close']
        high = tail['high']
        low = tail['low']
        returns = close.pct_change().dropna()

        ema_fast = close.ewm(span=20, adjust=False).mean()
        ema_slow = close.ewm(span=50, adjust=False).mean()
        trend_gap = float(((ema_fast.iloc[-1] / (ema_slow.iloc[-1] + 1e-10)) - 1) * 100)
        trend_strength = float(min(abs(trend_gap) * 18, 1.0))

        recent_window = min(20, len(close))
        range_high = float(close.tail(recent_window).max())
        range_low = float(close.tail(recent_window).min())
        range_span = max(range_high - range_low, 1e-10)
        price_position = float((close.iloc[-1] - range_low) / range_span)

        recent_range = ((high - low) / (close + 1e-10)).tail(50)
        atr_pct = float(recent_range.median() * 100) if not recent_range.empty else 0.1
        return_vol = float(returns.tail(50).std() * 100) if not returns.empty else 0.0

        if trend_gap > 0.08:
            direction = 'trend_up'
        elif trend_gap < -0.08:
            direction = 'trend_down'
        else:
            direction = 'range'

        if atr_pct < 0.12:
            volatility_bucket = 'low'
        elif atr_pct < 0.45:
            volatility_bucket = 'medium'
        else:
            volatility_bucket = 'high'

        breakout_pressure = float(min(max(abs(price_position - 0.5) * 2 + trend_strength * 0.35, 0), 1))
        range_score = float(min(max(1.0 - trend_strength + (0.25 if 0.25 <= price_position <= 0.75 else 0.0), 0), 1))

        pip_size = self._estimate_pip_size(symbol_name)
        avg_bar_move = float((high - low).tail(30).median()) if len(tail) >= 10 else float(close.iloc[-1] * 0.001)
        base_stop = max(8, int(round(avg_bar_move / (pip_size + 1e-10))))
        base_target = max(base_stop + 5, int(round(base_stop * (1.8 if direction == 'range' else 2.4))))

        context = {
            'direction': direction,
            'trendStrength': round(trend_strength, 3),
            'rangeScore': round(range_score, 3),
            'breakoutPressure': round(breakout_pressure, 3),
            'pricePosition': round(price_position, 3),
            'atrPct': round(atr_pct, 4),
            'returnVolPct': round(return_vol, 4),
            'volatilityBucket': volatility_bucket,
            'baseStopLoss': base_stop,
            'baseTakeProfit': base_target,
        }
        if microstructure:
            context['microstructure'] = microstructure
            pressure_bias = str(microstructure.get('pressureBias', 'indefinido'))
            context['pressureBias'] = pressure_bias
            context['uptickRatio'] = float(microstructure.get('uptickRatio', 0) or 0)
            context['spreadState'] = str(microstructure.get('spreadState', 'normal'))
            if pressure_bias in ('compradora', 'vendedora'):
                context['trendStrength'] = round(min(context['trendStrength'] + 0.08, 1.0), 3)
                context['breakoutPressure'] = round(min(context['breakoutPressure'] + 0.06, 1.0), 3)
            elif pressure_bias == 'balanceada':
                context['rangeScore'] = round(min(context['rangeScore'] + 0.08, 1.0), 3)
            if context['spreadState'] == 'alargado':
                context['volatilityBucket'] = 'high'
                context['baseStopLoss'] = max(context['baseStopLoss'], int(context['baseStopLoss'] * 1.2))
                context['baseTakeProfit'] = max(context['baseTakeProfit'], int(context['baseTakeProfit'] * 1.2))
        return context

    def _build_candidate(self, family: str, strategy_type: str, name: str, params: Dict, indicators: List[str], priority: float) -> Dict:
        readable = '_'.join(f"{key}_{str(value).replace('.', '_')}" for key, value in sorted(params.items()))
        return {
            'id': f"disc_{family}_{readable}",
            'family': family,
            'name': name,
            'type': strategy_type,
            'parameters': params,
            'indicators': indicators,
            'priority': priority,
        }

    def _generate_dynamic_candidates(self, df: pd.DataFrame, symbol_name: str = "EURUSD", microstructure: Optional[Dict] = None) -> (List[Dict], Dict):
        """Generate parameterized candidates instead of scoring a fixed menu of strategies."""
        context = self._infer_market_context(df, symbol_name, microstructure=microstructure)
        stop_base = max(10, context['baseStopLoss'])
        tp_base = max(stop_base + 5, context['baseTakeProfit'])

        trend_bias = 0.25 if context['direction'] != 'range' else -0.05
        range_bias = 0.25 if context['rangeScore'] >= 0.55 else -0.05
        breakout_bias = 0.20 if context['breakoutPressure'] >= 0.55 else 0.0
        scalping_bias = 0.15 if context['volatilityBucket'] in ('low', 'medium') else -0.1
        pressure_bias = str(context.get('pressureBias', 'indefinido'))
        spread_state = str(context.get('spreadState', 'normal'))
        if pressure_bias in ('compradora', 'vendedora'):
            trend_bias += 0.1
            breakout_bias += 0.08
        if pressure_bias == 'balanceada':
            range_bias += 0.08
        if spread_state == 'apertado':
            scalping_bias += 0.08
        elif spread_state == 'alargado':
            scalping_bias -= 0.18

        candidates = []

        trend_pairs = [(5, 21), (9, 34), (12, 55)]
        if context['volatilityBucket'] == 'high':
            trend_pairs.append((18, 72))
        for fast, slow in trend_pairs:
            params = {
                'fastEMA': fast,
                'slowEMA': slow,
                'stopLoss': stop_base,
                'takeProfit': max(tp_base, int(stop_base * 2.2)),
            }
            candidates.append(self._build_candidate(
                'ema_trend',
                'trend',
                f"EMA Trend {fast}x{slow}",
                params,
                [f"EMA({fast})", f"EMA({slow})"],
                1.0 + trend_bias,
            ))

        reversal_sets = [(7, 78, 22), (14, 72, 28), (21, 68, 32)]
        for period, ob, os_val in reversal_sets:
            params = {
                'rsiPeriod': period,
                'overbought': ob,
                'oversold': os_val,
                'stopLoss': max(8, int(stop_base * 0.9)),
                'takeProfit': max(12, int(tp_base * 0.85)),
            }
            candidates.append(self._build_candidate(
                'rsi_reversal',
                'reversal',
                f"RSI Reversal {period}",
                params,
                [f"RSI({period})"],
                1.0 + range_bias,
            ))

        breakout_sets = [(14, 1.8), (20, 2.0), (30, 2.4)]
        for period, std_dev in breakout_sets:
            params = {
                'bbPeriod': period,
                'bbStd': std_dev,
                'stopLoss': max(12, int(stop_base * 1.1)),
                'takeProfit': max(18, int(tp_base * 1.1)),
            }
            candidates.append(self._build_candidate(
                'bb_breakout',
                'breakout',
                f"Bollinger Breakout {period}/{std_dev}",
                params,
                [f"BB({period},{std_dev})"],
                0.95 + breakout_bias,
            ))

        scalper_sets = [(3, 8, 5), (5, 13, 7), (8, 21, 9)]
        for fast, slow, rsi_period in scalper_sets:
            params = {
                'fastEMA': fast,
                'slowEMA': slow,
                'rsiPeriod': rsi_period,
                'stopLoss': max(6, int(stop_base * 0.5)),
                'takeProfit': max(10, int(tp_base * 0.45)),
            }
            candidates.append(self._build_candidate(
                'momentum_scalper',
                'scalping',
                f"Momentum Scalper {fast}/{slow}",
                params,
                [f"EMA({fast})", f"EMA({slow})", f"RSI({rsi_period})"],
                0.9 + scalping_bias,
            ))

        mean_rev_sets = [(14, 1.8), (20, 2.0), (30, 2.2)]
        for period, std_dev in mean_rev_sets:
            params = {
                'period': period,
                'std': std_dev,
                'stopLoss': max(8, int(stop_base * 0.8)),
                'takeProfit': max(14, int(tp_base * 0.75)),
            }
            candidates.append(self._build_candidate(
                'mean_reversion',
                'mean_reversion',
                f"Mean Reversion %B {period}/{std_dev}",
                params,
                [f"BB %B ({period}, {std_dev})"],
                0.95 + range_bias,
            ))

        donchian_periods = [10, 20, 30]
        if context['direction'] != 'range':
            donchian_periods.append(55)
        for period in donchian_periods:
            params = {
                'period': period,
                'stopLoss': max(12, int(stop_base * 1.15)),
                'takeProfit': max(20, int(tp_base * 1.25)),
            }
            candidates.append(self._build_candidate(
                'donchian_breakout',
                'donchian',
                f"Donchian Breakout {period}",
                params,
                [f"Donchian Channel({period})"],
                1.0 + max(trend_bias, breakout_bias),
            ))

        deduped = []
        seen = set()
        for candidate in candidates:
            if candidate['id'] in seen:
                continue
            seen.add(candidate['id'])
            deduped.append(candidate)

        return deduped, context

    def _score_fast_candidate(self, metrics: Dict, candidate: Dict, context: Dict) -> float:
        sharpe = float(metrics.get('sharpeIS', -2) or -2)
        total_return = float(metrics.get('totalReturn', -50) or -50)
        max_drawdown = float(metrics.get('maxDrawdown', 100) or 100)

        alignment_bonus = 0.0
        strategy_type = candidate['type']
        if strategy_type in ('trend', 'donchian', 'breakout') and context['direction'] != 'range':
            alignment_bonus += 8.0
        if strategy_type in ('reversal', 'mean_reversion') and context['rangeScore'] >= 0.5:
            alignment_bonus += 8.0
        if strategy_type == 'scalping' and context['volatilityBucket'] in ('low', 'medium'):
            alignment_bonus += 5.0
        if strategy_type in ('breakout', 'donchian') and context['breakoutPressure'] >= 0.55:
            alignment_bonus += 4.0
        pressure_bias = str(context.get('pressureBias', 'indefinido'))
        if pressure_bias in ('compradora', 'vendedora') and strategy_type in ('trend', 'breakout', 'donchian'):
            alignment_bonus += 4.0
        if pressure_bias == 'balanceada' and strategy_type in ('reversal', 'mean_reversion'):
            alignment_bonus += 4.0
        if str(context.get('spreadState', 'normal')) == 'apertado' and strategy_type == 'scalping':
            alignment_bonus += 5.0
        if str(context.get('spreadState', 'normal')) == 'alargado' and strategy_type == 'scalping':
            alignment_bonus -= 6.0

        return round(
            sharpe * 18.0
            + total_return * 1.2
            - max_drawdown * 1.5
            + alignment_bonus
            + float(candidate.get('priority', 0) or 0) * 5.0,
            2,
        )

    def _select_top_candidates(self, scored_candidates: List[Dict], limit: int = 10, max_per_type: int = 2) -> List[Dict]:
        selected = []
        counts = {}

        for item in sorted(scored_candidates, key=lambda x: x['fastScore'], reverse=True):
            strategy_type = item['candidate']['type']
            if counts.get(strategy_type, 0) >= max_per_type:
                continue
            selected.append(item)
            counts[strategy_type] = counts.get(strategy_type, 0) + 1
            if len(selected) >= limit:
                break

        if len(selected) < min(limit, len(scored_candidates)):
            seen_ids = {item['candidate']['id'] for item in selected}
            for item in sorted(scored_candidates, key=lambda x: x['fastScore'], reverse=True):
                if item['candidate']['id'] in seen_ids:
                    continue
                selected.append(item)
                if len(selected) >= limit:
                    break

        return selected

    def discover_strategies(self, df: pd.DataFrame, symbol_name: str = "EURUSD", microstructure: Optional[Dict] = None) -> List[Dict]:
        """Generate, pre-filter, validate, and rank dynamic strategy candidates."""
        results = []
        candidates, market_context = self._generate_dynamic_candidates(df, symbol_name=symbol_name, microstructure=microstructure)
        scored_candidates = []

        for candidate in candidates:
            try:
                fast_metrics = self.run_backtest(
                    df,
                    candidate['type'],
                    candidate['parameters'],
                    symbol_name=symbol_name,
                    fast=True,
                    market_context=market_context,
                )
                if fast_metrics.get('maxDrawdown', 100) >= 80:
                    continue
                fast_score = self._score_fast_candidate(fast_metrics, candidate, market_context)
                scored_candidates.append({
                    'candidate': candidate,
                    'fastMetrics': fast_metrics,
                    'fastScore': fast_score,
                })
            except Exception as e:
                logger.error(f"Error scoring candidate {candidate['name']}: {e}")

        finalists = self._select_top_candidates(scored_candidates, limit=10, max_per_type=2)

        for item in finalists:
            candidate = item['candidate']
            try:
                signals = self._generate_signals(df, candidate['type'], candidate['parameters'], market_context=market_context)
                returns = df['close'].pct_change()
                strategy_returns = signals.shift(1) * returns
                equity_curve = (1 + strategy_returns).cumprod() * 10000
                equity_curve = equity_curve.ffill().fillna(10000)

                metrics = self._compute_metrics(equity_curve, signals)
                wfa = self.run_wfa(df, candidate['type'], candidate['parameters'], symbol_name=symbol_name, n_windows=3)
                cpcv = self.run_cpcv(df, candidate['type'], candidate['parameters'], symbol_name=symbol_name, n_folds=6, embargo=5)
                mc = self.run_monte_carlo(df, candidate['type'], candidate['parameters'], symbol_name=symbol_name, n_simulations=500)
                pbo = self._compute_pbo(cpcv)

                metrics['wfe'] = wfa['efficiency']
                metrics['sharpeOOS'] = max(wfa.get('oosSharpe', 0), cpcv.get('avgSharpe', 0))
                metrics['maxDrawdownMC'] = mc.get('maxDrawdownP95', 0)

                status = self._classify_strategy_status(wfa, cpcv, mc, pbo, strategy_type=candidate['type'], market_context=market_context)
                results.append({
                    'id': candidate['id'],
                    'name': candidate['name'],
                    'type': candidate['type'],
                    'parameters': candidate['parameters'],
                    'indicators': candidate['indicators'],
                    'metrics': metrics,
                    'status': status,
                    'validation': {
                        'wfa': wfa,
                        'cpcv': cpcv,
                        'monteCarlo': mc,
                        'pbo': pbo,
                        'microstructure': market_context.get('microstructure') if isinstance(market_context, dict) else None,
                        'microstructureAdjustment': self._microstructure_validation_adjustment(market_context, candidate['type']),
                    },
                    'discoveryMeta': {
                        'marketContext': market_context,
                        'fastScore': item['fastScore'],
                        'fastMetrics': item['fastMetrics'],
                        'family': candidate['family'],
                    },
                    'createdAt': int(pd.Timestamp.now().timestamp() * 1000),
                })
            except Exception as e:
                logger.error(f"Error validating candidate {candidate['name']}: {e}")

        status_rank = {'approved': 2, 'testing': 1, 'rejected': 0}
        results.sort(
            key=lambda x: (
                status_rank.get(x['status'], 0),
                x['metrics'].get('wfe', 0),
                x['metrics'].get('sharpeOOS', 0),
                -x['metrics'].get('maxDrawdownMC', 100),
                x.get('discoveryMeta', {}).get('fastScore', 0),
            ),
            reverse=True,
        )
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

        # Custom sessions for heatmap based on market type
        # Forex/Crypto: 0-23, Stock: 9-18
        is_crypto = "BTC" in df_copy.columns or "ETH" in df_copy.columns or (hasattr(df_copy, 'name') and "USD" in str(df_copy.name)) # Simplified
        
        hours = list(range(0, 24)) if is_crypto else list(range(9, 21))
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
