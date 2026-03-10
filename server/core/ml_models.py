import pandas as pd
from typing import Dict, List
import logging
from .feature_engineer import feature_engineer

logger = logging.getLogger(__name__)


class MLModels:
    def __init__(self):
        self.regime_model = None

    def detect_regime(self, df: pd.DataFrame) -> Dict:
        """
        Detect market regime using the advanced FeatureEngineer HMM.
        """
        try:
            # 1. Compute advanced features
            df_feat = feature_engineer.compute_all_features(df)
            
            # 2. Detect regime using HMM from FeatureEngineer
            df_regime = feature_engineer.detect_regime_hmm(df_feat)
            
            curr_regime_id = int(df_regime['regime'].iloc[-1])
            
            # Map regime IDs to human readable types
            # FeatureEngineer HMM returns 0, 1, 2...
            regime_map = {0: "range", 1: "trend_up", 2: "trend_down"}
            regime_type = regime_map.get(curr_regime_id, "range")
            
            # 3. Extract metrics
            adx_val = df_regime['adx'].iloc[-1] if 'adx' in df_regime.columns else 25
            volatility = df_regime['atr_14'].iloc[-1] / df_regime['close'].iloc[-1] if 'atr_14' in df_regime.columns else 0
            
            vol_profile = "Estável"
            if 'volume_ratio' in df_regime.columns:
                vr = df_regime['volume_ratio'].iloc[-1]
                if vr > 1.2: vol_profile = "Crescente"
                elif vr < 0.8: vol_profile = "Decrescente"

            return {
                "type": regime_type,
                "confidence": 85, # HMM is generally more stable now
                "indicators": {
                    "adx": round(float(adx_val), 1),
                    "volatility": round(float(volatility * 100), 4),
                    "volumeProfile": vol_profile,
                },
            }
        except Exception as e:
            logger.error(f"Error in detect_regime: {e}")
            return {"type": "range", "confidence": 50, "indicators": {"adx": 25, "volatility": 0, "volumeProfile": "N/A"}}
        except Exception as e:
            logger.error(f"Error in detect_regime: {e}")
            return {"type": "undefined", "confidence": 0, "indicators": default_indicators}

    def detect_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """Detect geometric and candlestick patterns."""
        patterns = []
        try:
            # Candlestick Patterns
            if len(df) >= 3:
                last_candle = df.iloc[-1]
                prev_candle = df.iloc[-2]
                prev_prev_candle = df.iloc[-3]
                
                body = abs(last_candle['open'] - last_candle['close'])
                upper_wick = last_candle['high'] - max(last_candle['open'], last_candle['close'])
                lower_wick = min(last_candle['open'], last_candle['close']) - last_candle['low']
                is_bullish = last_candle['close'] > last_candle['open']
                is_bearish = last_candle['close'] < last_candle['open']
                
                prev_body = abs(prev_candle['open'] - prev_candle['close'])
                prev_is_bullish = prev_candle['close'] > prev_candle['open']
                prev_is_bearish = prev_candle['close'] < prev_candle['open']
                
                range_candle = last_candle['high'] - last_candle['low']
                
                # Pin Bars (Hammer / Shooting Star equivalents)
                if lower_wick > body * 2 and upper_wick < body * 0.5:
                    patterns.append({
                        "id": "pat_hammer", "type": "candlestick", "name": "Martelo (Rej. Baixa)",
                        "timestamp": int(last_candle['time'].timestamp() * 1000),
                        "direction": "up", "frequency": 1, "accuracy": 82,
                    })

                elif upper_wick > body * 2 and lower_wick < body * 0.5:
                    patterns.append({
                        "id": "pat_shooting", "type": "candlestick", "name": "Estrela Cadente (Rej. Alta)",
                        "timestamp": int(last_candle['time'].timestamp() * 1000),
                        "direction": "down", "frequency": 1, "accuracy": 78,
                    })
                    
                # Engulfing (Engolfo)
                elif is_bullish and prev_is_bearish and body > prev_body and last_candle['close'] > prev_candle['open'] and last_candle['open'] < prev_candle['close']:
                    patterns.append({
                        "id": "pat_bull_eng", "type": "candlestick", "name": "Engolfo de Alta",
                        "timestamp": int(last_candle['time'].timestamp() * 1000),
                        "direction": "up", "frequency": 1, "accuracy": 85,
                    })
                elif is_bearish and prev_is_bullish and body > prev_body and last_candle['close'] < prev_candle['open'] and last_candle['open'] > prev_candle['close']:
                    patterns.append({
                        "id": "pat_bear_eng", "type": "candlestick", "name": "Engolfo de Baixa",
                        "timestamp": int(last_candle['time'].timestamp() * 1000),
                        "direction": "down", "frequency": 1, "accuracy": 85,
                    })
                    
                # Doji
                elif body <= (range_candle * 0.1) and range_candle > 0:
                     patterns.append({
                        "id": "pat_doji", "type": "candlestick", "name": "Doji (Indecisão)",
                        "timestamp": int(last_candle['time'].timestamp() * 1000),
                        "direction": "neutral", "frequency": 1, "accuracy": 60,
                    })
                     
                # Marubozu
                elif body >= (range_candle * 0.95) and range_candle > 0:
                     direction_str = "up" if is_bullish else "down"
                     name_str = "Marubozu de Alta" if is_bullish else "Marubozu de Baixa"
                     patterns.append({
                        "id": "pat_marubozu", "type": "candlestick", "name": name_str,
                        "timestamp": int(last_candle['time'].timestamp() * 1000),
                        "direction": direction_str, "frequency": 1, "accuracy": 88,
                    })
                     
                # 3-Candle Patterns (Morning/Evening Star approach)
                else:
                    pp_is_bearish = prev_prev_candle['close'] < prev_prev_candle['open']
                    pp_is_bullish = prev_prev_candle['close'] > prev_prev_candle['open']
                    
                    # Evening Star: Bullish, small body gap up, bearish closing well into first candle
                    if pp_is_bullish and prev_body <= (prev_candle['high'] - prev_candle['low']) * 0.3 and is_bearish and last_candle['close'] < (prev_prev_candle['open'] + prev_prev_candle['close'])/2:
                        patterns.append({
                            "id": "pat_evening_star", "type": "candlestick", "name": "Estrela da Tarde",
                            "timestamp": int(last_candle['time'].timestamp() * 1000),
                            "direction": "down", "frequency": 1, "accuracy": 89,
                        })
                    # Morning Star: Bearish, small body gap down, bullish closing well into first candle
                    elif pp_is_bearish and prev_body <= (prev_candle['high'] - prev_candle['low']) * 0.3 and is_bullish and last_candle['close'] > (prev_prev_candle['open'] + prev_prev_candle['close'])/2:
                        patterns.append({
                            "id": "pat_morning_star", "type": "candlestick", "name": "Estrela da Manhã",
                            "timestamp": int(last_candle['time'].timestamp() * 1000),
                            "direction": "up", "frequency": 1, "accuracy": 89,
                        })

            # Geometric Patterns (Support / Resistance)
            window = 20
            if len(df) > window * 2:
                df_slice = df.tail(window * 2)
                for i in range(window, len(df_slice) - window):
                    center_high = df_slice.iloc[i]['high']
                    center_low = df_slice.iloc[i]['low']
                    if all(center_high >= df_slice.iloc[i-j]['high'] for j in range(1, 3)) and \
                       all(center_high >= df_slice.iloc[i+j]['high'] for j in range(1, 3)):
                        patterns.append({
                            "id": f"geo_res_{i}", "type": "geometric", "name": "Resistência Local",
                            "timestamp": int(df_slice.iloc[i]['time'].timestamp() * 1000),
                            "direction": "down", "frequency": 1, "accuracy": 70,
                        })
                    if all(center_low <= df_slice.iloc[i-j]['low'] for j in range(1, 3)) and \
                       all(center_low <= df_slice.iloc[i+j]['low'] for j in range(1, 3)):
                        patterns.append({
                            "id": f"geo_sup_{i}", "type": "geometric", "name": "Suporte Local",
                            "timestamp": int(df_slice.iloc[i]['time'].timestamp() * 1000),
                            "direction": "up", "frequency": 1, "accuracy": 72,
                        })
        except Exception as e:
            logger.error(f"Error in detect_patterns: {e}")

        return patterns[-5:]

    def get_recommendation(self, regime_type: str) -> Dict:
        """Get a quick strategy recommendation based on market regime."""
        recommendations = {
            "trend_up": {
                "strategy": "EMA Crossover",
                "reason": "O mercado está em tendência de alta clara. Estratégias de cruzamento tendem a performar melhor aqui.",
                "confidence": 85
            },
            "trend_down": {
                "strategy": "EMA Crossover / Bollinger",
                "reason": "Tendência de baixa detectada. Cruzamentos ou rompimentos de volatilidade são ideais.",
                "confidence": 82
            },
            "range": {
                "strategy": "RSI Reversal",
                "reason": "Mercado lateralizado. Estratégias de reversão à média (oversold/overbought) têm maior probabilidade.",
                "confidence": 78
            }
        }
        return recommendations.get(regime_type, {
            "strategy": "Aguardar Confirmação",
            "reason": "Regime incerto. Recomenda-se aguardar uma definição clara de tendência ou volatilidade.",
            "confidence": 50
        })


ml_models = MLModels()
