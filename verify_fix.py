import sys
import os
import pandas as pd
import numpy as np

# Adicionar o diretório do servidor ao path
sys.path.append(os.path.join(os.getcwd(), 'server'))

from core.mql_generator import mql_generator
from core.mql_parser import mql_parser
from core.backtest_engine import backtest_engine

def verify_cycle():
    print("Step 1: Define original strategy")
    original_strategy = {
        "name": "Test Strategy",
        "type": "trend",
        "parameters": {
            "fastEMA": 12,
            "slowEMA": 26,
            "stopLoss": 55,
            "takeProfit": 110
        },
        "indicators": ["EMA(12)", "EMA(26)"]
    }
    
    print("Step 2: Generate MQL5")
    mql5_code = mql_generator.generate_mql5(original_strategy)
    # print("Generated MQL5 Code:\n", mql5_code)
    print("MQL5 generated. Checking for 'Inp' prefix...")
    if "input int      InpFastEMA = 12;" in mql5_code:
        print("SUCCESS: InpFastEMA=12 found in MQL.")
    else:
        print("FAILURE: InpFastEMA=12 NOT found in MQL.")
        # Find what WAS generated
        for line in mql5_code.split('\n'):
            if 'InpFastEMA' in line or 'InpfastEMA' in line:
                print(f"Actually found: {line}")
        
    print("\nStep 3: Parse MQL5 back to strategy")
    parsed_result = mql_parser.parse(mql5_code)
    parsed_inputs = parsed_result['inputs']
    print("Parsed inputs keys:", sorted(parsed_inputs.keys()))
    
    expected_params = ["fastEMA", "slowEMA", "stopLoss", "takeProfit"]
    all_found = True
    for p in expected_params:
        if p not in parsed_inputs:
            print(f"FAILURE: Parameter '{p}' not found in parsed results!")
            all_found = False
        else:
            val = parsed_inputs[p]['default']
            orig_val = original_strategy['parameters'][p]
            if val != orig_val:
                print(f"FAILURE: Parameter '{p}' has value {val}, expected {orig_val}")
                all_found = False
    
    if all_found:
        print("SUCCESS: All parameters correctly stripped of 'Inp' and recovered.")
    
    print("\nStep 4: Verify backtest safety with parsed params")
    # Simulate what frontend does
    numeric_params = {k: v['default'] for k, v in parsed_inputs.items()}
    
    df = pd.DataFrame({
        'time': pd.date_range(start='2023-01-01', periods=100, freq='H'),
        'close': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 101,
        'low': np.random.randn(100).cumsum() + 99
    })
    
    try:
        results = backtest_engine.run_backtest(df, "trend", numeric_params)
        if "error" in results:
            print(f"FAILURE: Backtest returned error: {results['error']}")
        else:
            print("SUCCESS: Backtest executed safely.")
    except Exception as e:
        print(f"FAILURE: Backtest crashed: {e}")

if __name__ == "__main__":
    verify_cycle()
