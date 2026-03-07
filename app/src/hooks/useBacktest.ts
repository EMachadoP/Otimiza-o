import { useState, useCallback } from 'react';
import type { BacktestResult, Strategy } from '@/types/trading';

const API_BASE_URL = 'http://localhost:8000/api';

export function useBacktest() {
  const [backtestResults, setBacktestResults] = useState<BacktestResult[]>([]);
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);

  const runBacktest = useCallback(async (strategy: Strategy, symbol: string, timeframe: string) => {
    setRunning(true);
    setProgress(0);

    try {
      // Fake progress for visual feedback
      const progressInterval = setInterval(() => {
        setProgress(prev => (prev < 90 ? prev + 10 : prev));
      }, 500);

      const response = await fetch(`${API_BASE_URL}/backtest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...strategy,
          symbol,
          timeframe
        })
      });

      clearInterval(progressInterval);
      setProgress(100);

      if (!response.ok) throw new Error('Backtest failed');
      const result = await response.json();

      const fullResult: BacktestResult = {
        ...result,
        strategyId: strategy.id,
        symbol,
        timeframe,
        manifest: {
          timestamp: new Date().toISOString(),
          configuration: { strategy, symbol, timeframe }
        }
      };

      setBacktestResults(prev => [...prev, fullResult]);
      return fullResult;
    } catch (err) {
      console.error('Backtest error', err);
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
  }, []);

  return {
    backtestResults,
    running,
    progress,
    runBacktest,
    runBatchBacktest,
    clearResults
  };
}
