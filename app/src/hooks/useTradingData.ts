import { useState, useEffect, useCallback } from 'react';
import type { Symbol, Timeframe, OHLCV, Pattern, MarketRegime, Strategy } from '@/types/trading';

const TIMEFRAMES: Timeframe[] = [
  { value: 'M1', label: 'M1', minutes: 1 },
  { value: 'M5', label: 'M5', minutes: 5 },
  { value: 'M15', label: 'M15', minutes: 15 },
  { value: 'M30', label: 'M30', minutes: 30 },
  { value: 'H1', label: 'H1', minutes: 60 },
  { value: 'H4', label: 'H4', minutes: 240 },
  { value: 'D1', label: 'D1', minutes: 1440 },
];

const API_BASE_URL = 'http://localhost:8000/api';

export function useTradingData() {
  const [symbols, setSymbols] = useState<Symbol[]>([]);
  const [timeframes] = useState<Timeframe[]>(TIMEFRAMES);
  const [selectedSymbol, setSelectedSymbol] = useState<Symbol>({ name: 'EURUSD' } as Symbol);
  const [selectedTimeframe, setSelectedTimeframe] = useState<Timeframe>(TIMEFRAMES[4]);
  const [data, setData] = useState<OHLCV[]>([]);
  const [patterns, setPatterns] = useState<Pattern[]>([]);
  const [regime, setRegime] = useState<MarketRegime | null>(null);
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSymbols = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/symbols`);
      if (!response.ok) throw new Error('API error');
      const data = await response.json();
      setSymbols(data);
      if (data.length > 0) setSelectedSymbol(data[0]);
    } catch (err) {
      console.error('Failed to fetch symbols', err);
    }
  }, []);

  const fetchData = useCallback(async () => {
    if (!selectedSymbol) return;
    
    setLoading(true);
    setError(null);
    
    try {
      // 1. Fetch OHLCV Data
      const ohlcvResponse = await fetch(`${API_BASE_URL}/ohlcv?symbol=${selectedSymbol.name}&timeframe=${selectedTimeframe.value}`);
      if (!ohlcvResponse.ok) throw new Error('Failed to fetch OHLCV');
      const ohlcv = await ohlcvResponse.json();
      
      // 2. Fetch Analysis (Regime & Patterns)
      const analysisResponse = await fetch(`${API_BASE_URL}/analysis?symbol=${selectedSymbol.name}&timeframe=${selectedTimeframe.value}`);
      if (!analysisResponse.ok) throw new Error('Failed to fetch analysis');
      const analysis = await analysisResponse.json();
      
      setData(ohlcv);
      setRegime(analysis.regime);
      setPatterns(analysis.patterns);
      
      // Keep mock strategies for now or fetch if available
      // setStrategies(recommendedStrategies);
    } catch (err) {
      setError('Erro ao conectar com o Backend/MT5. Verifique se o servidor está rodando.');
    } finally {
      setLoading(false);
    }
  }, [selectedSymbol, selectedTimeframe]);

  useEffect(() => {
    fetchSymbols();
  }, [fetchSymbols]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    symbols,
    timeframes,
    selectedSymbol,
    selectedTimeframe,
    data,
    patterns,
    regime,
    strategies,
    loading,
    error,
    setSelectedSymbol,
    setSelectedTimeframe,
    refreshData: fetchData
  };
}
