import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime

def test_mt5():
    print("Initializing MT5...")
    if not mt5.initialize():
        print(f"initialize() failed, error code = {mt5.last_error()}")
        return

    print("MT5 initialized successfully.")
    terminal_info = mt5.terminal_info()
    if terminal_info:
        print(f"Terminal: {terminal_info.name}, Company: {terminal_info.company}")
    
    symbol = "XAUUSDm"
    print(f"Checking symbol: {symbol}")
    
    # Check if symbol exists
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"Symbol {symbol} not found.")
        # Try finding similar
        all_symbols = mt5.symbols_get()
        if all_symbols:
            matches = [s.name for s in all_symbols if "XAUUSD" in s.name or "GOLD" in s.name]
            print(f"Found similar symbols: {matches}")
    else:
        print(f"Symbol {symbol} found. Description: {symbol_info.description}")
        
        # Ensure it is selected in Market Watch
        if not symbol_info.visible:
            print(f"Symbol {symbol} is not visible in Market Watch. Selecting it...")
            if not mt5.symbol_select(symbol, True):
                print(f"symbol_select({symbol}) failed, error code = {mt5.last_error()}")
            else:
                print(f"Symbol {symbol} is now visible.")
        
        # Try to fetch some bars
        print(f"Fetching last 10 bars for {symbol} M1...")
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 10)
        if rates is None:
            print(f"copy_rates_from_pos() failed, error code = {mt5.last_error()}")
        elif len(rates) == 0:
            print("No rates returned.")
        else:
            print(f"Successfully fetched {len(rates)} bars.")
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            print(df.tail())

    mt5.shutdown()

if __name__ == "__main__":
    test_mt5()
