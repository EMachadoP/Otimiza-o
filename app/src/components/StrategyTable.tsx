import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Eye, Download, Settings, TrendingUp, TrendingDown, Activity, Target, Zap } from 'lucide-react';
import type { Strategy } from '@/types/trading';
import { cn } from '@/lib/utils';

interface StrategyTableProps {
  strategies: Strategy[];
  onViewDetails?: (strategy: Strategy) => void;
  onExportEA?: (strategy: Strategy) => void;
  onGenerateParams?: (strategy: Strategy) => void;
  onOptimize?: (strategy: Strategy) => void;
}

const typeLabels: Record<string, string> = {
  trend: 'Tendência',
  reversal: 'Reversão',
  breakout: 'Breakout',
  scalping: 'Scalping',
  mean_reversion: 'Mean Reversion',
  donchian: 'Donchian'
};

const typeColors: Record<string, string> = {
  trend: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  reversal: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  breakout: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  scalping: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  mean_reversion: 'bg-pink-500/20 text-pink-400 border-pink-500/30',
  donchian: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30'
};

const statusColors: Record<string, string> = {
  approved: 'bg-emerald-500/20 text-emerald-400',
  testing: 'bg-amber-500/20 text-amber-400',
  rejected: 'bg-red-500/20 text-red-400'
};

const statusLabels: Record<string, string> = {
  approved: 'Aprovada',
  testing: 'Em Teste',
  rejected: 'Rejeitada'
};

export function StrategyTable({
  strategies,
  onViewDetails,
  onExportEA,
  onGenerateParams,
  onOptimize
}: StrategyTableProps) {
  const [selectedStrategy, setSelectedStrategy] = useState<Strategy | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  const handleViewDetails = (strategy: Strategy) => {
    setSelectedStrategy(strategy);
    setShowDetails(true);
    onViewDetails?.(strategy);
  };

  const getMetricColor = (value: number, type: 'good' | 'bad' = 'good') => {
    if (type === 'good') {
      if (value >= 0.8) return 'text-emerald-400';
      if (value >= 0.6) return 'text-amber-400';
      return 'text-red-400';
    }
    if (value <= 15) return 'text-emerald-400';
    if (value <= 25) return 'text-amber-400';
    return 'text-red-400';
  };

  return (
    <>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-700">
              <th className="text-left py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Rank</th>
              <th className="text-left py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Estratégia</th>
              <th className="text-left py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Tipo</th>
              <th className="text-right py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">WFE</th>
              <th className="text-right py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Sharpe OOS</th>
              <th className="text-right py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Max DD (MC P95)</th>
              <th className="text-center py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Status</th>
              <th className="text-center py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Ações</th>
            </tr>
          </thead>
          <tbody>
            {strategies.map((strategy, index) => (
              <tr
                key={strategy.id}
                className="border-b border-slate-800 hover:bg-slate-800/50 transition-colors"
              >
                <td className="py-3 px-4">
                  <div className="flex items-center gap-2">
                    {index === 0 && <span className="text-xl">🥇</span>}
                    {index === 1 && <span className="text-xl">🥈</span>}
                    {index === 2 && <span className="text-xl">🥉</span>}
                    {index > 2 && <span className="text-slate-500 font-mono">{index + 1}</span>}
                  </div>
                </td>
                <td className="py-3 px-4">
                  <div className="font-medium text-slate-200">{strategy.name}</div>
                  <div className="text-xs text-slate-500">
                    {strategy.indicators.join(' + ')}
                  </div>
                </td>
                <td className="py-3 px-4">
                  <Badge variant="outline" className={cn('text-xs', typeColors[strategy.type])}>
                    {typeLabels[strategy.type]}
                  </Badge>
                </td>
                <td className="py-3 px-4 text-right">
                  <span className={cn('font-mono font-semibold', getMetricColor(strategy.metrics?.wfe ?? 0))}>
                    {((strategy.metrics?.wfe ?? 0) * 100).toFixed(0)}%
                  </span>
                </td>
                <td className="py-3 px-4 text-right">
                  <span className={cn('font-mono font-semibold', getMetricColor((strategy.metrics?.sharpeOOS ?? 0) / 2))}>
                    {(strategy.metrics?.sharpeOOS ?? 0).toFixed(2)}
                  </span>
                </td>
                <td className="py-3 px-4 text-right">
                  <span className={cn('font-mono font-semibold', getMetricColor(strategy.metrics?.maxDrawdownMC ?? 0, 'bad'))}>
                    {(strategy.metrics?.maxDrawdownMC ?? 0).toFixed(1)}%
                  </span>
                </td>
                <td className="py-3 px-4 text-center">
                  <Badge className={cn('text-xs', statusColors[strategy.status])}>
                    {statusLabels[strategy.status]}
                  </Badge>
                </td>
                <td className="py-3 px-4">
                  <div className="flex items-center justify-center gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-slate-400 hover:text-slate-200"
                      onClick={() => handleViewDetails(strategy)}
                      title="Ver detalhes"
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-slate-400 hover:text-emerald-400"
                      onClick={() => onExportEA?.(strategy)}
                      title="Exportar para EA"
                    >
                      <Download className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-slate-400 hover:text-blue-400"
                      onClick={() => onGenerateParams?.(strategy)}
                      title="Gerar parâmetros"
                    >
                      <Settings className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-slate-400 hover:text-purple-400"
                      onClick={() => onOptimize?.(strategy)}
                      title="Otimizar estratégia"
                    >
                      <Zap className="h-4 w-4" />
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Dialog de detalhes */}
      <Dialog open={showDetails} onOpenChange={setShowDetails}>
        <DialogContent className="max-w-4xl bg-slate-900 border-slate-700 text-slate-200">
          <DialogHeader>
            <DialogTitle className="text-xl flex items-center gap-3">
              {selectedStrategy?.name}
              <Badge variant="outline" className={typeColors[selectedStrategy?.type || 'trend']}>
                {typeLabels[selectedStrategy?.type || 'trend']}
              </Badge>
            </DialogTitle>
          </DialogHeader>

          {selectedStrategy && (
            <div className="space-y-6">
              {/* Métricas principais */}
              <div className="grid grid-cols-4 gap-4">
                <div className="bg-slate-800 rounded-lg p-4">
                  <div className="flex items-center gap-2 text-slate-400 text-sm mb-1">
                    <TrendingUp className="h-4 w-4" />
                    WFE
                  </div>
                  <div className={cn('text-2xl font-bold font-mono', getMetricColor(selectedStrategy.metrics?.wfe ?? 0))}>
                    {((selectedStrategy.metrics?.wfe ?? 0) * 100).toFixed(0)}%
                  </div>
                  <div className="text-xs text-slate-500">Walk-Forward Efficiency</div>
                </div>

                <div className="bg-slate-800 rounded-lg p-4">
                  <div className="flex items-center gap-2 text-slate-400 text-sm mb-1">
                    <Activity className="h-4 w-4" />
                    Sharpe OOS
                  </div>
                  <div className={cn('text-2xl font-bold font-mono', getMetricColor((selectedStrategy.metrics?.sharpeOOS ?? 0) / 2))}>
                    {(selectedStrategy.metrics?.sharpeOOS ?? 0).toFixed(2)}
                  </div>
                  <div className="text-xs text-slate-500">Out-of-Sample</div>
                </div>

                <div className="bg-slate-800 rounded-lg p-4">
                  <div className="flex items-center gap-2 text-slate-400 text-sm mb-1">
                    <TrendingDown className="h-4 w-4" />
                    Max DD
                  </div>
                  <div className={cn('text-2xl font-bold font-mono', getMetricColor(selectedStrategy.metrics?.maxDrawdownMC ?? 0, 'bad'))}>
                    {(selectedStrategy.metrics?.maxDrawdownMC ?? 0).toFixed(1)}%
                  </div>
                  <div className="text-xs text-slate-500">Monte Carlo P95</div>
                </div>

                <div className="bg-slate-800 rounded-lg p-4">
                  <div className="flex items-center gap-2 text-slate-400 text-sm mb-1">
                    <Target className="h-4 w-4" />
                    Win Rate
                  </div>
                  <div className="text-2xl font-bold font-mono text-emerald-400">
                    {selectedStrategy.metrics?.winRate ?? 0}%
                  </div>
                  <div className="text-xs text-slate-500">Taxa de acerto</div>
                </div>
              </div>

              {/* Métricas secundárias */}
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-slate-800/50 rounded-lg p-4">
                  <div className="text-slate-400 text-sm mb-2">Performance</div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Profit Factor:</span>
                      <span className="font-mono text-slate-200">{(selectedStrategy.metrics?.profitFactor ?? 0).toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Expectancy:</span>
                      <span className="font-mono text-slate-200">{(selectedStrategy.metrics?.expectancy ?? 0).toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Avg Trade:</span>
                      <span className="font-mono text-slate-200">${selectedStrategy.metrics?.avgTrade ?? 0}</span>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-800/50 rounded-lg p-4">
                  <div className="text-slate-400 text-sm mb-2">Risco</div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Max DD (Real):</span>
                      <span className="font-mono text-slate-200">{(selectedStrategy.metrics?.maxDrawdown ?? 0).toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Calmar Ratio:</span>
                      <span className="font-mono text-slate-200">{(selectedStrategy.metrics?.calmarRatio ?? 0).toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Sortino:</span>
                      <span className="font-mono text-slate-200">{(selectedStrategy.metrics?.sortinoRatio ?? 0).toFixed(2)}</span>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-800/50 rounded-lg p-4">
                  <div className="text-slate-400 text-sm mb-2">Estatísticas</div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Total Trades:</span>
                      <span className="font-mono text-slate-200">{selectedStrategy.metrics?.totalTrades ?? 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Sharpe IS:</span>
                      <span className="font-mono text-slate-200">{(selectedStrategy.metrics?.sharpeIS ?? 0).toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Status:</span>
                      <Badge className={statusColors[selectedStrategy.status]}>
                        {statusLabels[selectedStrategy.status]}
                      </Badge>
                    </div>
                  </div>
                </div>
              </div>

              {/* Parâmetros */}
              <div className="bg-slate-800/50 rounded-lg p-4">
                <div className="text-slate-400 text-sm mb-3">Parâmetros da Estratégia</div>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(selectedStrategy.parameters).map(([key, value]) => (
                    <div key={key} className="bg-slate-700 rounded px-3 py-1.5 text-sm">
                      <span className="text-slate-400">{key}:</span>
                      <span className="ml-2 font-mono text-slate-200">{value}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Indicadores */}
              <div className="bg-slate-800/50 rounded-lg p-4">
                <div className="text-slate-400 text-sm mb-3">Indicadores Utilizados</div>
                <div className="flex flex-wrap gap-2">
                  {selectedStrategy.indicators.map(indicator => (
                    <Badge key={indicator} variant="outline" className="bg-slate-700 text-slate-300 border-slate-600">
                      {indicator}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}
