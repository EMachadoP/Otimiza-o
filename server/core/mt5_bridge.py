import MetaTrader5 as mt5
import pandas as pd
from typing import Optional, List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MT5Bridge:
    def __init__(self):
        self.connected = False

    def connect(self) -> bool:
        """Initialize connection to MetaTrader 5."""
        if not mt5.initialize():
            logger.error(f"initialize() failed, error code = {mt5.last_error()}")
            self.connected = False
            return False
        
        self.connected = True
        logger.info("MetaTrader 5 initialized successfully")
        return True

    def disconnect(self):
        """Shutdown connection to MetaTrader 5."""
        mt5.shutdown()
        self.connected = False
        logger.info("MetaTrader 5 connection closed")

    def get_status(self) -> Dict:
        """Get MT5 connection and terminal status."""
        if not self.connected:
            return {"connected": False, "terminal_info": None}
        
        terminal_info = mt5.terminal_info()
        if terminal_info is None:
            return {"connected": False, "error": mt5.last_error()}
            
        return {
            "connected": True,
            "terminal_info": terminal_info._asdict()
        }

    def get_ohlcv(self, symbol: str, timeframe: str, count: int = 1000) -> Optional[pd.DataFrame]:
        """Fetch historical candles for a symbol and timeframe."""
        if not self.connected and not self.connect():
            return None

        # Map string timeframe to MT5 constant
        tf_map = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30,
            "H1": mt5.TIMEFRAME_H1,
            "H4": mt5.TIMEFRAME_H4,
            "D1": mt5.TIMEFRAME_D1,
        }
        
        mt5_tf = tf_map.get(timeframe, mt5.TIMEFRAME_H1)
        
        # Try exact symbol first
        rates = mt5.copy_rates_from_pos(symbol, mt5_tf, 0, count)
        
        # Fallback: try to find symbol with suffix if not found (e.g. EURUSD -> EURUSDm)
        if rates is None:
            all_symbols = [s.name for s in mt5.symbols_get() or []]
            matches = [s for s in all_symbols if s.startswith(symbol)]
            if matches:
                logger.info(f"Symbol {symbol} not found, trying with suffix: {matches[0]}")
                rates = mt5.copy_rates_from_pos(matches[0], mt5_tf, 0, count)

        if rates is None or len(rates) == 0:
            logger.warning(f"No data for {symbol}, error = {mt5.last_error()}")
            return pd.DataFrame() # Return empty DF instead of None to prevent 500s
            
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df

    def get_symbols(self) -> List[str]:
        """List all available symbols in MT5."""
        if not self.connected and not self.connect():
            return []
            
        symbols = mt5.symbols_get()
        if symbols is None:
            return []
            
        return [s.name for s in symbols]

# Global instance
mt5_bridge = MT5Bridge()
