// Tipos principais para o sistema de trading

export interface Symbol {
  name: string;
  description: string;
  type: 'forex' | 'crypto' | 'index' | 'commodity';
  pipValue: number;
  spread: number;
}

export interface Timeframe {
  value: string;
  label: string;
  minutes: number;
}

export interface OHLCV {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface Pattern {
  id: string;
  type: 'triangle' | 'head_and_shoulders' | 'channel' | 'double_top' | 'double_bottom' | 'flag' | 'candlestick';
  name: string;
  timestamp: number;
  direction: 'up' | 'down' | 'neutral';
  frequency: number;
  accuracy: number;
  priceTarget?: number;
  stopLoss?: number;
}

export interface MarketRegime {
  type: 'trend_up' | 'trend_down' | 'range' | 'range_volatile' | 'breakout' | 'undefined';
  confidence: number;
  startTime: number;
  indicators: {
    adx: number;
    volatility: number;
    volumeProfile: string;
  };
}

export interface Strategy {
  id: string;
  name: string;
  type: 'trend' | 'reversal' | 'breakout' | 'scalping' | 'mean_reversion' | 'donchian';
  parameters: Record<string, number>;
  indicators: string[];
  metrics: StrategyMetrics;
  status: 'approved' | 'testing' | 'rejected';
  createdAt: number;
  pythonCode?: string;
}

export interface StrategyMetrics {
  wfe: number; // Walk-Forward Efficiency
  sharpeIS: number;
  sharpeOOS: number;
  profitFactor: number;
  winRate: number;
  maxDrawdown: number;
  maxDrawdownMC: number; // Monte Carlo P95
  totalTrades: number;
  avgTrade: number;
  expectancy: number;
  calmarRatio: number;
  sortinoRatio: number;
}

export interface BacktestResult {
  id: string;
  strategyId: string;
  symbol: string;
  timeframe: string;
  period: { start: string; end: string };
  metrics: StrategyMetrics;
  equityCurve: EquityPoint[];
  trades: Trade[];
  validation: ValidationResults;
  manifest: ReproducibilityManifest;
}

export interface EquityPoint {
  timestamp: number;
  equity: number;
  drawdown: number;
  trades: number;
}

export interface Trade {
  id: string;
  entryTime: number;
  exitTime: number;
  entryPrice: number;
  exitPrice: number;
  direction: 'long' | 'short';
  volume: number;
  profit: number;
  pips: number;
  sl: number;
  tp: number;
  exitReason: 'tp' | 'sl' | 'signal' | 'end';
}

export interface ValidationResults {
  wfa: WFAResult;
  cpcv: CPCVResult;
  monteCarlo: MonteCarloResult;
  pbo: number; // Probability of Backtest Overfitting
}

export interface WFAResult {
  efficiency: number;
  isCAGR: number;
  oosCAGR: number;
  windows: WFWindow[];
}

export interface WFWindow {
  trainStart: string;
  trainEnd: string;
  testStart: string;
  testEnd: string;
  trainReturn: number;
  testReturn: number;
  efficiency: number;
}

export interface CPCVResult {
  avgSharpe: number;
  sharpeStd: number;
  purgedSplits: number;
  embargoSize: number;
  foldResults: FoldResult[];
}

export interface FoldResult {
  fold: number;
  trainSize: number;
  testSize: number;
  sharpe: number;
  trades: number;
}

export interface MonteCarloResult {
  simulations: number;
  profitablePct: number;
  maxDrawdownP95: number;
  maxDrawdownP99: number;
  worstCaseEquity: number;
  bestCaseEquity: number;
  medianEquity: number;
}

export interface ReproducibilityManifest {
  seed: number;
  datasetHash: string;
  codeHash: string;
  branch: string;
  pythonVersion: string;
  dependenciesHash: string;
  timestamp: string;
  configuration: Record<string, any>;
}

export interface MLFeatures {
  rsi: number;
  macd: number;
  macdSignal: number;
  atr: number;
  bbUpper: number;
  bbLower: number;
  bbWidth: number;
  volume: number;
  volumeMA: number;
  returns: number;
  volatility: number;
  zScore: number;
  ema20: number;
  ema50: number;
  ema200: number;
}

export interface FeatureImportance {
  feature: string;
  importance: number;
  description: string;
}

export interface IndicatorScorecardItem {
  indicator: string;
  currentSignal: string;
  accuracy: number;
  avgEdge: number;
  fitScore: number;
  sampleSize: number;
  rationale: string;
}

export interface TradePlaybook {
  title: string;
  bias: string;
  confidence: number;
  setup: string;
  entry: string;
  confirmation: string;
  invalidation: string;
  holdingPeriod: string;
}

export interface ActiveWindow {
  label: string;
  bias: string;
  edge: number;
  samples: number;
}

export interface EntryTimingInsight {
  bestWindow: ActiveWindow | null;
  trigger: string;
  executionHint: string;
}

export interface MicrostructureInsight {
  pressureBias: string;
  uptickRatio: number;
  spreadState: string;
  avgSpread: number;
  recentSpread: number;
  activeBursts: Array<{
    label: string;
    bias: string;
    tickCount: number;
    avgSpread: number;
    intensity: number;
  }>;
}

export interface StrategyRecommendation {
  strategy: Strategy;
  confidence: number;
  expectedReturn: number;
  riskLevel: 'low' | 'medium' | 'high';
  explanation: string;
  similarSetups: number;
  successRate: number;
}

export interface EAExport {
  code: string;
  language: 'mql4' | 'mql5';
  parameters: Record<string, number>;
  setFile: string;
  jsonConfig: string;
  yamlConfig: string;
}

export interface UserSettings {
  mt5Path: string;
  defaultRisk: number;
  maxDrawdown: number;
  minTrades: number;
  minPeriod: number;
  apiEndpoint: string;
  theme: 'dark' | 'light';
}
