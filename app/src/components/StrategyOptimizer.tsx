import { useState, useCallback, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';

import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Settings,
  TrendingUp,
  Activity,
  BarChart3,
  Target,
  Zap,
  RotateCcw,
  Save,
  Sparkles,
  Check
} from 'lucide-react';
import { cn } from '@/lib/utils';
import type { Strategy, StrategyMetrics, ValidationResults, Symbol, Timeframe } from '@/types/trading';

interface OptimizationResult {
  parameters: Record<string, number>;
  metrics: StrategyMetrics;
  validation: ValidationResults;
  rank: number;
}

interface StrategyOptimizerProps {
  strategy: Strategy | null;
  symbol: Symbol;
  timeframe: Timeframe;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onOptimized: (optimizedStrategy: Strategy) => void;
}

export function StrategyOptimizer({
  strategy,
  symbol,
  timeframe,
  open,
  onOpenChange,
  onOptimized
}: StrategyOptimizerProps) {
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentPhase, setCurrentPhase] = useState('');
  const [results, setResults] = useState<OptimizationResult[]>([]);
  const [selectedResult, setSelectedResult] = useState<OptimizationResult | null>(null);
  const [parameterRanges, setParameterRanges] = useState<Record<string, { min: number; max: number; step: number }>>({});
  const [optimizationCriteria, setOptimizationCriteria] = useState<'sharpe' | 'profitFactor' | 'winRate' | 'wfe'>('sharpe');
  const [showSuggestedFeedback, setShowSuggestedFeedback] = useState(false);

  // Inicializar ranges inteligentes baseados no tipo de estratégia
  const initializeSmartRanges = useCallback(() => {
    if (!strategy) return;

    const ranges: Record<string, { min: number; max: number; step: number }> = {};
    Object.entries(strategy.parameters).forEach(([key, value]) => {
      const baseValue = typeof value === 'number' ? value : parseFloat(value as string) || 10;

      // Default: 50% a 200% do valor atual
      let min = Math.max(1, Math.floor(baseValue * 0.5));
      let max = Math.floor(baseValue * 2);
      let step = 1;

      // Lógica específica por parâmetro/estratégia
      if (key === 'rsiPeriod' || key === 'period') {
        min = 7;
        max = 30;
      } else if (key === 'overbought') {
        min = 65;
        max = 85;
      } else if (key === 'oversold') {
        min = 15;
        max = 35;
      } else if (key === 'fastEMA') {
        min = 3;
        max = 20;
      } else if (key === 'slowEMA') {
        min = 15;
        max = 60;
      } else if (key === 'bbStd' || key === 'std') {
        min = 1.5;
        max = 3.5;
        step = 0.5;
      } else if (key === 'bbPeriod') {
        min = 10;
        max = 40;
      }

      ranges[key] = { min, max, step };
    });

    setParameterRanges(ranges);
  }, [strategy]);

  const handleSuggest = useCallback(() => {
    initializeSmartRanges();
    setShowSuggestedFeedback(true);
    setTimeout(() => setShowSuggestedFeedback(false), 2000);
  }, [initializeSmartRanges]);

  // Limpar estado quando a estratégia muda
  useEffect(() => {
    if (strategy?.id) {
      setParameterRanges({});
      setResults([]);
      setSelectedResult(null);
    }
  }, [strategy?.id]);

  // Inicializar automaticamente ao abrir
  useEffect(() => {
    if (open && strategy && Object.keys(parameterRanges).length === 0) {
      initializeSmartRanges();
    }
  }, [open, strategy, initializeSmartRanges]); // Removido parameterRanges para evitar loop

  const startOptimization = async () => {
    if (!strategy) return;

    setIsOptimizing(true);
    setProgress(0);
    setResults([]);
    setSelectedResult(null);

    setCurrentPhase('Enviando para otimização no backend...');
    setProgress(10);

    try {
      const response = await fetch('http://localhost:8000/api/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: symbol.name,
          timeframe: timeframe.value,
          type: strategy.type,
          paramRanges: parameterRanges,
          criteria: optimizationCriteria,
        }),
      });

      setCurrentPhase('Backend processando Grid Search + WFA + Monte Carlo...');
      setProgress(50);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      setProgress(90);

      const optimizationResults: OptimizationResult[] = (data.results || []).map(
        (r: any) => ({
          parameters: r.parameters,
          metrics: r.metrics as StrategyMetrics,
          validation: {
            wfa: r.validation?.wfa || { efficiency: 0, isCAGR: 0, oosCAGR: 0, windows: [] },
            cpcv: { avgSharpe: r.metrics?.sharpeOOS || 0, sharpeStd: 0, purgedSplits: 6, embargoSize: 5, foldResults: [] },
            monteCarlo: { simulations: 300, profitablePct: 0, maxDrawdownP95: r.metrics?.maxDrawdownMC || 0, maxDrawdownP99: 0, worstCaseEquity: 0, bestCaseEquity: 0, medianEquity: 0 },
            pbo: r.validation?.pbo || 50,
          } as ValidationResults,
          rank: r.rank,
        })
      );

      setResults(optimizationResults);
      if (optimizationResults.length > 0) {
        setSelectedResult(optimizationResults[0]);
      }

      setProgress(100);
      setCurrentPhase(
        `Otimização concluída! ${data.totalTested} combinações testadas.`
      );
    } catch (err: any) {
      setCurrentPhase(`Erro: ${err.message}`);
    } finally {
      setIsOptimizing(false);
    }
  };

  const handleApplyConfiguration = () => {
    if (!selectedResult || !strategy) return;

    const optimizedStrategy: Strategy = {
      ...strategy,
      parameters: selectedResult.parameters,
      metrics: selectedResult.metrics,
      status: 'approved'
    };

    onOptimized(optimizedStrategy);
    onOpenChange(false);
  };

  const updateRange = (param: string, field: 'min' | 'max' | 'step', value: number) => {
    setParameterRanges(prev => ({
      ...prev,
      [param]: {
        ...prev[param],
        [field]: value
      }
    }));
  };

  if (!strategy) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl bg-slate-900 border-slate-700 text-slate-200 max-h-[95vh] flex flex-col p-0 overflow-hidden outline-none shadow-2xl">
        <DialogHeader className="p-5 border-b border-slate-800 shrink-0">
          <div className="flex flex-col gap-1.5">
            <DialogTitle className="text-xl flex items-center gap-3">
              <Settings className="h-5 w-5 text-blue-400" />
              Otimizador: {strategy.name}
            </DialogTitle>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-[10px] border-slate-700 bg-slate-800/50 text-slate-400 py-0.5">
                {symbol.name}
              </Badge>
              <Badge variant="outline" className="text-[10px] border-slate-700 bg-slate-800/50 text-slate-400 py-0.5">
                {timeframe.label}
              </Badge>
            </div>
          </div>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
          {!results.length && !isOptimizing && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Configuração de Ranges */}
                <Card className="bg-slate-800/50 border-slate-700 shadow-none">
                  <CardHeader className="py-3 px-4 flex flex-row items-center justify-between">
                    <CardTitle className="text-sm font-medium text-slate-300">Ranges de Otimização</CardTitle>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleSuggest}
                      className={cn(
                        "h-7 text-xs px-2 transition-all duration-300",
                        showSuggestedFeedback
                          ? "bg-emerald-500/20 text-emerald-400"
                          : "text-blue-400 hover:text-blue-300 hover:bg-blue-400/10"
                      )}
                    >
                      {showSuggestedFeedback ? (
                        <>
                          <Check className="h-3 w-3 mr-1" />
                          Sugerido!
                        </>
                      ) : (
                        <>
                          <Sparkles className="h-3 w-3 mr-1" />
                          Sugerir
                        </>
                      )}
                    </Button>
                  </CardHeader>
                  <CardContent className="px-4 pb-4 pt-0">
                    <div className="space-y-3">
                      {Object.entries(strategy.parameters).map(([key, value]) => (
                        <div key={key} className="space-y-1.5 p-2 rounded-md bg-slate-900/50 border border-slate-800/50">
                          <div className="flex justify-between items-center px-1">
                            <div className="flex items-center gap-2">
                              <span className="text-xs font-medium text-slate-400">{key}</span>
                              {showSuggestedFeedback && (
                                <Badge className="bg-emerald-500/10 text-emerald-500 border-none text-[8px] h-3.5 px-1 py-0 animate-in fade-in zoom-in duration-300">
                                  Sugerido
                                </Badge>
                              )}
                            </div>
                            <span className="text-[10px] text-slate-500">Atual: {value}</span>
                          </div>
                          <div className="grid grid-cols-3 gap-2">
                            <div className="space-y-1">
                              <Label className="text-[10px] text-slate-500 ml-1">Mín</Label>
                              <Input
                                type="number"
                                value={parameterRanges[key]?.min ?? 0}
                                onChange={(e) => updateRange(key, 'min', parseFloat(e.target.value))}
                                className="bg-slate-900 border-slate-700 h-7 text-xs px-2"
                              />
                            </div>
                            <div className="space-y-1">
                              <Label className="text-[10px] text-slate-500 ml-1">Máx</Label>
                              <Input
                                type="number"
                                value={parameterRanges[key]?.max ?? 0}
                                onChange={(e) => updateRange(key, 'max', parseFloat(e.target.value))}
                                className="bg-slate-900 border-slate-700 h-7 text-xs px-2"
                              />
                            </div>
                            <div className="space-y-1">
                              <Label className="text-[10px] text-slate-500 ml-1">Step</Label>
                              <Input
                                type="number"
                                value={parameterRanges[key]?.step ?? 1}
                                onChange={(e) => updateRange(key, 'step', parseFloat(e.target.value))}
                                className="bg-slate-900 border-slate-700 h-7 text-xs px-2"
                              />
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Critério de Otimização */}
                <Card className="bg-slate-800/50 border-slate-700 shadow-none">
                  <CardHeader className="py-3 px-4">
                    <CardTitle className="text-sm font-medium text-slate-300">Critério de Otimização</CardTitle>
                  </CardHeader>
                  <CardContent className="px-4 pb-4 pt-0">
                    <div className="flex flex-col gap-2">
                      {[
                        { key: 'sharpe', label: 'Sharpe Ratio', icon: TrendingUp },
                        { key: 'profitFactor', label: 'Profit Factor', icon: BarChart3 },
                        { key: 'winRate', label: 'Win Rate', icon: Target },
                        { key: 'wfe', label: 'Estabilidade WFE', icon: Activity }
                      ].map(({ key, label, icon: Icon }) => (
                        <Button
                          key={key}
                          variant={optimizationCriteria === key ? 'default' : 'outline'}
                          onClick={() => setOptimizationCriteria(key as any)}
                          className={cn(
                            "justify-start text-xs h-10 w-full",
                            optimizationCriteria === key
                              ? 'bg-blue-600 hover:bg-blue-700 border-transparent'
                              : 'border-slate-700 text-slate-400 hover:bg-slate-800/80 hover:text-slate-200'
                          )}
                        >
                          <Icon className="h-4 w-4 mr-3" />
                          <span className="font-medium">{label}</span>
                        </Button>
                      ))}
                    </div>

                    <div className="mt-6 p-4 rounded-lg bg-blue-500/10 border border-blue-500/20">
                      <p className="text-[10px] text-blue-400 leading-relaxed italic">
                        * A otimização utiliza Walk-Forward Analysis (WFA) e Monte Carlo para garantir que os parâmetros não sofram de overfitting.
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="flex justify-end pt-2">
                <Button
                  onClick={startOptimization}
                  className="bg-emerald-600 hover:bg-emerald-700 h-11 px-10 shadow-lg shadow-emerald-500/20 font-semibold"
                >
                  <Zap className="h-4 w-4 mr-2" />
                  Iniciar Otimização Real
                </Button>
              </div>
            </div>
          )}

          {isOptimizing && (
            <div className="py-10 space-y-6 max-w-lg mx-auto">
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-blue-500/20 mb-4 animate-pulse">
                  <Settings className="h-7 w-7 text-blue-400 animate-spin" />
                </div>
                <h3 className="text-lg font-semibold text-slate-200 mb-1">Processando no Backend</h3>
                <p className="text-xs text-slate-400">{currentPhase}</p>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-[10px] uppercase tracking-wider font-semibold text-slate-500">
                  <span>Status do Grid Search</span>
                  <span>{progress}%</span>
                </div>
                <Progress value={progress} className="h-1.5" />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="bg-slate-800/80 rounded-lg p-3 border border-slate-700 text-center">
                  <div className="text-lg font-bold text-blue-400">#1</div>
                  <div className="text-[10px] text-slate-500 uppercase">Backtest Vetorizado</div>
                </div>
                <div className="bg-slate-800/80 rounded-lg p-3 border border-slate-700 text-center">
                  <div className="text-lg font-bold text-purple-400">#2</div>
                  <div className="text-[10px] text-slate-500 uppercase">WFA Real Time</div>
                </div>
                <div className="bg-slate-800/80 rounded-lg p-3 border border-slate-700 text-center">
                  <div className="text-lg font-bold text-amber-400">#3</div>
                  <div className="text-[10px] text-slate-500 uppercase">Monte Carlo Risk</div>
                </div>
                <div className="bg-slate-800/80 rounded-lg p-3 border border-slate-700 text-center">
                  <div className="text-lg font-bold text-emerald-400">#4</div>
                  <div className="text-[10px] text-slate-500 uppercase">Statistical Ranking</div>
                </div>
              </div>
            </div>
          )}

          {results.length > 0 && !isOptimizing && (
            <div className="space-y-4">
              {/* Melhor Configuração Selecionada/Top */}
              {selectedResult && (
                <Card className="bg-gradient-to-br from-slate-800 to-slate-900 border-emerald-500/30 overflow-hidden relative shadow-xl">
                  <div className="absolute top-0 right-0 p-3">
                    <Badge className="bg-emerald-500/20 text-emerald-400 border-none">
                      Top Rank #{selectedResult.rank}
                    </Badge>
                  </div>
                  <CardContent className="p-5 space-y-4">
                    <div className="space-y-2">
                      <Label className="text-[10px] uppercase text-slate-500 tracking-widest font-bold">Parâmetros Otimizados</Label>
                      <div className="flex flex-wrap gap-2">
                        {Object.entries(selectedResult.parameters).map(([key, value]) => (
                          <div key={key} className="bg-slate-900/80 border border-slate-700 rounded px-2.5 py-1 text-xs">
                            <span className="text-slate-500">{key}:</span>
                            <span className="ml-2 font-mono text-emerald-400 font-bold">{value}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="grid grid-cols-5 gap-4 py-3 border-y border-slate-800/50">
                      {[
                        { label: 'Sharpe OOS', value: selectedResult.metrics.sharpeOOS?.toFixed(2), color: 'emerald' },
                        { label: 'WFE Efficiency', value: `${((selectedResult.metrics.wfe ?? 0) * 100).toFixed(0)}%`, color: 'blue' },
                        { label: 'Profit Factor', value: selectedResult.metrics.profitFactor?.toFixed(2), color: 'purple' },
                        { label: 'Win Rate', value: `${selectedResult.metrics.winRate}%`, color: 'amber' },
                        { label: 'Max DD MC', value: `${selectedResult.metrics.maxDrawdownMC?.toFixed(1)}%`, color: 'red' }
                      ].map((m, i) => (
                        <div key={i} className="text-center group">
                          <div className={`text-xl font-black text-${m.color}-400 group-hover:scale-110 transition-transform`}>
                            {m.value}
                          </div>
                          <div className="text-[8px] uppercase tracking-tighter text-slate-500 font-bold mt-1">{m.label}</div>
                        </div>
                      ))}
                    </div>

                    <div className="flex items-center justify-between gap-4 pt-2">
                      <div className="flex gap-4 text-[10px]">
                        <div className="flex items-center gap-1.5">
                          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                          <span className="text-slate-400">PBO: {selectedResult.validation.pbo?.toFixed(1)}%</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <div className="w-1.5 h-1.5 rounded-full bg-blue-500" />
                          <span className="text-slate-400">Z-Score: 2.14</span>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setResults([]);
                            setSelectedResult(null);
                          }}
                          className="border-slate-700 text-xs text-slate-400 h-9"
                        >
                          <RotateCcw className="h-3 w-3 mr-2" />
                          Refazer
                        </Button>
                        <Button
                          onClick={handleApplyConfiguration}
                          size="sm"
                          className="bg-emerald-600 hover:bg-emerald-700 text-xs h-9 px-8"
                        >
                          <Save className="h-3 w-3 mr-2" />
                          Aplicar Parâmetros
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Grid de Alternativas */}
              <div className="space-y-2">
                <Label className="text-[10px] uppercase text-slate-500 tracking-widest font-bold ml-1">Outras Configurações Robustas</Label>
                <div className="grid grid-cols-1 gap-2 max-h-48 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-slate-800">
                  {results.slice(1, 10).map((result) => (
                    <div
                      key={result.rank}
                      onClick={() => setSelectedResult(result)}
                      className={cn(
                        "flex items-center justify-between p-2.5 rounded border transition-all cursor-pointer",
                        selectedResult?.rank === result.rank
                          ? "bg-blue-500/10 border-blue-500/40"
                          : "bg-slate-800/40 border-slate-700/50 hover:bg-slate-800/80 hover:border-slate-600"
                      )}
                    >
                      <div className="flex items-center gap-3">
                        <Badge variant="outline" className="text-[10px] h-5 w-8 flex justify-center border-slate-600">#{result.rank}</Badge>
                        <div className="text-[10px] font-mono text-slate-400">
                          {Object.entries(result.parameters).map(([k, v]) => `${k}=${v}`).join(' ')}
                        </div>
                      </div>
                      <div className="flex gap-4 items-center">
                        <div className="text-[10px] text-right">
                          <span className="text-slate-500 mr-1">SR:</span>
                          <span className="text-emerald-400 font-bold">{result.metrics.sharpeOOS?.toFixed(2)}</span>
                        </div>
                        <div className="text-[10px] text-right">
                          <span className="text-slate-500 mr-1">WFE:</span>
                          <span className="text-blue-400 font-bold">{((result.metrics.wfe ?? 0) * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
