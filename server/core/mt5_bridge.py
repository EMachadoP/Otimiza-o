import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MT5Connector:
    """Professional connector for MetaTrader 5 via Python API."""
    
    TIMEFRAMES = {
        'M1': mt5.TIMEFRAME_M1,
        'M5': mt5.TIMEFRAME_M5,
        'M15': mt5.TIMEFRAME_M15,
        'M30': mt5.TIMEFRAME_M30,
        'H1': mt5.TIMEFRAME_H1,
        'H4': mt5.TIMEFRAME_H4,
        'D1': mt5.TIMEFRAME_D1,
        'W1': mt5.TIMEFRAME_W1,
        'MN1': mt5.TIMEFRAME_MN1,
    }
    
    def __init__(self, mt5_path: Optional[str] = None):
        self.mt5_path = mt5_path
        self.initialized = False
        
    def connect(self) -> bool:
        """Initialize connection to MT5."""
        try:
            if self.mt5_path:
                self.initialized = mt5.initialize(self.mt5_path)
            else:
                self.initialized = mt5.initialize()
                
            if self.initialized:
                logger.info(f"MT5 Connected: {mt5.terminal_info().name if mt5.terminal_info() else 'Unknown'}")
                return True
            else:
                logger.error(f"Failed to connect to MT5: {mt5.last_error()}")
                return False
        except Exception as e:
            logger.error(f"Error connecting to MT5: {e}")
            return False
    
    def disconnect(self):
        """Shutdown connection to MT5."""
        if self.initialized:
            mt5.shutdown()
            self.initialized = False
            logger.info("MT5 disconnected")
            
    def get_status(self) -> Dict:
        """Get MT5 connection and terminal status."""
        if not self.initialized and not self.connect():
            return {"connected": False, "terminal_info": None}
        
        terminal_info = mt5.terminal_info()
        if terminal_info is None:
            return {"connected": False, "error": mt5.last_error()}
            
        return {
            "connected": True,
            "terminal_info": terminal_info._asdict()
        }
    
    def get_ohlcv(
        self, 
        symbol: str, 
        timeframe: str, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        count: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data from MT5 with symbol suffix fallback logic.
        
        Args:
            symbol: Symbol name (e.g. 'EURUSD')
            timeframe: Timeframe (M1, M5, M15, H1, H4, D1, etc.)
            start_date: Start date (optional)
            end_date: End date (optional, default=now)
            count: Number of bars (alternative to dates)
        
        Returns:
            DataFrame with columns: time, open, high, low, close, tick_volume, spread, real_volume
        """
        if not self.initialized and not self.connect():
            logger.error("MT5 not connected and initialization failed.")
            return pd.DataFrame()
        
        tf = self.TIMEFRAMES.get(timeframe, mt5.TIMEFRAME_H1)
        
        def fetch_data(s):
            if count:
                return mt5.copy_rates_from_pos(s, tf, 0, count)
            elif start_date and end_date:
                return mt5.copy_rates_range(s, tf, start_date, end_date)
            elif start_date:
                return mt5.copy_rates_from(s, tf, start_date, 10000)
            else:
                return mt5.copy_rates_from_pos(s, tf, 0, 1000)
        
        # Ensure symbol is selected and available
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            # Fallback logic for suffixes (e.g. EURUSD -> EURUSDm)
            all_symbols = [s.name for s in mt5.symbols_get() or []]
            
            # Prioritized matches:
            # 1. Exact case-insensitive
            # 2. String starts with symbol or symbol starts with string
            matches = [s for s in all_symbols if s.lower() == symbol.lower()]
            if not matches:
                matches = [s for s in all_symbols if s.lower().startswith(symbol.lower()) or symbol.lower().startswith(s.lower())]
            
            if matches:
                 symbol = matches[0]
                 logger.info(f"Symbol {symbol} found via fallback (match: {matches[0]})")
                 symbol_info = mt5.symbol_info(symbol)
            else:
                 logger.error(f"Symbol {symbol} not found in MT5 after fallback search.")
                 return pd.DataFrame()

        # Selection in Market Watch is mandatory for data fetching
        if not symbol_info.visible:
            if not mt5.symbol_select(symbol, True):
                logger.error(f"Failed to select symbol {symbol}: {mt5.last_error()}")
                return pd.DataFrame()

        # Try fetching data
        rates = fetch_data(symbol)
        
        if rates is None or len(rates) == 0:
            error = mt5.last_error()
            logger.warning(f"No data returned for {symbol} {timeframe}. Error: {error}")
            # Try to force a selection refresh
            mt5.symbol_select(symbol, True)
            return pd.DataFrame()
        
        df = pd.DataFrame(rates)
        if df.empty:
            return df
            
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df
    
    def get_ticks(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        n_ticks: Optional[int] = None
    ) -> pd.DataFrame:
        """Get tick data from MT5."""
        if not self.initialized and not self.connect():
            return pd.DataFrame()
        
        if n_ticks:
            ticks = mt5.copy_ticks_from(symbol, start_date or datetime.now() - timedelta(days=1), n_ticks, mt5.COPY_TICKS_ALL)
        elif start_date and end_date:
            ticks = mt5.copy_ticks_range(symbol, start_date, end_date, mt5.COPY_TICKS_ALL)
        else:
            ticks = mt5.copy_ticks_from(symbol, datetime.now() - timedelta(days=1), 100000, mt5.COPY_TICKS_ALL)
        
        if ticks is None or len(ticks) == 0:
            return pd.DataFrame()
        
        df = pd.DataFrame(ticks)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        return df
    
    def get_symbols(self) -> List[str]:
        """List available symbols."""
        if not self.initialized and not self.connect():
            logger.error("MT5 Bridge: Failed to connect while getting symbols.")
            return []
        
        # Get all symbols from MT5 terminal, even those not in Market Watch
        symbols = mt5.symbols_get()
        if symbols is None:
            logger.error(f"Failed to get symbols: {mt5.last_error()}")
            return []
        return [s.name for s in symbols]
    
    def get_symbol_info(self, symbol: str) -> Dict:
        """Get detailed symbol information."""
        if not self.initialized and not self.connect():
            return {}
        
        info = mt5.symbol_info(symbol)
        if info is None:
            # Try with fallback if direct symbol fails
            all_symbols = [s.name for s in mt5.symbols_get() or []]
            matches = [s for s in all_symbols if s.startswith(symbol)]
            if matches:
                info = mt5.symbol_info(matches[0])
            
        if info is None:
            return {}
        
        return {
            'name': info.name,
            'description': info.description,
            'currency_base': info.currency_base,
            'currency_profit': info.currency_profit,
            'digits': info.digits,
            'point': info.point,
            'spread': info.spread,
            'trade_contract_size': info.trade_contract_size,
            'volume_min': info.volume_min,
            'volume_max': info.volume_max,
            'volume_step': info.volume_step,
        }


# Global instance for compatibility with existing modules
mt5_bridge = MT5Connector()
