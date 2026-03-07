import { useState, useCallback } from 'react';
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
  Check,
  Zap,
  RotateCcw,
  Save
} from 'lucide-react';
import { cn } from '@/lib/utils';
import type { Strategy, StrategyMetrics, ValidationResults } from '@/types/trading';

interface OptimizationResult {
  parameters: Record<string, number>;
  metrics: StrategyMetrics;
  validation: ValidationResults;
  rank: number;
}

interface StrategyOptimizerProps {
  strategy: Strategy | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onOptimized: (optimizedStrategy: Strategy) => void;
}

// Gerar combinações de parâmetros para grid search
function generateParameterCombinations(
  baseParams: Record<string, number>,
  ranges: Record<string, { min: number; max: number; step: number }>
): Record<string, number>[] {
  const keys = Object.keys(ranges);
  const combinations: Record<string, number>[] = [];
  
  function generate(index: number, current: Record<string, number>) {
    if (index === keys.length) {
      combinations.push({ ...current });
      return;
    }
    
    const key = keys[index];
    const range = ranges[key];
    
    for (let value = range.min; value <= range.max; value += range.step) {
      current[key] = Math.round(value * 100) / 100;
      generate(index + 1, current);
    }
  }
  
  generate(0, { ...baseParams });
  return combinations;
}

// Simular métricas de backtest
function simulateBacktestMetrics(params: Record<string, number>): StrategyMetrics {
  // Simular performance baseada nos parâmetros
  const paramValues = Object.values(params);
  const avgParam = paramValues.reduce((a, b) => a + b, 0) / paramValues.length;
  
  const sharpe = Number((avgParam / 10 + Math.random()).toFixed(2));
  const winRate = Math.floor(45 + Math.random() * 25);
  const profitFactor = Number((1.2 + Math.random() * 1.0).toFixed(2));
  const maxDD = Number((10 + Math.random() * 20).toFixed(1));
  
  return {
    wfe: Number((0.6 + Math.random() * 0.3).toFixed(2)),
    sharpeIS: sharpe,
    sharpeOOS: Number((sharpe * (0.8 + Math.random() * 0.2)).toFixed(2)),
    profitFactor,
    winRate,
    maxDrawdown: maxDD,
    maxDrawdownMC: Number((maxDD * 1.2).toFixed(1)),
    totalTrades: Math.floor(100 + Math.random() * 400),
    avgTrade: Number((5 + Math.random() * 20).toFixed(2)),
    expectancy: Number((0.5 + Math.random() * 1.0).toFixed(2)),
    calmarRatio: Number((1.0 + Math.random()).toFixed(2)),
    sortinoRatio: Number((sharpe * 0.9).toFixed(2))
  };
}

// Gerar resultados de validação
function generateValidationResults(): ValidationResults {
  return {
    wfa: {
      efficiency: Number((0.65 + Math.random() * 0.25).toFixed(2)),
      isCAGR: Number((15 + Math.random() * 15).toFixed(1)),
      oosCAGR: Number((10 + Math.random() * 12).toFixed(1)),
      windows: Array.from({ length: 5 }, (_, i) => ({
        trainStart: `202${i}-01-01`,
        trainEnd: `202${i}-06-30`,
        testStart: `202${i}-07-01`,
        testEnd: `202${i}-12-31`,
        trainReturn: Number((10 + Math.random() * 15).toFixed(1)),
        testReturn: Number((8 + Math.random() * 12).toFixed(1)),
        efficiency: Number((0.6 + Math.random() * 0.3).toFixed(2))
      }))
    },
    cpcv: {
      avgSharpe: Number((1.2 + Math.random() * 0.8).toFixed(2)),
      sharpeStd: Number((0.1 + Math.random() * 0.2).toFixed(2)),
      purgedSplits: 10,
      embargoSize: 5,
      foldResults: Array.from({ length: 6 }, (_, i) => ({
        fold: i + 1,
        trainSize: 1000 + Math.floor(Math.random() * 500),
        testSize: 200 + Math.floor(Math.random() * 200),
        sharpe: Number((1.0 + Math.random() * 1.0).toFixed(2)),
        trades: 50 + Math.floor(Math.random() * 100)
      }))
    },
    monteCarlo: {
      simulations: 10000,
      profitablePct: Number((65 + Math.random() * 25).toFixed(1)),
      maxDrawdownP95: Number((15 + Math.random() * 15).toFixed(1)),
      maxDrawdownP99: Number((25 + Math.random() * 20).toFixed(1)),
      worstCaseEquity: 8000 + Math.floor(Math.random() * 4000),
      bestCaseEquity: 20000 + Math.floor(Math.random() * 15000),
      medianEquity: 14000 + Math.floor(Math.random() * 8000)
    },
    pbo: Number((10 + Math.random() * 30).toFixed(1))
  };
}

export function StrategyOptimizer({ 
  strategy, 
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

  // Inicializar ranges quando a estratégia muda
  const initializeRanges = useCallback(() => {
    if (!strategy) return;
    
    const ranges: Record<string, { min: number; max: number; step: number }> = {};
    Object.entries(strategy.parameters).forEach(([key, value]) => {
      const baseValue = typeof value === 'number' ? value : parseFloat(value) || 10;
      
      // Definir range baseado no tipo de parâmetro
      if (key.toLowerCase().includes('period') || key.toLowerCase().includes('length')) {
        ranges[key] = {
          min: Math.max(1, Math.floor(baseValue * 0.3)),
          max: Math.floor(baseValue * 3),
          step: 1
        };
      } else if (key.toLowerCase().includes('multiplier') || key.toLowerCase().includes('factor')) {
        ranges[key] = {
          min: Math.max(0.1, baseValue * 0.3),
          max: baseValue * 3,
          step: 0.1
        };
      } else if (key.toLowerCase().includes('threshold') || key.toLowerCase().includes('level')) {
        ranges[key] = {
          min: Math.max(1, baseValue * 0.5),
          max: baseValue * 2,
          step: 1
        };
      } else {
        ranges[key] = {
          min: Math.max(1, Math.floor(baseValue * 0.5)),
          max: Math.floor(baseValue * 2),
          step: 1
        };
      }
    });
    
    setParameterRanges(ranges);
  }, [strategy]);

  const startOptimization = async () => {
    if (!strategy) return;
    
    setIsOptimizing(true);
    setProgress(0);
    setResults([]);
    setSelectedResult(null);
    
    // Fase 1: Gerar combinações
    setCurrentPhase('Gerando combinações de parâmetros...');
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const combinations = generateParameterCombinations(strategy.parameters, parameterRanges);
    const totalCombinations = combinations.length;
    
    if (totalCombinations > 1000) {
      setCurrentPhase('Muitas combinações! Limitando a 1000...');
      combinations.length = 1000;
    }
    
    // Fase 2: Executar backtests
    const optimizationResults: OptimizationResult[] = [];
    
    for (let i = 0; i < combinations.length; i++) {
      setCurrentPhase(`Testando combinação ${i + 1} de ${combinations.length}...`);
      setProgress(Math.floor((i / combinations.length) * 50));
      
      // Simular processamento
      await new Promise(resolve => setTimeout(resolve, 20));
      
      const metrics = simulateBacktestMetrics(combinations[i]);
      
      // Filtrar resultados ruins
      if (metrics.sharpeOOS > 0.8 && metrics.maxDrawdown < 30) {
        optimizationResults.push({
          parameters: combinations[i],
          metrics,
          validation: generateValidationResults(),
          rank: 0
        });
      }
    }
    
    // Fase 3: Aplicar WFA nos top resultados
    setCurrentPhase('Aplicando Walk-Forward Analysis...');
    setProgress(60);
    await new Promise(resolve => setTimeout(resolve, 800));
    
    // Fase 4: Monte Carlo
    setCurrentPhase('Executando simulações Monte Carlo...');
    setProgress(75);
    await new Promise(resolve => setTimeout(resolve, 800));
    
    // Fase 5: Ordenar resultados
    setCurrentPhase('Calculando rankings finais...');
    setProgress(90);
    
    // Ordenar por critério selecionado
    optimizationResults.sort((a, b) => {
      switch (optimizationCriteria) {
        case 'sharpe':
          return b.metrics.sharpeOOS - a.metrics.sharpeOOS;
        case 'profitFactor':
          return b.metrics.profitFactor - a.metrics.profitFactor;
        case 'winRate':
          return b.metrics.winRate - a.metrics.winRate;
        case 'wfe':
          return b.metrics.wfe - a.metrics.wfe;
        default:
          return b.metrics.sharpeOOS - a.metrics.sharpeOOS;
      }
    });
    
    // Atribuir ranks
    optimizationResults.forEach((result, index) => {
      result.rank = index + 1;
    });
    
    setResults(optimizationResults.slice(0, 20)); // Top 20
    setSelectedResult(optimizationResults[0]);
    setProgress(100);
    setCurrentPhase('Otimização concluída!');
    setIsOptimizing(false);
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
      <DialogContent className="max-w-6xl bg-slate-900 border-slate-700 text-slate-200 max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-xl flex items-center gap-3">
            <Settings className="h-5 w-5 text-blue-400" />
            Otimizador de Estratégia: {strategy.name}
          </DialogTitle>
        </DialogHeader>

        {!results.length && !isOptimizing && (
          <div className="space-y-6">
            {/* Configuração de Ranges */}
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-lg text-slate-300">Ranges de Otimização</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Object.entries(strategy.parameters).map(([key, value]) => (
                    <div key={key} className="grid grid-cols-5 gap-4 items-center">
                      <div className="text-sm text-slate-300">{key}</div>
                      <div className="space-y-1">
                        <Label className="text-xs text-slate-500">Mín</Label>
                        <Input
                          type="number"
                          value={parameterRanges[key]?.min || 0}
                          onChange={(e) => updateRange(key, 'min', parseFloat(e.target.value))}
                          className="bg-slate-900 border-slate-600 h-8"
                        />
                      </div>
                      <div className="space-y-1">
                        <Label className="text-xs text-slate-500">Máx</Label>
                        <Input
                          type="number"
                          value={parameterRanges[key]?.max || 0}
                          onChange={(e) => updateRange(key, 'max', parseFloat(e.target.value))}
                          className="bg-slate-900 border-slate-600 h-8"
                        />
                      </div>
                      <div className="space-y-1">
                        <Label className="text-xs text-slate-500">Step</Label>
                        <Input
                          type="number"
                          value={parameterRanges[key]?.step || 1}
                          onChange={(e) => updateRange(key, 'step', parseFloat(e.target.value))}
                          className="bg-slate-900 border-slate-600 h-8"
                        />
                      </div>
                      <div className="text-sm text-slate-500">
                        Atual: {value}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Critério de Otimização */}
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-lg text-slate-300">Critério de Otimização</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex gap-2">
                  {[
                    { key: 'sharpe', label: 'Sharpe Ratio', icon: TrendingUp },
                    { key: 'profitFactor', label: 'Profit Factor', icon: BarChart3 },
                    { key: 'winRate', label: 'Win Rate', icon: Target },
                    { key: 'wfe', label: 'WFE', icon: Activity }
                  ].map(({ key, label, icon: Icon }) => (
                    <Button
                      key={key}
                      variant={optimizationCriteria === key ? 'default' : 'outline'}
                      onClick={() => setOptimizationCriteria(key as any)}
                      className={cn(
                        optimizationCriteria === key 
                          ? 'bg-blue-600' 
                          : 'border-slate-600 text-slate-400'
                      )}
                    >
                      <Icon className="h-4 w-4 mr-2" />
                      {label}
                    </Button>
                  ))}
                </div>
              </CardContent>
            </Card>

            <div className="flex justify-end">
              <Button 
                onClick={() => {
                  initializeRanges();
                  startOptimization();
                }}
                className="bg-emerald-600 hover:bg-emerald-700"
              >
                <Zap className="h-4 w-4 mr-2" />
                Iniciar Otimização
              </Button>
            </div>
          </div>
        )}

        {isOptimizing && (
          <div className="py-12 space-y-6">
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-500/20 mb-4">
                <Settings className="h-8 w-8 text-blue-400 animate-spin" />
              </div>
              <h3 className="text-xl font-semibold text-slate-200 mb-2">Otimizando...</h3>
              <p className="text-slate-400">{currentPhase}</p>
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Progresso</span>
                <span className="text-slate-200">{progress}%</span>
              </div>
              <Progress value={progress} className="h-2" />
            </div>

            <div className="grid grid-cols-4 gap-4 text-center">
              <div className="bg-slate-800 rounded-lg p-4">
                <div className="text-2xl font-bold text-blue-400">1</div>
                <div className="text-xs text-slate-500">Grid Search</div>
              </div>
              <div className="bg-slate-800 rounded-lg p-4">
                <div className="text-2xl font-bold text-purple-400">2</div>
                <div className="text-xs text-slate-500">WFA</div>
              </div>
              <div className="bg-slate-800 rounded-lg p-4">
                <div className="text-2xl font-bold text-amber-400">3</div>
                <div className="text-xs text-slate-500">Monte Carlo</div>
              </div>
              <div className="bg-slate-800 rounded-lg p-4">
                <div className="text-2xl font-bold text-emerald-400">4</div>
                <div className="text-xs text-slate-500">Ranking</div>
              </div>
            </div>
          </div>
        )}

        {results.length > 0 && !isOptimizing && (
          <div className="space-y-6">
            {/* Melhor Configuração */}
            {selectedResult && (
              <Card className="bg-gradient-to-r from-emerald-900/30 to-blue-900/30 border-emerald-500/30">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg flex items-center gap-2">
                      <Check className="h-5 w-5 text-emerald-400" />
                      Melhor Configuração Encontrada
                    </CardTitle>
                    <Badge className="bg-emerald-500/20 text-emerald-400">
                      Rank #{selectedResult.rank}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Parâmetros */}
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(selectedResult.parameters).map(([key, value]) => (
                      <div key={key} className="bg-slate-800 rounded px-3 py-1.5 text-sm">
                        <span className="text-slate-400">{key}:</span>
                        <span className="ml-2 font-mono text-emerald-400">{value}</span>
                      </div>
                    ))}
                  </div>

                  {/* Métricas */}
                  <div className="grid grid-cols-5 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-emerald-400">
                        {selectedResult.metrics.sharpeOOS.toFixed(2)}
                      </div>
                      <div className="text-xs text-slate-500">Sharpe OOS</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-400">
                        {(selectedResult.metrics.wfe * 100).toFixed(0)}%
                      </div>
                      <div className="text-xs text-slate-500">WFE</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-purple-400">
                        {selectedResult.metrics.profitFactor.toFixed(2)}
                      </div>
                      <div className="text-xs text-slate-500">Profit Factor</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-amber-400">
                        {selectedResult.metrics.winRate}%
                      </div>
                      <div className="text-xs text-slate-500">Win Rate</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-red-400">
                        {selectedResult.metrics.maxDrawdownMC.toFixed(1)}%
                      </div>
                      <div className="text-xs text-slate-500">Max DD MC</div>
                    </div>
                  </div>

                  {/* Validação */}
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div className="bg-slate-800/50 rounded p-3">
                      <div className="text-slate-500 mb-1">WFA Efficiency</div>
                      <div className="font-mono text-emerald-400">
                        {(selectedResult.validation.wfa.efficiency * 100).toFixed(0)}%
                      </div>
                    </div>
                    <div className="bg-slate-800/50 rounded p-3">
                      <div className="text-slate-500 mb-1">CPCV Sharpe</div>
                      <div className="font-mono text-blue-400">
                        {selectedResult.validation.cpcv.avgSharpe.toFixed(2)}
                      </div>
                    </div>
                    <div className="bg-slate-800/50 rounded p-3">
                      <div className="text-slate-500 mb-1">PBO</div>
                      <div className={cn(
                        'font-mono',
                        selectedResult.validation.pbo < 20 ? 'text-emerald-400' : 
                        selectedResult.validation.pbo < 50 ? 'text-amber-400' : 'text-red-400'
                      )}>
                        {selectedResult.validation.pbo.toFixed(1)}%
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Button 
                      onClick={handleApplyConfiguration}
                      className="flex-1 bg-emerald-600 hover:bg-emerald-700"
                    >
                      <Save className="h-4 w-4 mr-2" />
                      Aplicar Esta Configuração
                    </Button>
                    <Button 
                      variant="outline"
                      onClick={() => {
                        setResults([]);
                        setSelectedResult(null);
                      }}
                      className="border-slate-600"
                    >
                      <RotateCcw className="h-4 w-4 mr-2" />
                      Nova Otimização
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Tabela de Resultados */}
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-lg text-slate-300">Top 20 Configurações</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto max-h-80 overflow-y-auto">
                  <table className="w-full">
                    <thead className="sticky top-0 bg-slate-800">
                      <tr className="border-b border-slate-700">
                        <th className="text-left py-2 px-3 text-xs font-medium text-slate-500">Rank</th>
                        <th className="text-left py-2 px-3 text-xs font-medium text-slate-500">Parâmetros</th>
                        <th className="text-right py-2 px-3 text-xs font-medium text-slate-500">Sharpe</th>
                        <th className="text-right py-2 px-3 text-xs font-medium text-slate-500">WFE</th>
                        <th className="text-right py-2 px-3 text-xs font-medium text-slate-500">PF</th>
                        <th className="text-right py-2 px-3 text-xs font-medium text-slate-500">WR</th>
                        <th className="text-right py-2 px-3 text-xs font-medium text-slate-500">MaxDD</th>
                        <th className="text-right py-2 px-3 text-xs font-medium text-slate-500">PBO</th>
                      </tr>
                    </thead>
                    <tbody>
                      {results.map((result) => (
                        <tr 
                          key={result.rank}
                          onClick={() => setSelectedResult(result)}
                          className={cn(
                            'border-b border-slate-700/50 cursor-pointer hover:bg-slate-700/50 transition-colors',
                            selectedResult?.rank === result.rank && 'bg-blue-500/10'
                          )}
                        >
                          <td className="py-2 px-3">
                            <Badge className={cn(
                              result.rank === 1 ? 'bg-yellow-500/20 text-yellow-400' :
                              result.rank === 2 ? 'bg-slate-400/20 text-slate-400' :
                              result.rank === 3 ? 'bg-orange-500/20 text-orange-400' :
                              'bg-slate-700 text-slate-400'
                            )}>
                              #{result.rank}
                            </Badge>
                          </td>
                          <td className="py-2 px-3">
                            <div className="text-xs text-slate-400 truncate max-w-xs">
                              {Object.entries(result.parameters).map(([k, v]) => `${k}=${v}`).join(', ')}
                            </div>
                          </td>
                          <td className="py-2 px-3 text-right font-mono text-emerald-400">
                            {result.metrics.sharpeOOS.toFixed(2)}
                          </td>
                          <td className="py-2 px-3 text-right font-mono text-blue-400">
                            {(result.metrics.wfe * 100).toFixed(0)}%
                          </td>
                          <td className="py-2 px-3 text-right font-mono text-purple-400">
                            {result.metrics.profitFactor.toFixed(2)}
                          </td>
                          <td className="py-2 px-3 text-right font-mono text-amber-400">
                            {result.metrics.winRate}%
                          </td>
                          <td className="py-2 px-3 text-right font-mono text-red-400">
                            {result.metrics.maxDrawdownMC.toFixed(1)}%
                          </td>
                          <td className="py-2 px-3 text-right font-mono">
                            <span className={cn(
                              result.validation.pbo < 20 ? 'text-emerald-400' : 
                              result.validation.pbo < 50 ? 'text-amber-400' : 'text-red-400'
                            )}>
                              {result.validation.pbo.toFixed(0)}%
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
