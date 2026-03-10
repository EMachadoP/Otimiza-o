"""
RF-03: Gerar indicadores técnicos (130+) e features derivadas
"""

import pandas as pd
import numpy as np
import pandas_ta as ta
from typing import Dict, List, Optional
from hmmlearn.hmm import GaussianHMM
import logging

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Gera features técnicas avançadas para ML."""
    
    def __init__(self):
        self.feature_names = []
        
    def compute_all_features(self, df: pd.DataFrame, blocks: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Computa blocos específicos de features técnicas.
        
        Args:
            df: DataFrame original
            blocks: Lista de blocos ('trend', 'momentum', 'volatility', 'volume', 'derived', 'micro')
                   Se None, computa todos.
        """
        df = df.copy()
        
        if blocks is None:
            blocks = ['trend', 'momentum', 'volatility', 'volume', 'derived', 'micro']
            
        for block in blocks:
            try:
                if block == 'trend': df = self._add_trend_features(df)
                elif block == 'momentum': df = self._add_momentum_features(df)
                elif block == 'volatility': df = self._add_volatility_features(df)
                elif block == 'volume': df = self._add_volume_features(df)
                elif block == 'derived': df = self._add_derived_features(df)
                elif block == 'micro': df = self._add_microstructure_features(df)
            except Exception as e:
                logger.error(f"Error computing feature block '{block}': {e}")
        
        return df
    
    def _add_trend_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adiciona indicadores de tendência."""
        close = df['close']
        
        # Médias Móveis
        for period in [5, 9, 10, 12, 20, 21, 26, 50, 100, 200]:
            df[f'sma_{period}'] = ta.sma(close, length=period)
            df[f'ema_{period}'] = ta.ema(close, length=period)
        
        # MACD
        macd = ta.macd(close, fast=12, slow=26, signal=9)
        if macd is not None and not macd.empty:
            df['macd'] = macd.iloc[:, 0]
            df['macd_signal'] = macd.iloc[:, 1]
            df['macd_hist'] = macd.iloc[:, 2]
        
        # ADX
        adx = ta.adx(df['high'], df['low'], close, length=14)
        if adx is not None:
            df['adx'] = adx['ADX_14']
            df['adx_pos'] = adx['DMP_14']
            df['adx_neg'] = adx['DMN_14']
        
        # Parabolic SAR
        psar = ta.psar(df['high'], df['low'], close)
        if psar is not None:
            df['psar'] = psar['PSARl_0.02_0.2'] # Fixed key name
        
        # Ichimoku
        try:
            ichimoku, _ = ta.ichimoku(df['high'], df['low'], close)
            if ichimoku is not None:
                # Use fuzzy match for keys as they may contain period suffixes
                for col in ichimoku.columns:
                    if col.startswith('ITS'): df['ichi_tenkan'] = ichimoku[col]
                    elif col.startswith('IKS'): df['ichi_kijun'] = ichimoku[col]
                    elif col.startswith('ISA'): df['ichi_senkou_a'] = ichimoku[col]
                    elif col.startswith('ISB'): df['ichi_senkou_b'] = ichimoku[col]
        except Exception as e:
            logger.warning(f"Ichimoku failed: {e}")
        
        return df
    
    def _add_momentum_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adiciona indicadores de momentum."""
        close = df['close']
        
        # RSI
        for period in [7, 14, 21]:
            df[f'rsi_{period}'] = ta.rsi(close, length=period)
        
        # Stochastic
        stoch = ta.stoch(df['high'], df['low'], close, k=14, d=3)
        if stoch is not None:
            df['stoch_k'] = stoch['STOCHk_14_3_3']
            df['stoch_d'] = stoch['STOCHd_14_3_3']
        
        # CCI
        df['cci'] = ta.cci(df['high'], df['low'], close, length=20)
        
        # Williams %R
        df['willr'] = ta.willr(df['high'], df['low'], close, length=14)
        
        # Momentum
        df['mom'] = ta.mom(close, length=10)
        
        # ROC
        df['roc'] = ta.roc(close, length=12)
        
        # Awesome Oscillator
        df['ao'] = ta.ao(df['high'], df['low'], fast=5, slow=34)
        
        return df
    
    def _add_volatility_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adiciona indicadores de volatilidade."""
        close = df['close']
        
        # ATR
        for period in [7, 14, 21]:
            df[f'atr_{period}'] = ta.atr(df['high'], df['low'], close, length=period)
        
        # Bollinger Bands
        bb = ta.bbands(close, length=20, std=2)
        if bb is not None and not bb.empty:
            df['bb_lower'] = bb.iloc[:, 0]
            df['bb_middle'] = bb.iloc[:, 1]
            df['bb_upper'] = bb.iloc[:, 2]
            bb_range = (df['bb_upper'] - df['bb_lower'])
            df['bb_width'] = bb_range / (df['bb_middle'] + 1e-10)
            df['bb_percent'] = (close - df['bb_lower']) / (bb_range + 1e-10)
        
        # Keltner Channels
        kc = ta.kc(df['high'], df['low'], close, length=20, scalar=2)
        if kc is not None and not kc.empty:
            df['kc_upper'] = kc.iloc[:, 0]
            df['kc_lower'] = kc.iloc[:, 2]
        
        # Donchian Channels
        dc = ta.donchian(df['high'], df['low'], lower_length=20, upper_length=20)
        if dc is not None and not dc.empty:
            df['dc_upper'] = dc.iloc[:, 0]
            df['dc_lower'] = dc.iloc[:, 2]
        
        return df
    
    def _add_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adiciona indicadores de volume."""
        if 'tick_volume' not in df.columns:
            return df
        
        volume = df['tick_volume']
        close = df['close']
        
        # OBV
        df['obv'] = ta.obv(close, volume)
        
        # VWAP
        try:
            # Need hlc3 for some ta functions if available or it computes internally
            df['vwap'] = ta.vwap(df['high'], df['low'], close, volume)
        except:
            pass
        
        # MFI
        df['mfi'] = ta.mfi(df['high'], df['low'], close, volume, length=14)
        
        # Volume MA
        for period in [10, 20, 50]:
            df[f'volume_sma_{period}'] = volume.rolling(period).mean()
        
        # Volume Ratio
        df['volume_ratio'] = volume / (df['volume_sma_20'] + 1e-10)
        
        return df
    
    def _add_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adiciona features derivadas."""
        close = df['close']
        
        # Retornos
        for lag in [1, 5, 10, 21]:
            df[f'return_{lag}d'] = close.pct_change(lag)
        
        # Z-Score
        for window in [20, 50]:
            mean = close.rolling(window).mean()
            std = close.rolling(window).std()
            df[f'zscore_{window}'] = (close - mean) / (std + 1e-10)
        
        # Range
        df['range'] = df['high'] - df['low']
        df['range_pct'] = df['range'] / (close + 1e-10)
        
        # Body
        df['body'] = abs(close - df['open'])
        df['body_pct'] = df['body'] / (df['range'] + 1e-10)
        
        # Gap
        df['gap'] = df['open'] - close.shift(1)
        df['gap_pct'] = df['gap'] / (close.shift(1) + 1e-10)
        
        return df
    
    def _add_microstructure_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adiciona features de microestrutura de mercado."""
        if 'spread' in df.columns:
            df['spread_pct'] = df['spread'] / (df['close'] + 1e-10)
        
        # Volatilidade intraday
        df['intraday_vol'] = (df['high'] - df['low']) / (df['open'] + 1e-10)
        
        return df
    
    def detect_regime_hmm(self, df: pd.DataFrame, n_states: int = 3, 
                           train_end_idx: Optional[int] = None) -> pd.DataFrame:
        """
        Detecta regimes de mercado usando HMM.
        
        Args:
            train_end_idx: Índice final do conjunto de treino (para evitar vazamento)
        """
        df = df.copy()
        
        # Features para HMM
        returns = df['close'].pct_change().dropna()
        volatility = returns.rolling(20).std()
        
        features = pd.DataFrame({
            'returns': returns,
            'volatility': volatility
        }).dropna()
        
        if len(features) < 100:
            df['regime'] = 0
            return df
        
        # Determinar conjunto de treino (evita look-ahead bias)
        if train_end_idx is not None:
            # Garantir que o índice está dentro do range de features
            train_limit = min(train_end_idx, len(features) - 1)
            train_features = features.iloc[:train_limit]
            predict_features = features
        else:
            train_features = features
            predict_features = features
        
        # Treinar HMM apenas no treino
        try:
            hmm = GaussianHMM(
                n_components=n_states, 
                covariance_type="full", 
                n_iter=100, 
                random_state=42
            )
            hmm.fit(train_features.values)
            
            # Prever em todo o conjunto (mas modelo treinado só no treino)
            regimes = hmm.predict(predict_features.values)
            
            df.loc[predict_features.index, 'regime'] = regimes
            df['regime'] = df['regime'].ffill().fillna(0)
        except Exception as e:
            logger.error(f"Erro no HMM: {e}")
            df['regime'] = 0
        
        return df
    
    def select_features(self, df: pd.DataFrame, target_col: str = 'future_return', n_features: int = 20, train_idx: Optional[int] = None) -> List[str]:
        """
        Seleciona as features mais relevantes usando correlação.
        Se train_idx for informado, calcula correlação apenas no conjunto de treino.
        """
        df_copy = df.copy()
        if 'future_return' not in df_copy.columns:
            df_copy['future_return'] = df_copy['close'].pct_change().shift(-1)
        
        # Filtrar treino se solicitado
        if train_idx is not None:
            df_study = df_copy.iloc[:train_idx].copy()
        else:
            df_study = df_copy.copy()
            
        # Features numéricas
        feature_cols = df_study.select_dtypes(include=[np.number]).columns.tolist()
        exclude = ['time', 'future_return', 'open', 'high', 'low', 'close', 'tick_volume', 'regime', 'spread']
        feature_cols = [c for c in feature_cols if c not in exclude]
        
        # Drop rows with NaN for correlation
        df_corr = df_study[feature_cols + ['future_return']].dropna()
        
        if df_corr.empty or len(df_corr) < 20:
            return []
            
        # Calcular correlações
        correlations = df_corr.corr()['future_return'].abs().drop('future_return', errors='ignore')
        correlations = correlations.dropna()
        
        # Selecionar top features
        selected = correlations.nlargest(n_features).index.tolist()
        
        return selected


feature_engineer = FeatureEngineer()
