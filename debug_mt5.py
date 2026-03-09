import MetaTrader5 as mt5
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MT5_DEBUG")

def debug_mt5():
    if not mt5.initialize():
        print(f"FAILED TO INITIALIZE: {mt5.last_error()}")
        return

    print("--- CONNECTION INFO ---")
    info = mt5.terminal_info()
    if info:
        print(f"Terminal: {info.name}")
        print(f"Connected: {info.connected}")
        print(f"Trade allowed: {info.trade_allowed}")
    else:
        print("Terminal info is NONE")

    print("\n--- SYMBOLS TEST ---")
    # Tenta pegar EURUSD primeiro
    eurusd = mt5.symbol_info("EURUSD")
    if eurusd:
        print(f"EURUSD found! Visible: {eurusd.visible}")
    else:
        print("EURUSD NOT found directly.")
    
    # Lista todos os símbolos que contêm 'EURUSD'
    all_syms = mt5.symbols_get()
    if all_syms:
        print(f"Total symbols found: {len(all_syms)}")
        matches = [s.name for s in all_syms if "EURUSD" in s.name]
        print(f"Matches for 'EURUSD': {matches}")
        
        # Check first 5 symbols
        print(f"First 5 symbols: {[s.name for s in all_syms[:5]]}")
    else:
        print(f"symbols_get() returned NONE. Error: {mt5.last_error()}")

    mt5.shutdown()

if __name__ == "__main__":
    debug_mt5()
