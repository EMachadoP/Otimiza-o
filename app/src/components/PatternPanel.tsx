import { Badge } from '@/components/ui/badge';
import { TrendingUp, TrendingDown, Minus, Triangle, Hexagon, Waves, CandlestickChart } from 'lucide-react';
import type { Pattern } from '@/types/trading';
import { cn } from '@/lib/utils';

interface PatternPanelProps {
  patterns: Pattern[];
}

const patternIcons: Record<string, React.ReactNode> = {
  triangle: <Triangle className="h-4 w-4" />,
  head_and_shoulders: <Hexagon className="h-4 w-4" />,
  channel: <Waves className="h-4 w-4" />,
  flag: <Waves className="h-4 w-4" />,
  candlestick: <CandlestickChart className="h-4 w-4" />,
  double_top: <Hexagon className="h-4 w-4" />,
  double_bottom: <Hexagon className="h-4 w-4" />
};

const directionIcons = {
  up: <TrendingUp className="h-4 w-4 text-emerald-400" />,
  down: <TrendingDown className="h-4 w-4 text-red-400" />,
  neutral: <Minus className="h-4 w-4 text-slate-400" />
};

export function PatternPanel({ patterns }: PatternPanelProps) {
  const formatDate = (timestamp: number) => {
    const date = new Date(timestamp);
    return `${date.getDate().toString().padStart(2, '0')}/${(date.getMonth() + 1).toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
  };

  const getAccuracyColor = (accuracy: number) => {
    if (accuracy >= 70) return 'text-emerald-400';
    if (accuracy >= 55) return 'text-amber-400';
    return 'text-red-400';
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
          Padrões Detectados
        </h3>
        <Badge variant="outline" className="text-xs bg-slate-800 text-slate-400 border-slate-700">
          Últimos 20
        </Badge>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-700">
              <th className="text-left py-2 px-2 text-xs font-medium text-slate-500">Padrão</th>
              <th className="text-left py-2 px-2 text-xs font-medium text-slate-500">Data/Hora</th>
              <th className="text-center py-2 px-2 text-xs font-medium text-slate-500">Dir</th>
              <th className="text-right py-2 px-2 text-xs font-medium text-slate-500">Freq</th>
              <th className="text-right py-2 px-2 text-xs font-medium text-slate-500">Acerto</th>
            </tr>
          </thead>
          <tbody>
            {patterns.slice(0, 10).map((pattern) => (
              <tr 
                key={pattern.id} 
                className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors"
              >
                <td className="py-2 px-2">
                  <div className="flex items-center gap-2">
                    <span className="text-slate-500">
                      {patternIcons[pattern.type] || <CandlestickChart className="h-4 w-4" />}
                    </span>
                    <span className="text-sm text-slate-300">{pattern.name}</span>
                  </div>
                </td>
                <td className="py-2 px-2">
                  <span className="text-sm text-slate-400 font-mono">
                    {formatDate(pattern.timestamp)}
                  </span>
                </td>
                <td className="py-2 px-2 text-center">
                  {directionIcons[pattern.direction]}
                </td>
                <td className="py-2 px-2 text-right">
                  <div className="flex items-center justify-end gap-2">
                    <div className="w-12 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-blue-500 rounded-full"
                        style={{ width: `${pattern.frequency}%` }}
                      />
                    </div>
                    <span className="text-sm text-slate-400 font-mono">{pattern.frequency}%</span>
                  </div>
                </td>
                <td className="py-2 px-2 text-right">
                  <span className={cn('text-sm font-mono font-semibold', getAccuracyColor(pattern.accuracy))}>
                    {pattern.accuracy}%
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {patterns.length > 10 && (
        <div className="text-center">
          <button className="text-xs text-blue-400 hover:text-blue-300 transition-colors">
            Ver todos os {patterns.length} padrões →
          </button>
        </div>
      )}
    </div>
  );
}
