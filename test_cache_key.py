import pandas as pd
import numpy as np
import hashlib
import json
import sys
import os

def test_cache_key():
    print("Testing _get_cache_key for pandas compatibility...")
    
    df = pd.DataFrame({
        'time': pd.date_range(start='2023-01-01', periods=200, freq='h'),
        'open': np.random.randn(200),
        'high': np.random.randn(200),
        'low': np.random.randn(200),
        'close': np.random.randn(200)
    })
    
    strategy_type = "trend"
    param_ranges = {"fastEMA": {"min": 5, "max": 15, "step": 1}}
    criteria = "sharpe"
    
    try:
        # Replicating logic from optimizer.py
        print("Slicing head and tail...")
        head = df.head(100)
        tail = df.tail(100)
        
        print("Attempting _append...")
        try:
            subset = head._append(tail)
            print("Successfully used _append")
        except AttributeError:
            print("_append failed, trying append...")
            subset = head.append(tail)
        
        print("Hashing...")
        df_hash = hashlib.md5(
            pd.util.hash_pandas_object(subset).values.tobytes()
        ).hexdigest()[:16]
        
        print(f"DF Hash: {df_hash}")
        
    except Exception as e:
        print(f"CRASHED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cache_key()
