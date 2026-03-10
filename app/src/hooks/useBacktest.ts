import { useState, useCallback } from 'react';
import type { BacktestResult, Strategy, ValidationResults } from '@/types/trading';

const API_BASE_URL = '/api';

export function useBacktest() {
  const [backtestResults, setBacktestResults] = useState<BacktestResult[]>([]);
  const [validation, setValidation] = useState<ValidationResults | null>(null);
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);

  const runBacktest = useCallback(async (strategy: Strategy, symbol: string, timeframe: string) => {
    setRunning(true);
    setProgress(0);

    try {
      const progressInterval = setInterval(() => {
        setProgress(prev => (prev < 90 ? prev + 5 : prev));
      }, 300);

      // Run backtest and validation in parallel
      const [btRes, valRes] = await Promise.all([
        fetch(`${API_BASE_URL}/backtest`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ...strategy, symbol, timeframe }),
        }),
        fetch(`${API_BASE_URL}/validate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ...strategy, symbol, timeframe }),
        }),
      ]);

      clearInterval(progressInterval);
      setProgress(100);

      let btResult = null;
      let valResult = null;

      if (btRes.ok) btResult = await btRes.json();
      if (valRes.ok) valResult = await valRes.json();

      if (valResult) {
        setValidation(valResult);
      }

      if (btResult) {
        const fullResult: BacktestResult = {
          ...btResult,
          strategyId: strategy.id,
          symbol,
          timeframe,
          period: { start: 'auto', end: 'auto' },
          trades: [],
          validation: valResult || btResult.validation,
          manifest: {
            seed: 42,
            datasetHash: 'real-mt5',
            codeHash: 'live',
            branch: 'main',
            pythonVersion: '3.13',
            dependenciesHash: 'live',
            timestamp: new Date().toISOString(),
            configuration: { strategy, symbol, timeframe },
          },
        };
        setBacktestResults(prev => [...prev, fullResult]);
        return fullResult;
      }
    } catch (err) {
      console.error('Backtest/validation error', err);
    } finally {
      setRunning(false);
      setProgress(0);
    }
  }, []);

  const runBatchBacktest = useCallback(async (strategies: Strategy[], symbol: string, timeframe: string) => {
    const results: BacktestResult[] = [];
    for (const strategy of strategies) {
      const result = await runBacktest(strategy, symbol, timeframe);
      if (result) results.push(result);
    }
    return results;
  }, [runBacktest]);

  const clearResults = useCallback(() => {
    setBacktestResults([]);
    setValidation(null);
  }, []);

  return {
    backtestResults,
    validation,
    running,
    progress,
    runBacktest,
    runBatchBacktest,
    clearResults,
  };
}
