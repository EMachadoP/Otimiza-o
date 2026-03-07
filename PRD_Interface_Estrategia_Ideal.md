# PRODUCT REQUIREMENTS DOCUMENT (PRD)
## Seções de Interface e Experiência do Usuário

---

## 9. FLUXO DE NAVEGAÇÃO

### 9.1 Arquitetura de Informação

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           APLICATIVO TRADE STRATEGIST                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────┐ │
│  │   DASHBOARD  │────│  ANÁLISE DE  │────│  BACKTEST &  │────│   CONFIG   │ │
│  │   PRINCIPAL  │    │    ATIVOS    │    │ OTIMIZAÇÃO   │    │   E AJUDA  │ │
│  └──────────────┘    └──────────────┘    └──────────────┘    └────────────┘ │
│         │                   │                   │                           │
│         ▼                   ▼                   ▼                           │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │  Portfólio   │    │  HISTÓRICO & │    │  Resultados  │                   │
│  │   Overview   │    │  ESTRATÉGIA  │    │  Detalhados  │                   │
│  │              │    │    IDEAL     │◄───┤              │                   │
│  └──────────────┘    └──────────────┘    └──────────────┘                   │
│         │                   │                                               │
│         ▼                   ▼                                               │
│  ┌──────────────┐    ┌──────────────┐                                       │
│  │   Alertas    │    │   Simulação  │                                       │
│  │   e Notif.   │    │   de Trade   │                                       │
│  └──────────────┘    └──────────────┘                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.2 Mapa de Navegação - Telas Principais

| ID | Tela | Descrição | Acesso |
|----|------|-----------|--------|
| T01 | **Dashboard Principal** | Visão geral do portfólio, ativos monitorados, alertas ativos | Menu principal / Inicial |
| T02 | **Histórico & Estratégia Ideal** | Análise técnica detalhada, padrões detectados, recomendações de estratégias | Menu Análise > Estratégia Ideal |
| T03 | **Análise de Ativos** | Scanner de múltiplos ativos, comparação de timeframes | Menu Análise > Scanner |
| T04 | **Backtest & Otimização** | Execução de backtests, otimização de parâmetros, walk-forward analysis | Menu Backtest > Novo Teste |
| T05 | **Resultados Detalhados** | Métricas de performance, relatórios, exportação de dados | Menu Backtest > Resultados |
| T06 | **Simulação de Trade** | Simulação interativa de entradas no gráfico | A partir de T02 (modal) |
| T07 | **Configurações** | Conexão MT4/MT5, preferências de exibição, gerenciamento de contas | Menu Config > Geral |
| T08 | **Biblioteca de Estratégias** | Catálogo de estratégias salvas, templates, histórico de exports | Menu Estratégias > Biblioteca |

### 9.3 Fluxos de Usuário Principais

#### Fluxo 1: Análise e Recomendação de Estratégia
```
┌─────────┐     ┌─────────────┐     ┌─────────────────────┐     ┌──────────────┐
│  Início │────▶│ Selecionar  │────▶│  Histórico &        │────▶│  Revisar     │
│         │     │  Ativo/TF   │     │  Estratégia Ideal   │     │  Recomendações│
└─────────┘     └─────────────┘     └─────────────────────┘     └──────────────┘
                                                                          │
                    ┌─────────────────────────────────────────────────────┘
                    │
                    ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Exportar   │◀────│   Simular    │◀────│   Ajustar    │
│   para EA    │     │   Trade      │     │   Parâmetros │
└──────────────┘     └──────────────┘     └──────────────┘
```

**Passos do Fluxo:**
1. Usuário acessa a tela "Histórico & Estratégia Ideal"
2. Seleciona ativo e timeframe desejados
3. Sistema carrega análise automática (padrões, regime, recomendações)
4. Usuário revisa recomendações de estratégias ranqueadas
5. [Opcional] Ajusta parâmetros de risco e refina busca
6. [Opcional] Simula trade em ponto específico do gráfico
7. Exporta estratégia selecionada para EA (MT4/MT5)

#### Fluxo 2: Validação de Estratégia com Backtest
```
┌─────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Início │────▶│  Selecionar  │────▶│  Executar    │────▶│  Analisar    │
│         │     │  Estratégia  │     │  Backtest    │     │  Resultados  │
└─────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

#### Fluxo 3: Monitoramento Contínuo
```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Dashboard   │────▶│  Receber     │────▶│  Navegar     │
│  Principal   │     │  Alerta      │     │  para Análise│
└──────────────┘     └──────────────┘     └──────────────┘
```

### 9.4 Estados de Navegação

| Estado | Descrição | Indicador Visual |
|--------|-----------|------------------|
| **Inicial** | Tela carregada sem dados | Placeholders cinza, botões habilitados |
| **Carregando** | Sistema processando dados | Spinners, skeleton screens, progress bars |
| **Com Dados** | Análise completa exibida | Todos os painéis populados, gráfico renderizado |
| **Atualizando** | Recarregamento em segundo plano | Indicador sutil no header, dados não bloqueados |
| **Erro** | Falha na conexão ou processamento | Mensagem de erro, botão "Tentar Novamente" |
| **Offline** | Sem conexão com MT4/MT5 | Banner de alerta, modo de visualização limitada |

---

## 10. ESPECIFICAÇÃO DA TELA "HISTÓRICO & ESTRATÉGIA IDEAL"

### 10.1 Wireframe Descritivo

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ HEADER                                                                                      │
│ ┌─────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ [Logo]  Trade Strategist                    [🔔] [⚙️] [👤 Usuário]        [? Ajuda]    │ │
│ └─────────────────────────────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ BARRA DE CONTROLES                                                                          │
│ ┌─────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │  Símbolo: [EURUSD ▼]  Timeframe: [H1 ▼]  Período: [6M ▼]  Estratégia: [Tendência ▼]   │ │
│ │                                                                           [🔄 Atualizar]│ │
│ └─────────────────────────────────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│  ┌──────────────────────────────────────────────┐  ┌─────────────────────────────────────┐  │
│  │                                              │  │  PADRÕES & ESTATÍSTICAS             │  │
│  │           PAINEL PRINCIPAL                   │  │  ┌─────────────────────────────────┐│  │
│  │              GRÁFICO                         │  │  │ Padrões Detectados (últimos 20) ││  │
│  │                                              │  │  │ ┌────────┬─────┬────┬────┬────┐ ││  │
│  │    ┌─────────────────────────────┐          │  │  │ │Padrão  │Data │Dir │Freq│Acrt│ ││  │
│  │    │                             │          │  │  │ ├────────┼─────┼────┼────┼────┤ ││  │
│  │    │    [CANDLESTICK CHART]      │          │  │  │ │Triâng. │14:30│↑   │78% │72% │ ││  │
│  │    │                             │          │  │  │ │Canal   │12:15│→   │65% │68% │ ││  │
│  │    │  ═══ S/R Levels            │          │  │  │ │H&O     │09:45│↓   │45% │61% │ ││  │
│  │    │  ─── Trendlines            │          │  │  │ └────────┴─────┴────┴────┴────┘ ││  │
│  │    │  ▲▼ Pattern Markers        │          │  │  │                                 ││  │
│  │    │                             │          │  │  │ [Ver todos os padrões →]        ││  │
│  │    │  ┌─────────────────────┐    │          │  │  └─────────────────────────────────┘│  │
│  │    │  │ REGIME: TREND UP 🟢 │    │          │  │  ┌─────────────────────────────────┐│  │
│  │    │  │ Vol: Alta | RSI: 67 │    │          │  │  │ HEATMAP RECORRÊNCIA             ││  │
│  │    │  └─────────────────────┘    │          │  │  │     [Heatmap horário visual]    ││  │
│  │    │                             │          │  │  │     Seg Ter Qua Qui Sex         ││  │
│  │    └─────────────────────────────┘          │  │  │  09 ██░░██░░██░░                ││  │
│  │                                             │  │  │  12 ████░░████░░                ││  │
│  │  [📸 Snapshot]  [📊 Simular Trade]          │  │  │  15 ░░████░░███░                ││  │
│  │                                             │  │  └─────────────────────────────────┘│  │
│  └──────────────────────────────────────────────┘  └─────────────────────────────────────┘  │
│                                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐    │
│  │ MELHORES ESTRATÉGIAS AGORA                                                          │    │
│  │ ┌────────┬───────────┬──────────┬───────────┬──────────┬───────────┬──────────────┐ │    │
│  │ │Rank    │Estratégia │Tipo      │WFE        │Sharpe OOS│Max DD MC  │Ações         │ │    │
│  │ ├────────┼───────────┼──────────┼───────────┼──────────┼───────────┼──────────────┤ │    │
│  │ │🥇 1    │TrendBreak │Tendência │0.89       │1.87      │12.3%      │[👁] [📥] [⚙️]│ │    │
│  │ │🥈 2    │RevChannel │Reversão  │0.82       │1.64      │15.1%      │[👁] [📥] [⚙️]│ │    │
│  │ │🥉 3    │ScalpEMA   │Scalping  │0.78       │1.45      │18.7%      │[👁] [📥] [⚙️]│ │    │
│  │ │4       │BreakVol   │Breakout  │0.71       │1.32      │21.4%      │[👁] [📥] [⚙️]│ │    │
│  │ └────────┴───────────┴──────────┴───────────┴──────────┴───────────┴──────────────┘ │    │
│  │ Legenda: [👁 Ver detalhes] [📥 Exportar EA] [⚙️ Gerar parâmetros]                   │    │
│  └─────────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐    │
│  │ INSIGHTS DE ML                                                                      │    │
│  │ ┌─────────────────────────────┐  ┌─────────────────────────────┐  ┌───────────────┐ │    │
│  │ │ FEATURE IMPORTANCE          │  │ PROBABILIDADE DE SUCESSO    │  │   ANÁLISE     │ │    │
│  │ │                             │  │                             │  │    GERADA     │ │    │
│  │ │ 1. RSI (14)      ████████░░ │  │                             │  │               │ │    │
│  │ │ 2. ATR (14)      ██████░░░░ │  │      ┌─────────────┐        │  │ "O mercado     │ │    │
│  │ │ 3. Volume        █████░░░░░ │  │      │             │        │  │  está em uma  │ │    │
│  │ │ 4. EMA (50)      ████░░░░░░ │  │      │    78%      │        │  │  tendência de │ │    │
│  │ │ 5. MACD          ███░░░░░░░ │  │      │   ━━━━━━━   │        │  │  alta com     │ │    │
│  │ │    ...                      │  │      │  Confiança  │        │  │  volume       │ │    │
│  │ │                             │  │      │    ALTA     │        │  │  crescente.   │ │    │
│  │ │                             │  │      └─────────────┘        │  │  A estratégia │ │    │
│  │ │                             │  │                             │  │  TrendBreak   │ │    │
│  │ │                             │  │ Prob. baseada no regime     │  │  tem 72% de   │ │    │
│  │ │                             │  │ atual e condições similares │  │  acerto em    │ │    │
│  │ │                             │  │ históricas                  │  │  condições    │ │    │
│  │ └─────────────────────────────┘  └─────────────────────────────┘  │  similares."  │ │    │
│  │                                                                    └───────────────┘ │    │
│  └─────────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                             │
│ STATUS BAR                                                                                  │
│ ┌─────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ 🟢 Conectado MT5 | Última atualização: 14:32:15 | Latência: 45ms | v2.1.0              │ │
│ └─────────────────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 10.2 Elementos UI Detalhados

#### 10.2.1 Header Global

| Elemento | Tipo | Comportamento |
|----------|------|---------------|
| Logo | Imagem + Texto | Redireciona para Dashboard Principal |
| Ícone Notificações | Badge + Dropdown | Exibe alertas recentes, contador de não lidas |
| Ícone Configurações | Dropdown | Acesso rápido a configurações comuns |
| Perfil do Usuário | Dropdown | Gerenciamento de conta, logout |
| Ajuda | Modal | Documentação, tutoriais, suporte |

#### 10.2.2 Barra de Controles

| Controle | Tipo | Opções/Default | Comportamento |
|----------|------|----------------|---------------|
| **Símbolo** | Dropdown Search | EURUSD, GBPUSD, USDJPY, BTCUSD, ETHUSD, WINQ26, etc. | Filtra ativos disponíveis na conta conectada |
| **Timeframe** | Dropdown | M1, M5, M15, M30, H1, H4, D1, W1, MN | Atualiza granularidade do gráfico e análise |
| **Período** | Dropdown | 1M, 3M, 6M, 1Y, 2Y, Custom | Define janela de dados históricos |
| **Tipo de Estratégia** | Dropdown Multi-select | Todas, Tendência, Reversão, Breakout, Scalping | Filtra recomendações por categoria |
| **Atualizar** | Botão Primário | - | Recarrega todos os dados e análises |

#### 10.2.3 Painel Principal - Gráfico

**Área do Gráfico (70% da largura da tela):**

| Elemento | Descrição | Interação |
|----------|-----------|-----------|
| **Candlesticks** | OHLC padrão com cores verde/alta, vermelho/baixa | Hover: tooltip com OHLC, volume |
| **Linhas de Suporte/Resistência** | Horizontais automáticas baseadas em pivôs históricos | Clique: destaque, mostra valor e toques |
| **Trendlines** | Linhas de tendência automáticas (mínimos/máximos) | Clique: mostra ângulo e força |
| **Marcadores de Padrões** | Ícones sobrepostos (△ triângulo, ⬡ H&O, etc.) | Hover: detalhes do padrão; Clique: zoom para área |
| **Badge de Regime** | Tag flutuante com regime atual | Clique: expande explicação dos indicadores |

**Toolbar do Gráfico:**

| Ferramenta | Ícone | Função |
|------------|-------|--------|
| Crosshair | + | Medir distâncias, ver valores |
| Zoom In/Out | 🔍+/🔍- | Navegação temporal |
| Pan | ✋ | Arrastar gráfico |
| Medir | 📏 | Medir pips/distância entre pontos |
| Desenho | ✏️ | Adicionar linhas manualmente |
| Indicadores | 📊 | Overlay de indicadores técnicos |

#### 10.2.4 Painel Padrões & Estatísticas

**Tabela de Padrões Detectados:**

| Coluna | Descrição | Formato |
|--------|-----------|---------|
| Padrão | Nome do padrão técnico | Texto + ícone visual |
| Data/Hora | Timestamp da detecção | DD/MM HH:MM |
| Direção | Sentido sugerido | Seta ↑ ↓ → |
| Frequência | % de ocorrência histórica | Percentual com barra |
| Acerto | Taxa de sucesso histórica | Percentual colorido |

**Heatmap de Recorrência:**

- **Eixo X:** Dias da semana (Seg a Sex)
- **Eixo Y:** Horários (00-24 em blocos de 1h ou agrupado)
- **Cores:** Escala de verde (alta recorrência) a transparente (baixa/nenhuma)
- **Interação:** Hover mostra valor exato e estatísticas

#### 10.2.5 Painel Melhores Estratégias Agora

**Tabela de Ranking:**

| Coluna | Descrição | Critério de Ordenação |
|--------|-----------|----------------------|
| Rank | Posição no ranking | Default: por WFE desc |
| Estratégia | Nome da estratégia | - |
| Tipo | Categoria | Badge colorido |
| WFE | Walk-Forward Efficiency | 0-1, >0.8 verde |
| Sharpe OOS | Sharpe Ratio Out-of-Sample | >1.5 verde |
| Max DD MC P95 | Drawdown máximo (Monte Carlo P95) | <15% verde |
| Ações | Botões de ação | - |

**Botões por Linha:**

| Botão | Ícone | Ação |
|-------|-------|------|
| Ver Detalhes | 👁️ | Abre modal com métricas completas, equity curve, trades |
| Exportar para EA | 📥 | Gera arquivo .mq4/.mq5 pronto para MT4/MT5 |
| Gerar Parâmetros | ⚙️ | Abre tela de otimização com valores sugeridos |

#### 10.2.6 Painel Insights de ML

**Feature Importance:**
- Gráfico de barras horizontal
- Top 5 features do modelo
- Barras proporcionais à importância
- Tooltip com descrição da feature

**Probabilidade de Sucesso:**
- Gauge circular ou semi-circular
- Zonas coloridas: Vermelho (<50%), Amarelo (50-70%), Verde (>70%)
- Valor percentual central
- Indicador de confiança (Baixa/Média/Alta)

**Análise Gerada (NLP):**
- Texto em linguagem natural
- Atualizado conforme contexto muda
- Destaques em negrito para termos técnicos
- Máximo 200 caracteres (expandível)

### 10.3 Comportamentos e Estados

#### 10.3.1 Estados do Gráfico

| Estado | Descrição | Feedback Visual |
|--------|-----------|-----------------|
| **Vazio** | Sem ativo selecionado | Placeholder: "Selecione um ativo para iniciar" |
| **Carregando Dados** | Buscando candles históricos | Skeleton screen, spinner no canto |
| **Processando Análise** | ML detectando padrões | Barra de progresso: "Analisando padrões..." |
| **Completo** | Todos os dados carregados | Animação suave de entrada dos elementos |
| **Atualizando Tick** | Novo candle em formação | Indicador "LIVE" pulsando |
| **Erro de Dados** | Falha ao carregar do broker | Mensagem de erro com retry |

#### 10.3.2 Estados de Seleção

| Ação | Estado | Feedback |
|------|--------|----------|
| Hover em padrão | Destaque | Padrão no gráfico pulsa, linha na tabela destacada |
| Seleção de estratégia | Ativo | Linha da tabela com fundo destacado |
| Simulação de trade | Modo ativo | Cursor muda para crosshair, instruções aparecem |
| Trade simulado | Resultado | Popup com estatísticas históricas do ponto |

#### 10.3.3 Tooltips e Ajuda Contextual

| Elemento | Tooltip |
|----------|---------|
| WFE | "Walk-Forward Efficiency: mede a robustez da estratégia em dados não vistos" |
| Sharpe OOS | "Sharpe Ratio calculado em período fora da amostra de treino" |
| Max DD MC P95 | "Maximum Drawdown com 95% de confiança via simulação Monte Carlo" |
| Feature Importance | "Features mais relevantes para a decisão do modelo ML" |

#### 10.3.4 Ações de Atalho (Keyboard Shortcuts)

| Atalho | Ação |
|--------|------|
| `R` | Atualizar dados |
| `S` | Salvar snapshot |
| `T` | Ativar modo simulação de trade |
| `1-5` | Selecionar estratégia do ranking (1=top) |
| `Esc` | Cancelar simulação/fechar modal |
| `F` | Fullscreen do gráfico |

### 10.4 Fluxos de Interação Detalhados

#### Fluxo: Simulação de Trade

```
1. Usuário clica em "[📊 Simular Trade]"
   ↓
2. Modo simulação ativado:
   - Cursor muda para crosshair
   - Instrução aparece: "Clique no ponto de entrada desejado"
   - Botão "Cancelar" aparece
   ↓
3. Usuário clica no gráfico:
   - Marcador de entrada aparece
   - Prompt: "Selecione stop loss (opcional)"
   ↓
4. [Opcional] Usuário clica segundo ponto (SL):
   - Linha de SL tracejada aparece
   - Prompt: "Selecione take profit (opcional)"
   ↓
5. [Opcional] Usuário clica terceiro ponto (TP):
   - Linha de TP tracejada aparece
   - R:R calculado e exibido
   ↓
6. Usuário confirma ou ajusta:
   - Botão "Analisar" habilitado
   ↓
7. Sistema processa:
   - Busca trades históricos similares
   - Calcula estatísticas
   ↓
8. Resultado exibido em modal:
   - Win rate histórico
   - Expectância matemática
   - Distribuição de resultados
   - Trades similares encontrados
```

#### Fluxo: Exportar para EA

```
1. Usuário clica "[📥 Exportar EA]" na estratégia desejada
   ↓
2. Modal de exportação aparece:
   - Preview do código (read-only)
   - Campos editáveis: Lote, SL/TP padrão, Magic Number
   - Seleção: MT4 ou MT5
   ↓
3. Usuário ajusta parâmetros
   ↓
4. Clique em "Gerar Código"
   ↓
5. Sistema gera arquivo .mq4/.mq5
   ↓
6. Download automático ou copiar para clipboard
   ↓
7. Confirmação: "EA exportado com sucesso!"
   ↓
8. [Opcional] Botão "Abrir pasta do MT5" (se path configurado)
```

---

## 11. DESIGN SYSTEM

### 11.1 Paleta de Cores

#### Cores Primárias

| Nome | Hex | Uso |
|------|-----|-----|
| **Primary** | `#2563EB` | Botões primários, links, destaques |
| **Primary Hover** | `#1D4ED8` | Estado hover de elementos primários |
| **Primary Light** | `#DBEAFE` | Backgrounds de seleção, badges |

#### Cores de Trading (Semânticas)

| Nome | Hex | Uso |
|------|-----|-----|
| **Bullish** | `#10B981` | Candles de alta, valores positivos, tendência up |
| **Bullish Light** | `#34D399` | Hover em elementos bullish |
| **Bearish** | `#EF4444` | Candles de baixa, valores negativos, tendência down |
| **Bearish Light** | `#F87171` | Hover em elementos bearish |
| **Neutral** | `#6B7280` | Valores neutros, sideways |

#### Cores de Background

| Nome | Hex | Uso |
|------|-----|-----|
| **Bg Primary** | `#0F172A` | Background principal (dark mode) |
| **Bg Secondary** | `#1E293B` | Cards, painéis, containers |
| **Bg Tertiary** | `#334155` | Elementos elevados, hover states |
| **Bg Chart** | `#0B1120` | Área do gráfico (mais escuro) |

#### Cores de Texto

| Nome | Hex | Uso |
|------|-----|-----|
| **Text Primary** | `#F8FAFC` | Títulos, texto principal |
| **Text Secondary** | `#94A3B8` | Labels, descrições |
| **Text Muted** | `#64748B` | Placeholders, desabilitado |

#### Cores de Status

| Nome | Hex | Uso |
|------|-----|-----|
| **Success** | `#22C55E` | Sucesso, conectado, operação ok |
| **Warning** | `#F59E0B` | Alerta, atenção necessária |
| **Error** | `#DC2626` | Erro, desconectado, falha |
| **Info** | `#3B82F6` | Informação, processando |

#### Cores de Regime de Mercado

| Regime | Cor | Badge |
|--------|-----|-------|
| Trend Up | `#10B981` | 🟢 TREND UP |
| Trend Down | `#EF4444` | 🔴 TREND DOWN |
| Range | `#F59E0B` | 🟡 RANGE |
| Range Volátil | `#F97316` | 🟠 RANGE VOLÁTIL |
| Breakout | `#8B5CF6` | 🟣 BREAKOUT |
| Indefinido | `#6B7280` | ⚪ ANALISANDO |

#### Heatmap - Escala de Recorrência

| Intensidade | Cor | Significado |
|-------------|-----|-------------|
| Muito Alta | `#10B981` | >80% de recorrência |
| Alta | `#34D399` | 60-80% |
| Média | `#FBBF24` | 40-60% |
| Baixa | `#F97316` | 20-40% |
| Muito Baixa | `#EF4444` | <20% |

### 11.2 Tipografia

#### Font Family

| Uso | Fonte | Fallback |
|-----|-------|----------|
| **UI/Body** | Inter | system-ui, sans-serif |
| **Monospace** | JetBrains Mono | Consolas, monospace |
| **Números/Dados** | Tabular Figures (Inter) | monospace |

#### Escala de Tamanhos

| Token | Tamanho | Uso |
|-------|---------|-----|
| `text-xs` | 12px | Labels de eixo, timestamps |
| `text-sm` | 14px | Body secundário, descrições |
| `text-base` | 16px | Body principal |
| `text-lg` | 18px | Subtítulos |
| `text-xl` | 20px | Títulos de seção |
| `text-2xl` | 24px | Títulos de painel |
| `text-3xl` | 30px | Títulos de página |
| `text-4xl` | 36px | Valores grandes (métricas) |

#### Pesos de Fonte

| Peso | Uso |
|------|-----|
| 400 (Regular) | Body text |
| 500 (Medium) | Labels, botões |
| 600 (Semibold) | Títulos, destaques |
| 700 (Bold) | Valores principais, alerts |

#### Estilos Específicos

| Elemento | Fonte | Tamanho | Peso | Cor |
|----------|-------|---------|------|-----|
| Preço no gráfico | JetBrains Mono | 14px | 600 | Text Primary |
| Variação % | Inter | 14px | 600 | Bullish/Bearish |
| Timestamp | Inter | 12px | 400 | Text Muted |
| Métrica principal | Inter | 32px | 700 | Text Primary |
| Label de métrica | Inter | 12px | 500 | Text Secondary |

### 11.3 Componentes Base

#### 11.3.1 Botões

**Botão Primário:**
```
Background: #2563EB
Text: #FFFFFF
Padding: 10px 20px
Border Radius: 6px
Font: 14px / 500
Hover: #1D4ED8
Active: #1E40AF
Disabled: #334155 (bg), #64748B (text)
```

**Botão Secundário:**
```
Background: transparent
Border: 1px solid #475569
Text: #F8FAFC
Padding: 10px 20px
Border Radius: 6px
Hover: Background #334155
```

**Botão de Ação (Ícone):**
```
Size: 36px x 36px
Background: #1E293B
Border Radius: 6px
Icon Color: #94A3B8
Hover: Background #334155, Icon #F8FAFC
```

**Botão de Destaque (Bullish/Bearish):**
```
Bullish: Background #064E3B, Text #34D399, Border #10B981
Bearish: Background #7F1D1D, Text #F87171, Border #EF4444
```

#### 11.3.2 Inputs

**Dropdown:**
```
Background: #1E293B
Border: 1px solid #334155
Border Radius: 6px
Padding: 8px 12px
Text: #F8FAFC
Placeholder: #64748B
Focus Border: #2563EB
Dropdown BG: #0F172A
```

**Input Numérico:**
```
Background: #1E293B
Border: 1px solid #334155
Font: JetBrains Mono
Text Align: Right
Stepper: ± botões à direita
```

#### 11.3.3 Cards e Painéis

**Card Padrão:**
```
Background: #1E293B
Border Radius: 8px
Padding: 16px
Border: 1px solid #334155 (opcional)
Shadow: none (flat design)
```

**Card com Header:**
```
Header BG: #0F172A (ligeiramente diferente)
Header Padding: 12px 16px
Title: 14px / 600
Content Padding: 16px
```

**Painel de Destaque (Alerta):**
```
Success: Border-left 3px #22C55E, BG #064E3B/20%
Warning: Border-left 3px #F59E0B, BG #78350F/20%
Error: Border-left 3px #DC2626, BG #7F1D1D/20%
```

#### 11.3.4 Tabelas

**Tabela de Dados:**
```
Header BG: #0F172A
Header Text: #94A3B8 / 12px / 600 / UPPERCASE
Row BG: transparent
Row BG (hover): #334155/30%
Row BG (selected): #2563EB/20%
Border: 1px solid #334155 (entre linhas)
Cell Padding: 12px 16px
```

#### 11.3.5 Badges e Tags

**Badge de Status:**
```
Padding: 4px 10px
Border Radius: 9999px (pill)
Font: 11px / 600 / UPPERCASE
Success: BG #064E3B, Text #22C55E
Warning: BG #78350F, Text #F59E0B
Error: BG #7F1D1D, Text #EF4444
```

**Tag de Categoria:**
```
Padding: 4px 8px
Border Radius: 4px
Font: 12px / 500
Tendência: BG #1E3A8A, Text #60A5FA
Reversão: BG #581C87, Text #C084FC
Breakout: BG #7C2D12, Text #FDBA74
Scalping: BG #064E3B, Text #34D399
```

#### 11.3.6 Gráficos e Visualizações

**Candlestick:**
```
Candle Up: Fill #10B981, Border #10B981
Candle Down: Fill #EF4444, Border #EF4444
Wick: Same color as candle body
Width: Adaptativo (2-10px)
Spacing: 1px entre candles
```

**Linhas de Overlay:**
```
S/R Levels: #94A3B8, 1px dashed, opacity 0.7
Trendline Up: #10B981, 2px solid
Trendline Down: #EF4444, 2px solid
Moving Average: #3B82F6, 2px solid
Volume: #475569, histograma
```

**Gauge de Probabilidade:**
```
Arco: #334155 (background)
Preenchimento: Gradiente verde (#10B981 → #34D399)
Zona <50%: #EF4444
Zona 50-70%: #F59E0B
Zona >70%: #10B981
Valor Central: 28px / 700
```

#### 11.3.7 Scrollbars

```
Width: 8px
Track: transparent
Thumb: #475569
Thumb Hover: #64748B
Border Radius: 4px
```

#### 11.3.8 Modais

```
Overlay: #000000 / 70%
Modal BG: #1E293B
Border Radius: 12px
Max Width: 600px (padrão), 900px (grande)
Padding: 24px
Shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5)
Close Button: Top-right, × ícone
```

#### 11.3.9 Tooltips

```
Background: #0F172A
Border: 1px solid #334155
Border Radius: 6px
Padding: 8px 12px
Font: 12px / 400
Max Width: 250px
Arrow: 6px, same BG
```

#### 11.3.10 Loading e Estados

**Spinner:**
```
Size: 24px (padrão), 40px (grande)
Color: #2563EB
Border: 3px solid #334155
Border-top: 3px solid #2563EB
Animation: rotate 1s linear infinite
```

**Skeleton:**
```
BG: #334155
Shimmer: Gradiente linear de #334155 → #475569 → #334155
Animation: translateX(-100%) → translateX(100%), 1.5s
Border Radius: 4px
```

**Progress Bar:**
```
Height: 4px (fino), 8px (padrão)
BG Track: #334155
BG Fill: Gradiente #2563EB → #3B82F6
Border Radius: 2px
```

### 11.4 Ícones

| Categoria | Conjunto | Uso |
|-----------|----------|-----|
| **UI Geral** | Lucide React / Heroicons | Botões, navegação |
| **Trading** | Custom / FontAwesome | Padrões técnicos, indicadores |
| **Status** | Lucide | Conexão, alertas, loading |

**Ícones Específicos:**

| Ação | Ícone | Nome |
|------|-------|------|
| Atualizar | 🔄 | RefreshCw |
| Snapshot | 📸 | Camera |
| Simular | 📊 | LineChart |
| Ver | 👁️ | Eye |
| Exportar | 📥 | Download |
| Configurar | ⚙️ | Settings |
| Alerta | 🔔 | Bell |
| Sucesso | ✓ | Check |
| Erro | ✕ | X |
| Info | ℹ️ | Info |
| Tendência Up | ↗️ | TrendingUp |
| Tendência Down | ↘️ | TrendingDown |

### 11.5 Espaçamento e Grid

**Sistema de Espaçamento (8px base):**

| Token | Valor |
|-------|-------|
| `space-1` | 4px |
| `space-2` | 8px |
| `space-3` | 12px |
| `space-4` | 16px |
| `space-5` | 20px |
| `space-6` | 24px |
| `space-8` | 32px |
| `space-10` | 40px |
| `space-12` | 48px |

**Grid de Layout:**
- Container máximo: 1920px
- Gutters: 16px (desktop), 12px (tablet), 8px (mobile)
- Margens laterais: 24px (desktop), 16px (tablet), 12px (mobile)

**Breakpoints:**

| Breakpoint | Largura | Ajustes |
|------------|---------|---------|
| Desktop XL | ≥1600px | Layout completo, 4 colunas |
| Desktop | ≥1280px | Layout padrão, 3 colunas |
| Tablet | ≥768px | Sidebar colapsável, 2 colunas |
| Mobile | <768px | Layout empilhado, 1 coluna |

---

## APÊNDICE: GLOSSÁRIO DE TERMOS UI

| Termo | Definição |
|-------|-----------|
| **WFE** | Walk-Forward Efficiency - métrica de robustez da estratégia |
| **Sharpe OOS** | Sharpe Ratio calculado em dados Out-of-Sample |
| **Max DD MC P95** | Maximum Drawdown com 95% de confiança via Monte Carlo |
| **Regime** | Estado atual do mercado (tendência, range, etc.) |
| **Feature Importance** | Relevância das variáveis no modelo de ML |
| **Snapshot** | Captura do estado atual da análise para referência |
| **EA** | Expert Advisor - robô de trading para MT4/MT5 |

---

*Documento gerado para Product Requirements Document (PRD)*
*Versão: 1.0*
*Última atualização: 2025*
