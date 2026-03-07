import { useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Brain, TrendingUp, BarChart3, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

interface FeatureImportance {
  feature: string;
  importance: number;
  description: string;
}

interface MLInsightsProps {
  features?: FeatureImportance[];
  successProbability?: number;
  explanation?: string;
}

const defaultFeatures: FeatureImportance[] = [
  { feature: 'RSI (14)', importance: 85, description: 'Índice de Força Relativa' },
  { feature: 'ATR (14)', importance: 72, description: 'Average True Range' },
  { feature: 'Volume', importance: 68, description: 'Volume de negociação' },
  { feature: 'EMA (50)', importance: 55, description: 'Média Móvel Exponencial' },
  { feature: 'MACD', importance: 48, description: 'Convergência/Divergência de Médias' },
];

export function MLInsights({ 
  features = defaultFeatures, 
  successProbability = 78,
  explanation = 'O mercado está em uma tendência de alta com volume crescente. A estratégia TrendBreak tem 72% de acerto em condições similares.'
}: MLInsightsProps) {
  const [expandedFeature, setExpandedFeature] = useState<string | null>(null);

  const getProbabilityColor = (prob: number) => {
    if (prob >= 70) return 'text-emerald-400';
    if (prob >= 50) return 'text-amber-400';
    return 'text-red-400';
  };

  const getConfidenceLabel = (prob: number) => {
    if (prob >= 80) return { label: 'ALTA', color: 'bg-emerald-500/20 text-emerald-400' };
    if (prob >= 60) return { label: 'MÉDIA', color: 'bg-amber-500/20 text-amber-400' };
    return { label: 'BAIXA', color: 'bg-red-500/20 text-red-400' };
  };

  const confidence = getConfidenceLabel(successProbability);

  return (
    <div className="space-y-6">
      {/* Feature Importance */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <BarChart3 className="h-4 w-4 text-slate-400" />
          <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
            Feature Importance
          </h3>
        </div>
        
        <div className="space-y-2">
          {features.map((feat) => (
            <div 
              key={feat.feature}
              className="space-y-1"
              onMouseEnter={() => setExpandedFeature(feat.feature)}
              onMouseLeave={() => setExpandedFeature(null)}
            >
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <span className="text-slate-300">{feat.feature}</span>
                  {expandedFeature === feat.feature && (
                    <span className="text-xs text-slate-500">{feat.description}</span>
                  )}
                </div>
                <span className="text-slate-400 font-mono">{feat.importance}%</span>
              </div>
              <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                <div 
                  className={cn(
                    'h-full rounded-full transition-all duration-500',
                    feat.importance >= 80 ? 'bg-emerald-500' :
                    feat.importance >= 60 ? 'bg-blue-500' :
                    feat.importance >= 40 ? 'bg-amber-500' : 'bg-slate-500'
                  )}
                  style={{ width: `${feat.importance}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Probabilidade de Sucesso */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <TrendingUp className="h-4 w-4 text-slate-400" />
          <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
            Probabilidade de Sucesso
          </h3>
        </div>
        
        <div className="bg-slate-800/50 rounded-lg p-4">
          <div className="flex items-center justify-center">
            <div className="relative w-32 h-32">
              {/* Círculo de fundo */}
              <svg className="w-full h-full transform -rotate-90">
                <circle
                  cx="64"
                  cy="64"
                  r="56"
                  fill="none"
                  stroke="#1E293B"
                  strokeWidth="12"
                />
                {/* Círculo de progresso */}
                <circle
                  cx="64"
                  cy="64"
                  r="56"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="12"
                  strokeLinecap="round"
                  strokeDasharray={`${2 * Math.PI * 56}`}
                  strokeDashoffset={`${2 * Math.PI * 56 * (1 - successProbability / 100)}`}
                  className={cn('transition-all duration-1000', getProbabilityColor(successProbability))}
                />
              </svg>
              
              {/* Valor central */}
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className={cn('text-3xl font-bold font-mono', getProbabilityColor(successProbability))}>
                  {successProbability}%
                </span>
                <Badge className={cn('mt-1 text-xs', confidence.color)}>
                  {confidence.label}
                </Badge>
              </div>
            </div>
          </div>
          
          <div className="mt-4 text-center text-xs text-slate-500">
            Probabilidade baseada no regime atual e condições similares históricas
          </div>
        </div>
      </div>

      {/* Análise Gerada */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-slate-400" />
          <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
            Análise Gerada
          </h3>
        </div>
        
        <div className="bg-slate-800/50 rounded-lg p-4 border-l-4 border-blue-500">
          <div className="flex items-start gap-3">
            <Brain className="h-5 w-5 text-blue-400 mt-0.5 flex-shrink-0" />
            <p className="text-sm text-slate-300 leading-relaxed">
              {explanation.split(/(TrendBreak|tendência de alta|volume crescente|72%)/).map((part, i) => {
                const highlights = ['TrendBreak', 'tendência de alta', 'volume crescente', '72%'];
                if (highlights.includes(part)) {
                  return <span key={i} className="font-semibold text-blue-400">{part}</span>;
                }
                return part;
              })}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
