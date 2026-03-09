from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict
import uvicorn
import sys
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from itertools import product
import logging
from dataclasses import dataclass, asdict

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger(__name__)

from core.backtest_engine import backtest_engine
# Ensure optimizer is available
from core.optimizer import ParameterOptimizer
optimizer = ParameterOptimizer(backtest_engine)
from core.feature_engineer import feature_engineer
from core.mql_parser import mql_parser
from core.mql_generator import mql_generator
from core.ml_models import ml_models
from core.mt5_bridge import mt5_bridge

parameter_optimizer = optimizer # Consolidate


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
    
    # Prioritization logic: Major Forex and Metals (Gold)
    majors = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD", "ETHUSD"]
    
    # Sort: Prioritize majors, then alphabetical
    def sort_key(s):
        # Check if symbol contains any major names (handling suffixes like 'm')
        for m in majors:
            if m.lower() in s.lower():
                return (0, s)
        return (1, s)
    
    sorted_symbols = sorted(symbols, key=sort_key)
    return [{"name": s} for s in sorted_symbols[:100]]


@app.get("/api/ohlcv")
async def get_ohlcv(symbol: str, timeframe: str, count: int = 500):
    df = mt5_bridge.get_ohlcv(symbol, timeframe, count=count)
    if df is None or df.empty:
        return [] # Return empty list instead of 500 to keep frontend alive
    data = df.copy()
    data['time'] = data['time'].astype(int) // 10**6
    return data.to_dict(orient='records')


@app.get("/api/analysis")
async def get_analysis(symbol: str, timeframe: str):
    df = mt5_bridge.get_ohlcv(symbol, timeframe, count=200)
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
    df = mt5_bridge.get_ohlcv(symbol, timeframe, count=1000)
    if df is None or df.empty:
        return []
    strategies = backtest_engine.discover_strategies(df, symbol_name=symbol)
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

    df = mt5_bridge.get_ohlcv(symbol, timeframe, count=2000)
    if df is None:
        raise HTTPException(status_code=500, detail="Failed to fetch data")

    wfa = backtest_engine.run_wfa(df, strategy_type, params, symbol_name=symbol)
    cpcv = backtest_engine.run_cpcv(df, strategy_type, params, symbol_name=symbol)
    mc = backtest_engine.run_monte_carlo(df, strategy_type, params, symbol_name=symbol, n_simulations=5000)

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
    return backtest_engine.run_backtest(df, strategy_type, params, symbol_name=symbol)


# ──────────────────────────────────────────
# NEW: Recurrence Heatmap (real data)
# ──────────────────────────────────────────
@app.get("/api/heatmap")
async def get_heatmap(symbol: str, timeframe: str):
    """Compute win rate heatmap by hour/day from real MT5 data."""
    df = mt5_bridge.get_ohlcv(symbol, timeframe, count=2000)
    if df is None or df.empty:
        return [[0]*24 for _ in range(5)] # 5 days x 24 hours
    return backtest_engine.compute_heatmap(df)


# ──────────────────────────────────────────
# NEW: ML Feature Importance (real data)
# ──────────────────────────────────────────
@app.get("/api/ml-insights")
async def get_ml_insights(symbol: str, timeframe: str):
    """Compute ML feature importance using 130+ technical indicators."""
    df = mt5_bridge.get_ohlcv(symbol, timeframe, 500)
    if df is None or df.empty:
        return {"features": [], "successProbability": 0, "explanation": "Dados insuficientes."}
    
    # 1. Compute all features
    df_feat = feature_engineer.compute_all_features(df)
    
    # 2. Detect regime and select features
    df_regime = feature_engineer.detect_regime_hmm(df_feat)
    top_features = feature_engineer.select_features(df_regime, n_features=10)
    
    # 3. Format response - ENSURE future_return exists
    if 'future_return' not in df_regime.columns:
        df_regime['future_return'] = df_regime['close'].pct_change().shift(-1)
        
    valid_top_features = [f for f in top_features if f in df_regime.columns]
    if not valid_top_features:
        return {"features": [], "successProbability": 50, "explanation": "Não foi possível extrair features relevantes."}
        
    corrs = df_regime[valid_top_features + ['future_return']].corr()['future_return'].abs().drop('future_return', errors='ignore')
    total_corr = corrs.sum()
    
    features_list = []
    for feat in valid_top_features:
        features_list.append({
            "feature": feat.upper().replace('_', ' '),
            "importance": round(float(corrs[feat] / (total_corr + 1e-10) * 100), 1),
            "description": f"Indicador técnico avançado: {feat}"
        })
    
    # Sort by importance
    features_list.sort(key=lambda x: x['importance'], reverse=True)
    
    # Probability based on recent return consistency
    recent_rets = df_regime['future_return'].tail(20).dropna()
    prob = round(float((recent_rets > 0).mean() * 100), 1) if not recent_rets.empty else 50
    
    regime_type = "alta" if df_regime['return_1d'].tail(5).mean() > 0 else "baixa"
    explanation = (
        f"Análise de 130+ indicadores concluída. O mercado apresenta viés de {regime_type}. "
        f"As features mais preditivas no momento são {', '.join(valid_top_features[:2])}."
    )
    
    return {
        "features": features_list,
        "successProbability": min(max(prob, 30), 95),
        "explanation": explanation
    }


# ──────────────────────────────────────────
# NEW: Real Parameter Optimization
# ──────────────────────────────────────────
@app.post("/api/optimize")
async def optimize(payload: Dict):
    """Run strategy optimization with high performance funnel."""
    symbol = payload.get("symbol", "EURUSD")
    timeframe = payload.get("timeframe", "H1")
    strategy_type = payload.get("type", "trend")
    param_ranges = payload.get("paramRanges", {})
    criteria = payload.get("criteria", "sharpe")
    
    logger.info(f"Otimizador: Recebida requisição para {strategy_type} em {symbol}")
    
    # 1. Get Data
    df = mt5_bridge.get_ohlcv(symbol, timeframe, count=1000)
    if df is None or df.empty:
        raise HTTPException(status_code=400, detail="Sem dados disponíveis no MT5")
        
    # 2. Add Basic Features
    df = feature_engineer.compute_all_features(df, blocks=['trend', 'momentum', 'volatility'])
    
    # 3. Run Optimization Funnel
    try:
        results = optimizer.optimize(
            df=df,
            strategy_type=strategy_type,
            param_ranges=param_ranges,
            criteria=criteria,
            symbol_name=symbol
        )
        return results
    except Exception as e:
        logger.error(f"Erro na otimização: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/convert-mql")
async def convert_mql(payload: Dict):
    """Convert MQL4/5 code into a Python strategy."""
    mql_code = str(payload.get("code") or "").strip()
    if not mql_code:
        raise HTTPException(status_code=400, detail="MQL code is required")

    parsed = {
        "name": "Custom_MQL_Strategy",
        "type": "trend",
        "inputs": {},
        "indicators": [],
        "signals_logic": "",
        "errors": [],
    }

    try:
        parsed = mql_parser.parse(mql_code)
    except Exception as e:
        logger.warning("Error parsing MQL snippet", exc_info=True)
        parsed["signals_logic"] = mql_code
        parsed["errors"].append(f"Falha ao interpretar o snippet: {e}")

    errors = list(parsed.get("errors", []))
    has_logic = bool((parsed.get("signals_logic") or "").strip())

    try:
        python_code = mql_parser.convert_to_python(mql_code)
    except Exception as e:
        logger.warning("Error converting MQL to Python", exc_info=True)
        errors.append(f"Falha na conversão automática para Python: {e}")
        python_code = mql_parser.build_fallback_python(mql_code, parsed=parsed)

    if not has_logic:
        errors.append("Não foi possível extrair a lógica de sinais completa.")

    status = "success" if has_logic and not errors else "partial"

    return {
        "strategy": parsed,
        "pythonCode": python_code,
        "status": status,
        "errors": errors,
    }


@app.post("/api/export-ea")
async def export_ea(payload: Dict):
    """Export a strategy to MQL4, MQL5, JSON or YAML."""
    strategy = payload.get("strategy")
    if not strategy:
        logger.error("Export EA failed: No strategy in payload")
        raise HTTPException(status_code=400, detail="Strategy data is required")
    
    try:
        logger.info(f"Generating export files for strategy: {strategy.get('name', 'Unknown')}")
        mql4 = mql_generator.generate_mql4(strategy)
        mql5 = mql_generator.generate_mql5(strategy)
        json_config = mql_generator.generate_json(strategy)
        yaml_config = mql_generator.generate_yaml(strategy)
        
        logger.info("Export files generated successfully")
        return {
            "mql4": mql4,
            "mql5": mql5,
            "json": json_config,
            "yaml": yaml_config,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error exporting EA: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
