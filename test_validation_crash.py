import sys
import os
import pandas as pd
import numpy as np

# Adicionar o diretório do servidor ao path
sys.path.append(os.path.join(os.getcwd(), 'server'))

from core.backtest_engine import backtest_engine
from core.mt5_bridge import mt5_bridge

def test_validation_crash():
    print("Testing validation crash...")
    
    # Mock data if MT5 is not connected
    df = pd.DataFrame({
        'time': pd.date_range(start='2023-01-01', periods=1000, freq='H'),
        'open': np.random.randn(1000).cumsum() + 100,
        'high': np.random.randn(1000).cumsum() + 101,
        'low': np.random.randn(1000).cumsum() + 99,
        'close': np.random.randn(1000).cumsum() + 100,
        'tick_volume': np.random.randint(100, 1000, 1000)
    })
    
    strategy_type = "trend"
    # Sinister parameters that might cause issues if not handled
    params = {
        "InpFastEMA": 15,
        "InpSlowEMA": 30,
        "stopLoss": "invalid", # String instead of int
        "takeProfit": 100
    }
    
    try:
        print("Running backtest...")
        result = backtest_engine.run_backtest(df, strategy_type, params, symbol_name="EURUSD")
        print("Backtest results keys:", result.keys())
        
        print("\nRunning WFA...")
        wfa = backtest_engine.run_wfa(df, strategy_type, params, symbol_name="EURUSD")
        print("WFA done.")
        
        print("\nRunning CPCV...")
        cpcv = backtest_engine.run_cpcv(df, strategy_type, params, symbol_name="EURUSD")
        print("CPCV done.")
        
        print("\nRunning Monte Carlo...")
        mc = backtest_engine.run_monte_carlo(df, strategy_type, params, symbol_name="EURUSD")
        print("MC done.")
        
    except Exception as e:
        print(f"CRASHED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_validation_crash()
