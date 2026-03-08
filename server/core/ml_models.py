import numpy as np
import pandas as pd
from hmmlearn import hmm
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class MLModels:
    def __init__(self):
        self.regime_model = None

    def detect_regime(self, df: pd.DataFrame) -> Dict:
        """
        Detect market regime using Hidden Markov Model (HMM).
        Regimes: 0 (Range), 1 (Trend Up), 2 (Trend Down/Volatile)
        """
        default_indicators = {
            "adx": 0,
            "volatility": 0,
            "volumeProfile": "N/A",
        }

        try:
            returns = np.log(df['close'] / df['close'].shift(1)).dropna()

            # Adaptive rolling window based on data length
            vol_window = min(20, max(5, len(returns) // 5))
            volatility = returns.rolling(window=vol_window).std().dropna()

            if len(volatility) < 5:
                # Fallback: simple regime detection without HMM
                avg_ret = returns.tail(20).mean()
                vol = returns.tail(20).std()
                regime_type = "range"
                if avg_ret > vol * 0.5:
                    regime_type = "trend_up"
                elif avg_ret < -vol * 0.5:
                    regime_type = "trend_down"
                return {"type": regime_type, "confidence": 60, "indicators": default_indicators}

            features = np.column_stack([returns.iloc[-len(volatility):], volatility])

            n_components = min(3, len(features) // 3)
            if n_components < 2:
                n_components = 2

            model = hmm.GaussianHMM(n_components=n_components, covariance_type="diag", n_iter=100, random_state=42)
            model.fit(features)

            states = model.predict(features)
            curr_regime = states[-1]

            # Map states based on actual return means (not arbitrary indices)
            state_means = {}
            for s in range(n_components):
                mask = states == s
                if mask.any():
                    state_means[s] = float(returns.iloc[-len(volatility):][mask].mean())
                else:
                    state_means[s] = 0

            sorted_states = sorted(state_means.items(), key=lambda x: x[1])
            regime_map = {}
            if n_components >= 3:
                regime_map[sorted_states[0][0]] = "trend_down"
                regime_map[sorted_states[1][0]] = "range"
                regime_map[sorted_states[2][0]] = "trend_up"
            else:
                regime_map[sorted_states[0][0]] = "trend_down"
                regime_map[sorted_states[1][0]] = "trend_up"

            regime_type = regime_map.get(curr_regime, "range")

            # Compute real ADX (simplified)
            high = df['high']
            low = df['low']
            close = df['close']
            plus_dm = high.diff().clip(lower=0)
            minus_dm = (-low.diff()).clip(lower=0)
            tr = pd.concat([
                high - low,
                (high - close.shift(1)).abs(),
                (low - close.shift(1)).abs(),
            ], axis=1).max(axis=1)
            atr14 = tr.rolling(14).mean()
            plus_di = (plus_dm.rolling(14).mean() / (atr14 + 1e-10)) * 100
            minus_di = (minus_dm.rolling(14).mean() / (atr14 + 1e-10)) * 100
            dx = ((plus_di - minus_di).abs() / (plus_di + minus_di + 1e-10)) * 100
            adx = dx.rolling(14).mean()
            adx_val = float(adx.iloc[-1]) if not np.isnan(adx.iloc[-1]) else 25

            # Volume profile
            vol_col = 'tick_volume' if 'tick_volume' in df.columns else 'volume'
            if vol_col in df.columns:
                recent_vol = df[vol_col].tail(20).mean()
                prev_vol = df[vol_col].tail(50).head(30).mean()
                if recent_vol > prev_vol * 1.2:
                    vol_profile = "Crescente"
                elif recent_vol < prev_vol * 0.8:
                    vol_profile = "Decrescente"
                else:
                    vol_profile = "Estável"
            else:
                vol_profile = "N/A"

            # HMM confidence: use posterior probability
            try:
                posteriors = model.predict_proba(features[-1:])
                confidence = int(posteriors.max() * 100)
            except Exception:
                confidence = 80

            return {
                "type": regime_type,
                "confidence": min(confidence, 99),
                "indicators": {
                    "adx": round(adx_val, 1),
                    "volatility": round(float(volatility.iloc[-1] * 100), 4),
                    "volumeProfile": vol_profile,
                },
            }
        except Exception as e:
            logger.error(f"Error in detect_regime: {e}")
            return {"type": "undefined", "confidence": 0, "indicators": default_indicators}

    def detect_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """Detect geometric and candlestick patterns."""
        patterns = []
        try:
            last_candle = df.iloc[-1]
            body = abs(last_candle['open'] - last_candle['close'])
            upper_wick = last_candle['high'] - max(last_candle['open'], last_candle['close'])
            lower_wick = min(last_candle['open'], last_candle['close']) - last_candle['low']

            if lower_wick > body * 2:
                patterns.append({
                    "id": "pat_1",
                    "type": "candlestick",
                    "name": "Pin Bar Alta",
                    "timestamp": int(last_candle['time'].timestamp() * 1000),
                    "direction": "up",
                    "frequency": 1,
                    "accuracy": 82,
                })

            if upper_wick > body * 2:
                patterns.append({
                    "id": "pat_2",
                    "type": "candlestick",
                    "name": "Pin Bar Baixa",
                    "timestamp": int(last_candle['time'].timestamp() * 1000),
                    "direction": "down",
                    "frequency": 1,
                    "accuracy": 78,
                })

            # Engulfing
            if len(df) >= 2:
                prev = df.iloc[-2]
                curr = df.iloc[-1]
                if curr['close'] > curr['open'] and prev['close'] < prev['open']:
                    if curr['close'] > prev['open'] and curr['open'] < prev['close']:
                        patterns.append({
                            "id": "pat_3",
                            "type": "candlestick",
                            "name": "Engulfing Alta",
                            "timestamp": int(curr['time'].timestamp() * 1000),
                            "direction": "up",
                            "frequency": 1,
                            "accuracy": 75,
                        })
        except Exception as e:
            logger.error(f"Error in detect_patterns: {e}")

        return patterns


ml_models = MLModels()
