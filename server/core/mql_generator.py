"""
RF-08: Exportar estratégias para template de EA MQL4/5
"""

from typing import Dict, List, Any
import json
import yaml
import logging
import pandas as pd

logger = logging.getLogger(__name__)


class MQLGenerator:
    """Gera código MQL4/5 a partir de estratégias."""
    
    # ── TEMPLATES ──────────────────────────────────────────────────
    # NOTE: Use single braces { } for MQL code blocks.
    # Placeholders use <<name>> syntax to avoid conflicts with MQL braces.
    # This eliminates the previous bug where {{ was never converted to {.
    
    MQL4_TEMPLATE = '''//+------------------------------------------------------------------+
//|                                       <<name>>.mq4
//|                        TradeStrategist Auto-Generated EA
//|                        Generated: <<timestamp>>
//+------------------------------------------------------------------+
#property copyright "TradeStrategist"
#property link      "https://tradestrategist.com"
#property version   "1.00"
#property strict

//--- Input Parameters
<<inputs>>

//--- Global Variables
int g_ticket = -1;
datetime g_lastBarTime = 0;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("<<name>> EA initialized");
   Print("Strategy Type: <<type>>");
   Print("Indicators: <<indicators>>");
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   Print("<<name>> EA deinitialized. Reason: ", reason);
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
   if(MarketInfo(Symbol(), MODE_SPREAD) > InpMaxSpread) return;
   
   // Check for open positions
   if(OrderSelect(g_ticket, SELECT_BY_TICKET) && OrderCloseTime() == 0)
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
<<signal_logic>>
}

//+------------------------------------------------------------------+
//| Open Buy Order                                                   |
//+------------------------------------------------------------------+
void OpenBuyOrder()
{
   double price = Ask;
   double sl = price - InpStopLoss * Point;
   double tp = price + InpTakeProfit * Point;
   
   g_ticket = OrderSend(Symbol(), OP_BUY, InpLotSize, price, 10, sl, tp, "<<name>>", InpMagicNumber, 0, clrGreen);
   if(g_ticket < 0)
   {
      Print("OrderSend error: ", GetLastError());
   }
   else
   {
      Print("Buy order opened: ", g_ticket);
   }
}

//+------------------------------------------------------------------+
//| Open Sell Order                                                  |
//+------------------------------------------------------------------+
void OpenSellOrder()
{
   double price = Bid;
   double sl = price + InpStopLoss * Point;
   double tp = price - InpTakeProfit * Point;
   
   g_ticket = OrderSend(Symbol(), OP_SELL, InpLotSize, price, 10, sl, tp, "<<name>>", InpMagicNumber, 0, clrRed);
   if(g_ticket < 0)
   {
      Print("OrderSend error: ", GetLastError());
   }
   else
   {
      Print("Sell order opened: ", g_ticket);
   }
}

//+------------------------------------------------------------------+
//| Manage Open Position                                             |
//+------------------------------------------------------------------+
void ManageOpenPosition()
{
   if(!InpUseTrailingStop) return;
   
   if(OrderSelect(g_ticket, SELECT_BY_TICKET))
   {
      double openPrice = OrderOpenPrice();
      double currentSL = OrderStopLoss();
      double newSL = 0;
      
      if(OrderType() == OP_BUY)
      {
         newSL = Bid - InpTrailingStop * Point;
         if(newSL > currentSL)
         {
            OrderModify(g_ticket, openPrice, newSL, OrderTakeProfit(), 0, clrBlue);
         }
      }
      else if(OrderType() == OP_SELL)
      {
         newSL = Ask + InpTrailingStop * Point;
         if(newSL < currentSL || currentSL == 0)
         {
            OrderModify(g_ticket, openPrice, newSL, OrderTakeProfit(), 0, clrBlue);
         }
      }
   }
}
//+------------------------------------------------------------------+
'''
    
    MQL5_TEMPLATE = '''//+------------------------------------------------------------------+
//|                                       <<name>>.mq5
//|                        TradeStrategist Auto-Generated EA
//|                        Generated: <<timestamp>>
//+------------------------------------------------------------------+
#property copyright "TradeStrategist"
#property link      "https://tradestrategist.com"
#property version   "1.00"

//--- Input Parameters
<<inputs>>

//--- Global Variables
ulong g_ticket = 0;
datetime g_lastBarTime = 0;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("<<name>> EA initialized");
   Print("Strategy Type: <<type>>");
   Print("Indicators: <<indicators>>");
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   Print("<<name>> EA deinitialized. Reason: ", reason);
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
<<signal_logic>>
}

//+------------------------------------------------------------------+
//| Open Buy Order                                                   |
//+------------------------------------------------------------------+
void OpenBuyOrder()
{
   MqlTradeRequest request = {};
   MqlTradeResult result = {};
   
   double price = SymbolInfoDouble(Symbol(), SYMBOL_ASK);
   double sl = price - InpStopLoss * SymbolInfoDouble(Symbol(), SYMBOL_POINT);
   double tp = price + InpTakeProfit * SymbolInfoDouble(Symbol(), SYMBOL_POINT);
   
   request.action = TRADE_ACTION_DEAL;
   request.symbol = Symbol();
   request.volume = InpLotSize;
   request.type = ORDER_TYPE_BUY;
   request.price = price;
   request.sl = sl;
   request.tp = tp;
   request.deviation = 10;
   request.magic = InpMagicNumber;
   request.comment = "<<name>>";
   
   if(!OrderSend(request, result))
   {
      Print("OrderSend error: ", GetLastError());
   }
   else
   {
      g_ticket = result.order;
      Print("Buy order opened: ", result.order);
   }
}

//+------------------------------------------------------------------+
//| Open Sell Order                                                  |
//+------------------------------------------------------------------+
void OpenSellOrder()
{
   MqlTradeRequest request = {};
   MqlTradeResult result = {};
   
   double price = SymbolInfoDouble(Symbol(), SYMBOL_BID);
   double sl = price + InpStopLoss * SymbolInfoDouble(Symbol(), SYMBOL_POINT);
   double tp = price - InpTakeProfit * SymbolInfoDouble(Symbol(), SYMBOL_POINT);
   
   request.action = TRADE_ACTION_DEAL;
   request.symbol = Symbol();
   request.volume = InpLotSize;
   request.type = ORDER_TYPE_SELL;
   request.price = price;
   request.sl = sl;
   request.tp = tp;
   request.deviation = 10;
   request.magic = InpMagicNumber;
   request.comment = "<<name>>";
   
   if(!OrderSend(request, result))
   {
      Print("OrderSend error: ", GetLastError());
   }
   else
   {
      g_ticket = result.order;
      Print("Sell order opened: ", result.order);
   }
}

//+------------------------------------------------------------------+
//| Manage Open Position                                             |
//+------------------------------------------------------------------+
void ManageOpenPosition()
{
   if(!InpUseTrailingStop) return;
   
   double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
   double currentSL = PositionGetDouble(POSITION_SL);
   double newSL = 0;
   
   if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY)
   {
      newSL = SymbolInfoDouble(Symbol(), SYMBOL_BID) - InpTrailingStop * SymbolInfoDouble(Symbol(), SYMBOL_POINT);
      if(newSL > currentSL)
      {
         ModifyPosition(newSL);
      }
   }
   else
   {
      newSL = SymbolInfoDouble(Symbol(), SYMBOL_ASK) + InpTrailingStop * SymbolInfoDouble(Symbol(), SYMBOL_POINT);
      if(newSL < currentSL || currentSL == 0)
      {
         ModifyPosition(newSL);
      }
   }
}

//+------------------------------------------------------------------+
//| Modify Position                                                  |
//+------------------------------------------------------------------+
void ModifyPosition(double newSL)
{
   MqlTradeRequest request = {};
   MqlTradeResult result = {};
   
   request.action = TRADE_ACTION_SLTP;
   request.position = PositionGetInteger(POSITION_TICKET);
   request.sl = newSL;
   request.tp = PositionGetDouble(POSITION_TP);
   
   if(!OrderSend(request, result))
   {
      Print("OrderModify error: ", GetLastError());
   }
}
//+------------------------------------------------------------------+
'''
    
    def generate_mql4(self, strategy: Dict) -> str:
        """Gera código MQL4 para a estratégia."""
        return self._generate_mql(strategy, 'mql4')
    
    def generate_mql5(self, strategy: Dict) -> str:
        """Gera código MQL5 para a estratégia."""
        return self._generate_mql(strategy, 'mql5')
    
    def _generate_mql(self, strategy: Dict, version: str) -> str:
        """Gera código MQL."""
        template = self.MQL4_TEMPLATE if version == 'mql4' else self.MQL5_TEMPLATE
        
        if not strategy:
            strategy = {}
            
        # Gerar inputs com defaults explícitos
        parameters = strategy.get('parameters') or {}
        
        # FIX: Coerce parameter values to numeric types
        # JSON payloads may send numbers as strings
        parameters = self._coerce_params(parameters)
        
        strategy_type = str(strategy.get('type') or 'trend').lower()
        
        if strategy_type == 'trend':
            parameters.setdefault("FastEMA", 9)
            parameters.setdefault("SlowEMA", 21)
        elif strategy_type == 'reversal':
            parameters.setdefault("RsiPeriod", 14)
            parameters.setdefault("Oversold", 30)
            parameters.setdefault("Overbought", 70)
        elif strategy_type == 'mean_reversion':
            parameters.setdefault("period", 20)
            parameters.setdefault("std", 2.0)
        elif strategy_type in ['donchian', 'breakout']:
            parameters.setdefault("DonchianPeriod", 20)
            
        inputs_str = self._generate_inputs(parameters, version)
        
        # Gerar lógica de sinais
        signal_logic = self._generate_signal_logic(strategy_type, version)
        
        indicators = strategy.get('indicators') or []
        
        name = str(strategy.get('name') or 'CustomStrategy').replace(' ', '_')
        timestamp = str(pd.Timestamp.now())
        indicators_str = ', '.join(str(i) for i in indicators)
        
        # FIX: Use <<placeholder>> syntax to avoid conflicts with MQL braces
        output = template.replace('<<name>>', name)
        output = output.replace('<<timestamp>>', timestamp)
        output = output.replace('<<type>>', strategy_type)
        output = output.replace('<<indicators>>', indicators_str)
        output = output.replace('<<inputs>>', inputs_str)
        output = output.replace('<<signal_logic>>', signal_logic)
        
        return output
    
    @staticmethod
    def _coerce_params(parameters: Dict) -> Dict:
        """Coerce parameter values from strings to int/float when possible."""
        coerced = {}
        for key, value in parameters.items():
            if isinstance(value, (int, float)):
                coerced[key] = value
            elif isinstance(value, str):
                try:
                    # Try int first, then float
                    if '.' in value:
                        coerced[key] = float(value)
                    else:
                        coerced[key] = int(value)
                except (ValueError, TypeError):
                    logger.warning(f"Cannot coerce parameter {key}={value!r} to numeric, skipping")
                    coerced[key] = value
            else:
                coerced[key] = value
        return coerced
    
    def _generate_inputs(self, parameters: Dict, version: str) -> str:
        """Gera seção de inputs MQL."""
        lines = []
        if version == 'mql5':
            lines.append('input group "=== Trading Parameters ==="')
        
        # Parâmetros padrão
        lines.append('input double   InpLotSize = 0.1;        // Lot Size')
        lines.append(f'input int      InpStopLoss = {parameters.get("stopLoss", 50)};        // Stop Loss (pips)')
        lines.append(f'input int      InpTakeProfit = {parameters.get("takeProfit", 100)};     // Take Profit (pips)')
        lines.append('input int      InpMaxSpread = 30;       // Max Spread (points)')
        lines.append('input ulong    InpMagicNumber = 12345;  // Magic Number')
        lines.append('input bool     InpUseTrailingStop = true; // Use Trailing Stop')
        lines.append('input int      InpTrailingStop = 30;    // Trailing Stop (pips)')
        
        lines.append('')
        if version == 'mql5':
            lines.append('input group "=== Strategy Parameters ==="')
        
        # Parâmetros da estratégia
        for name, value in parameters.items():
            if name in ["stopLoss", "takeProfit"]:
                continue
            if isinstance(value, int):
                lines.append(f'input int      Inp{name} = {value};        // {name}')
            elif isinstance(value, float):
                lines.append(f'input double   Inp{name} = {value};        // {name}')
            else:
                # Fallback: treat as string comment for unsupported types
                logger.warning(f"Skipping non-numeric parameter: {name}={value!r}")
        
        return '\n'.join(lines)
    
    def _generate_signal_logic(self, strategy_type: str, version: str) -> str:
        """Gera lógica de sinais baseada no tipo e versão."""
        if version == 'mql4':
            if strategy_type == 'trend':
                return '''   double fastMA = iMA(Symbol(), PERIOD_CURRENT, InpFastEMA, 0, MODE_EMA, PRICE_CLOSE, 0);
   double slowMA = iMA(Symbol(), PERIOD_CURRENT, InpSlowEMA, 0, MODE_EMA, PRICE_CLOSE, 0);
   double fastMAPrev = iMA(Symbol(), PERIOD_CURRENT, InpFastEMA, 0, MODE_EMA, PRICE_CLOSE, 1);
   double slowMAPrev = iMA(Symbol(), PERIOD_CURRENT, InpSlowEMA, 0, MODE_EMA, PRICE_CLOSE, 1);
   
   if(fastMA > slowMA && fastMAPrev <= slowMAPrev) return 1;
   if(fastMA < slowMA && fastMAPrev >= slowMAPrev) return -1;
   return 0;'''
            
            elif strategy_type == 'reversal':
                return '''   double rsi = iRSI(Symbol(), PERIOD_CURRENT, InpRsiPeriod, PRICE_CLOSE, 0);
   
   if(rsi < InpOversold) return 1;
   if(rsi > InpOverbought) return -1;
   return 0;'''
            
            elif strategy_type == 'mean_reversion':
                return '''   double upper = iBands(Symbol(), PERIOD_CURRENT, Inpperiod, Inpstd, 0, PRICE_CLOSE, MODE_UPPER, 0);
   double lower = iBands(Symbol(), PERIOD_CURRENT, Inpperiod, Inpstd, 0, PRICE_CLOSE, MODE_LOWER, 0);
   double close = iClose(Symbol(), PERIOD_CURRENT, 0);
   
   if(close < lower) return 1;
   if(close > upper) return -1;
   return 0;'''
            
            elif strategy_type in ['donchian', 'breakout']:
                return '''   double upper = iHigh(Symbol(), PERIOD_CURRENT, iHighest(Symbol(), PERIOD_CURRENT, MODE_HIGH, InpDonchianPeriod, 1));
   double lower = iLow(Symbol(), PERIOD_CURRENT, iLowest(Symbol(), PERIOD_CURRENT, MODE_LOW, InpDonchianPeriod, 1));
   double close = iClose(Symbol(), PERIOD_CURRENT, 0);
   
   if(close > upper) return 1;
   if(close < lower) return -1;
   return 0;'''
            
            elif strategy_type == 'scalping':
                return '''   double fastMA = iMA(Symbol(), PERIOD_CURRENT, 5, 0, MODE_EMA, PRICE_CLOSE, 0);
   double slowMA = iMA(Symbol(), PERIOD_CURRENT, 13, 0, MODE_EMA, PRICE_CLOSE, 0);
   double rsi = iRSI(Symbol(), PERIOD_CURRENT, 7, PRICE_CLOSE, 0);
   
   if(fastMA > slowMA && rsi < 70) return 1;
   if(fastMA < slowMA && rsi > 30) return -1;
   return 0;'''
            
            else:
                return '''   // Default: EMA Crossover
   double fastMA = iMA(Symbol(), PERIOD_CURRENT, 9, 0, MODE_EMA, PRICE_CLOSE, 0);
   double slowMA = iMA(Symbol(), PERIOD_CURRENT, 21, 0, MODE_EMA, PRICE_CLOSE, 0);
   
   if(fastMA > slowMA) return 1;
   if(fastMA < slowMA) return -1;
   return 0;'''
        
        else: # MQL5 logic using Handles and CopyBuffer
            if strategy_type == 'trend':
                return '''   static int hFast = INVALID_HANDLE;
   static int hSlow = INVALID_HANDLE;
   if(hFast == INVALID_HANDLE) hFast = iMA(_Symbol, _Period, InpFastEMA, 0, MODE_EMA, PRICE_CLOSE);
   if(hSlow == INVALID_HANDLE) hSlow = iMA(_Symbol, _Period, InpSlowEMA, 0, MODE_EMA, PRICE_CLOSE);
   
   double f[2], s[2];
   if(CopyBuffer(hFast, 0, 0, 2, f) < 2 || CopyBuffer(hSlow, 0, 0, 2, s) < 2) return 0;
   
   // In MQL5 CopyBuffer: [0] is oldest (previous), [1] is newest (current)
   if(f[1] > s[1] && f[0] <= s[0]) return 1;
   if(f[1] < s[1] && f[0] >= s[0]) return -1;
   return 0;'''
            
            elif strategy_type == 'reversal':
                return '''   static int hRsi = INVALID_HANDLE;
   if(hRsi == INVALID_HANDLE) hRsi = iRSI(_Symbol, _Period, InpRsiPeriod, PRICE_CLOSE);
   
   double r[1];
   if(CopyBuffer(hRsi, 0, 0, 1, r) < 1) return 0;
   
   if(r[0] < InpOversold) return 1;
   if(r[0] > InpOverbought) return -1;
   return 0;'''
            
            elif strategy_type == 'mean_reversion':
                return '''   static int hBands = INVALID_HANDLE;
   if(hBands == INVALID_HANDLE) hBands = iBands(_Symbol, _Period, Inpperiod, 0, Inpstd, PRICE_CLOSE);
   
   double upper[1], lower[1], close[1];
   if(CopyBuffer(hBands, 1, 0, 1, upper) < 1 || CopyBuffer(hBands, 2, 0, 1, lower) < 1) return 0;
   CopyClose(_Symbol, _Period, 0, 1, close);
   
   if(close[0] < lower[0]) return 1;
   if(close[0] > upper[0]) return -1;
   return 0;'''
            
            elif strategy_type in ['donchian', 'breakout']:
                return '''   double high[1], low[1], close[1];
   int highest_idx = iHighest(_Symbol, _Period, MODE_HIGH, InpDonchianPeriod, 1);
   int lowest_idx = iLowest(_Symbol, _Period, MODE_LOW, InpDonchianPeriod, 1);
   
   CopyHigh(_Symbol, _Period, highest_idx, 1, high);
   CopyLow(_Symbol, _Period, lowest_idx, 1, low);
   CopyClose(_Symbol, _Period, 0, 1, close);
   
   if(close[0] > high[0]) return 1;
   if(close[0] < low[0]) return -1;
   return 0;'''

            elif strategy_type == 'scalping':
                return '''   static int hFast = INVALID_HANDLE;
   static int hSlow = INVALID_HANDLE;
   static int hRsi = INVALID_HANDLE;
   if(hFast == INVALID_HANDLE) hFast = iMA(_Symbol, _Period, 5, 0, MODE_EMA, PRICE_CLOSE);
   if(hSlow == INVALID_HANDLE) hSlow = iMA(_Symbol, _Period, 13, 0, MODE_EMA, PRICE_CLOSE);
   if(hRsi == INVALID_HANDLE) hRsi = iRSI(_Symbol, _Period, 7, PRICE_CLOSE);
   
   double f[1], s[1], r[1];
   if(CopyBuffer(hFast, 0, 0, 1, f) < 1 || CopyBuffer(hSlow, 0, 0, 1, s) < 1 || CopyBuffer(hRsi, 0, 0, 1, r) < 1) return 0;
   
   if(f[0] > s[0] && r[0] < 70) return 1;
   if(f[0] < s[0] && r[0] > 30) return -1;
   return 0;'''

            else:
                return '''   static int hFast = INVALID_HANDLE;
   static int hSlow = INVALID_HANDLE;
   if(hFast == INVALID_HANDLE) hFast = iMA(_Symbol, _Period, 9, 0, MODE_EMA, PRICE_CLOSE);
   if(hSlow == INVALID_HANDLE) hSlow = iMA(_Symbol, _Period, 21, 0, MODE_EMA, PRICE_CLOSE);
   
   double f[1], s[1];
   if(CopyBuffer(hFast, 0, 0, 1, f) < 1 || CopyBuffer(hSlow, 0, 0, 1, s) < 1) return 0;
   
   if(f[0] > s[0]) return 1;
   if(f[0] < s[0]) return -1;
   return 0;'''
    
    def generate_json(self, strategy: Dict) -> str:
        """Gera configuração JSON."""
        config = {
            'strategy': {
                'name': strategy.get('name', 'CustomStrategy'),
                'type': strategy.get('type', 'trend'),
                'parameters': strategy.get('parameters', {}),
                'indicators': strategy.get('indicators', [])
            },
            'trading': {
                'lotSize': 0.1,
                'stopLoss': 50,
                'takeProfit': 100,
                'maxSpread': 30
            },
            'risk': {
                'maxRiskPercent': 2.0,
                'useTrailingStop': True,
                'trailingStop': 30
            }
        }
        return json.dumps(config, indent=2)
    
    def generate_yaml(self, strategy: Dict) -> str:
        """Gera configuração YAML."""
        config = {
            'strategy': {
                'name': strategy.get('name', 'CustomStrategy'),
                'type': strategy.get('type', 'trend'),
                'parameters': strategy.get('parameters', {}),
                'indicators': strategy.get('indicators', [])
            }
        }
        return yaml.dump(config, default_flow_style=False)


mql_generator = MQLGenerator()
