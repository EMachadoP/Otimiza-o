import { useMemo } from 'react';
import { cn } from '@/lib/utils';

interface RecurrenceHeatmapProps {
  data?: number[][];
}

const days = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex'];
const hours = ['09', '10', '11', '12', '13', '14', '15', '16', '17'];

export function RecurrenceHeatmap({ data }: RecurrenceHeatmapProps) {
  // Gerar dados simulados se não fornecidos
  const heatmapData = useMemo(() => {
    if (data) return data;
    
    return hours.map(() => 
      days.map(() => Math.floor(Math.random() * 100))
    );
  }, [data]);

  const getColor = (value: number) => {
    if (value >= 80) return 'bg-emerald-500';
    if (value >= 60) return 'bg-emerald-400';
    if (value >= 40) return 'bg-amber-400';
    if (value >= 20) return 'bg-orange-400';
    return 'bg-red-400';
  };

  const getOpacity = (value: number) => {
    return Math.max(0.2, value / 100);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
          Heatmap de Recorrência
        </h3>
        <div className="flex items-center gap-2 text-xs">
          <span className="text-slate-500">Baixa</span>
          <div className="flex gap-0.5">
            <div className="w-3 h-3 bg-red-400 rounded-sm" />
            <div className="w-3 h-3 bg-orange-400 rounded-sm" />
            <div className="w-3 h-3 bg-amber-400 rounded-sm" />
            <div className="w-3 h-3 bg-emerald-400 rounded-sm" />
            <div className="w-3 h-3 bg-emerald-500 rounded-sm" />
          </div>
          <span className="text-slate-500">Alta</span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <div className="inline-block">
          {/* Header com dias */}
          <div className="flex">
            <div className="w-8" /> {/* Espaço para horas */}
            {days.map(day => (
              <div key={day} className="w-10 text-center text-xs text-slate-500 py-1">
                {day}
              </div>
            ))}
          </div>

          {/* Grid com horas e dados */}
          <div className="space-y-1">
            {hours.map((hour, hourIndex) => (
              <div key={hour} className="flex items-center">
                <div className="w-8 text-xs text-slate-500 text-right pr-2">
                  {hour}h
                </div>
                <div className="flex gap-1">
                  {days.map((_, dayIndex) => {
                    const value = heatmapData[hourIndex]?.[dayIndex] || 0;
                    return (
                      <div
                        key={`${hourIndex}-${dayIndex}`}
                        className={cn(
                          'w-9 h-6 rounded-sm cursor-pointer transition-all hover:scale-110',
                          getColor(value)
                        )}
                        style={{ opacity: getOpacity(value) }}
                        title={`${hour}h - ${days[dayIndex]}: ${value}% de recorrência`}
                      />
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="text-xs text-slate-500 text-center">
        Clique em uma célula para ver detalhes estatísticos
      </div>
    </div>
  );
}
