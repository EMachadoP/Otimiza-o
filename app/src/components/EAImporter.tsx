import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  Upload, 
  FileCode, 
  Settings, 
  Play, 
  Check, 
  AlertCircle, 
  Code,
  Trash2,
  Edit
} from 'lucide-react';
import { cn } from '@/lib/utils';
import type { Strategy } from '@/types/trading';

interface ParsedEA {
  name: string;
  type: 'ea' | 'indicator';
  inputs: Array<{
    name: string;
    type: string;
    defaultValue: string;
    description: string;
  }>;
  indicators: string[];
  code: string;
}

interface EAImporterProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onImport: (strategy: Strategy) => void;
}

// Parser básico para extrair inputs de código MQL
function parseMQLCode(code: string): ParsedEA | null {
  try {
    // Detectar tipo (EA ou Indicador)
    const isIndicator = code.includes('int OnCalculate') || code.includes('#property indicator');
    const type = isIndicator ? 'indicator' : 'ea';
    
    // Extrair nome
    const nameMatch = code.match(/#property\s+name\s+"([^"]+)"/i) || 
                      code.match(/class\s+(\w+)|input\s+group\s+"([^"]+)"/i);
    const name = nameMatch ? (nameMatch[1] || nameMatch[2] || 'Custom Strategy') : 'Custom Strategy';
    
    // Extrair inputs
    const inputRegex = /input\s+(\w+)\s+(\w+)\s*=\s*([^;]+);(?:\s*\/\/\s*(.+))?/gi;
    const inputs: Array<{name: string; type: string; defaultValue: string; description: string}> = [];
    let match;
    
    while ((match = inputRegex.exec(code)) !== null) {
      inputs.push({
        type: match[1],
        name: match[2],
        defaultValue: match[3].trim(),
        description: match[4] || match[2]
      });
    }
    
    // Extrair indicadores usados
    const indicators: string[] = [];
    const indicatorPatterns = [
      { name: 'iMA', label: 'Moving Average' },
      { name: 'iRSI', label: 'RSI' },
      { name: 'iMACD', label: 'MACD' },
      { name: 'iATR', label: 'ATR' },
      { name: 'iBands', label: 'Bollinger Bands' },
      { name: 'iStochastic', label: 'Stochastic' },
      { name: 'iCCI', label: 'CCI' },
      { name: 'iADX', label: 'ADX' },
      { name: 'iOBV', label: 'OBV' },
      { name: 'iMFI', label: 'MFI' },
      { name: 'iSAR', label: 'Parabolic SAR' },
      { name: 'iIchimoku', label: 'Ichimoku' },
      { name: 'iFractals', label: 'Fractals' },
      { name: 'iAlligator', label: 'Alligator' },
      { name: 'iEnvelopes', label: 'Envelopes' },
      { name: 'iMomentum', label: 'Momentum' },
      { name: 'iWPR', label: 'Williams %R' },
      { name: 'iStdDev', label: 'Standard Deviation' }
    ];
    
    indicatorPatterns.forEach(ind => {
      if (code.includes(ind.name)) {
        indicators.push(ind.label);
      }
    });
    
    return {
      name,
      type,
      inputs,
      indicators: indicators.length > 0 ? indicators : ['Price Action'],
      code
    };
  } catch (error) {
    console.error('Erro ao parsear código MQL:', error);
    return null;
  }
}

// Templates de exemplo
const exampleEA = `//+------------------------------------------------------------------+
//|                                       Moving_Average_Crossover.mq5
//|                        Exemplo: Estratégia de Cruzamento de Médias
//+------------------------------------------------------------------+
#property copyright "TradeStrategist"
#property version   "1.00"

input group "=== Strategy Parameters ==="
input int      InpFastPeriod = 10;      // Fast EMA Period
input int      InpSlowPeriod = 30;      // Slow EMA Period
input double   InpLotSize = 0.1;        // Lot Size
input int      InpStopLoss = 50;        // Stop Loss (pips)
input int      InpTakeProfit = 100;     // Take Profit (pips)
input int      InpMagicNumber = 12345;  // Magic Number

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   double fastMA = iMA(Symbol(), PERIOD_CURRENT, InpFastPeriod, 0, MODE_EMA, PRICE_CLOSE, 0);
   double slowMA = iMA(Symbol(), PERIOD_CURRENT, InpSlowPeriod, 0, MODE_EMA, PRICE_CLOSE, 0);
   double fastMAPrev = iMA(Symbol(), PERIOD_CURRENT, InpFastPeriod, 0, MODE_EMA, PRICE_CLOSE, 1);
   double slowMAPrev = iMA(Symbol(), PERIOD_CURRENT, InpSlowPeriod, 0, MODE_EMA, PRICE_CLOSE, 1);
   
   // Buy signal: Fast crosses above Slow
   if(fastMA > slowMA && fastMAPrev <= slowMAPrev)
   {
      // Open Buy Order
   }
   
   // Sell signal: Fast crosses below Slow
   if(fastMA < slowMA && fastMAPrev >= slowMAPrev)
   {
      // Open Sell Order
   }
}
`;

const exampleIndicator = `//+------------------------------------------------------------------+
//|                                      Custom_RSI_Signals.mq5
//|                        Exemplo: Indicador RSI com Sinais
//+------------------------------------------------------------------+
#property copyright "TradeStrategist"
#property version   "1.00"
#property indicator_separate_window
#property indicator_buffers 2
#property indicator_color1 Blue, Red
#property indicator_color2 Green

input group "=== RSI Parameters ==="
input int      InpRSIPeriod = 14;       // RSI Period
input int      InpOverbought = 70;      // Overbought Level
input int      InpOversold = 30;        // Oversold Level
input int      InpSmoothing = 3;        // Smoothing Period

//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int OnInit()
{
   SetIndexBuffer(0, RSIBuffer);
   SetIndexBuffer(1, SignalBuffer);
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Custom indicator iteration function                              |
//+------------------------------------------------------------------+
int OnCalculate(const int rates_total,
                const int prev_calculated,
                const datetime &time[],
                const double &open[],
                const double &high[],
                const double &low[],
                const double &close[],
                const long &tick_volume[],
                const long &volume[],
                const int &spread[])
{
   int start = prev_calculated == 0 ? InpRSIPeriod : prev_calculated;
   
   for(int i = start; i < rates_total; i++)
   {
      RSIBuffer[i] = iRSI(Symbol(), PERIOD_CURRENT, InpRSIPeriod, PRICE_CLOSE, i);
      
      // Generate signals
      if(RSIBuffer[i] < InpOversold && RSIBuffer[i-1] >= InpOversold)
         SignalBuffer[i] = 1;  // Oversold bounce
      else if(RSIBuffer[i] > InpOverbought && RSIBuffer[i-1] <= InpOverbought)
         SignalBuffer[i] = -1; // Overbought rejection
      else
         SignalBuffer[i] = 0;
   }
   
   return(rates_total);
}
`;

export function EAImporter({ open, onOpenChange, onImport }: EAImporterProps) {
  const [code, setCode] = useState('');
  const [parsedEA, setParsedEA] = useState<ParsedEA | null>(null);
  const [parseError, setParseError] = useState<string | null>(null);
  const [editedParams, setEditedParams] = useState<Record<string, string>>({});
  const [strategyName, setStrategyName] = useState('');
  const [strategyType, setStrategyType] = useState<'trend' | 'reversal' | 'breakout' | 'scalping' | 'mean_reversion'>('trend');

  const handleParse = () => {
    setParseError(null);
    const parsed = parseMQLCode(code);
    
    if (parsed) {
      setParsedEA(parsed);
      setStrategyName(parsed.name);
      
      // Inicializar parâmetros editáveis
      const params: Record<string, string> = {};
      parsed.inputs.forEach(input => {
        params[input.name] = input.defaultValue;
      });
      setEditedParams(params);
    } else {
      setParseError('Não foi possível parsear o código. Verifique se é um código MQL4/5 válido.');
    }
  };

  const handleImport = () => {
    if (!parsedEA) return;

    // Converter parâmetros para números quando possível
    const numericParams: Record<string, number> = {};
    Object.entries(editedParams).forEach(([key, value]) => {
      const numValue = parseFloat(value);
      if (!isNaN(numValue)) {
        numericParams[key] = numValue;
      }
    });

    const newStrategy: Strategy = {
      id: `custom-${Date.now()}`,
      name: strategyName || parsedEA.name,
      type: strategyType,
      parameters: numericParams,
      indicators: parsedEA.indicators,
      metrics: {
        wfe: 0,
        sharpeIS: 0,
        sharpeOOS: 0,
        profitFactor: 0,
        winRate: 0,
        maxDrawdown: 0,
        maxDrawdownMC: 0,
        totalTrades: 0,
        avgTrade: 0,
        expectancy: 0,
        calmarRatio: 0,
        sortinoRatio: 0
      },
      status: 'testing',
      createdAt: Date.now()
    };

    onImport(newStrategy);
    onOpenChange(false);
    
    // Reset
    setCode('');
    setParsedEA(null);
    setEditedParams({});
    setStrategyName('');
  };

  const loadExample = (type: 'ea' | 'indicator') => {
    setCode(type === 'ea' ? exampleEA : exampleIndicator);
    setParsedEA(null);
    setParseError(null);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-5xl bg-slate-900 border-slate-700 text-slate-200 max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-xl flex items-center gap-3">
            <Upload className="h-5 w-5 text-blue-400" />
            Importar EA ou Indicador
          </DialogTitle>
        </DialogHeader>

        <Tabs defaultValue="import" className="w-full">
          <TabsList className="grid w-full grid-cols-2 bg-slate-800">
            <TabsTrigger value="import" className="data-[state=active]:bg-slate-700">
              <Code className="h-4 w-4 mr-2" />
              Importar Código
            </TabsTrigger>
            <TabsTrigger value="examples" className="data-[state=active]:bg-slate-700">
              <FileCode className="h-4 w-4 mr-2" />
              Exemplos
            </TabsTrigger>
          </TabsList>

          {/* Import Tab */}
          <TabsContent value="import" className="space-y-4">
            {!parsedEA ? (
              <>
                <div className="space-y-2">
                  <Label className="text-slate-300">Cole seu código MQL4/5 aqui:</Label>
                  <Textarea
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    placeholder="// Cole o código do seu EA ou Indicador aqui..."
                    className="min-h-[300px] font-mono text-sm bg-slate-950 border-slate-700 text-slate-300"
                  />
                </div>

                {parseError && (
                  <div className="flex items-center gap-2 text-red-400 text-sm bg-red-500/10 p-3 rounded-lg">
                    <AlertCircle className="h-4 w-4" />
                    {parseError}
                  </div>
                )}

                <div className="flex justify-between">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setCode('');
                      setParseError(null);
                    }}
                    className="border-slate-600"
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Limpar
                  </Button>
                  <Button
                    onClick={handleParse}
                    disabled={!code.trim()}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    <Play className="h-4 w-4 mr-2" />
                    Analisar Código
                  </Button>
                </div>
              </>
            ) : (
              <div className="space-y-4">
                {/* Preview do EA parseado */}
                <Card className="bg-slate-800 border-slate-700">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Badge className={cn(
                          parsedEA.type === 'ea' 
                            ? 'bg-blue-500/20 text-blue-400' 
                            : 'bg-purple-500/20 text-purple-400'
                        )}>
                          {parsedEA.type === 'ea' ? 'Expert Advisor' : 'Indicador'}
                        </Badge>
                        <Input
                          value={strategyName}
                          onChange={(e) => setStrategyName(e.target.value)}
                          className="w-64 bg-slate-900 border-slate-600"
                          placeholder="Nome da estratégia"
                        />
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setParsedEA(null)}
                        className="text-slate-400"
                      >
                        <Edit className="h-4 w-4 mr-2" />
                        Editar Código
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* Tipo de estratégia */}
                    <div className="space-y-2">
                      <Label className="text-slate-400">Tipo de Estratégia:</Label>
                      <div className="flex gap-2">
                        {(['trend', 'reversal', 'breakout', 'scalping', 'mean_reversion'] as const).map(type => (
                          <Button
                            key={type}
                            variant={strategyType === type ? 'default' : 'outline'}
                            size="sm"
                            onClick={() => setStrategyType(type)}
                            className={cn(
                              strategyType === type 
                                ? 'bg-blue-600' 
                                : 'border-slate-600 text-slate-400'
                            )}
                          >
                            {type === 'trend' && 'Tendência'}
                            {type === 'reversal' && 'Reversão'}
                            {type === 'breakout' && 'Breakout'}
                            {type === 'scalping' && 'Scalping'}
                            {type === 'mean_reversion' && 'Mean Reversion'}
                          </Button>
                        ))}
                      </div>
                    </div>

                    {/* Indicadores detectados */}
                    <div className="space-y-2">
                      <Label className="text-slate-400">Indicadores Detectados:</Label>
                      <div className="flex flex-wrap gap-2">
                        {parsedEA.indicators.map(ind => (
                          <Badge key={ind} variant="outline" className="bg-slate-700 text-slate-300 border-slate-600">
                            {ind}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    {/* Parâmetros */}
                    <div className="space-y-2">
                      <Label className="text-slate-400">Parâmetros ({parsedEA.inputs.length}):</Label>
                      <div className="grid grid-cols-2 gap-3">
                        {parsedEA.inputs.map((input) => (
                          <div key={input.name} className="space-y-1">
                            <Label className="text-xs text-slate-500">{input.description}</Label>
                            <div className="flex gap-2">
                              <Input
                                value={editedParams[input.name] || input.defaultValue}
                                onChange={(e) => setEditedParams(prev => ({
                                  ...prev,
                                  [input.name]: e.target.value
                                }))}
                                className="bg-slate-900 border-slate-600 font-mono text-sm"
                              />
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Preview do código */}
                <div className="space-y-2">
                  <Label className="text-slate-400">Preview do Código:</Label>
                  <div className="bg-slate-950 rounded-lg p-4 max-h-48 overflow-y-auto">
                    <pre className="text-xs font-mono text-slate-400">
                      {parsedEA.code.substring(0, 1000)}...
                    </pre>
                  </div>
                </div>

                <div className="flex justify-between">
                  <Button
                    variant="outline"
                    onClick={() => setParsedEA(null)}
                    className="border-slate-600"
                  >
                    Voltar
                  </Button>
                  <Button
                    onClick={handleImport}
                    className="bg-emerald-600 hover:bg-emerald-700"
                  >
                    <Check className="h-4 w-4 mr-2" />
                    Importar para Backtest
                  </Button>
                </div>
              </div>
            )}
          </TabsContent>

          {/* Examples Tab */}
          <TabsContent value="examples" className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <Card className="bg-slate-800 border-slate-700 cursor-pointer hover:border-blue-500/50 transition-colors"
                    onClick={() => loadExample('ea')}>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <FileCode className="h-5 w-5 text-blue-400" />
                    Moving Average Crossover
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-slate-400 mb-3">
                    Estratégia clássica de cruzamento de médias móveis. Compra quando a EMA rápida cruza acima da EMA lenta.
                  </p>
                  <div className="flex flex-wrap gap-2">
                    <Badge variant="outline" className="bg-slate-700">EMA</Badge>
                    <Badge variant="outline" className="bg-slate-700">Trend Following</Badge>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-slate-800 border-slate-700 cursor-pointer hover:border-purple-500/50 transition-colors"
                    onClick={() => loadExample('indicator')}>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Settings className="h-5 w-5 text-purple-400" />
                    Custom RSI Signals
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-slate-400 mb-3">
                    Indicador RSI com níveis de sobrecompra/sobrevenda personalizados e sinais visuais.
                  </p>
                  <div className="flex flex-wrap gap-2">
                    <Badge variant="outline" className="bg-slate-700">RSI</Badge>
                    <Badge variant="outline" className="bg-slate-700">Oscillator</Badge>
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="bg-slate-800/50 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-slate-300 mb-2">Como importar seu EA/Indicador:</h4>
              <ol className="text-sm text-slate-400 space-y-2 list-decimal list-inside">
                <li>Copie o código fonte do seu EA (.mq4/.mq5) ou Indicador</li>
                <li>Cole na aba "Importar Código"</li>
                <li>Clique em "Analisar Código" para extrair parâmetros</li>
                <li>Revise e ajuste os parâmetros se necessário</li>
                <li>Clique em "Importar para Backtest"</li>
                <li>O EA aparecerá na lista de estratégias para backtesting</li>
              </ol>
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
