from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict
import uvicorn
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.mt5_bridge import mt5_bridge
from core.ml_models import ml_models
from core.backtest_engine import backtest_engine
from core.optimizer import ParameterOptimizer

parameter_optimizer = ParameterOptimizer(backtest_engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    mt5_bridge.connect()
    yield
    mt5_bridge.disconnect()


app = FastAPI(title="TradeStrategist API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "name": "TradeStrategist Pro API",
        "version": "2.0.0",
        "status": "running",
        "frontend": "http://localhost:5173",
        "endpoints": [
            "/api/status", "/api/symbols", "/api/ohlcv",
            "/api/analysis", "/api/strategies", "/api/backtest",
            "/api/validate", "/api/heatmap", "/api/ml-insights",
        ],
    }


@app.get("/api/status")
async def get_status():
    return mt5_bridge.get_status()


@app.get("/api/symbols")
async def get_symbols():
    symbols = mt5_bridge.get_symbols()
    return [{"name": s} for s in symbols[:20]]


@app.get("/api/ohlcv")
async def get_ohlcv(symbol: str, timeframe: str, count: int = 500):
    df = mt5_bridge.get_ohlcv(symbol, timeframe, count)
    if df is None or df.empty:
        return [] # Return empty list instead of 500 to keep frontend alive
    data = df.copy()
    data['time'] = data['time'].astype(int) // 10**6
    return data.to_dict(orient='records')


@app.get("/api/analysis")
async def get_analysis(symbol: str, timeframe: str):
    df = mt5_bridge.get_ohlcv(symbol, timeframe, 200)
    if df is None or df.empty:
        return {
            "regime": {"type": "undefined", "confidence": 0, "indicators": {}}, 
            "patterns": [],
            "recommendation": {"strategy": "N/A", "reason": "Sem dados", "confidence": 0}
        }
    regime = ml_models.detect_regime(df)
    patterns = ml_models.detect_patterns(df)
    recommendation = ml_models.get_recommendation(regime.get("type", "undefined"))
    return {"regime": regime, "patterns": patterns, "recommendation": recommendation}


# ──────────────────────────────────────────
# NEW: Strategy Discovery
# ──────────────────────────────────────────
@app.get("/api/strategies")
async def get_strategies(symbol: str, timeframe: str):
    """Discover and rank strategies using real MT5 data."""
    df = mt5_bridge.get_ohlcv(symbol, timeframe, 1000)
    if df is None or df.empty:
        return []
    strategies = backtest_engine.discover_strategies(df)
    return strategies


# ──────────────────────────────────────────
# NEW: Full Validation (WFA + CPCV + MC)
# ──────────────────────────────────────────
@app.post("/api/validate")
async def run_validation(payload: Dict):
    """Run WFA, CPCV, and Monte Carlo on a strategy."""
    symbol = payload.get("symbol", "EURUSD")
    timeframe = payload.get("timeframe", "H1")
    strategy_type = payload.get("type", "trend")
    params = payload.get("parameters", {})

    df = mt5_bridge.get_ohlcv(symbol, timeframe, 2000)
    if df is None:
        raise HTTPException(status_code=500, detail="Failed to fetch data")

    wfa = backtest_engine.run_wfa(df, strategy_type, params)
    cpcv = backtest_engine.run_cpcv(df, strategy_type, params)
    mc = backtest_engine.run_monte_carlo(df, strategy_type, params, n_simulations=5000)

    # PBO approximation from CPCV sharpe variance
    pbo = min(float(cpcv['sharpeStd'] / (abs(cpcv['avgSharpe']) + 1e-10) * 100), 100)

    return {
        "wfa": wfa,
        "cpcv": cpcv,
        "monteCarlo": mc,
        "pbo": round(pbo, 1),
    }


# ──────────────────────────────────────────
# NEW: Backtest with full validation
# ──────────────────────────────────────────
@app.post("/api/backtest")
async def run_backtest(payload: Dict):
    """Run a full backtest with equity curve."""
    symbol = payload.get("symbol", "EURUSD")
    timeframe = payload.get("timeframe", "H1")
    strategy_type = payload.get("type", "trend")
    params = payload.get("parameters", {})

    df = mt5_bridge.get_ohlcv(symbol, timeframe, 1000)
    if df is None or df.empty:
        return {"equity": [], "metrics": {}, "trades": []}
    return backtest_engine.run_backtest(df, strategy_type, params)


# ──────────────────────────────────────────
# NEW: Recurrence Heatmap (real data)
# ──────────────────────────────────────────
@app.get("/api/heatmap")
async def get_heatmap(symbol: str, timeframe: str):
    """Compute win rate heatmap by hour/day from real MT5 data."""
    df = mt5_bridge.get_ohlcv(symbol, timeframe, 2000)
    if df is None or df.empty:
        return [[0]*24 for _ in range(5)] # 5 days x 24 hours
    return backtest_engine.compute_heatmap(df)


# ──────────────────────────────────────────
# NEW: ML Feature Importance (real data)
# ──────────────────────────────────────────
@app.get("/api/ml-insights")
async def get_ml_insights(symbol: str, timeframe: str):
    """Compute ML feature importance and success probability from real data."""
    df = mt5_bridge.get_ohlcv(symbol, timeframe, 500)
    if df is None or df.empty:
        return {
            "features": [],
            "successProbability": 0,
            "explanation": "Dados insuficientes no MT5 para este símbolo/timeframe."
        }
    return backtest_engine.compute_feature_importance(df)


# ──────────────────────────────────────────
# NEW: Real Parameter Optimization
# ──────────────────────────────────────────
@app.post("/api/optimize")
async def run_optimization(payload: Dict):
    """Run grid-search parameter optimization with real WFA validation."""
    symbol = payload.get("symbol", "EURUSD")
    timeframe = payload.get("timeframe", "H1")
    strategy_type = payload.get("type", "trend")
    param_ranges = payload.get("paramRanges", {})
    criteria = payload.get("criteria", "sharpe")

    if not param_ranges:
        raise HTTPException(status_code=400, detail="paramRanges is required")

    df = mt5_bridge.get_ohlcv(symbol, timeframe, 2000)
    if df is None or df.empty:
        raise HTTPException(status_code=500, detail="Failed to fetch data from MT5")

    result = parameter_optimizer.optimize_strategy(
        df, strategy_type, param_ranges, criteria
    )
    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
