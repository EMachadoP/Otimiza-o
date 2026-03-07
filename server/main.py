from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict
import uvicorn
import sys
import os

# Add server directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.mt5_bridge import mt5_bridge
from core.ml_models import ml_models
from core.backtest_engine import backtest_engine

app = FastAPI(title="TradeStrategist API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    mt5_bridge.connect()

@app.on_event("shutdown")
async def shutdown_event():
    mt5_bridge.disconnect()

@app.get("/api/status")
async def get_status():
    return mt5_bridge.get_status()

@app.get("/api/symbols")
async def get_symbols():
    symbols = mt5_bridge.get_symbols()
    return [{"name": s} for s in symbols[:20]] # Limit to 20 for now

@app.get("/api/ohlcv")
async def get_ohlcv(symbol: str, timeframe: str, count: int = 500):
    df = mt5_bridge.get_ohlcv(symbol, timeframe, count)
    if df is None:
        raise HTTPException(status_code=500, detail="Failed to fetch data from MT5")
    
    # Convert to JSON serializable format
    data = df.copy()
    data['time'] = (data['time'].astype(int) // 10**6) # to ms
    return data.to_dict(orient='records')

@app.get("/api/analysis")
async def get_analysis(symbol: str, timeframe: str):
    df = mt5_bridge.get_ohlcv(symbol, timeframe, 100)
    if df is None:
        raise HTTPException(status_code=500, detail="Failed to fetch data for analysis")
    
    regime = ml_models.detect_regime(df)
    patterns = ml_models.detect_patterns(df)
    
    return {
        "regime": regime,
        "patterns": patterns
    }

@app.post("/api/backtest")
async def run_backtest(strategy: Dict):
    symbol = strategy.get("symbol", "EURUSD")
    timeframe = strategy.get("timeframe", "H1")
    strategy_type = strategy.get("type", "trend")
    params = strategy.get("parameters", {})
    
    df = mt5_bridge.get_ohlcv(symbol, timeframe, 1000)
    if df is None:
        raise HTTPException(status_code=500, detail="Failed to fetch data for backtest")
        
    result = backtest_engine.run_backtest(df, strategy_type, params)
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
