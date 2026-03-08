import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  TrendingUp,
  Activity,
  BarChart3,
  Brain,
  Target,
  RefreshCw,
  Settings,
  Play,
  Zap,
  Upload
} from 'lucide-react';
import { CandlestickChart } from '@/components/CandlestickChart';
import { StrategyTable } from '@/components/StrategyTable';
import { PatternPanel } from '@/components/PatternPanel';
import { RecurrenceHeatmap } from '@/components/RecurrenceHeatmap';
import { MLInsights } from '@/components/MLInsights';
import { ValidationPanel } from '@/components/ValidationPanel';
import { EAExporter } from '@/components/EAExporter';
import { EAImporter } from '@/components/EAImporter';
import { StrategyOptimizer } from '@/components/StrategyOptimizer';
import { useTradingData } from '@/hooks/useTradingData';
import { useBacktest } from '@/hooks/useBacktest';
import type { Strategy, OHLCV } from '@/types/trading';
import { cn } from '@/lib/utils';

export function Dashboard() {
  const {
    symbols,
    timeframes,
    selectedSymbol,
    selectedTimeframe,
    data,
    patterns,
    regime,
    strategies,
    heatmapData,
    mlInsights,
    loading,
    error,
    setSelectedSymbol,
    setSelectedTimeframe,
    refreshData
  } = useTradingData();

  const { running, progress, validation, runBacktest } = useBacktest();

  const [selectedStrategy, setSelectedStrategy] = useState<Strategy | null>(null);
  const [showEAExporter, setShowEAExporter] = useState(false);
  const [showEAImporter, setShowEAImporter] = useState(false);
  const [showOptimizer, setShowOptimizer] = useState(false);
  const [customStrategies, setCustomStrategies] = useState<Strategy[]>([]);

  // Combinar estratégias padrão com customizadas
  const allStrategies = [...strategies, ...customStrategies];

  const handleExportEA = (strategy: Strategy) => {
    setSelectedStrategy(strategy);
    setShowEAExporter(true);
  };

  const handleViewDetails = (strategy: Strategy) => {
    setSelectedStrategy(strategy);
  };

  const handleSimulateTrade = (candle: OHLCV) => {
    // Implementar simulação de trade
    console.log('Simulando trade em:', candle);
  };

  const handleImportStrategy = (strategy: Strategy) => {
    setCustomStrategies(prev => [...prev, strategy]);
  };

  const handleOptimizeStrategy = (strategy: Strategy) => {
    setSelectedStrategy(strategy);
    setShowOptimizer(true);
  };

  const handleOptimizedStrategy = (optimizedStrategy: Strategy) => {
    setCustomStrategies(prev => {
      const filtered = prev.filter(s => s.id !== optimizedStrategy.id);
      return [...filtered, optimizedStrategy];
    });
  };

  const regimeLabels: Record<string, string> = {
    trend_up: 'TREND UP',
    trend_down: 'TREND DOWN',
    range: 'RANGE',
    range_volatile: 'RANGE VOLÁTIL',
    breakout: 'BREAKOUT',
    undefined: 'ANALISANDO'
  };

  const regimeColors: Record<string, string> = {
    trend_up: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    trend_down: 'bg-red-500/20 text-red-400 border-red-500/30',
    range: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    range_volatile: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    breakout: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    undefined: 'bg-slate-500/20 text-slate-400 border-slate-500/30'
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <TrendingUp className="h-5 w-5 text-white" />
                </div>
                <h1 className="text-xl font-bold text-slate-100">TradeStrategist</h1>
              </div>
              <Badge variant="outline" className="bg-slate-800 text-slate-400 border-slate-700">
                v1.0.0
              </Badge>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 text-sm text-slate-400">
                <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                Conectado MT5
              </div>
              <Button variant="ghost" size="icon" className="text-slate-400">
                <Settings className="h-5 w-5" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="p-6">
        {/* Controls Bar */}
        <div className="mb-6 flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-sm text-slate-400">Símbolo:</span>
            <Select
              value={selectedSymbol.name}
              onValueChange={(value) => {
                const symbol = symbols.find(s => s.name === value);
                if (symbol) setSelectedSymbol(symbol);
              }}
            >
              <SelectTrigger className="w-32 bg-slate-800 border-slate-700">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-700">
                {symbols.map(symbol => (
                  <SelectItem key={symbol.name} value={symbol.name}>
                    {symbol.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-sm text-slate-400">Timeframe:</span>
            <Select
              value={selectedTimeframe.value}
              onValueChange={(value) => {
                const tf = timeframes.find(t => t.value === value);
                if (tf) setSelectedTimeframe(tf);
              }}
            >
              <SelectTrigger className="w-24 bg-slate-800 border-slate-700">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-700">
                {timeframes.map(tf => (
                  <SelectItem key={tf.value} value={tf.value}>
                    {tf.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-sm text-slate-400">Período:</span>
            <Select defaultValue="6M">
              <SelectTrigger className="w-24 bg-slate-800 border-slate-700">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-700">
                <SelectItem value="1M">1M</SelectItem>
                <SelectItem value="3M">3M</SelectItem>
                <SelectItem value="6M">6M</SelectItem>
                <SelectItem value="1Y">1Y</SelectItem>
                <SelectItem value="2Y">2Y</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-sm text-slate-400">Estratégia:</span>
            <Select defaultValue="all">
              <SelectTrigger className="w-32 bg-slate-800 border-slate-700">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-700">
                <SelectItem value="all">Todas</SelectItem>
                <SelectItem value="trend">Tendência</SelectItem>
                <SelectItem value="reversal">Reversão</SelectItem>
                <SelectItem value="breakout">Breakout</SelectItem>
                <SelectItem value="scalping">Scalping</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Button
            onClick={refreshData}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700"
          >
            <RefreshCw className={cn("h-4 w-4 mr-2", loading && "animate-spin")} />
            Atualizar
          </Button>

          {regime && (
            <Badge variant="outline" className={cn('ml-auto', regimeColors[regime.type])}>
              {regimeLabels[regime.type]} ({regime.confidence}%)
            </Badge>
          )}
        </div>

        {/* Error Banner */}
        {error && (
          <div className="mb-4 p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
            ⚠️ {error}
          </div>
        )}

        {/* Grid Layout */}
        <div className="grid grid-cols-12 gap-6">
          {/* Main Chart - 8 columns */}
          <div className="col-span-12 lg:col-span-8 space-y-6">
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg text-slate-200">
                    {selectedSymbol.name} - {selectedTimeframe.label}
                  </CardTitle>
                  <div className="flex items-center gap-2">
                    <Button variant="ghost" size="sm" className="text-slate-400">
                      <Zap className="h-4 w-4 mr-2" />
                      Simular Trade
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="h-[500px] flex items-center justify-center">
                    <div className="flex flex-col items-center gap-4">
                      <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
                      <span className="text-slate-400">Carregando dados...</span>
                    </div>
                  </div>
                ) : data.length === 0 ? (
                  <div className="h-[500px] flex items-center justify-center">
                    <div className="flex flex-col items-center gap-4">
                      <span className="text-4xl">📊</span>
                      <span className="text-slate-400">Sem dados para este símbolo/timeframe</span>
                    </div>
                  </div>
                ) : (
                  <CandlestickChart
                    data={data}
                    patterns={patterns}
                    regime={regime}
                    height={500}
                    onCandleClick={handleSimulateTrade}
                  />
                )}
              </CardContent>
            </Card>

            {/* Strategy Ranking */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg text-slate-200 flex items-center gap-2">
                    <Target className="h-5 w-5 text-blue-400" />
                    Melhores Estratégias Agora
                  </CardTitle>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setShowEAImporter(true)}
                      className="border-slate-700"
                    >
                      <Upload className="h-4 w-4 mr-2" />
                      Importar EA
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        allStrategies.forEach(s => runBacktest(s, selectedSymbol.name, selectedTimeframe.value));
                      }}
                      disabled={running}
                      className="border-slate-700"
                    >
                      <Play className="h-4 w-4 mr-2" />
                      {running ? 'Executando...' : 'Validar Todas'}
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <StrategyTable
                  strategies={allStrategies}
                  onViewDetails={handleViewDetails}
                  onExportEA={handleExportEA}
                  onOptimize={handleOptimizeStrategy}
                />
              </CardContent>
            </Card>

            {/* Validation Panel */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg text-slate-200 flex items-center gap-2">
                  <Activity className="h-5 w-5 text-purple-400" />
                  Validação Estatística
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ValidationPanel
                  validation={validation || undefined}
                  isRunning={running}
                  progress={progress}
                  onRunValidation={() => {
                    if (strategies[0]) {
                      runBacktest(strategies[0], selectedSymbol.name, selectedTimeframe.value);
                    }
                  }}
                />
              </CardContent>
            </Card>
          </div>

          {/* Sidebar - 4 columns */}
          <div className="col-span-12 lg:col-span-4 space-y-6">
            {/* Market Regime */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg text-slate-200 flex items-center gap-2">
                  <BarChart3 className="h-5 w-5 text-emerald-400" />
                  Regime de Mercado
                </CardTitle>
              </CardHeader>
              <CardContent>
                {regime ? (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Regime Atual:</span>
                      <Badge variant="outline" className={regimeColors[regime.type]}>
                        {regimeLabels[regime.type]}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Confiança:</span>
                      <span className="font-mono text-slate-200">{regime.confidence}%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">ADX:</span>
                      <span className="font-mono text-slate-200">{regime.indicators.adx}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Volatilidade:</span>
                      <span className="font-mono text-slate-200">{regime.indicators.volatility}%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400">Volume:</span>
                      <span className="font-mono text-slate-200">{regime.indicators.volumeProfile}</span>
                    </div>
                  </div>
                ) : (
                  <div className="text-center text-slate-500 py-4">
                    Analisando regime...
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Patterns */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg text-slate-200 flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-amber-400" />
                  Padrões & Estatísticas
                </CardTitle>
              </CardHeader>
              <CardContent>
                <PatternPanel patterns={patterns} />
              </CardContent>
            </Card>

            {/* Recurrence Heatmap */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg text-slate-200 flex items-center gap-2">
                  <BarChart3 className="h-5 w-5 text-purple-400" />
                  Recorrência por Horário
                </CardTitle>
              </CardHeader>
              <CardContent>
                <RecurrenceHeatmap data={heatmapData || undefined} />
              </CardContent>
            </Card>

            {/* ML Insights */}
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg text-slate-200 flex items-center gap-2">
                  <Brain className="h-5 w-5 text-pink-400" />
                  Insights de ML
                </CardTitle>
              </CardHeader>
              <CardContent>
                <MLInsights
                  features={mlInsights?.features}
                  successProbability={mlInsights?.successProbability}
                  explanation={mlInsights?.explanation}
                />
              </CardContent>
            </Card>
          </div>
        </div>
      </main>

      {/* EA Exporter Dialog */}
      <EAExporter
        strategy={selectedStrategy}
        open={showEAExporter}
        onOpenChange={setShowEAExporter}
      />

      {/* EA Importer Dialog */}
      <EAImporter
        open={showEAImporter}
        onOpenChange={setShowEAImporter}
        onImport={handleImportStrategy}
      />

      {/* Strategy Optimizer Dialog */}
      <StrategyOptimizer
        strategy={selectedStrategy}
        open={showOptimizer}
        onOpenChange={setShowOptimizer}
        onOptimized={handleOptimizedStrategy}
      />
    </div>
  );
}
