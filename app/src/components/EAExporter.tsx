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
    // Note: The professional template is primarily MQL5. For MQL4, we'll use a simplified version for now
    // but the request was specifically for the professional MQL5 version provided.
    if (ver === 'mql4') {
      return `//+------------------------------------------------------------------+
//|                                      ${strat.name.replace(/\s+/g, '_')}.mq4
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
input int      InpStopLoss = ${strat.parameters.stopLoss || 50};        // Stop Loss (pips)
input int      InpTakeProfit = ${strat.parameters.takeProfit || 100};     // Take Profit (pips)
input int      InpMagicNumber = ${Math.floor(Math.random() * 90000) + 10000};  // Magic Number

input group "=== Strategy Parameters ==="
${Object.entries(strat.parameters)
          .filter(([key]) => key !== 'stopLoss' && key !== 'takeProfit')
          .map(([key, value]) => {
            const type = key.toLowerCase().includes('std') ? 'double' : 'int';
            const name = `Inp${key.charAt(0).toUpperCase() + key.slice(1)}`;
            return `input ${type.padEnd(8)} ${name} = ${value}${type === 'double' && String(value).indexOf('.') === -1 ? '.0' : ''};        // ${key}`;
          }).join('\n')}

input group "=== Risk Management ==="
input double   InpMaxRiskPercent = 2.0;  // Max Risk per Trade (%)

void OnTick() {
    // Simplified MQL4 Placeholder
}
`;
    }

    // Professional MQL5 Template
    return `//+------------------------------------------------------------------+
//|                                   ${strat.name.replace(/\s+/g, '_')}.mq5
//|                        TradeStrategist Auto-Generated EA         |
//|                        With On-Chart Panel & Risk Management     |
//+------------------------------------------------------------------+
#property copyright "TradeStrategist"
#property link      "https://tradestrategist.com"
#property version   "2.00"
#property strict
#property description "${strat.name} - Otimizado por TradeStrategist"

//+------------------------------------------------------------------+
//| Includes                                                         |
//+------------------------------------------------------------------+
#include <Trade\\Trade.mqh>
#include <Trade\\PositionInfo.mqh>
#include <Trade\\SymbolInfo.mqh>

//--- Input Parameters
input group "══════ Parâmetros de Negociação ══════"
input double   InpLotSize        = 0.1;     // Tamanho do Lote
input int      InpStopLoss       = ${strat.parameters.stopLoss || 50};      // Stop Loss (pontos)
input int      InpTakeProfit     = ${strat.parameters.takeProfit || 100};     // Take Profit (pontos)
input int      InpMagicNumber    = ${Math.floor(Math.random() * 90000) + 10000};   // Número Mágico

input group "══════ Parâmetros da Estratégia ══════"
${Object.entries(strat.parameters)
        .filter(([key]) => key !== 'stopLoss' && key !== 'takeProfit')
        .map(([key, value]) => {
          const type = key.toLowerCase().includes('std') || key.toLowerCase().includes('level') || key.toLowerCase().includes('deviation') ? 'double' : 'int';
          const name = `Inp${key.charAt(0).toUpperCase() + key.slice(1)}`;
          return `input ${type.padEnd(8)} ${name} = ${value}${type === 'double' && String(value).indexOf('.') === -1 ? '.0' : ''};        // ${key}`;
        }).join('\n')}

input group "══════ Gestão de Risco ══════"
input double   InpMaxRiskPercent = 2.0;     // Risco Máximo por Trade (%)
input int      InpMaxSpread      = 30;      // Spread Máximo (pontos)
input bool     InpUseTrailingStop= true;    // Usar Trailing Stop
input int      InpTrailingStart  = 30;      // Trailing Start (pontos)
input int      InpTrailingStep   = 10;      // Trailing Step (pontos)
input bool     InpUseBreakeven   = true;    // Usar Break Even
input int      InpBreakevenStart = 20;      // Break Even Ativação (pontos)
input int      InpBreakevenProfit= 5;       // Break Even Lucro (pontos)

input group "══════ Painel ══════"
input int      InpPanelX         = 10;      // Posição X do Painel
input int      InpPanelY         = 30;      // Posição Y do Painel
input int      InpPanelWidth     = 280;     // Largura do Painel
input color    InpPanelBG        = C'20,20,30';       // Cor de Fundo
input color    InpPanelBorder    = C'60,60,80';       // Cor da Borda
input color    InpPanelHeader    = C'30,35,55';       // Cor do Cabeçalho
input color    InpTextColor      = C'200,200,220';    // Cor do Texto
input color    InpAccentColor    = C'0,150,255';      // Cor de Destaque
input color    InpProfitColor    = C'0,200,100';      // Cor de Lucro
input color    InpLossColor      = C'220,50,50';      // Cor de Prejuízo
input int      InpFontSize       = 9;                 // Tamanho da Fonte

//--- Objetos de trade
CTrade         m_trade;
CPositionInfo  m_position;
CSymbolInfo    m_symbol;

//--- Handles dos indicadores
int            g_handle1 = INVALID_HANDLE;
int            g_handle2 = INVALID_HANDLE;

//--- Buffers
double         g_buffer1[];
double         g_buffer2[];
double         g_buffer3[];

//--- Variáveis globais
datetime       g_lastBarTime     = 0;
int            g_totalBuys       = 0;
int            g_totalSells      = 0;
int            g_totalTrades     = 0;
int            g_winTrades       = 0;
int            g_lossTrades      = 0;
double         g_totalProfit     = 0;
double         g_currentProfit   = 0;
double         g_maxDrawdown     = 0;
double         g_peakBalance     = 0;
string         g_lastSignal      = "Aguardando...";
datetime       g_lastSignalTime  = 0;
bool           g_panelMinimized  = false;

//--- Prefixo dos objetos
#define PANEL_PREFIX  "MR_PANEL_"

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   //--- Configurar trade
   m_trade.SetExpertMagicNumber(InpMagicNumber);
   m_trade.SetDeviationInPoints(10);
   m_trade.SetTypeFilling(ORDER_FILLING_FOK);
   
   //--- Inicializar símbolo
   if(!m_symbol.Name(Symbol()))
   {
      Print("Erro ao inicializar símbolo!");
      return(INIT_FAILED);
   }
   
   //--- Inicializar Indicadores baseado no tipo
${strat.type === 'trend' ? `
   g_handle1 = iMA(Symbol(), PERIOD_CURRENT, InpFastEMA, 0, MODE_EMA, PRICE_CLOSE);
   g_handle2 = iMA(Symbol(), PERIOD_CURRENT, InpSlowEMA, 0, MODE_EMA, PRICE_CLOSE);
` : strat.type === 'reversal' || strat.type === 'scalping' ? `
   g_handle1 = iRSI(Symbol(), PERIOD_CURRENT, InpRsiPeriod, PRICE_CLOSE);
   ${strat.type === 'scalping' ? `
   g_handle2 = iMA(Symbol(), PERIOD_CURRENT, InpFastEMA, 0, MODE_EMA, PRICE_CLOSE);
   ` : ''}
` : strat.type === 'breakout' || strat.type === 'mean_reversion' ? `
   g_handle1 = iBands(Symbol(), PERIOD_CURRENT, ${strat.type === 'breakout' ? 'InpBbPeriod' : 'InpPeriod'}, 0, ${strat.type === 'breakout' ? 'InpBbStd' : 'InpStd'}, PRICE_CLOSE);
` : strat.type === 'donchian' ? `
   // Donchian use simple MA or custom iDonchian. Simplified for base iMA
   g_handle1 = iMA(Symbol(), PERIOD_CURRENT, InpPeriod, 0, MODE_SMA, PRICE_CLOSE);
` : `
   g_handle1 = iMA(Symbol(), PERIOD_CURRENT, 9, 0, MODE_EMA, PRICE_CLOSE);
`}

   if(g_handle1 == INVALID_HANDLE)
   {
      Print("Erro ao criar indicadores! Erro: ", GetLastError());
      return(INIT_FAILED);
   }
   
   //--- Configurar buffers como séries
   ArraySetAsSeries(g_buffer1, true);
   ArraySetAsSeries(g_buffer2, true);
   ArraySetAsSeries(g_buffer3, true);
   
   //--- Inicializar pico de saldo
   g_peakBalance = AccountInfoDouble(ACCOUNT_BALANCE);
   
   //--- Criar painel
   CreatePanel();
   
   //--- Habilitar eventos de gráfico
   ChartSetInteger(0, CHART_EVENT_OBJECT_CREATE, true);
   ChartSetInteger(0, CHART_EVENT_OBJECT_DELETE, true);
   
   Print("══════════════════════════════════════════");
   Print("  ${strat.name} EA Profissional Inicializado");
   Print("  Estratégia: ${strat.type}");
   Print("══════════════════════════════════════════");
   
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   if(g_handle1 != INVALID_HANDLE) IndicatorRelease(g_handle1);
   if(g_handle2 != INVALID_HANDLE) IndicatorRelease(g_handle2);
   ObjectsDeleteAll(0, PANEL_PREFIX);
   Print("${strat.name} EA desativado. Razão: ", reason);
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   m_symbol.RefreshRates();
   
   // Copiar indicadores
   CopyBuffer(g_handle1, 0, 0, 3, g_buffer1);
   if(g_handle2 != INVALID_HANDLE) CopyBuffer(g_handle2, 0, 0, 3, g_buffer2);
   
   // No breakout/mean_reversion precisamos de upper/lower
   if(StringFind("${strat.type}", "breakout") >= 0 || StringFind("${strat.type}", "mean_reversion") >= 0) {
      CopyBuffer(g_handle1, 1, 0, 3, g_buffer2); // Upper
      CopyBuffer(g_handle1, 2, 0, 3, g_buffer3); // Lower
   }

   CalculateCurrentProfit();
   
   double currentBalance = AccountInfoDouble(ACCOUNT_BALANCE);
   if(currentBalance > g_peakBalance) g_peakBalance = currentBalance;
   double dd = g_peakBalance - currentBalance;
   if(dd > g_maxDrawdown) g_maxDrawdown = dd;
   
   UpdatePanel();
   
   datetime currentBarTime = iTime(Symbol(), PERIOD_CURRENT, 0);
   if(currentBarTime == g_lastBarTime) return;
   g_lastBarTime = currentBarTime;
   
   if(m_symbol.Spread() > InpMaxSpread) {
      g_lastSignal = "Spread alto!";
      return;
   }
   
   if(HasOpenPosition()) {
      ManageOpenPosition();
      return;
   }
   
   int signal = CheckEntrySignal();
   
   if(signal > 0) {
      if(OpenBuyOrder()) {
         g_totalBuys++; g_totalTrades++;
         g_lastSignal = "COMPRA";
         g_lastSignalTime = TimeCurrent();
      }
   }
   else if(signal < 0) {
      if(OpenSellOrder()) {
         g_totalSells++; g_totalTrades++;
         g_lastSignal = "VENDA";
         g_lastSignalTime = TimeCurrent();
      }
   }
}

//+------------------------------------------------------------------+
//| Chart event handler                                              |
//+------------------------------------------------------------------+
void OnChartEvent(const int id, const long &lparam, const double &dparam, const string &sparam)
{
   if(id == CHARTEVENT_OBJECT_CLICK)
   {
      if(sparam == PANEL_PREFIX + "BTN_MINIMIZE")
      {
         g_panelMinimized = !g_panelMinimized;
         ObjectsDeleteAll(0, PANEL_PREFIX);
         CreatePanel();
         UpdatePanel();
         ChartRedraw(0);
      }
      else if(sparam == PANEL_PREFIX + "BTN_CLOSEALL")
      {
         CloseAllPositions();
      }
   }
}

//+------------------------------------------------------------------+
//| OnTrade - Atualizar estatísticas                                 |
//+------------------------------------------------------------------+
void OnTrade()
{
   HistorySelect(TimeCurrent() - 60, TimeCurrent());
   int totalDeals = HistoryDealsTotal();
   for(int i = totalDeals - 1; i >= 0; i--)
   {
      ulong ticket = HistoryDealGetTicket(i);
      if(HistoryDealGetInteger(ticket, DEAL_MAGIC) != InpMagicNumber) continue;
      if(HistoryDealGetInteger(ticket, DEAL_ENTRY) != DEAL_ENTRY_OUT) continue;
      double profit = HistoryDealGetDouble(ticket, DEAL_PROFIT) + HistoryDealGetDouble(ticket, DEAL_SWAP) + HistoryDealGetDouble(ticket, DEAL_COMMISSION);
      g_totalProfit += profit;
      if(profit >= 0) g_winTrades++; else g_lossTrades++;
   }
}

bool HasOpenPosition() {
   for(int i = PositionsTotal() - 1; i >= 0; i--) {
      if(m_position.SelectByIndex(i)) {
         if(m_position.Symbol() == Symbol() && m_position.Magic() == InpMagicNumber) return true;
      }
   }
   return false;
}

int CheckEntrySignal() {
${strat.type === 'trend' ? `
   // EMA Crossover
   if(g_buffer1[1] > g_buffer2[1] && g_buffer1[2] <= g_buffer2[2]) return 1;
   if(g_buffer1[1] < g_buffer2[1] && g_buffer1[2] >= g_buffer2[2]) return -1;
` : strat.type === 'reversal' ? `
   // RSI Reversal
   if(g_buffer1[1] < InpOversold) return 1;
   if(g_buffer1[1] > InpOverbought) return -1;
` : strat.type === 'breakout' ? `
   // BB Breakout
   double close = iClose(Symbol(), PERIOD_CURRENT, 1);
   if(close > g_buffer2[1]) return 1;
   if(close < g_buffer3[1]) return -1;
` : strat.type === 'scalping' ? `
   // EMA + RSI Scalper
   if(g_buffer2[1] > g_buffer1[1] && g_buffer1[1] > 50) return 1;
   if(g_buffer2[1] < g_buffer1[1] && g_buffer1[1] < 50) return -1;
` : strat.type === 'mean_reversion' ? `
   // BB %B Mean Reversion
   double close = iClose(Symbol(), PERIOD_CURRENT, 1);
   double pctB = (close - g_buffer3[1]) / (g_buffer2[1] - g_buffer3[1] + 1e-9);
   if(pctB < InpOversoldLevel) return 1;
   if(pctB > InpOverboughtLevel) return -1;
` : `
   return 0;
`}
   return 0;
}

bool OpenBuyOrder() {
   m_symbol.RefreshRates();
   double price = m_symbol.Ask();
   double sl = price - InpStopLoss * m_symbol.Point();
   double tp = price + InpTakeProfit * m_symbol.Point();
   double lots = CalculateLotSize(InpStopLoss);
   sl = NormalizeDouble(sl, m_symbol.Digits());
   tp = NormalizeDouble(tp, m_symbol.Digits());
   return m_trade.Buy(lots, Symbol(), price, sl, tp, "${strat.type} BUY");
}

bool OpenSellOrder() {
   m_symbol.RefreshRates();
   double price = m_symbol.Bid();
   double sl = price + InpStopLoss * m_symbol.Point();
   double tp = price - InpTakeProfit * m_symbol.Point();
   double lots = CalculateLotSize(InpStopLoss);
   sl = NormalizeDouble(sl, m_symbol.Digits());
   tp = NormalizeDouble(tp, m_symbol.Digits());
   return m_trade.Sell(lots, Symbol(), price, sl, tp, "${strat.type} SELL");
}

double CalculateLotSize(int slPoints) {
   if(InpMaxRiskPercent <= 0 || slPoints <= 0) return InpLotSize;
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double riskAmount = balance * InpMaxRiskPercent / 100.0;
   double tickValue = m_symbol.TickValue();
   double tickSize = m_symbol.TickSize();
   if(tickValue <= 0 || tickSize <= 0) return InpLotSize;
   double slValue = slPoints * m_symbol.Point();
   double lots = riskAmount / (slValue / tickSize * tickValue);
   double minLot = m_symbol.LotsMin();
   double maxLot = m_symbol.LotsMax();
   double lotStep = m_symbol.LotsStep();
   lots = MathFloor(lots / lotStep) * lotStep;
   lots = MathMax(lots, minLot);
   lots = MathMin(lots, maxLot);
   lots = MathMin(lots, InpLotSize);
   return NormalizeDouble(lots, 2);
}

void ManageOpenPosition() {
   for(int i = PositionsTotal() - 1; i >= 0; i--) {
      if(!m_position.SelectByIndex(i)) continue;
      if(m_position.Symbol() != Symbol() || m_position.Magic() != InpMagicNumber) continue;
      double openPrice = m_position.PriceOpen();
      double currentSL = m_position.StopLoss();
      double currentTP = m_position.TakeProfit();
      ulong ticket = m_position.Ticket();
      if(InpUseBreakeven) ApplyBreakeven(openPrice, currentSL, currentTP, ticket);
      if(InpUseTrailingStop) ApplyTrailingStop(openPrice, currentSL, currentTP, ticket);
   }
}

void ApplyBreakeven(double openPrice, double currentSL, double currentTP, ulong ticket) {
   double point = m_symbol.Point();
   if(m_position.PositionType() == POSITION_TYPE_BUY) {
      if(m_symbol.Bid() >= openPrice + InpBreakevenStart * point && currentSL < openPrice)
         m_trade.PositionModify(ticket, NormalizeDouble(openPrice + InpBreakevenProfit * point, m_symbol.Digits()), currentTP);
   } else {
      if(m_symbol.Ask() <= openPrice - InpBreakevenStart * point && (currentSL > openPrice || currentSL == 0))
         m_trade.PositionModify(ticket, NormalizeDouble(openPrice - InpBreakevenProfit * point, m_symbol.Digits()), currentTP);
   }
}

void ApplyTrailingStop(double openPrice, double currentSL, double currentTP, ulong ticket) {
   double point = m_symbol.Point();
   if(m_position.PositionType() == POSITION_TYPE_BUY) {
      if(m_symbol.Bid() >= openPrice + InpTrailingStart * point) {
         double newSL = NormalizeDouble(m_symbol.Bid() - InpStopLoss * point, m_symbol.Digits());
         if(newSL > currentSL + InpTrailingStep * point) m_trade.PositionModify(ticket, newSL, currentTP);
      }
   } else {
      if(m_symbol.Ask() <= openPrice - InpTrailingStart * point) {
         double newSL = NormalizeDouble(m_symbol.Ask() + InpStopLoss * point, m_symbol.Digits());
         if(newSL < currentSL - InpTrailingStep * point || currentSL == 0) m_trade.PositionModify(ticket, newSL, currentTP);
      }
   }
}

void CalculateCurrentProfit() {
   g_currentProfit = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--) {
      if(m_position.SelectByIndex(i) && m_position.Symbol() == Symbol() && m_position.Magic() == InpMagicNumber)
         g_currentProfit += m_position.Profit() + m_position.Swap() + m_position.Commission();
   }
}

void CloseAllPositions() {
   for(int i = PositionsTotal() - 1; i >= 0; i--) {
      if(m_position.SelectByIndex(i) && m_position.Symbol() == Symbol() && m_position.Magic() == InpMagicNumber)
         m_trade.PositionClose(m_position.Ticket());
   }
}

void CreatePanel() {
   int x = InpPanelX; int y = InpPanelY; int w = InpPanelWidth;
   if(g_panelMinimized) {
      CreatePanelRect(PANEL_PREFIX + "BG_HEADER", x, y, w, 28, InpPanelHeader, InpPanelBorder);
      CreateLabel(PANEL_PREFIX + "TITLE", x + 10, y + 6, "▶ ${strat.name}", InpAccentColor, 10, "Segoe UI Semibold");
      CreateButton(PANEL_PREFIX + "BTN_MINIMIZE", x + w - 26, y + 4, 20, 20, "□", InpTextColor, InpPanelHeader);
      return;
   }
   int panelH = 370;
   CreatePanelRect(PANEL_PREFIX + "BG_MAIN", x, y, w, panelH, InpPanelBG, InpPanelBorder);
   CreatePanelRect(PANEL_PREFIX + "BG_HEADER", x, y, w, 28, InpPanelHeader, InpPanelBorder);
   CreateLabel(PANEL_PREFIX + "TITLE", x + 10, y + 6, "◆ ${strat.name}", InpAccentColor, 10, "Segoe UI Semibold");
   CreateButton(PANEL_PREFIX + "BTN_MINIMIZE", x + w - 26, y + 4, 20, 20, "─", InpTextColor, InpPanelHeader);
   int row = y + 36; CreateLabel(PANEL_PREFIX + "SEC_ACC", x + 10, row, "━━ CONTA ━━", InpAccentColor, InpFontSize, "Segoe UI Semibold");
   row += 20; CreateLabel(PANEL_PREFIX + "L_BAL", x + 10, row, "Saldo:", InpTextColor, InpFontSize);
   CreateLabel(PANEL_PREFIX + "V_BAL", x + w - 10, row, "---", InpTextColor, InpFontSize, "Consolas", ANCHOR_RIGHT_UPPER);
   row += 18; CreateLabel(PANEL_PREFIX + "L_EQU", x + 10, row, "Patrimônio:", InpTextColor, InpFontSize);
   CreateLabel(PANEL_PREFIX + "V_EQU", x + w - 10, row, "---", InpTextColor, InpFontSize, "Consolas", ANCHOR_RIGHT_UPPER);
   row += 24; CreateLabel(PANEL_PREFIX + "SEC_STR", x + 10, row, "━━ ESTRATÉGIA ━━", InpAccentColor, InpFontSize, "Segoe UI Semibold");
   row += 20; CreateLabel(PANEL_PREFIX + "L_SIG", x + 10, row, "Sinal:", InpTextColor, InpFontSize);
   CreateLabel(PANEL_PREFIX + "V_SIG", x + w - 10, row, "Aguardando", InpTextColor, InpFontSize, "Consolas", ANCHOR_RIGHT_UPPER);
   row += 18; CreateLabel(PANEL_PREFIX + "L_PRO", x + 10, row, "Lucro:", InpTextColor, InpFontSize);
   CreateLabel(PANEL_PREFIX + "V_PRO", x + w - 10, row, "0.00", InpTextColor, InpFontSize, "Consolas", ANCHOR_RIGHT_UPPER);
   row += 50; CreateButton(PANEL_PREFIX + "BTN_CLOSEALL", x + 10, row, w - 20, 24, "✕ FECHAR TUDO", InpLossColor, C'40,20,20');
}

void UpdatePanel() {
   if(g_panelMinimized) return;
   ObjectSetString(0, PANEL_PREFIX + "V_BAL", OBJPROP_TEXT, DoubleToString(AccountInfoDouble(ACCOUNT_BALANCE), 2));
   ObjectSetString(0, PANEL_PREFIX + "V_EQU", OBJPROP_TEXT, DoubleToString(AccountInfoDouble(ACCOUNT_EQUITY), 2));
   ObjectSetString(0, PANEL_PREFIX + "V_SIG", OBJPROP_TEXT, g_lastSignal);
   ObjectSetString(0, PANEL_PREFIX + "V_PRO", OBJPROP_TEXT, DoubleToString(g_currentProfit, 2));
}

void CreatePanelRect(string name, int x, int y, int w, int h, color bg, color border) {
   ObjectCreate(0, name, OBJ_RECTANGLE_LABEL, 0, 0, 0);
   ObjectSetInteger(0, name, OBJPROP_XDISTANCE, x); ObjectSetInteger(0, name, OBJPROP_YDISTANCE, y);
   ObjectSetInteger(0, name, OBJPROP_XSIZE, w); ObjectSetInteger(0, name, OBJPROP_YSIZE, h);
   ObjectSetInteger(0, name, OBJPROP_BGCOLOR, bg); ObjectSetInteger(0, name, OBJPROP_BORDER_COLOR, border);
   ObjectSetInteger(0, name, OBJPROP_CORNER, CORNER_LEFT_UPPER); ObjectSetInteger(0, name, OBJPROP_SELECTABLE, false);
}

void CreateLabel(string name, int x, int y, string text, color clr, int sz, string font="Segoe UI", ENUM_ANCHOR_POINT anchor=ANCHOR_LEFT_UPPER) {
   ObjectCreate(0, name, OBJ_LABEL, 0, 0, 0);
   ObjectSetInteger(0, name, OBJPROP_XDISTANCE, x); ObjectSetInteger(0, name, OBJPROP_YDISTANCE, y);
   ObjectSetString(0, name, OBJPROP_TEXT, text); ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
   ObjectSetInteger(0, name, OBJPROP_FONTSIZE, sz); ObjectSetString(0, name, OBJPROP_FONT, font);
   ObjectSetInteger(0, name, OBJPROP_ANCHOR, anchor); ObjectSetInteger(0, name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
}

void CreateButton(string name, int x, int y, int w, int h, string text, color txtClr, color bg) {
   ObjectCreate(0, name, OBJ_BUTTON, 0, 0, 0);
   ObjectSetInteger(0, name, OBJPROP_XDISTANCE, x); ObjectSetInteger(0, name, OBJPROP_YDISTANCE, y);
   ObjectSetInteger(0, name, OBJPROP_XSIZE, w); ObjectSetInteger(0, name, OBJPROP_YSIZE, h);
   ObjectSetString(0, name, OBJPROP_TEXT, text); ObjectSetInteger(0, name, OBJPROP_COLOR, txtClr);
   ObjectSetInteger(0, name, OBJPROP_BGCOLOR, bg); ObjectSetInteger(0, name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
}
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
        stopLoss: strat.parameters.stopLoss || 50,
        takeProfit: strat.parameters.takeProfit || 100,
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
  stop_loss: ${strat.parameters.stopLoss || 50}
  take_profit: ${strat.parameters.takeProfit || 100}
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
            Exportar EA Profissional: {strategy.name}
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
              <div className="flex flex-col gap-1">
                <select
                  value={version}
                  onChange={(e) => setVersion(e.target.value as 'mql4' | 'mql5')}
                  className="w-32 bg-slate-800 border border-slate-600 rounded px-3 py-2 text-sm"
                >
                  <option value="mql4">MQL4</option>
                  <option value="mql5">MQL5</option>
                </select>
                <p className="text-[10px] text-slate-500 italic">* MQL5 inclui Painel Visual e Gestão Avançada</p>
              </div>

              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleCopy(mqlCode)}
                  className="border-slate-600"
                >
                  {copied ? <Check className="h-4 w-4 mr-2" /> : <Copy className="h-4 w-4 mr-2" />}
                  Copiar Código
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleDownload(mqlCode, `${strategy.name.replace(/\s+/g, '_')}.${version}`)}
                  className="border-slate-600"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Salvar .${version}
                </Button>
              </div>
            </div>

            <div className="bg-slate-950 rounded-lg p-4 overflow-x-auto max-h-96 overflow-y-auto border border-slate-800">
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
