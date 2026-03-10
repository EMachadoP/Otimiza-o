import unittest
import pandas as pd
import numpy as np
import sys
import os

# Ensure the parent directory is in the path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.backtest_engine import backtest_engine

class TestBacktestEngine(unittest.TestCase):
    
    def test_ema_crossover_signals(self):
        """Testa geração de sinais EMA crossover."""
        df = pd.DataFrame({
            'close': [1.0, 1.1, 1.2, 1.1, 1.0, 0.9, 1.0, 1.1, 1.2, 1.3],
            'high': [1.1, 1.2, 1.3, 1.2, 1.1, 1.0, 1.1, 1.2, 1.3, 1.4],
            'low': [0.9, 1.0, 1.1, 1.0, 0.9, 0.8, 0.9, 1.0, 1.1, 1.2],
            'time': pd.date_range('2024-01-01', periods=10, freq='H')
        })
        
        signals = backtest_engine._generate_signals(
            df, 'trend', {'fastEMA': 3, 'slowEMA': 5}
        )
        
        self.assertEqual(len(signals), len(df))
        self.assertTrue(signals.isin([-1, 0, 1]).all())
    
    def test_backtest_returns_dict(self):
        """Testa se backtest retorna estrutura correta."""
        df = pd.DataFrame({
            'time': pd.date_range('2024-01-01', periods=100, freq='H'),
            'open': np.random.randn(100).cumsum() + 100,
            'high': np.random.randn(100).cumsum() + 101,
            'low': np.random.randn(100).cumsum() + 99,
            'close': np.random.randn(100).cumsum() + 100,
            'tick_volume': np.random.randint(1000, 10000, 100),
        })
        
        result = backtest_engine.run_backtest(
            df, 'trend', {'fastEMA': 9, 'slowEMA': 21}, 'EURUSD'
        )
        
        self.assertIn('id', result)
        self.assertIn('metrics', result)
        self.assertIn('equityCurve', result)
        self.assertNotIn('error', result)

    def test_precise_sl_tp(self):
        """Testa se o SL/TP preciso funciona (intra-bar)."""
        df = pd.DataFrame({
            'time': pd.date_range('2024-01-01', periods=2, freq='H'),
            'open': [100.0, 100.0],
            'high': [100.0, 105.0],
            'low': [100.0, 90.0],
            'close': [100.0, 101.0],
        })
        
        params = {'stopLoss': 50, 'takeProfit': 0}
        signals = pd.Series([1, 1], index=df.index)
        
        original_gen = backtest_engine._generate_signals
        backtest_engine._generate_signals = lambda d, s, p: signals
        
        result = backtest_engine.run_backtest(df, 'trend', params, symbol_name='XAU')
        
        self.assertGreater(result['metrics']['maxDrawdown'], 0)
        final_equity = result['equityCurve'][-1]['equity']
        self.assertLess(final_equity, 10000.0)
        
        backtest_engine._generate_signals = original_gen

if __name__ == '__main__':
    unittest.main()
