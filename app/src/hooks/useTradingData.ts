import { useState, useEffect, useCallback } from 'react';
import type { Symbol, Timeframe, OHLCV, Pattern, MarketRegime, Strategy, IndicatorScorecardItem, TradePlaybook, ActiveWindow, MicrostructureInsight, EntryTimingInsight } from '@/types/trading';

const TIMEFRAMES: Timeframe[] = [
  { value: 'M1', label: 'M1', minutes: 1 },
  { value: 'M5', label: 'M5', minutes: 5 },
  { value: 'M15', label: 'M15', minutes: 15 },
  { value: 'M30', label: 'M30', minutes: 30 },
  { value: 'H1', label: 'H1', minutes: 60 },
  { value: 'H4', label: 'H4', minutes: 240 },
  { value: 'D1', label: 'D1', minutes: 1440 },
];

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '');

async function safeFetch<T>(url: string, fallback: T): Promise<T> {
  try {
    const res = await fetch(url);
    if (!res.ok) return fallback;
    return await res.json();
  } catch {
    return fallback;
  }
}

export function useTradingData() {
  const [symbols, setSymbols] = useState<Symbol[]>([]);
  const [timeframes] = useState<Timeframe[]>(TIMEFRAMES);
  const [selectedSymbol, setSelectedSymbol] = useState<Symbol>({ name: 'EURUSD' } as Symbol);
  const [selectedTimeframe, setSelectedTimeframe] = useState<Timeframe>(TIMEFRAMES[4]);
  const [data, setData] = useState<OHLCV[]>([]);
  const [patterns, setPatterns] = useState<Pattern[]>([]);
  const [regime, setRegime] = useState<MarketRegime | null>(null);
  const [recommendation, setRecommendation] = useState<{ strategy: string; reason: string; confidence: number } | null>(null);
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [heatmapData, setHeatmapData] = useState<number[][] | null>(null);
  const [mlInsights, setMlInsights] = useState<{
    features: { feature: string; importance: number; description: string }[];
    successProbability: number;
    explanation: string;
    scorecard: IndicatorScorecardItem[];
    playbooks: TradePlaybook[];
    activeWindows: ActiveWindow[];
    microstructure: MicrostructureInsight;
    entryTiming: EntryTimingInsight;
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSymbols = useCallback(async () => {
    const data = await safeFetch<{ name: string }[]>(`${API_BASE_URL}/symbols`, []);
    const syms = data.map(s => ({ name: s.name } as Symbol));
    setSymbols(syms);
    if (syms.length > 0) setSelectedSymbol(syms[0]);
  }, []);

  const fetchData = useCallback(async () => {
    if (!selectedSymbol?.name) return;
    setLoading(true);
    setError(null);

    try {
      const sym = selectedSymbol.name;
      const tf = selectedTimeframe.value;

      // Fetch all data in parallel — each request is independent and won't crash if one fails
      const [ohlcv, analysis, strats, hm, ml] = await Promise.all([
        safeFetch<OHLCV[]>(`${API_BASE_URL}/ohlcv?symbol=${sym}&timeframe=${tf}`, []),
        safeFetch<{ regime: MarketRegime | null; patterns: Pattern[]; recommendation: any }>(
          `${API_BASE_URL}/analysis?symbol=${sym}&timeframe=${tf}`,
          { regime: null, patterns: [], recommendation: null }
        ),
        safeFetch<Strategy[]>(`${API_BASE_URL}/strategies?symbol=${sym}&timeframe=${tf}`, []),
        safeFetch<number[][]>(`${API_BASE_URL}/heatmap?symbol=${sym}&timeframe=${tf}`, []),
        safeFetch<{ features: any[]; successProbability: number; explanation: string; scorecard: IndicatorScorecardItem[]; playbooks: TradePlaybook[]; activeWindows: ActiveWindow[]; microstructure: MicrostructureInsight; entryTiming: EntryTimingInsight }>(
          `${API_BASE_URL}/ml-insights?symbol=${sym}&timeframe=${tf}`,
          { features: [], successProbability: 0, explanation: 'Sem dados disponíveis.', scorecard: [], playbooks: [], activeWindows: [], microstructure: { pressureBias: 'indefinido', uptickRatio: 0, spreadState: 'sem dados', avgSpread: 0, recentSpread: 0, activeBursts: [] }, entryTiming: { bestWindow: null, trigger: 'N/A', executionHint: 'Sem dados suficientes.' } }
        ),
      ]);

      if (ohlcv.length > 0) setData(ohlcv);
      setRegime(analysis.regime);
      setPatterns(analysis.patterns || []);
      setRecommendation(analysis.recommendation);
      setStrategies(strats);
      if (hm.length > 0) setHeatmapData(hm);
      setMlInsights(ml);

      if (ohlcv.length === 0) {
        setError(`Sem dados para ${sym} no timeframe ${tf}. Tente outro símbolo.`);
      }
    } catch (err) {
      setError('Erro ao conectar com o Backend/MT5.');
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
    recommendation,
    strategies,
    heatmapData,
    mlInsights,
    loading,
    error,
    setSelectedSymbol,
    setSelectedTimeframe,
    refreshData: fetchData,
  };
}
