import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Copy, Download, FileCode, Settings, Check } from 'lucide-react';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import type { Strategy } from '@/types/trading';

interface EAExporterProps {
  strategy: Strategy | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function EAExporter({ strategy, open, onOpenChange }: EAExporterProps) {
  const [version, setVersion] = useState<'mql4' | 'mql5'>('mql5');
  const [copied, setCopied] = useState(false);

  if (!strategy) return null;

  const generateMQLCode = (strat: Strategy, ver: 'mql4' | 'mql5'): string => {
    const isMQL5 = ver === 'mql5';
    
    return `//+------------------------------------------------------------------+
//|                                      ${strat.name.replace(/\s+/g, '_')}.${ver === 'mql5' ? 'mq5' : 'mq4'}
//|                        TradeStrategist Auto-Generated EA
//|                        Generated: ${new Date().toISOString()}
//+------------------------------------------------------------------+
#property copyright "TradeStrategist"
#property link      "https://tradestrategist.com"
#property version   "1.00"
#property strict

//--- Input Parameters
input group "=== Trading Parameters ==="
input double   InpLotSize = 0.1;        // Lot Size
input int      InpStopLoss = 50;        // Stop Loss (pips)
input int      InpTakeProfit = 100;     // Take Profit (pips)
input int      InpMagicNumber = ${Math.floor(Math.random() * 90000) + 10000};  // Magic Number

input group "=== Strategy Parameters ==="
${Object.entries(strat.parameters).map(([key, value]) => 
  `input int      Inp${key.charAt(0).toUpperCase() + key.slice(1)} = ${value};        // ${key}`
).join('\n')}

input group "=== Risk Management ==="
input double   InpMaxRiskPercent = 2.0;  // Max Risk per Trade (%)
input int      InpMaxSpread = 30;        // Max Spread (points)
input bool     InpUseTrailingStop = true; // Use Trailing Stop

//--- Global Variables
${isMQL5 ? 'int g_ticket = INVALID_TICKET;' : 'int g_ticket = -1;'}
datetime g_lastBarTime = 0;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("${strat.name} EA initialized");
   Print("Strategy Type: ${strat.type}");
   Print("Indicators: ${strat.indicators.join(', ')}");
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   Print("${strat.name} EA deinitialized. Reason: ", reason);
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   // Check for new bar
   datetime currentBarTime = iTime(Symbol(), PERIOD_CURRENT, 0);
   if(currentBarTime == g_lastBarTime) return;
   g_lastBarTime = currentBarTime;
   
   // Check spread
   if(SymbolInfoInteger(Symbol(), SYMBOL_SPREAD) > InpMaxSpread) return;
   
   // Check for open positions
   if(PositionSelect(Symbol()))
   {
      ManageOpenPosition();
      return;
   }
   
   // Check entry conditions
   int signal = CheckEntrySignal();
   
   if(signal > 0) // Buy signal
   {
      OpenBuyOrder();
   }
   else if(signal < 0) // Sell signal
   {
      OpenSellOrder();
   }
}

//+------------------------------------------------------------------+
//| Check entry signal                                               |
//+------------------------------------------------------------------+
int CheckEntrySignal()
{
   // Calculate indicators
   double emaFast = iMA(Symbol(), PERIOD_CURRENT, InpFastEma, 0, MODE_EMA, PRICE_CLOSE, 0);
   double emaSlow = iMA(Symbol(), PERIOD_CURRENT, InpSlowEma, 0, MODE_EMA, PRICE_CLOSE, 0);
   double emaFastPrev = iMA(Symbol(), PERIOD_CURRENT, InpFastEma, 0, MODE_EMA, PRICE_CLOSE, 1);
   double emaSlowPrev = iMA(Symbol(), PERIOD_CURRENT, InpSlowEma, 0, MODE_EMA, PRICE_CLOSE, 1);
   
   // Trend following logic
   if(emaFast > emaSlow && emaFastPrev <= emaSlowPrev)
   {
      return 1; // Buy signal
   }
   else if(emaFast < emaSlow && emaFastPrev >= emaSlowPrev)
   {
      return -1; // Sell signal
   }
   
   return 0; // No signal
}

//+------------------------------------------------------------------+
//| Open Buy Order                                                   |
//+------------------------------------------------------------------+
void OpenBuyOrder()
{
   double price = Ask;
   double sl = price - InpStopLoss * Point;
   double tp = price + InpTakeProfit * Point;
   
   ${isMQL5 ? `
   MqlTradeRequest request;
   MqlTradeResult result;
   ZeroMemory(request);
   ZeroMemory(result);
   
   request.action = TRADE_ACTION_DEAL;
   request.symbol = Symbol();
   request.volume = InpLotSize;
   request.type = ORDER_TYPE_BUY;
   request.price = price;
   request.sl = sl;
   request.tp = tp;
   request.deviation = 10;
   request.magic = InpMagicNumber;
   request.comment = "${strat.name}";
   
   if(!OrderSend(request, result))
   {
      Print("OrderSend error: ", GetLastError());
   }
   else
   {
      g_ticket = result.order;
      Print("Buy order opened: ", result.order);
   }
   ` : `
   g_ticket = OrderSend(Symbol(), OP_BUY, InpLotSize, price, 10, sl, tp, "${strat.name}", InpMagicNumber, 0, clrGreen);
   if(g_ticket < 0)
   {
      Print("OrderSend error: ", GetLastError());
   }
   else
   {
      Print("Buy order opened: ", g_ticket);
   }
   `}
}

//+------------------------------------------------------------------+
//| Open Sell Order                                                  |
//+------------------------------------------------------------------+
void OpenSellOrder()
{
   double price = Bid;
   double sl = price + InpStopLoss * Point;
   double tp = price - InpTakeProfit * Point;
   
   ${isMQL5 ? `
   MqlTradeRequest request;
   MqlTradeResult result;
   ZeroMemory(request);
   ZeroMemory(result);
   
   request.action = TRADE_ACTION_DEAL;
   request.symbol = Symbol();
   request.volume = InpLotSize;
   request.type = ORDER_TYPE_SELL;
   request.price = price;
   request.sl = sl;
   request.tp = tp;
   request.deviation = 10;
   request.magic = InpMagicNumber;
   request.comment = "${strat.name}";
   
   if(!OrderSend(request, result))
   {
      Print("OrderSend error: ", GetLastError());
   }
   else
   {
      g_ticket = result.order;
      Print("Sell order opened: ", result.order);
   }
   ` : `
   g_ticket = OrderSend(Symbol(), OP_SELL, InpLotSize, price, 10, sl, tp, "${strat.name}", InpMagicNumber, 0, clrRed);
   if(g_ticket < 0)
   {
      Print("OrderSend error: ", GetLastError());
   }
   else
   {
      Print("Sell order opened: ", g_ticket);
   }
   `}
}

//+------------------------------------------------------------------+
//| Manage Open Position                                             |
//+------------------------------------------------------------------+
void ManageOpenPosition()
{
   if(!InpUseTrailingStop) return;
   
   ${isMQL5 ? `
   double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
   double currentSL = PositionGetDouble(POSITION_SL);
   double newSL = 0;
   
   if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY)
   {
      newSL = Bid - InpStopLoss * Point;
      if(newSL > currentSL)
      {
         ModifyPosition(newSL);
      }
   }
   else
   {
      newSL = Ask + InpStopLoss * Point;
      if(newSL < currentSL || currentSL == 0)
      {
         ModifyPosition(newSL);
      }
   }
   ` : `
   if(OrderSelect(g_ticket, SELECT_BY_TICKET))
   {
      double openPrice = OrderOpenPrice();
      double currentSL = OrderStopLoss();
      double newSL = 0;
      
      if(OrderType() == OP_BUY)
      {
         newSL = Bid - InpStopLoss * Point;
         if(newSL > currentSL)
         {
            OrderModify(g_ticket, openPrice, newSL, OrderTakeProfit(), 0, clrBlue);
         }
      }
      else if(OrderType() == OP_SELL)
      {
         newSL = Ask + InpStopLoss * Point;
         if(newSL < currentSL || currentSL == 0)
         {
            OrderModify(g_ticket, openPrice, newSL, OrderTakeProfit(), 0, clrBlue);
         }
      }
   }
   `}
}

${isMQL5 ? `
//+------------------------------------------------------------------+
//| Modify Position                                                  |
//+------------------------------------------------------------------+
void ModifyPosition(double newSL)
{
   MqlTradeRequest request;
   MqlTradeResult result;
   ZeroMemory(request);
   ZeroMemory(result);
   
   request.action = TRADE_ACTION_SLTP;
   request.symbol = Symbol();
   request.sl = newSL;
   request.tp = PositionGetDouble(POSITION_TP);
   request.position = PositionGetInteger(POSITION_TICKET);
   
   if(!OrderSend(request, result))
   {
      Print("OrderModify error: ", GetLastError());
   }
}
` : ''}
//+------------------------------------------------------------------+
`;
  };

  const generateJSONConfig = (strat: Strategy): string => {
    return JSON.stringify({
      strategy: {
        name: strat.name,
        type: strat.type,
        version: '1.0.0',
        created: new Date().toISOString(),
        indicators: strat.indicators,
        parameters: strat.parameters,
        metrics: strat.metrics
      },
      trading: {
        lotSize: 0.1,
        stopLoss: 50,
        takeProfit: 100,
        maxSpread: 30,
        maxSlippage: 10,
        magicNumber: Math.floor(Math.random() * 90000) + 10000
      },
      risk: {
        maxRiskPercent: 2.0,
        maxDrawdownPercent: 20,
        useTrailingStop: true,
        trailingStopPips: 30
      },
      filters: {
        minSharpe: 1.0,
        minProfitFactor: 1.5,
        maxDrawdown: 25
      }
    }, null, 2);
  };

  const generateYAMLConfig = (strat: Strategy): string => {
    return `# TradeStrategist Configuration
# Strategy: ${strat.name}
# Generated: ${new Date().toISOString()}

strategy:
  name: "${strat.name}"
  type: ${strat.type}
  version: "1.0.0"
  created: "${new Date().toISOString()}"
  indicators:
${strat.indicators.map(i => `    - ${i}`).join('\n')}
  parameters:
${Object.entries(strat.parameters).map(([k, v]) => `    ${k}: ${v}`).join('\n')}
  metrics:
    wfe: ${strat.metrics.wfe}
    sharpe_oos: ${strat.metrics.sharpeOOS}
    max_drawdown: ${strat.metrics.maxDrawdown}
    win_rate: ${strat.metrics.winRate}

trading:
  lot_size: 0.1
  stop_loss: 50
  take_profit: 100
  max_spread: 30
  max_slippage: 10
  magic_number: ${Math.floor(Math.random() * 90000) + 10000}

risk_management:
  max_risk_percent: 2.0
  max_drawdown_percent: 20
  use_trailing_stop: true
  trailing_stop_pips: 30

filters:
  min_sharpe: 1.0
  min_profit_factor: 1.5
  max_drawdown: 25
`;
  };

  const mqlCode = generateMQLCode(strategy, version);
  const jsonConfig = generateJSONConfig(strategy);
  const yamlConfig = generateYAMLConfig(strategy);

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl bg-slate-900 border-slate-700 text-slate-200 max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-xl flex items-center gap-3">
            <FileCode className="h-5 w-5 text-blue-400" />
            Exportar EA: {strategy.name}
          </DialogTitle>
        </DialogHeader>

        <Tabs defaultValue="mql" className="w-full">
          <TabsList className="grid w-full grid-cols-3 bg-slate-800">
            <TabsTrigger value="mql" className="data-[state=active]:bg-slate-700">
              <FileCode className="h-4 w-4 mr-2" />
              MQL4/5
            </TabsTrigger>
            <TabsTrigger value="json" className="data-[state=active]:bg-slate-700">
              <Settings className="h-4 w-4 mr-2" />
              JSON
            </TabsTrigger>
            <TabsTrigger value="yaml" className="data-[state=active]:bg-slate-700">
              <Settings className="h-4 w-4 mr-2" />
              YAML
            </TabsTrigger>
          </TabsList>

          {/* MQL Tab */}
          <TabsContent value="mql" className="space-y-4">
            <div className="flex items-center justify-between">
              <select 
                value={version} 
                onChange={(e) => setVersion(e.target.value as 'mql4' | 'mql5')}
                className="w-32 bg-slate-800 border border-slate-600 rounded px-3 py-2 text-sm"
              >
                <option value="mql4">MQL4</option>
                <option value="mql5">MQL5</option>
              </select>

              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleCopy(mqlCode)}
                  className="border-slate-600"
                >
                  {copied ? <Check className="h-4 w-4 mr-2" /> : <Copy className="h-4 w-4 mr-2" />}
                  Copiar
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleDownload(mqlCode, `${strategy.name.replace(/\s+/g, '_')}.${version}`)}
                  className="border-slate-600"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download
                </Button>
              </div>
            </div>

            <div className="bg-slate-950 rounded-lg p-4 overflow-x-auto max-h-96 overflow-y-auto">
              <pre className="text-xs font-mono text-slate-300 whitespace-pre">
                {mqlCode}
              </pre>
            </div>
          </TabsContent>

          {/* JSON Tab */}
          <TabsContent value="json" className="space-y-4">
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleCopy(jsonConfig)}
                className="border-slate-600"
              >
                {copied ? <Check className="h-4 w-4 mr-2" /> : <Copy className="h-4 w-4 mr-2" />}
                Copiar
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleDownload(jsonConfig, `${strategy.name.replace(/\s+/g, '_')}.json`)}
                className="border-slate-600"
              >
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
            </div>

            <div className="bg-slate-950 rounded-lg p-4 overflow-x-auto max-h-96 overflow-y-auto">
              <pre className="text-xs font-mono text-slate-300 whitespace-pre">
                {jsonConfig}
              </pre>
            </div>
          </TabsContent>

          {/* YAML Tab */}
          <TabsContent value="yaml" className="space-y-4">
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleCopy(yamlConfig)}
                className="border-slate-600"
              >
                {copied ? <Check className="h-4 w-4 mr-2" /> : <Copy className="h-4 w-4 mr-2" />}
                Copiar
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleDownload(yamlConfig, `${strategy.name.replace(/\s+/g, '_')}.yaml`)}
                className="border-slate-600"
              >
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
            </div>

            <div className="bg-slate-950 rounded-lg p-4 overflow-x-auto max-h-96 overflow-y-auto">
              <pre className="text-xs font-mono text-slate-300 whitespace-pre">
                {yamlConfig}
              </pre>
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
