import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { LineChart, BarChart3, Activity } from 'lucide-react';
import type { ValidationResults } from '@/types/trading';
import { cn } from '@/lib/utils';

interface ValidationPanelProps {
  validation?: ValidationResults;
  isRunning?: boolean;
  progress?: number;
  onRunValidation?: () => void;
}

const defaultValidation: ValidationResults = {
  wfa: {
    efficiency: 0.82,
    isCAGR: 18.5,
    oosCAGR: 15.2,
    windows: [
      { trainStart: '2020-01-01', trainEnd: '2020-06-30', testStart: '2020-07-01', testEnd: '2020-12-31', trainReturn: 15.2, testReturn: 12.8, efficiency: 0.84 },
      { trainStart: '2020-07-01', trainEnd: '2020-12-31', testStart: '2021-01-01', testEnd: '2021-06-30', trainReturn: 18.5, testReturn: 14.2, efficiency: 0.77 },
      { trainStart: '2021-01-01', trainEnd: '2021-06-30', testStart: '2021-07-01', testEnd: '2021-12-31', trainReturn: 22.1, testReturn: 19.5, efficiency: 0.88 },
      { trainStart: '2021-07-01', trainEnd: '2021-12-31', testStart: '2022-01-01', testEnd: '2022-06-30', trainReturn: 16.8, testReturn: 13.5, efficiency: 0.80 },
      { trainStart: '2022-01-01', trainEnd: '2022-06-30', testStart: '2022-07-01', testEnd: '2022-12-31', trainReturn: 20.3, testReturn: 17.1, efficiency: 0.84 },
    ]
  },
  cpcv: {
    avgSharpe: 1.64,
    sharpeStd: 0.23,
    purgedSplits: 10,
    embargoSize: 5,
    foldResults: [
      { fold: 1, trainSize: 1250, testSize: 350, sharpe: 1.72, trades: 85 },
      { fold: 2, trainSize: 1280, testSize: 320, sharpe: 1.58, trades: 78 },
      { fold: 3, trainSize: 1220, testSize: 380, sharpe: 1.81, trades: 92 },
      { fold: 4, trainSize: 1300, testSize: 300, sharpe: 1.45, trades: 71 },
      { fold: 5, trainSize: 1180, testSize: 420, sharpe: 1.69, trades: 88 },
      { fold: 6, trainSize: 1350, testSize: 250, sharpe: 1.62, trades: 82 },
    ]
  },
  monteCarlo: {
    simulations: 10000,
    profitablePct: 78.5,
    maxDrawdownP95: 18.7,
    maxDrawdownP99: 28.3,
    worstCaseEquity: 8540,
    bestCaseEquity: 28500,
    medianEquity: 18200
  },
  pbo: 18.5
};

export function ValidationPanel({
  validation = defaultValidation,
  isRunning = false,
  progress = 0,
  onRunValidation
}: ValidationPanelProps) {

  // Safe accessors with fallbacks
  const wfa = validation?.wfa ?? defaultValidation.wfa;
  const cpcv = validation?.cpcv ?? defaultValidation.cpcv;
  const mc = validation?.monteCarlo ?? defaultValidation.monteCarlo;
  const pbo = validation?.pbo ?? defaultValidation.pbo;

  const getWFEStatus = (wfe: number) => {
    if (wfe >= 0.7) return { label: 'Excelente', color: 'text-emerald-400', bg: 'bg-emerald-500/20' };
    if (wfe >= 0.5) return { label: 'Bom', color: 'text-amber-400', bg: 'bg-amber-500/20' };
    return { label: 'Fraco', color: 'text-red-400', bg: 'bg-red-500/20' };
  };

  const getPBOStatus = (pbo: number) => {
    if (pbo < 20) return { label: 'Baixo Risco', color: 'text-emerald-400', bg: 'bg-emerald-500/20' };
    if (pbo < 50) return { label: 'Risco Moderado', color: 'text-amber-400', bg: 'bg-amber-500/20' };
    return { label: 'Alto Risco', color: 'text-red-400', bg: 'bg-red-500/20' };
  };

  const wfeStatus = getWFEStatus(wfa.efficiency ?? 0);
  const pboStatus = getPBOStatus(pbo);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
          Validação Estatística
        </h3>
        <Button
          size="sm"
          onClick={onRunValidation}
          disabled={isRunning}
          className="bg-blue-600 hover:bg-blue-700"
        >
          {isRunning ? 'Executando...' : 'Executar Validação'}
        </Button>
      </div>

      {isRunning && (
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-slate-400">Progresso</span>
            <span className="text-slate-200">{progress}%</span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>
      )}

      <Tabs defaultValue="wfa" className="w-full">
        <TabsList className="grid w-full grid-cols-3 bg-slate-800">
          <TabsTrigger value="wfa" className="data-[state=active]:bg-slate-700">
            <Activity className="h-4 w-4 mr-2" />
            WFA
          </TabsTrigger>
          <TabsTrigger value="cpcv" className="data-[state=active]:bg-slate-700">
            <BarChart3 className="h-4 w-4 mr-2" />
            CPCV
          </TabsTrigger>
          <TabsTrigger value="montecarlo" className="data-[state=active]:bg-slate-700">
            <LineChart className="h-4 w-4 mr-2" />
            Monte Carlo
          </TabsTrigger>
        </TabsList>

        {/* WFA Tab */}
        <TabsContent value="wfa" className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-slate-800 rounded-lg p-4 text-center">
              <div className="text-slate-400 text-sm mb-1">WFE</div>
              <div className={cn('text-2xl font-bold font-mono', wfeStatus.color)}>
                {((wfa.efficiency ?? 0) * 100).toFixed(0)}%
              </div>
              <Badge className={cn('mt-1 text-xs', wfeStatus.bg, wfeStatus.color)}>
                {wfeStatus.label}
              </Badge>
            </div>
            <div className="bg-slate-800 rounded-lg p-4 text-center">
              <div className="text-slate-400 text-sm mb-1">CAGR IS</div>
              <div className="text-2xl font-bold font-mono text-slate-200">
                {(wfa.isCAGR ?? 0).toFixed(1)}%
              </div>
            </div>
            <div className="bg-slate-800 rounded-lg p-4 text-center">
              <div className="text-slate-400 text-sm mb-1">CAGR OOS</div>
              <div className="text-2xl font-bold font-mono text-slate-200">
                {(wfa.oosCAGR ?? 0).toFixed(1)}%
              </div>
            </div>
          </div>

          <div className="bg-slate-800/50 rounded-lg p-4">
            <div className="text-slate-400 text-sm mb-3">Janelas de Validação</div>
            <div className="space-y-2">
              {(wfa.windows ?? []).map((window, i) => (
                <div key={i} className="flex items-center justify-between text-sm py-2 border-b border-slate-700/50 last:border-0">
                  <div className="flex items-center gap-4">
                    <span className="text-slate-500 font-mono text-xs">
                      {window.trainStart} → {window.testEnd}
                    </span>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-slate-400">
                      Train: <span className="text-emerald-400 font-mono">+{window.trainReturn}%</span>
                    </span>
                    <span className="text-slate-400">
                      Test: <span className="text-blue-400 font-mono">+{window.testReturn}%</span>
                    </span>
                    <Badge className={cn(
                      'text-xs',
                      (window.efficiency ?? 0) >= 0.7 ? 'bg-emerald-500/20 text-emerald-400' :
                        (window.efficiency ?? 0) >= 0.5 ? 'bg-amber-500/20 text-amber-400' :
                          'bg-red-500/20 text-red-400'
                    )}>
                      {((window.efficiency ?? 0) * 100).toFixed(0)}%
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </TabsContent>

        {/* CPCV Tab */}
        <TabsContent value="cpcv" className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-slate-800 rounded-lg p-4 text-center">
              <div className="text-slate-400 text-sm mb-1">Sharpe Médio</div>
              <div className="text-2xl font-bold font-mono text-slate-200">
                {(cpcv.avgSharpe ?? 0).toFixed(2)}
              </div>
            </div>
            <div className="bg-slate-800 rounded-lg p-4 text-center">
              <div className="text-slate-400 text-sm mb-1">Desvio Padrão</div>
              <div className="text-2xl font-bold font-mono text-slate-200">
                {(cpcv.sharpeStd ?? 0).toFixed(2)}
              </div>
            </div>
            <div className="bg-slate-800 rounded-lg p-4 text-center">
              <div className="text-slate-400 text-sm mb-1">PBO</div>
              <div className={cn('text-2xl font-bold font-mono', pboStatus.color)}>
                {(pbo ?? 0).toFixed(1)}%
              </div>
              <Badge className={cn('mt-1 text-xs', pboStatus.bg, pboStatus.color)}>
                {pboStatus.label}
              </Badge>
            </div>
          </div>

          <div className="bg-slate-800/50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="text-slate-400 text-sm">Resultados por Fold</div>
              <div className="text-xs text-slate-500">
                Purging: {cpcv.purgedSplits ?? 0} | Embargo: {cpcv.embargoSize ?? 0}
              </div>
            </div>
            <div className="space-y-2">
              {(cpcv.foldResults ?? []).map((fold) => (
                <div key={fold.fold} className="flex items-center justify-between text-sm py-2 border-b border-slate-700/50 last:border-0">
                  <div className="flex items-center gap-4">
                    <span className="text-slate-500">Fold {fold.fold}</span>
                    <span className="text-slate-600 text-xs">
                      Train: {fold.trainSize} | Test: {fold.testSize}
                    </span>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-slate-400">
                      Trades: <span className="font-mono text-slate-200">{fold.trades}</span>
                    </span>
                    <span className="text-slate-400">
                      Sharpe: <span className={cn('font-mono', (fold.sharpe ?? 0) >= 1.5 ? 'text-emerald-400' : 'text-amber-400')}>
                        {(fold.sharpe ?? 0).toFixed(2)}
                      </span>
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </TabsContent>

        {/* Monte Carlo Tab */}
        <TabsContent value="montecarlo" className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-slate-800 rounded-lg p-4 text-center">
              <div className="text-slate-400 text-sm mb-1">Simulações</div>
              <div className="text-2xl font-bold font-mono text-slate-200">
                {(mc.simulations ?? 0).toLocaleString()}
              </div>
            </div>
            <div className="bg-slate-800 rounded-lg p-4 text-center">
              <div className="text-slate-400 text-sm mb-1">% Lucrativo</div>
              <div className={cn('text-2xl font-bold font-mono',
                (mc.profitablePct ?? 0) >= 70 ? 'text-emerald-400' : 'text-amber-400'
              )}>
                {(mc.profitablePct ?? 0).toFixed(1)}%
              </div>
            </div>
            <div className="bg-slate-800 rounded-lg p-4 text-center">
              <div className="text-slate-400 text-sm mb-1">Max DD P95</div>
              <div className="text-2xl font-bold font-mono text-red-400">
                {(mc.maxDrawdownP95 ?? 0).toFixed(1)}%
              </div>
            </div>
          </div>

          <div className="bg-slate-800/50 rounded-lg p-4">
            <div className="text-slate-400 text-sm mb-3">Distribuição de Resultados</div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">Pior Caso:</span>
                  <span className="font-mono text-red-400">${(mc.worstCaseEquity ?? 0).toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">Mediana:</span>
                  <span className="font-mono text-slate-200">${(mc.medianEquity ?? 0).toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">Melhor Caso:</span>
                  <span className="font-mono text-emerald-400">${(mc.bestCaseEquity ?? 0).toLocaleString()}</span>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">Max DD P95:</span>
                  <span className="font-mono text-red-400">{(mc.maxDrawdownP95 ?? 0).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">Max DD P99:</span>
                  <span className="font-mono text-red-400">{(mc.maxDrawdownP99 ?? 0).toFixed(1)}%</span>
                </div>
              </div>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

