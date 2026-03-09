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
   double atr = iATR(Symbol(), PERIOD_CURRENT, InpATRPeriod, 1);
   if(atr <= 0) return;
   double slDist = atr * InpSLMultiplier;
   double tpDist = atr * InpTPMultiplier;
   
   double sl = Bid + slDist;
   double tp = Bid - tpDist;
   
   g_ticket = OrderSend(Symbol(), OP_SELL, InpLotSize, Bid, 10, sl, tp, "<<name>>", InpMagicNumber, 0, clrRed);
   if(g_ticket < 0) Print("Sell error: ", GetLastError());
}

//+------------------------------------------------------------------+
void ManageOpenPosition()
{
   if(!InpUseTrailingStop) return;
   if(!OrderSelect(g_ticket, SELECT_BY_TICKET)) return;

   double atr = iATR(Symbol(), PERIOD_CURRENT, InpATRPeriod, 1);
   if(atr <= 0) return;
   double trailDist = atr * InpTrailMultiplier;
   double currentSL = OrderStopLoss();

   if(OrderType() == OP_BUY)
   {
      double newSL = Bid - trailDist;
      if(newSL > currentSL && newSL > OrderOpenPrice())
         OrderModify(g_ticket, OrderOpenPrice(), newSL, OrderTakeProfit(), 0, clrBlue);
   }
   else if(OrderType() == OP_SELL)
   {
      double newSL = Ask + trailDist;
      if((newSL < currentSL || currentSL == 0) && newSL < OrderOpenPrice())
         OrderModify(g_ticket, OrderOpenPrice(), newSL, OrderTakeProfit(), 0, clrBlue);
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

#include <Trade/Trade.mqh>

//--- Input Parameters
<<inputs>>

//--- Global Variables
CTrade g_trade;
datetime g_lastBarTime = 0;
int g_hATR = INVALID_HANDLE;
<<global_vars>>

//--- Performance & Dashboard Vars
<<stats_vars>>
<<dashboard_vars>>
<<news_vars>>
<<global_limits_vars>>

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   // Setup Trade Class
   g_trade.SetExpertMagicNumber(InpMagicNumber);
   g_trade.SetDeviationInPoints(50);

   // ATR for adaptive SL/TP
   g_hATR = iATR(Symbol(), PERIOD_CURRENT, InpATRPeriod);
   if(g_hATR == INVALID_HANDLE)
   { Print("ATR handle error: ", GetLastError()); return(INIT_FAILED); }
   
<<init_logic>>

   // Initialize stats and dashboard
   LoadHistoryStats();
   CreatePanel();
   
   Print("<<name>> EA initialized | <<type>> | <<indicators>>");
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   if(g_hATR != INVALID_HANDLE) IndicatorRelease(g_hATR);
<<deinit_logic>>
   DeletePanel();
   Print("<<name>> removed. Reason: ", reason);
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   // Check global limits (Equity protective)
   CheckGlobalLimits();

   // Check for new bar
   datetime currentBarTime = iTime(Symbol(), PERIOD_CURRENT, 0);
   bool isNewBar = (currentBarTime != g_lastBarTime);
   
   if(isNewBar)
   {
      g_lastBarTime = currentBarTime;
      
      // Update news filter and stats on each new bar
      CheckNewsCalendar();
      UpdateStats();
      UpdatePanel();
   }
   
   // Update dashboard prices/equity on each tick (lightweight)
   UpdatePanelPrices();

   // News Filter Check
   if(InpUseNewsFilter && g_newsActive) return;

   // Check spread
   if(InpMaxSpread > 0 && (int)SymbolInfoInteger(Symbol(), SYMBOL_SPREAD) > InpMaxSpread) return;
   
   // Check for open positions (Filter by Magic and Symbol)
   bool hasPosition = false;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(PositionGetSymbol(i) == Symbol() && PositionGetInteger(POSITION_MAGIC) == InpMagicNumber)
      { hasPosition = true; break; }
   }

   if(hasPosition)
   {
      ManageOpenPosition();
      return;
   }
   
   // Check entry conditions
   int signal = CheckEntrySignal();
   
   if(signal > 0) // Buy signal
   {
      OpenOrder(ORDER_TYPE_BUY);
   }
   else if(signal < 0) // Sell signal
   {
      OpenOrder(ORDER_TYPE_SELL);
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
//| Open Order (ATR-based SL/TP)                                     |
//+------------------------------------------------------------------+
void OpenOrder(ENUM_ORDER_TYPE type)
{
   double atr[];
   ArrayResize(atr, 1);
   ArraySetAsSeries(atr, true);
   if(CopyBuffer(g_hATR, 0, 0, 1, atr) < 1 || atr[0] <= 0) return;

   double slDist = atr[0] * InpSLMultiplier;
   double tpDist = atr[0] * InpTPMultiplier;
   int digits = (int)SymbolInfoInteger(Symbol(), SYMBOL_DIGITS);

   if(type == ORDER_TYPE_BUY)
   {
      double price = SymbolInfoDouble(Symbol(), SYMBOL_ASK);
      double sl = (slDist > 0) ? NormalizeDouble(price - slDist, digits) : 0;
      double tp = (tpDist > 0) ? NormalizeDouble(price + tpDist, digits) : 0;
      if(!g_trade.Buy(InpLotSize, Symbol(), price, sl, tp, "<<name>>"))
         Print("Buy error: ", GetLastError());
   }
   else
   {
      double price = SymbolInfoDouble(Symbol(), SYMBOL_BID);
      double sl = (slDist > 0) ? NormalizeDouble(price + slDist, digits) : 0;
      double tp = (tpDist > 0) ? NormalizeDouble(price - tpDist, digits) : 0;
      if(!g_trade.Sell(InpLotSize, Symbol(), price, sl, tp, "<<name>>"))
         Print("Sell error: ", GetLastError());
   }
}

//+------------------------------------------------------------------+
//| Manage Open Position                                             |
//+------------------------------------------------------------------+
void ManageOpenPosition()
{
   if(!InpUseTrailingStop) return;
   
   double atr[];
   ArrayResize(atr, 1);
   ArraySetAsSeries(atr, true);
   if(CopyBuffer(g_hATR, 0, 0, 1, atr) < 1 || atr[0] <= 0) return;
   double trailDist = atr[0] * InpTrailMultiplier;
   int digits = (int)SymbolInfoInteger(Symbol(), SYMBOL_DIGITS);

   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if(PositionGetSymbol(i) != Symbol()) continue;
      if(PositionGetInteger(POSITION_MAGIC) != InpMagicNumber) continue;

      double currentSL = PositionGetDouble(POSITION_SL);
      double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
      ulong  ticket    = PositionGetInteger(POSITION_TICKET);

      if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY)
      {
         double newSL = NormalizeDouble(SymbolInfoDouble(Symbol(), SYMBOL_BID) - trailDist, digits);
         if(newSL > currentSL && newSL > openPrice)
            g_trade.PositionModify(ticket, newSL, PositionGetDouble(POSITION_TP));
      }
      else
      {
         double newSL = NormalizeDouble(SymbolInfoDouble(Symbol(), SYMBOL_ASK) + trailDist, digits);
         if((newSL < currentSL || currentSL == 0) && newSL < openPrice)
            g_trade.PositionModify(ticket, newSL, PositionGetDouble(POSITION_TP));
      }
   }
}

//--- Helper Modules logic
<<stats_logic>>
<<dashboard_logic>>
<<news_logic>>
<<global_limits_logic>>
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
        parameters = self._coerce_params(parameters)
        
        strategy_type = str(strategy.get('type') or 'trend').lower()
        
        # Default parameter stabilization
        # Default parameter stabilization - Use consistent camelCase
        if strategy_type == 'trend':
            parameters.setdefault("fastEMA", 9)
            parameters.setdefault("slowEMA", 21)
        elif strategy_type == 'reversal':
            parameters.setdefault("rsiPeriod", 14)
            parameters.setdefault("oversold", 30)
            parameters.setdefault("overbought", 70)
        elif strategy_type == 'mean_reversion':
            parameters.setdefault("period", 20)
            parameters.setdefault("std", 2.0)
        elif strategy_type in ['donchian', 'breakout']:
            parameters.setdefault("donchianPeriod", 20)
            
        inputs_str = self._generate_inputs(parameters, version)
        
        # Gerar componentes de lógica (pode ser dict para MQL5)
        logic_components = self._generate_signal_logic(strategy_type, version)
        
        if isinstance(logic_components, dict):
            signal_logic = logic_components.get('logic', '')
            global_vars = logic_components.get('global_vars', '')
            init_logic = logic_components.get('init_logic', '')
            deinit_logic = logic_components.get('deinit_logic', '')
        else:
            signal_logic = logic_components
            global_vars = ''
            init_logic = ''
            deinit_logic = ''
        
        indicators = strategy.get('indicators') or []
        name = str(strategy.get('name') or 'CustomStrategy').replace(' ', '_')
        timestamp = str(pd.Timestamp.now())
        indicators_str = ', '.join(str(i) for i in indicators)
        
        output = template.replace('<<name>>', name)
        output = output.replace('<<timestamp>>', timestamp)
        output = output.replace('<<type>>', strategy_type)
        output = output.replace('<<indicators>>', indicators_str)
        output = output.replace('<<inputs>>', inputs_str)
        output = output.replace('<<signal_logic>>', signal_logic)
        
        if version == 'mql5':
            output = output.replace('<<global_vars>>', global_vars)
            output = output.replace('<<init_logic>>', init_logic)
            output = output.replace('<<deinit_logic>>', deinit_logic)
            
            # Assembly of new modules
            stats = self._get_stats_module()
            dash = self._get_dashboard_module()
            news = self._get_news_module()
            glim = self._get_global_limits_module()
            
            output = output.replace('<<stats_vars>>', stats['vars'])
            output = output.replace('<<stats_logic>>', stats['logic'])
            output = output.replace('<<dashboard_vars>>', dash['vars'])
            output = output.replace('<<dashboard_logic>>', dash['logic'])
            output = output.replace('<<news_vars>>', news['vars'])
            output = output.replace('<<news_logic>>', news['logic'])
            output = output.replace('<<global_limits_vars>>', glim['vars'])
            output = output.replace('<<global_limits_logic>>', glim['logic'])
        else:
            # For MQL4, we might want to clear these or handle them if we add MQL4 support for them later
            for tag in ['stats', 'dashboard', 'news', 'global_limits']:
                output = output.replace(f'<<{tag}_vars>>', '')
                output = output.replace(f'<<{tag}_logic>>', '')
        
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
        lines.append('input int      InpATRPeriod = 14;       // ATR Period')
        lines.append(f'input double   InpSLMultiplier = {parameters.get("slMultiplier", 1.5)};     // SL = ATR x Multiplier')
        lines.append(f'input double   InpTPMultiplier = {parameters.get("tpMultiplier", 2.0)};     // TP = ATR x Multiplier')
        lines.append('input int      InpMaxSpread = 30;       // Max Spread (points)')
        lines.append('input ulong    InpMagicNumber = 12345;  // Magic Number')
        lines.append('input bool     InpUseTrailingStop = true; // Use Trailing Stop')
        lines.append(f'input double   InpTrailMultiplier = {parameters.get("trailMultiplier", 1.0)}; // Trail = ATR x Multiplier')
        
        if version == 'mql5':
            lines.append('')
            lines.append('input group "=== News Filter ==="')
            lines.append('input bool     InpUseNewsFilter = true; // Use News Filter')
            lines.append('input int      InpNewsBefore = 30;      // Mins Before News')
            lines.append('input int      InpNewsAfter = 15;       // Mins After News')
            
            lines.append('')
            lines.append('input group "=== Account Protection ==="')
            lines.append('input double   InpGlobalSL = 0;         // Global SL $ (0=off)')
            lines.append('input double   InpGlobalTP = 0;         // Global TP $ (0=off)')
            lines.append('input double   InpMaxDD = 20.0;         // Max Drawdown % (0=off)')

        lines.append('')
        if version == 'mql5':
            lines.append('input group "=== Strategy Parameters ==="')
        
        # Parâmetros da estratégia
        for name, value in parameters.items():
            if name in ["stopLoss", "takeProfit", "slMultiplier", "tpMultiplier", "trailMultiplier"]:
                continue
            
            # Garantir que o nome tenha o prefixo Inp mas não duplicado
            mql_name = name
            if not name.lower().startswith('inp'):
                mql_name = 'Inp' + name[0].upper() + name[1:]
            
            if isinstance(value, int):
                lines.append(f'input int      {mql_name} = {value};        // {name}')
            elif isinstance(value, float):
                lines.append(f'input double   {mql_name} = {value};        // {name}')
            elif isinstance(value, bool):
                lines.append(f'input bool     {mql_name} = {"true" if value else "false"};        // {name}')
        
        return '\n'.join(lines)

    # ──────────────────────────────────────────────────────────────────
    #  MQL5 Helper Modules
    # ──────────────────────────────────────────────────────────────────

    def _get_stats_module(self) -> Dict[str, str]:
        return {
            'vars': '''int    g_totalTrades = 0;
int    g_winTrades   = 0;
int    g_lossTrades  = 0;
double g_totalProfit = 0;
double g_totalLoss   = 0;
double g_peakBalance  = 0;
double g_currentDD    = 0;
double g_maxDrawdown  = 0;''',
            'logic': '''void LoadHistoryStats()
{
   g_totalTrades = 0; g_winTrades = 0; g_lossTrades = 0; g_totalProfit = 0; g_totalLoss = 0;
   if(!HistorySelect(0, TimeCurrent())) return;
   int total = HistoryDealsTotal();
   for(int i = 0; i < total; i++)
   {
      ulong ticket = HistoryDealGetTicket(i);
      if(ticket == 0 || HistoryDealGetInteger(ticket, DEAL_MAGIC) != InpMagicNumber || HistoryDealGetString(ticket, DEAL_SYMBOL) != Symbol()) continue;
      long entry = HistoryDealGetInteger(ticket, DEAL_ENTRY);
      if(entry != DEAL_ENTRY_OUT && entry != DEAL_ENTRY_INOUT) continue;
      double dealPL = HistoryDealGetDouble(ticket, DEAL_PROFIT) + HistoryDealGetDouble(ticket, DEAL_SWAP) + HistoryDealGetDouble(ticket, DEAL_COMMISSION);
      g_totalTrades++;
      if(dealPL >= 0) { g_winTrades++; g_totalProfit += dealPL; }
      else { g_lossTrades++; g_totalLoss += MathAbs(dealPL); }
   }
}

void UpdateStats()
{
   LoadHistoryStats();
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   if(g_peakBalance == 0) g_peakBalance = AccountInfoDouble(ACCOUNT_BALANCE);
   if(equity > g_peakBalance) g_peakBalance = equity;
   g_currentDD = (g_peakBalance > 0) ? (g_peakBalance - equity) / g_peakBalance * 100.0 : 0;
   if(g_currentDD > g_maxDrawdown) g_maxDrawdown = g_currentDD;
}'''
        }

    def _get_dashboard_module(self) -> Dict[str, str]:
        return {
            'vars': 'string g_panelPrefix = "MYPANEL_";',
            'logic': '''void CreatePanel()
{
   int panelX = 10, panelY = 30, panelW = 280, panelH = 300;
   CreateRect(g_panelPrefix + "BG", panelX, panelY, panelW, panelH, C'15,15,25', C'40,120,200');
   CreateRect(g_panelPrefix + "Header", panelX, panelY, panelW, 42, C'20,80,180', C'20,80,180');
   CreateLabel(g_panelPrefix + "Title", panelX + 12, panelY + 8, "TRADE STRATEGIST", 12, "Consolas", clrWhite, true);
   CreateLabel(g_panelPrefix + "Version", panelX + 12, panelY + 26, "v1.0 | " + Symbol() + " " + EnumToString(Period()), 8, "Consolas", C'140,180,255', false);
   int y = panelY + 52;
   CreateLabel(g_panelPrefix + "SecPerf", panelX + 12, y, "── PERFORMANCE ──", 8, "Consolas", C'80,160,255', true);
   y += 18;
   CreateLabel(g_panelPrefix + "lProfit",  panelX + 12,  y, "Profit: $0.00", 9, "Consolas", C'0,200,120', false);
   CreateLabel(g_panelPrefix + "lWinRate", panelX + 160, y, "WR: 0%", 9, "Consolas", C'180,200,220', false);
   y += 16;
   CreateLabel(g_panelPrefix + "lTrades", panelX + 12, y, "Trades: 0 (W:0 L:0)", 9, "Consolas", C'180,200,220', false);
   y += 16;
   CreateLabel(g_panelPrefix + "lDD",     panelX + 12, y, "DD: 0.0% | Max: 0.0%", 9, "Consolas", C'180,200,220', false);
   y += 16;
   CreateLabel(g_panelPrefix + "lEquity", panelX + 12, y, "Equity: $0.00", 9, "Consolas", C'180,200,220', false);
   ChartRedraw();
}

void UpdatePanel()
{
   double netProfit = g_totalProfit - g_totalLoss;
   color profitColor = (netProfit >= 0) ? C'0,220,120' : C'255,60,60';
   UpdateLabel(g_panelPrefix + "lProfit", "Profit: $" + DoubleToString(netProfit, 2), profitColor);
   double winRate = (g_totalTrades > 0) ? (double)g_winTrades / g_totalTrades * 100.0 : 0;
   UpdateLabel(g_panelPrefix + "lWinRate", "WR: " + DoubleToString(winRate, 1) + "%");
   UpdateLabel(g_panelPrefix + "lTrades", "Trades: " + IntegerToString(g_totalTrades) + " (W:" + IntegerToString(g_winTrades) + " L:" + IntegerToString(g_lossTrades) + ")");
   color ddColor = (g_currentDD > 10) ? C'255,60,60' : C'180,200,220';
   UpdateLabel(g_panelPrefix + "lDD", "DD: " + DoubleToString(g_currentDD, 1) + "% | Max: " + DoubleToString(g_maxDrawdown, 1) + "%", ddColor);
   UpdatePanelPrices();
}

void UpdatePanelPrices()
{
   UpdateLabel(g_panelPrefix + "lEquity", "Eq: $" + DoubleToString(AccountInfoDouble(ACCOUNT_EQUITY), 2));
   ChartRedraw();
}

void CreateRect(string name, int x, int y, int w, int h, color bg, color border)
{
   ObjectDelete(0, name);
   ObjectCreate(0, name, OBJ_RECTANGLE_LABEL, 0, 0, 0);
   ObjectSetInteger(0, name, OBJPROP_XDISTANCE, x); ObjectSetInteger(0, name, OBJPROP_YDISTANCE, y);
   ObjectSetInteger(0, name, OBJPROP_XSIZE, w); ObjectSetInteger(0, name, OBJPROP_YSIZE, h);
   ObjectSetInteger(0, name, OBJPROP_BGCOLOR, bg); ObjectSetInteger(0, name, OBJPROP_BORDER_COLOR, border);
   ObjectSetInteger(0, name, OBJPROP_BORDER_TYPE, BORDER_FLAT); ObjectSetInteger(0, name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
   ObjectSetInteger(0, name, OBJPROP_BACK, false); ObjectSetInteger(0, name, OBJPROP_SELECTABLE, false);
}

void CreateLabel(string name, int x, int y, string text, int size, string font, color clr, bool bold)
{
   ObjectDelete(0, name);
   ObjectCreate(0, name, OBJ_LABEL, 0, 0, 0);
   ObjectSetInteger(0, name, OBJPROP_XDISTANCE, x); ObjectSetInteger(0, name, OBJPROP_YDISTANCE, y);
   ObjectSetString(0, name, OBJPROP_TEXT, text); ObjectSetInteger(0, name, OBJPROP_FONTSIZE, size);
   ObjectSetString(0, name, OBJPROP_FONT, bold ? font + " Bold" : font);
   ObjectSetInteger(0, name, OBJPROP_COLOR, clr); ObjectSetInteger(0, name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
   ObjectSetInteger(0, name, OBJPROP_SELECTABLE, false);
}

void UpdateLabel(string name, string text, color clr = 0)
{
   if(ObjectFind(0, name) < 0) return;
   ObjectSetString(0, name, OBJPROP_TEXT, text);
   if(clr != 0) ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
}

void DeletePanel()
{
   for(int i = ObjectsTotal(0) - 1; i >= 0; i--)
   {
      string name = ObjectName(0, i);
      if(StringFind(name, g_panelPrefix) == 0) ObjectDelete(0, name);
   }
}'''
        }

    def _get_news_module(self) -> Dict[str, str]:
        return {
            'vars': '''bool     g_newsActive = false;
datetime g_nextNewsTime = 0;
string   g_nextNewsName = "";
datetime g_lastNewsCheck = 0;''',
            'logic': '''void CheckNewsCalendar()
{
   datetime now = TimeCurrent();
   if(now - g_lastNewsCheck < 60) return;
   g_lastNewsCheck = now;
   g_newsActive = false; g_nextNewsTime = 0; g_nextNewsName = "";
   datetime from = now - InpNewsAfter * 60;
   datetime to = now + (InpNewsBefore + 60) * 60;
   MqlCalendarValue values[];
   int count = CalendarValueHistory(values, from, to);
   if(count <= 0) return;
   for(int i = 0; i < count; i++) {
      MqlCalendarEvent event;
      if(!CalendarEventById(values[i].event_id, event) || event.importance != CALENDAR_IMPORTANCE_HIGH) continue;
      MqlCalendarCountry country;
      if(!CalendarCountryById(event.country_id, country) || StringFind(Symbol(), country.currency) < 0) continue;
      datetime eventTime = values[i].time;
      if(now >= eventTime - InpNewsBefore * 60 && now <= eventTime + InpNewsAfter * 60) {
         g_newsActive = true; g_nextNewsTime = eventTime; g_nextNewsName = event.name; return;
      }
   }
}'''
        }

    def _get_global_limits_module(self) -> Dict[str, str]:
        return {
            'vars': '',
            'logic': '''void CheckGlobalLimits()
{
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double floatingPL = equity - balance;
   if(InpGlobalSL > 0 && floatingPL <= -InpGlobalSL) { Print("GLOBAL SL HIT"); CloseAllPositions(); return; }
   if(InpGlobalTP > 0 && floatingPL >= InpGlobalTP) { Print("GLOBAL TP HIT"); CloseAllPositions(); return; }
   if(InpMaxDD > 0) {
      if(equity > g_peakBalance) g_peakBalance = equity;
      double dd = (g_peakBalance - equity) / g_peakBalance * 100.0;
      if(dd >= InpMaxDD) { Print("MAX DD HIT"); CloseAllPositions(); }
   }
}

void CloseAllPositions()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--) {
      if(PositionGetSymbol(i) == Symbol() && PositionGetInteger(POSITION_MAGIC) == InpMagicNumber)
         g_trade.PositionClose(PositionGetInteger(POSITION_TICKET));
   }
}'''
        }
    
    def _generate_signal_logic(self, strategy_type: str, version: str) -> Any:
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
            res = {
                'global_vars': '',
                'init_logic': '',
                'deinit_logic': '',
                'logic': ''
            }
            
            if strategy_type == 'trend':
                res['global_vars'] = 'int g_hFastMA = INVALID_HANDLE;\nint g_hSlowMA = INVALID_HANDLE;'
                res['init_logic'] = '   g_hFastMA = iMA(_Symbol, _Period, InpFastEMA, 0, MODE_EMA, PRICE_CLOSE);\n   g_hSlowMA = iMA(_Symbol, _Period, InpSlowEMA, 0, MODE_EMA, PRICE_CLOSE);\n   if(g_hFastMA == INVALID_HANDLE || g_hSlowMA == INVALID_HANDLE) return INIT_FAILED;'
                res['deinit_logic'] = '   IndicatorRelease(g_hFastMA);\n   IndicatorRelease(g_hSlowMA);'
                res['logic'] = '''   double f[], s[];
   ArrayResize(f, 2);
   ArrayResize(s, 2);
   ArraySetAsSeries(f, true);
   ArraySetAsSeries(s, true);
   
   if(CopyBuffer(g_hFastMA, 0, 0, 2, f) < 2 || CopyBuffer(g_hSlowMA, 0, 0, 2, s) < 2) return 0;
   
   // With ArraySetAsSeries: [0] = current, [1] = previous
   if(f[0] > s[0] && f[1] <= s[1]) return 1;
   if(f[0] < s[0] && f[1] >= s[1]) return -1;
   return 0;'''
            
            elif strategy_type == 'reversal':
                res['global_vars'] = 'int g_hRsi = INVALID_HANDLE;'
                res['init_logic'] = '   g_hRsi = iRSI(_Symbol, _Period, InpRsiPeriod, PRICE_CLOSE);\n   if(g_hRsi == INVALID_HANDLE) return INIT_FAILED;'
                res['deinit_logic'] = '   IndicatorRelease(g_hRsi);'
                res['logic'] = '''   double r[];
   ArrayResize(r, 2);
   ArraySetAsSeries(r, true);
   
   if(CopyBuffer(g_hRsi, 0, 0, 2, r) < 2) return 0;
   
   if(r[0] < InpOversold && r[1] >= InpOversold) return 1;
   if(r[0] > InpOverbought && r[1] <= InpOverbought) return -1;
   return 0;'''
            
            elif strategy_type == 'mean_reversion':
                res['global_vars'] = 'int g_hBands = INVALID_HANDLE;'
                res['init_logic'] = '   g_hBands = iBands(_Symbol, _Period, Inpperiod, 0, Inpstd, PRICE_CLOSE);\n   if(g_hBands == INVALID_HANDLE) return INIT_FAILED;'
                res['deinit_logic'] = '   IndicatorRelease(g_hBands);'
                res['logic'] = '''   double upper[], lower[], close[];
   ArrayResize(upper, 1);
   ArrayResize(lower, 1);
   ArrayResize(close, 1);
   if(CopyBuffer(g_hBands, 1, 0, 1, upper) < 1 || CopyBuffer(g_hBands, 2, 0, 1, lower) < 1) return 0;
   CopyClose(_Symbol, _Period, 0, 1, close);
   
   if(close[0] < lower[0]) return 1;
   if(close[0] > upper[0]) return -1;
   return 0;'''
            
            elif strategy_type in ['donchian', 'breakout']:
                res['logic'] = '''   double high[], low[], close[];
   ArrayResize(high, 1);
   ArrayResize(low, 1);
   ArrayResize(close, 1);
   int highest_idx = iHighest(_Symbol, _Period, MODE_HIGH, InpDonchianPeriod, 1);
   int lowest_idx = iLowest(_Symbol, _Period, MODE_LOW, InpDonchianPeriod, 1);
   
   CopyHigh(_Symbol, _Period, highest_idx, 1, high);
   CopyLow(_Symbol, _Period, lowest_idx, 1, low);
   CopyClose(_Symbol, _Period, 0, 1, close);
   
   if(close[0] > high[0]) return 1;
   if(close[0] < low[0]) return -1;
   return 0;'''

            elif strategy_type == 'scalping':
                res['global_vars'] = 'int g_hFast = INVALID_HANDLE;\nint g_hSlow = INVALID_HANDLE;\nint g_hRsi = INVALID_HANDLE;'
                res['init_logic'] = '   g_hFast = iMA(_Symbol, _Period, 5, 0, MODE_EMA, PRICE_CLOSE);\n   g_hSlow = iMA(_Symbol, _Period, 13, 0, MODE_EMA, PRICE_CLOSE);\n   g_hRsi = iRSI(_Symbol, _Period, 7, PRICE_CLOSE);\n   if(g_hFast == INVALID_HANDLE || g_hSlow == INVALID_HANDLE || g_hRsi == INVALID_HANDLE) return INIT_FAILED;'
                res['deinit_logic'] = '   IndicatorRelease(g_hFast);\n   IndicatorRelease(g_hSlow);\n   IndicatorRelease(g_hRsi);'
                res['logic'] = '''   double f[], s[], r[];
   ArrayResize(f, 1);
   ArrayResize(s, 1);
   ArrayResize(r, 1);
   if(CopyBuffer(g_hFast, 0, 0, 1, f) < 1 || CopyBuffer(g_hSlow, 0, 0, 1, s) < 1 || CopyBuffer(g_hRsi, 0, 0, 1, r) < 1) return 0;
   
   if(f[0] > s[0] && r[0] < 70) return 1;
   if(f[0] < s[0] && r[0] > 30) return -1;
   return 0;'''

            else:
                res['global_vars'] = 'int g_hFastMA = INVALID_HANDLE;\nint g_hSlowMA = INVALID_HANDLE;'
                res['init_logic'] = '   g_hFastMA = iMA(_Symbol, _Period, 9, 0, MODE_EMA, PRICE_CLOSE);\n   g_hSlowMA = iMA(_Symbol, _Period, 21, 0, MODE_EMA, PRICE_CLOSE);\n   if(g_hFastMA == INVALID_HANDLE || g_hSlowMA == INVALID_HANDLE) return INIT_FAILED;'
                res['deinit_logic'] = '   IndicatorRelease(g_hFastMA);\n   IndicatorRelease(g_hSlowMA);'
                res['logic'] = '''   double f[], s[];
   ArrayResize(f, 1);
   ArrayResize(s, 1);
   if(CopyBuffer(g_hFastMA, 0, 0, 1, f) < 1 || CopyBuffer(g_hSlowMA, 0, 0, 1, s) < 1) return 0;
   
   if(f[0] > s[0]) return 1;
   if(f[0] < s[0]) return -1;
   return 0;'''
            
            return res
    
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
