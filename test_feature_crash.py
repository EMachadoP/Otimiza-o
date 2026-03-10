import pandas as pd
import numpy as np
import sys
import os

# Adicionar o diretório do servidor ao path
sys.path.append(os.path.join(os.getcwd(), 'server'))

from core.feature_engineer import feature_engineer

def test_feature_crash():
    print("Testing FeatureEngineer for crashes...")
    
    # Mock data
    df = pd.DataFrame({
        'time': pd.to_datetime(pd.date_range(start='2023-01-01', periods=200, freq='h')),
        'open': np.random.randn(200).cumsum() + 100,
        'high': np.random.randn(200).cumsum() + 101,
        'low': np.random.randn(200).cumsum() + 99,
        'close': np.random.randn(200).cumsum() + 100,
        'tick_volume': np.random.randint(100, 1000, 200)
    })
    
    try:
        print("Computing all features...")
        df_feat = feature_engineer.compute_all_features(df)
        print(f"Success! Generated {len(df_feat.columns)} columns.")
        
        # Check for specific potentially problematic ones
        extra_blocks = ['trend', 'momentum', 'volatility', 'volume']
        for block in extra_blocks:
            print(f"Testing block: {block}")
            feature_engineer.compute_all_features(df, blocks=[block])
            
    except Exception as e:
        print(f"CRASHED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_feature_crash()
