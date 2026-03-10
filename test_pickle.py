import pickle
import sys
import os
import logging
from concurrent.futures import ProcessPoolExecutor

# Adicionar o diretório do servidor ao path
sys.path.append(os.path.join(os.getcwd(), 'server'))

from core.backtest_engine import BacktestEngine

def worker(engine):
    return engine is not None

def test_pickle():
    print("Testing if BacktestEngine is pickleable...")
    engine = BacktestEngine()
    
    try:
        data = pickle.dumps(engine)
        print("Successfully pickled!")
        
        print("Testing with ProcessPoolExecutor...")
        with ProcessPoolExecutor(max_workers=2) as executor:
            fut = executor.submit(worker, engine)
            print(f"Worker result: {fut.result()}")
            
    except Exception as e:
        print(f"CRASHED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pickle()
