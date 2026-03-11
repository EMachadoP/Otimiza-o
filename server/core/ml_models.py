import logging
from typing import Dict, List

import numpy as np
import pandas as pd

from .feature_engineer import feature_engineer

logger = logging.getLogger(__name__)


class MLModels:
    def __init__(self):
        self.regime_model = None

    def _prepare_feature_frame(self, df: pd.DataFrame) -> pd.DataFrame:
        df_feat = feature_engineer.compute_all_features(df)
        df_feat = feature_engineer.detect_regime_hmm(df_feat)
        if 'future_return' not in df_feat.columns:
            df_feat['future_return'] = df_feat['close'].pct_change().shift(-1)
        if 'future_return_3' not in df_feat.columns:
            df_feat['future_return_3'] = df_feat['close'].pct_change(3).shift(-3)
        return df_feat

    def detect_regime(self, df: pd.DataFrame) -> Dict:
        """Detect market regime using the advanced FeatureEngineer HMM."""
        try:
            df_regime = self._prepare_feature_frame(df)
            curr_regime_id = int(df_regime['regime'].iloc[-1])
            regime_map = {0: 'range', 1: 'trend_up', 2: 'trend_down'}
            regime_type = regime_map.get(curr_regime_id, 'range')

            adx_val = df_regime['adx'].iloc[-1] if 'adx' in df_regime.columns else 25
            volatility = df_regime['atr_14'].iloc[-1] / df_regime['close'].iloc[-1] if 'atr_14' in df_regime.columns else 0

            vol_profile = 'Estavel'
            if 'volume_ratio' in df_regime.columns:
                vr = df_regime['volume_ratio'].iloc[-1]
                if vr > 1.2:
                    vol_profile = 'Crescente'
                elif vr < 0.8:
                    vol_profile = 'Decrescente'

            return {
                'type': regime_type,
                'confidence': 85,
                'indicators': {
                    'adx': round(float(adx_val), 1),
                    'volatility': round(float(volatility * 100), 4),
                    'volumeProfile': vol_profile,
                },
            }
        except Exception as e:
            logger.error(f'Error in detect_regime: {e}')
            return {'type': 'range', 'confidence': 50, 'indicators': {'adx': 25, 'volatility': 0, 'volumeProfile': 'N/A'}}

    def _make_pattern(self, pattern_id: str, pattern_type: str, name: str, candle: pd.Series, direction: str, accuracy: float, frequency: float, price_target=None) -> Dict:
        return {
            'id': pattern_id,
            'type': pattern_type,
            'name': name,
            'timestamp': int(pd.Timestamp(candle['time']).timestamp() * 1000),
            'direction': direction,
            'frequency': round(float(frequency), 1),
            'accuracy': round(float(accuracy), 1),
            'priceTarget': round(float(price_target), 5) if price_target is not None else None,
        }

    def detect_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """Detect recurring candlestick and breakout patterns with simple historical scoring."""
        patterns: List[Dict] = []
        try:
            if len(df) < 30:
                return []

            work = df.copy().tail(180).reset_index(drop=True)
            work['body'] = (work['close'] - work['open']).abs()
            work['range'] = (work['high'] - work['low']).replace(0, np.nan)
            work['upper_wick'] = work['high'] - work[['open', 'close']].max(axis=1)
            work['lower_wick'] = work[['open', 'close']].min(axis=1) - work['low']
            work['future_return_3'] = work['close'].pct_change(3).shift(-3)
            work['prev_open'] = work['open'].shift(1)
            work['prev_close'] = work['close'].shift(1)
            work['rolling_high'] = work['high'].rolling(20).max().shift(1)
            work['rolling_low'] = work['low'].rolling(20).min().shift(1)

            hammer_mask = (work['lower_wick'] > work['body'] * 2.2) & (work['upper_wick'] < work['body'] * 1.2)
            shooting_mask = (work['upper_wick'] > work['body'] * 2.2) & (work['lower_wick'] < work['body'] * 1.2)
            bullish_engulf = (
                (work['close'] > work['open'])
                & (work['prev_close'] < work['prev_open'])
                & (work['close'] >= work['prev_open'])
                & (work['open'] <= work['prev_close'])
            )
            bearish_engulf = (
                (work['close'] < work['open'])
                & (work['prev_close'] > work['prev_open'])
                & (work['open'] >= work['prev_close'])
                & (work['close'] <= work['prev_open'])
            )
            breakout_up = work['close'] > work['rolling_high']
            breakout_down = work['close'] < work['rolling_low']

            specs = [
                ('hammer', 'candlestick', 'Martelo', hammer_mask, 'up', work['future_return_3']),
                ('shooting_star', 'candlestick', 'Estrela Cadente', shooting_mask, 'down', -work['future_return_3']),
                ('bullish_engulfing', 'candlestick', 'Engolfo de Alta', bullish_engulf, 'up', work['future_return_3']),
                ('bearish_engulfing', 'candlestick', 'Engolfo de Baixa', bearish_engulf, 'down', -work['future_return_3']),
                ('breakout_up', 'channel', 'Rompimento de Maxima', breakout_up, 'up', work['future_return_3']),
                ('breakout_down', 'channel', 'Rompimento de Minima', breakout_down, 'down', -work['future_return_3']),
            ]

            for name, ptype, label, mask, direction, edge_series in specs:
                subset = work[mask.fillna(False)].copy()
                if subset.empty:
                    continue
                mask_series = mask.fillna(False)
                valid_edges = edge_series[mask_series].dropna()
                accuracy = float((valid_edges > 0).mean() * 100) if not valid_edges.empty else 50.0
                frequency = float(len(subset) / max(len(work), 1) * 100)
                last_row = subset.iloc[-1]
                avg_move = float(valid_edges.mean()) if not valid_edges.empty else 0.0
                price_target = float(last_row['close'] * (1 + avg_move)) if direction == 'up' else float(last_row['close'] * (1 - avg_move))
                patterns.append(self._make_pattern(
                    f'pat_{name}_{int(last_row.name)}',
                    ptype,
                    label,
                    last_row,
                    direction,
                    accuracy,
                    frequency,
                    price_target,
                ))
        except Exception as e:
            logger.error(f'Error in detect_patterns: {e}')

        patterns.sort(key=lambda item: (item['accuracy'], item['frequency']), reverse=True)
        return patterns[:8]

    def evaluate_indicator_scorecard(self, df: pd.DataFrame) -> List[Dict]:
        """Score main indicators by historical directional edge on the selected market/context."""
        try:
            feat = self._prepare_feature_frame(df).copy()
            feat['ema_gap'] = (feat.get('ema_9', feat['close']) - feat.get('ema_21', feat['close'])) / (feat.get('ema_21', feat['close']) + 1e-10)
            feat['macd_hist_safe'] = feat.get('macd_hist', pd.Series(index=feat.index, dtype=float)).fillna(0)
            feat['bb_percent_safe'] = feat.get('bb_percent', pd.Series(index=feat.index, dtype=float)).fillna(0.5)
            feat['dc_mid'] = (feat.get('dc_upper', feat['high']) + feat.get('dc_lower', feat['low'])) / 2
            feat['future_edge'] = feat['future_return_3'].fillna(feat['future_return'])

            scorecard_specs = [
                {
                    'indicator': 'RSI Reversal',
                    'signal': np.where(feat.get('rsi_14', 50) < 30, 1, np.where(feat.get('rsi_14', 50) > 70, -1, 0)),
                    'currentSignal': lambda row: 'Compra em sobrevenda' if row.get('rsi_14', 50) < 30 else ('Venda em sobrecompra' if row.get('rsi_14', 50) > 70 else 'Neutro'),
                    'rationale': 'Mede reversao curta quando o ativo estica demais no timeframe atual.',
                },
                {
                    'indicator': 'EMA 9x21',
                    'signal': np.where(feat['ema_gap'] > 0, 1, -1),
                    'currentSignal': lambda row: 'Tendencia compradora' if row.get('ema_gap', 0) > 0 else 'Tendencia vendedora',
                    'rationale': 'Captura alinhamento de tendencia entre impulso curto e filtro intermediario.',
                },
                {
                    'indicator': 'MACD Histograma',
                    'signal': np.where(feat['macd_hist_safe'] > 0, 1, np.where(feat['macd_hist_safe'] < 0, -1, 0)),
                    'currentSignal': lambda row: 'Momentum positivo' if row.get('macd_hist_safe', 0) > 0 else ('Momentum negativo' if row.get('macd_hist_safe', 0) < 0 else 'Neutro'),
                    'rationale': 'Mostra aceleracao ou perda de forca do movimento dominante.',
                },
                {
                    'indicator': 'Bollinger %B',
                    'signal': np.where(feat['bb_percent_safe'] < 0.1, 1, np.where(feat['bb_percent_safe'] > 0.9, -1, 0)),
                    'currentSignal': lambda row: 'Extremo inferior' if row.get('bb_percent_safe', 0.5) < 0.1 else ('Extremo superior' if row.get('bb_percent_safe', 0.5) > 0.9 else 'Centro da banda'),
                    'rationale': 'Avalia esticamento estatistico e probabilidade de reversao ou continuacao.',
                },
                {
                    'indicator': 'Donchian 20',
                    'signal': np.where(feat['close'] > feat.get('dc_upper', feat['high']).shift(1), 1, np.where(feat['close'] < feat.get('dc_lower', feat['low']).shift(1), -1, 0)),
                    'currentSignal': lambda row: 'Pressao de rompimento' if row.get('close', 0) > row.get('dc_mid', 0) else 'Pressao de perda',
                    'rationale': 'Mede rompimentos de faixa e continuidade quando o preco expande range.',
                },
                {
                    'indicator': 'ADX + Volume',
                    'signal': np.where((feat.get('adx', 0) > 23) & (feat.get('volume_ratio', 1) > 1.05), np.where(feat['ema_gap'] > 0, 1, -1), 0),
                    'currentSignal': lambda row: 'Tendencia confirmada' if row.get('adx', 0) > 23 and row.get('volume_ratio', 1) > 1.05 else 'Sem confirmacao',
                    'rationale': 'Combina forca direcional e participacao para evitar sinais fracos.',
                },
            ]

            scorecard: List[Dict] = []
            for spec in scorecard_specs:
                signal = pd.Series(spec['signal'], index=feat.index).fillna(0)
                active = signal != 0
                if active.sum() < 8:
                    continue
                directional_edge = (signal[active] * feat.loc[active, 'future_edge']).dropna()
                if directional_edge.empty:
                    continue

                hit_rate = float((directional_edge > 0).mean() * 100)
                avg_edge = float(directional_edge.mean() * 100)
                sample_size = int(len(directional_edge))
                stability = float(max(0, min(100, 50 + avg_edge * 12 + (sample_size / max(len(feat), 1)) * 100)))
                fit_score = float(max(1, min(100, hit_rate * 0.7 + stability * 0.3)))
                current_signal = spec['currentSignal'](feat.iloc[-1].to_dict())

                scorecard.append({
                    'indicator': spec['indicator'],
                    'currentSignal': current_signal,
                    'accuracy': round(hit_rate, 1),
                    'avgEdge': round(avg_edge, 3),
                    'fitScore': round(fit_score, 1),
                    'sampleSize': sample_size,
                    'rationale': spec['rationale'],
                })

            scorecard.sort(key=lambda item: (item['fitScore'], item['accuracy'], item['avgEdge']), reverse=True)
            return scorecard[:6]
        except Exception as e:
            logger.error(f'Error in evaluate_indicator_scorecard: {e}')
            return []

    def _build_feature_importance(self, df_feat: pd.DataFrame) -> List[Dict]:
        top_features = feature_engineer.select_features(df_feat, n_features=10)
        valid_top_features = [f for f in top_features if f in df_feat.columns]
        if not valid_top_features:
            return []

        corrs = df_feat[valid_top_features + ['future_return']].corr()['future_return'].abs().drop('future_return', errors='ignore')
        total_corr = corrs.sum()
        features_list = []
        for feat in valid_top_features:
            features_list.append({
                'feature': feat.upper().replace('_', ' '),
                'importance': round(float(corrs[feat] / (total_corr + 1e-10) * 100), 1),
                'description': f'Indicador tecnico avancado: {feat}'
            })
        features_list.sort(key=lambda x: x['importance'], reverse=True)
        return features_list

    def _build_active_windows(self, df_feat: pd.DataFrame) -> List[Dict]:
        if 'time' not in df_feat.columns:
            return []
        hourly = df_feat.copy()
        hourly['hour'] = hourly['time'].dt.hour
        hourly['future_edge'] = hourly['future_return_3'].fillna(hourly['future_return'])
        grouped = hourly.groupby('hour')['future_edge'].agg(['mean', 'count']).reset_index()
        grouped = grouped[grouped['count'] >= 5]
        if grouped.empty:
            return []
        grouped['score'] = grouped['mean'] * grouped['count']
        top = grouped.sort_values('score', ascending=False).head(3)
        windows = []
        for _, row in top.iterrows():
            hour = int(row['hour'])
            bias = 'Compra' if row['mean'] > 0 else 'Venda'
            windows.append({
                'label': f'{hour:02d}:00-{(hour + 1) % 24:02d}:00',
                'bias': bias,
                'edge': round(float(row['mean'] * 100), 3),
                'samples': int(row['count']),
            })
        return windows

    def _build_entry_timing(self, active_windows: List[Dict], patterns: List[Dict], microstructure: Dict, regime: Dict) -> Dict:
        """Combine recurring windows, recent patterns, and tick pressure into an execution hint."""
        best_window = active_windows[0] if active_windows else None
        top_pattern = patterns[0] if patterns else None
        pressure_bias = str(microstructure.get('pressureBias', 'indefinido'))
        spread_state = str(microstructure.get('spreadState', 'normal'))
        uptick_ratio = float(microstructure.get('uptickRatio', 0) or 0)
        regime_type = str(regime.get('type', 'undefined'))

        if top_pattern:
            trigger = top_pattern['name']
        elif regime_type in ('trend_up', 'trend_down'):
            trigger = 'Pullback curto com retomada de momentum'
        elif regime_type == 'range':
            trigger = 'Rejeicao em extremo de faixa'
        else:
            trigger = 'Aguardar candle gatilho'

        hint_parts = []
        if best_window:
            hint_parts.append(
                f"Priorize a janela {best_window['label']} com vies de {str(best_window['bias']).lower()}."
            )
        else:
            hint_parts.append('Nao ha janela historica forte o suficiente; reduza agressividade de entrada.')

        if pressure_bias in ('compradora', 'vendedora'):
            hint_parts.append(
                f"A microestrutura esta {pressure_bias} com uptick ratio de {uptick_ratio:.1f}%."
            )
        else:
            hint_parts.append('A microestrutura esta balanceada; prefira confirmacao extra antes da execucao.')

        if spread_state == 'apertado':
            hint_parts.append('Spread apertado favorece execucao imediata no gatilho.')
        elif spread_state == 'alargado':
            hint_parts.append('Spread alargado pede paciencia: espere reteste ou reducao de friccao antes de entrar.')
        else:
            hint_parts.append('Spread normal permite entrada seletiva quando padrao e janela coincidirem.')

        if top_pattern:
            hint_parts.append(f"Gatilho principal: {top_pattern['name']}.")

        return {
            'bestWindow': best_window,
            'trigger': trigger,
            'executionHint': ' '.join(hint_parts),
        }

    def analyze_microstructure(self, ticks: pd.DataFrame) -> Dict:
        """Summarize intraday pressure and spread behavior from real tick data."""
        try:
            if ticks is None or ticks.empty:
                return {
                    'pressureBias': 'indefinido',
                    'uptickRatio': 0,
                    'spreadState': 'sem ticks',
                    'avgSpread': 0,
                    'recentSpread': 0,
                    'activeBursts': [],
                }

            work = ticks.copy().tail(min(len(ticks), 20000))
            if 'bid' not in work.columns or 'ask' not in work.columns:
                return {
                    'pressureBias': 'indefinido',
                    'uptickRatio': 0,
                    'spreadState': 'ticks incompletos',
                    'avgSpread': 0,
                    'recentSpread': 0,
                    'activeBursts': [],
                }

            work['mid'] = (work['bid'] + work['ask']) / 2
            work['spread'] = (work['ask'] - work['bid']).clip(lower=0)
            work['mid_change'] = work['mid'].diff()
            work['hour'] = work['time'].dt.hour
            work['abs_move'] = work['mid_change'].abs()

            uptick_ratio = float((work['mid_change'] > 0).mean() * 100)
            if uptick_ratio >= 53:
                pressure_bias = 'compradora'
            elif uptick_ratio <= 47:
                pressure_bias = 'vendedora'
            else:
                pressure_bias = 'balanceada'

            avg_spread = float(work['spread'].median())
            recent_spread = float(work['spread'].tail(200).median()) if len(work) >= 200 else avg_spread
            if recent_spread <= avg_spread * 1.1:
                spread_state = 'apertado'
            elif recent_spread >= avg_spread * 1.5:
                spread_state = 'alargado'
            else:
                spread_state = 'normal'

            bursts = work.groupby('hour').agg(
                tick_count=('mid', 'count'),
                avg_move=('abs_move', 'mean'),
                signed_move=('mid_change', 'mean'),
                avg_spread=('spread', 'mean'),
            ).reset_index()
            bursts = bursts[bursts['tick_count'] >= 20]
            bursts['burst_score'] = bursts['tick_count'] * bursts['avg_move']
            bursts = bursts.sort_values('burst_score', ascending=False).head(3)

            active_bursts = []
            for _, row in bursts.iterrows():
                active_bursts.append({
                    'label': f"{int(row['hour']):02d}:00-{(int(row['hour']) + 1) % 24:02d}:00",
                    'bias': 'compra' if row['signed_move'] >= 0 else 'venda',
                    'tickCount': int(row['tick_count']),
                    'avgSpread': round(float(row['avg_spread']), 6),
                    'intensity': round(float(row['burst_score']), 6),
                })

            return {
                'pressureBias': pressure_bias,
                'uptickRatio': round(uptick_ratio, 1),
                'spreadState': spread_state,
                'avgSpread': round(avg_spread, 6),
                'recentSpread': round(recent_spread, 6),
                'activeBursts': active_bursts,
            }
        except Exception as e:
            logger.error(f'Error in analyze_microstructure: {e}')
            return {
                'pressureBias': 'indefinido',
                'uptickRatio': 0,
                'spreadState': 'erro',
                'avgSpread': 0,
                'recentSpread': 0,
                'activeBursts': [],
            }

    def build_ml_insights(self, df: pd.DataFrame, microstructure: Dict | None = None) -> Dict:
        """Generate indicator ranking plus playbooks that are actionable on the current chart."""
        try:
            df_feat = self._prepare_feature_frame(df)
            regime = self.detect_regime(df)
            patterns = self.detect_patterns(df)
            scorecard = self.evaluate_indicator_scorecard(df)
            features = self._build_feature_importance(df_feat)
            active_windows = self._build_active_windows(df_feat)
            micro = microstructure or {
                'pressureBias': 'indefinido',
                'uptickRatio': 0,
                'spreadState': 'sem ticks',
                'avgSpread': 0,
                'recentSpread': 0,
                'activeBursts': [],
            }

            recent_rets = df_feat['future_return'].tail(20).dropna()
            raw_prob = round(float((recent_rets > 0).mean() * 100), 1) if not recent_rets.empty else 50
            top_fit = scorecard[0]['fitScore'] if scorecard else 50
            success_probability = round(float(min(max(raw_prob * 0.6 + top_fit * 0.4, 30), 95)), 1)

            close_now = float(df_feat['close'].iloc[-1])
            atr = float(df_feat['atr_14'].iloc[-1]) if 'atr_14' in df_feat.columns and pd.notna(df_feat['atr_14'].iloc[-1]) else close_now * 0.003
            top_indicator = scorecard[0] if scorecard else None

            playbooks: List[Dict] = []
            if regime['type'] in ('trend_up', 'trend_down'):
                bias = 'long' if regime['type'] == 'trend_up' else 'short'
                playbooks.append({
                    'title': 'Continuacao de tendencia com confirmacao',
                    'bias': bias,
                    'confidence': min(95, int((top_indicator['fitScore'] if top_indicator else 55) + 10)),
                    'setup': 'Esperar recuo para media curta e confirmar retorno do momentum.',
                    'entry': f'Entrada acima/abaixo do gatilho da EMA 9 com filtro de ATR ~ {atr:.3f}.',
                    'confirmation': 'EMA 9x21 alinhada, MACD histograma na mesma direcao e ADX acima de 23.',
                    'invalidation': f'Cancelar se o preco perder {atr * 1.2:.3f} contra a direcao esperada.',
                    'holdingPeriod': '2 a 8 candles, enquanto o momentum permanecer alinhado.',
                })
            if regime['type'] == 'range' or any(item['indicator'] in ('RSI Reversal', 'Bollinger %B') for item in scorecard[:2]):
                playbooks.append({
                    'title': 'Reversao estatistica em extremos',
                    'bias': 'mean_reversion',
                    'confidence': min(90, int((scorecard[0]['accuracy'] if scorecard else 55))),
                    'setup': 'Buscar sobrecompra/sobrevenda com candle de rejeicao e retorno para o miolo da faixa.',
                    'entry': 'Entrada quando RSI volta da zona extrema ou %B retorna para dentro da banda.',
                    'confirmation': 'Martelo, engolfo ou candle de rejeicao nas proximidades da banda externa.',
                    'invalidation': f'Cancelar se o preco romper a faixa em mais de {atr:.3f}.',
                    'holdingPeriod': '1 a 4 candles, priorizando alvos curtos ate a media.',
                })
            if any(item['name'] in ('Rompimento de Maxima', 'Rompimento de Minima') for item in patterns) or regime['indicators'].get('volumeProfile') == 'Crescente':
                playbooks.append({
                    'title': 'Rompimento com expansao de range',
                    'bias': 'breakout',
                    'confidence': min(88, int((top_indicator['fitScore'] if top_indicator else 50) + 5)),
                    'setup': 'Esperar candle de expansao seguido de reteste curto sem perder a faixa rompida.',
                    'entry': 'Entrada no reteste da maxima/minima rompida com volume sustentando.',
                    'confirmation': 'Donchian ou Bollinger abrindo, volume relativo acima da media e candle fechando fora da faixa.',
                    'invalidation': 'Descartar se o rompimento voltar inteiro para dentro da faixa no candle seguinte.',
                    'holdingPeriod': '2 a 6 candles ou ate enfraquecimento do range.',
                })

            playbooks = playbooks[:3]
            explanation_parts = []
            explanation_parts.append(f"Regime atual: {regime['type']} com ADX em {regime['indicators'].get('adx', 0)}.")
            if top_indicator:
                explanation_parts.append(
                    f"O indicador mais aderente no contexto atual e {top_indicator['indicator']} com fit {top_indicator['fitScore']} e assertividade historica de {top_indicator['accuracy']}%."
                )
            if patterns:
                explanation_parts.append(f"Padrao mais relevante recente: {patterns[0]['name']} com historico de {patterns[0]['accuracy']}%.")
            if active_windows:
                explanation_parts.append(f"Janela mais favoravel detectada: {active_windows[0]['label']} com vies de {active_windows[0]['bias'].lower()}.")

            entry_timing = self._build_entry_timing(active_windows, patterns, micro, regime)
            return {
                'features': features,
                'successProbability': success_probability,
                'explanation': ' '.join(explanation_parts),
                'scorecard': scorecard,
                'playbooks': playbooks,
                'activeWindows': active_windows,
                'entryTiming': entry_timing,
                'microstructure': micro,
            }
        except Exception as e:
            logger.error(f'Error in build_ml_insights: {e}')
            return {
                'features': [],
                'successProbability': 50,
                'explanation': 'Nao foi possivel gerar os insights avancados no momento.',
                'scorecard': [],
                'playbooks': [],
                'activeWindows': [],
                'entryTiming': {'bestWindow': None, 'trigger': 'N/A', 'executionHint': 'Sem dados suficientes.'},
                'microstructure': {
                    'pressureBias': 'indefinido',
                    'uptickRatio': 0,
                    'spreadState': 'erro',
                    'avgSpread': 0,
                    'recentSpread': 0,
                    'activeBursts': [],
                },
            }

    def get_recommendation(self, regime_type: str) -> Dict:
        """Get a quick strategy recommendation based on market regime."""
        recommendations = {
            'trend_up': {
                'strategy': 'Continuacao com EMA + MACD',
                'reason': 'O mercado esta em tendencia de alta. Priorize pullbacks curtos e confirmacao de momentum.',
                'confidence': 85
            },
            'trend_down': {
                'strategy': 'Continuacao vendida / Breakout de baixa',
                'reason': 'Tendencia de baixa detectada. Rompimentos e continuacao tendem a ter melhor aderencia.',
                'confidence': 82
            },
            'range': {
                'strategy': 'RSI Reversal / Mean Reversion',
                'reason': 'Mercado lateralizado. Reversao estatistica e leitura de extremos tem maior probabilidade.',
                'confidence': 78
            }
        }
        return recommendations.get(regime_type, {
            'strategy': 'Aguardar confirmacao',
            'reason': 'Regime incerto. O ideal e esperar alinhamento entre contexto, volatilidade e candle gatilho.',
            'confidence': 50
        })


ml_models = MLModels()


