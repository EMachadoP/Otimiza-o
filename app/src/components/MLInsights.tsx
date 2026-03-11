import { useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Brain, TrendingUp, BarChart3, Sparkles, Radar, Clock3 } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { IndicatorScorecardItem, TradePlaybook, MicrostructureInsight, EntryTimingInsight } from '@/types/trading';

interface FeatureImportance {
  feature: string;
  importance: number;
  description: string;
}

interface ActiveWindow {
  label: string;
  bias: string;
  edge: number;
  samples: number;
}

interface MLInsightsProps {
  features?: FeatureImportance[];
  successProbability?: number;
  explanation?: string;
  recommendation?: { strategy: string; reason: string; confidence: number } | null;
  scorecard?: IndicatorScorecardItem[];
  playbooks?: TradePlaybook[];
  activeWindows?: ActiveWindow[];
  microstructure?: MicrostructureInsight;
  entryTiming?: EntryTimingInsight;
}

const defaultFeatures: FeatureImportance[] = [
  { feature: 'RSI (14)', importance: 85, description: 'Indice de Forca Relativa' },
  { feature: 'ATR (14)', importance: 72, description: 'Average True Range' },
  { feature: 'Volume', importance: 68, description: 'Volume de negociacao' },
  { feature: 'EMA (50)', importance: 55, description: 'Media Movel Exponencial' },
  { feature: 'MACD', importance: 48, description: 'Convergencia/Divergencia de Medias' },
];

export function MLInsights({
  features = defaultFeatures,
  successProbability = 78,
  explanation = 'O mercado esta em uma tendencia de alta com volume crescente.',
  recommendation,
  scorecard = [],
  playbooks = [],
  activeWindows = [],
  microstructure,
  entryTiming,
}: MLInsightsProps) {
  const [expandedFeature, setExpandedFeature] = useState<string | null>(null);

  const getProbabilityColor = (prob: number) => {
    if (prob >= 70) return 'text-emerald-400';
    if (prob >= 50) return 'text-amber-400';
    return 'text-red-400';
  };

  const getConfidenceLabel = (prob: number) => {
    if (prob >= 80) return { label: 'ALTA', color: 'bg-emerald-500/20 text-emerald-400' };
    if (prob >= 60) return { label: 'MEDIA', color: 'bg-amber-500/20 text-amber-400' };
    return { label: 'BAIXA', color: 'bg-red-500/20 text-red-400' };
  };

  const confidence = getConfidenceLabel(successProbability);

  return (
    <div className="space-y-6">
      {recommendation && (
        <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4 space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-blue-400">
              <Sparkles className="h-4 w-4" />
              <span className="text-xs font-bold uppercase tracking-wider">Recomendacao Rapida</span>
            </div>
            <Badge variant="outline" className="text-[10px] border-blue-500/30 text-blue-400">
              {recommendation.confidence}% CONFIANCA
            </Badge>
          </div>
          <div className="text-sm font-bold text-white">{recommendation.strategy}</div>
          <p className="text-xs text-slate-400 leading-relaxed">{recommendation.reason}</p>
        </div>
      )}

      {scorecard.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Radar className="h-4 w-4 text-cyan-400" />
            <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">Scorecard de Indicadores</h3>
          </div>

          <div className="space-y-2">
            {scorecard.slice(0, 4).map((item) => (
              <div key={item.indicator} className="rounded-lg border border-slate-800 bg-slate-800/50 p-3">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <div className="text-sm font-semibold text-slate-200">{item.indicator}</div>
                    <div className="text-[11px] text-slate-500">{item.currentSignal}</div>
                  </div>
                  <Badge className="bg-cyan-500/10 text-cyan-300 border-none text-[10px]">
                    Fit {item.fitScore}%
                  </Badge>
                </div>
                <div className="mt-2 grid grid-cols-3 gap-2 text-[11px]">
                  <div className="rounded bg-slate-950/50 p-2">
                    <div className="text-slate-500">Assertividade</div>
                    <div className="font-mono text-emerald-400">{item.accuracy}%</div>
                  </div>
                  <div className="rounded bg-slate-950/50 p-2">
                    <div className="text-slate-500">Edge Medio</div>
                    <div className={cn('font-mono', item.avgEdge >= 0 ? 'text-blue-400' : 'text-red-400')}>
                      {item.avgEdge}%
                    </div>
                  </div>
                  <div className="rounded bg-slate-950/50 p-2">
                    <div className="text-slate-500">Amostras</div>
                    <div className="font-mono text-slate-300">{item.sampleSize}</div>
                  </div>
                </div>
                <p className="mt-2 text-[11px] text-slate-400 leading-relaxed">{item.rationale}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {playbooks.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Brain className="h-4 w-4 text-emerald-400" />
            <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">Playbooks Sugeridos</h3>
          </div>
          <div className="space-y-3">
            {playbooks.map((playbook) => (
              <div key={playbook.title} className="rounded-lg border border-emerald-500/20 bg-emerald-500/5 p-4 space-y-2">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <div className="text-sm font-semibold text-slate-100">{playbook.title}</div>
                    <div className="text-[11px] text-slate-500 uppercase">Bias: {playbook.bias}</div>
                  </div>
                  <Badge className="bg-emerald-500/10 text-emerald-300 border-none text-[10px]">
                    {playbook.confidence}%
                  </Badge>
                </div>
                <div className="space-y-1 text-[11px] text-slate-300 leading-relaxed">
                  <p><span className="text-slate-500">Setup:</span> {playbook.setup}</p>
                  <p><span className="text-slate-500">Entrada:</span> {playbook.entry}</p>
                  <p><span className="text-slate-500">Confirmacao:</span> {playbook.confirmation}</p>
                  <p><span className="text-slate-500">Invalidacao:</span> {playbook.invalidation}</p>
                  <p><span className="text-slate-500">Holding:</span> {playbook.holdingPeriod}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {entryTiming && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-amber-300" />
            <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">Timing de Entrada</h3>
          </div>
          <div className="rounded-lg border border-amber-500/20 bg-amber-500/5 p-4 text-xs space-y-2">
            <div><span className="text-slate-500">Janela:</span> <span className="text-slate-200">{entryTiming.bestWindow?.label || 'Aguardando'}</span></div>
            <div><span className="text-slate-500">Trigger:</span> <span className="text-slate-200">{entryTiming.trigger}</span></div>
            <div className="text-slate-400 leading-relaxed">{entryTiming.executionHint}</div>
          </div>
        </div>
      )}

      {microstructure && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Clock3 className="h-4 w-4 text-cyan-400" />
            <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">Microestrutura</h3>
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-800/50 p-4 space-y-3 text-xs">
            <div className="grid grid-cols-3 gap-2">
              <div className="rounded bg-slate-950/50 p-2">
                <div className="text-slate-500">Pressao</div>
                <div className="text-slate-200 font-medium capitalize">{microstructure.pressureBias}</div>
              </div>
              <div className="rounded bg-slate-950/50 p-2">
                <div className="text-slate-500">Uptick Ratio</div>
                <div className="font-mono text-cyan-300">{microstructure.uptickRatio}%</div>
              </div>
              <div className="rounded bg-slate-950/50 p-2">
                <div className="text-slate-500">Spread</div>
                <div className="text-slate-200 font-medium capitalize">{microstructure.spreadState}</div>
              </div>
            </div>
            {microstructure.activeBursts.length > 0 && (
              <div className="space-y-2">
                <div className="text-slate-500 uppercase tracking-wider text-[10px]">Bursts de atividade</div>
                {microstructure.activeBursts.map((burst) => (
                  <div key={burst.label} className="flex items-center justify-between rounded bg-slate-950/40 p-2">
                    <div>
                      <div className="text-slate-200">{burst.label}</div>
                      <div className="text-slate-500">Bias: {burst.bias}</div>
                    </div>
                    <div className="text-right">
                      <div className="font-mono text-cyan-300">{burst.tickCount} ticks</div>
                      <div className="text-slate-500">Spread {burst.avgSpread}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {activeWindows.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Clock3 className="h-4 w-4 text-amber-400" />
            <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">Janelas Mais Favoraveis</h3>
          </div>
          <div className="grid grid-cols-1 gap-2">
            {activeWindows.map((window) => (
              <div key={window.label} className="rounded-lg bg-slate-800/50 border border-slate-800 p-3 flex items-center justify-between text-xs">
                <div>
                  <div className="text-slate-200 font-medium">{window.label}</div>
                  <div className="text-slate-500">Bias: {window.bias}</div>
                </div>
                <div className="text-right">
                  <div className={cn('font-mono', window.edge >= 0 ? 'text-amber-300' : 'text-red-400')}>{window.edge}%</div>
                  <div className="text-slate-500">{window.samples} amostras</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <BarChart3 className="h-4 w-4 text-slate-400" />
          <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">Feature Importance</h3>
        </div>

        <div className="space-y-2">
          {features.slice(0, 5).map((feat) => (
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
                  style={{ width: feat.importance + '%' }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <TrendingUp className="h-4 w-4 text-slate-400" />
          <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">Probabilidade de Sucesso</h3>
        </div>

        <div className="bg-slate-800/50 rounded-lg p-4">
          <div className="flex items-center justify-center">
            <div className="relative w-32 h-32">
              <svg className="w-full h-full transform -rotate-90">
                <circle cx="64" cy="64" r="56" fill="none" stroke="#1E293B" strokeWidth="12" />
                <circle
                  cx="64"
                  cy="64"
                  r="56"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="12"
                  strokeLinecap="round"
                  strokeDasharray={String(2 * Math.PI * 56)}
                  strokeDashoffset={String(2 * Math.PI * 56 * (1 - successProbability / 100))}
                  className={cn('transition-all duration-1000', getProbabilityColor(successProbability))}
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className={cn('text-3xl font-bold font-mono', getProbabilityColor(successProbability))}>{successProbability}%</span>
                <Badge className={cn('mt-1 text-xs', confidence.color)}>{confidence.label}</Badge>
              </div>
            </div>
          </div>
          <div className="mt-4 text-center text-xs text-slate-500">
            Probabilidade baseada no regime atual, scorecard dos indicadores e ocorrencias historicas parecidas.
          </div>
        </div>
      </div>

      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-slate-400" />
          <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">Analise Gerada</h3>
        </div>

        <div className="bg-slate-800/50 rounded-lg p-4 border-l-4 border-blue-500">
          <div className="flex items-start gap-3">
            <Brain className="h-5 w-5 text-blue-400 mt-0.5 flex-shrink-0" />
            <p className="text-sm text-slate-300 leading-relaxed">{explanation}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
