# PRD - Arquitetura e Requisitos Técnicos
## Sistema de Backtesting e Otimização de Estratégias de Trading

---

## 4. Arquitetura do Sistema

### 4.1 Visão Conceitual da Arquitetura

O sistema adota uma arquitetura em camadas com separação clara de responsabilidades, permitindo escalabilidade horizontal, manutenibilidade e testabilidade independente de cada componente.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CAMADA DE APRESENTAÇÃO                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  Dashboard  │  │  Backtest   │  │  Analytics  │  │  Strategy Builder   │ │
│  │    Web UI   │  │   Viewer    │  │    ML       │  │    (Visual)         │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CAMADA DE API E ORQUESTRAÇÃO                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    REST API / GraphQL Gateway                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐ │
│  │  Job Scheduler  │  │  Task Queue     │  │  Event Bus (Pub/Sub)        │ │
│  │  (APScheduler)  │  │  (Redis/RQ)     │  │  (Redis Streams)            │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CAMADA DE PROCESSAMENTO                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Data      │  │   Feature   │  │  Backtest   │  │    ML Pipeline      │ │
│  │  Ingestor   │  │  Engineer   │  │   Engine    │  │   (Train/Inference) │ │
│  │             │  │             │  │             │  │                     │ │
│  │ • MT5 API   │  │ • pandas-ta │  │ • VectorBT  │  │ • XGBoost/LightGBM  │ │
│  │ • CSV Load  │  │ • ta-lib    │  │ • Backtrader│  │ • LSTM (Keras)      │ │
│  │ • Dukascopy │  │ • Custom    │  │ • Backtest  │  │ • HMM (hmmlearn)    │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CAMADA DE VALIDAÇÃO E ANÁLISE                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │    WFA      │  │    CPCV     │  │ Monte Carlo │  │  Statistical Tests  │ │
│  │   Engine    │  │   Engine    │  │  Simulator  │  │  (Sharpe, Sortino)  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CAMADA DE ARMAZENAMENTO                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ Time-Series │  │  Metadata   │  │   Cache     │  │   Artifact Store    │ │
│  │  Database   │  │  Database   │  │   Layer     │  │   (MQL4/5, JSON)    │ │
│  │ (InfluxDB/  │  │  (PostgreSQL│  │  (Redis)    │  │                     │ │
│  │  Timescale) │  │  /SQLite)   │  │             │  │                     │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Componentes Principais

#### 4.2.1 Data Ingestion Layer

| Componente | Responsabilidade | Interfaces |
|------------|------------------|------------|
| **MT5 Connector** | Conexão com MetaTrader 5 via `MetaTrader5` Python API | `connect()`, `get_ohlcv()`, `get_ticks()` |
| **CSV Loader** | Importação de dados históricos em formato CSV/ZIP | `load_csv()`, `validate_schema()` |
| **API Client** | Integração com Dukascopy, Darwinex e outras fontes | `fetch_range()`, `stream_realtime()` |
| **Data Normalizer** | Padronização de schema e timezone para todos os sources | `normalize()`, `resample()` |

#### 4.2.2 Feature Engineering Engine

| Componente | Responsabilidade | Tecnologias |
|------------|------------------|-------------|
| **Indicator Generator** | Cálculo de 130+ indicadores técnicos | `ta-lib`, `pandas-ta` |
| **Feature Composer** | Criação de features derivadas e interações | Custom Python |
| **Label Generator** | Geração de labels para ML (regimes, direção, retorno) | `hmmlearn`, custom logic |
| **Feature Store** | Armazenamento e versionamento de features | Parquet + Metadata DB |

#### 4.2.3 Backtest Engine

| Componente | Responsabilidade | Tecnologias |
|------------|------------------|-------------|
| **Vectorized Engine** | Backtest exploratório de alta velocidade | `vectorbt` |
| **Event-Driven Engine** | Backtest detalhado com execução realista | `backtrader`, `backtesting.py` |
| **Parameter Grid** | Geração de combinações de parâmetros | `itertools`, `optuna` |
| **Results Aggregator** | Consolidação e ranking de resultados | Custom Python |

#### 4.2.4 ML Pipeline

| Componente | Responsabilidade | Tecnologias |
|------------|------------------|-------------|
| **Signal Classifier** | Predição de direção/probabilidade de sinais | `xgboost`, `lightgbm` |
| **Regime Detector** | Identificação de regimes de mercado | `hmmlearn` (HMM) |
| **Sequence Model** | Modelagem temporal de séries | `keras`/`pytorch` (LSTM) |
| **Model Registry** | Versionamento e tracking de experimentos | MLflow / Custom |

#### 4.2.5 Validation Framework

| Componente | Responsabilidade | Tecnologias |
|------------|------------------|-------------|
| **WFA Engine** | Walk-Forward Analysis com rolling windows | Custom implementation |
| **CPCV Engine** | Combinatorial Purged Cross-Validation | Custom (baseado em Lopez de Prado) |
| **Monte Carlo** | Simulação de cenários e stress testing | `numpy` |
| **Stats Calculator** | Métricas estatísticas avançadas | `scipy`, `empyrical` |

#### 4.2.6 Export & Integration

| Componente | Responsabilidade | Saídas |
|------------|------------------|--------|
| **MQL Generator** | Geração de Expert Advisors MQL4/5 | `.mq4`, `.mq5` files |
| **Config Exporter** | Exportação de parâmetros otimizados | `.json`, `.yaml` |
| **Report Generator** | PDF/HTML com análise completa | `.pdf`, `.html` |
| **API Integration** | Endpoints para integração externa | REST/GraphQL |

### 4.3 Fluxo de Dados

```
┌─────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Fonte  │───▶│   Raw Data  │───▶│  Features   │───▶│  Backtest   │
│  Dados  │    │   (OHLCV)   │    │  (+130 ind) │    │   Engine    │
└─────────┘    └─────────────┘    └─────────────┘    └──────┬──────┘
                                                            │
                              ┌─────────────────────────────┼─────────────────────────────┐
                              │                             │                             │
                              ▼                             ▼                             ▼
                        ┌─────────────┐              ┌─────────────┐              ┌─────────────┐
                        │   ML Train  │              │  Validation │              │   Results   │
                        │  (XGB/LSTM) │              │ (WFA/CPCV)  │              │   Store     │
                        └──────┬──────┘              └──────┬──────┘              └──────┬──────┘
                               │                             │                             │
                               └─────────────────────────────┘                             │
                                                             │                             │
                                                             ▼                             ▼
                                                       ┌─────────────┐              ┌─────────────┐
                                                       │   Ranking   │─────────────▶│  Artifacts  │
                                                       │   Engine    │              │  (MQL/JSON) │
                                                       └─────────────┘              └─────────────┘
```

### 4.4 Padrões Arquiteturais

| Padrão | Aplicação | Justificativa |
|--------|-----------|---------------|
| **Strategy** | Engines de backtest | Permite trocar entre VectorBT, Backtrader, etc. |
| **Pipeline** | Feature engineering | Fluxo sequencial de transformações reprodutíveis |
| **Observer** | Eventos de trading | Notificação de sinais, execuções, métricas |
| **Factory** | Criação de conectores | Instanciação dinâmica de data sources |
| **Repository** | Acesso a dados | Abstração do storage (DB, cache, files) |

### 4.5 Diagrama de Sequência - Fluxo de Backtest Completo

```
Usuário    UI    API    Job Queue    Worker    Data Layer    Backtest    ML    Validation
  │         │      │         │          │          │          │         │         │
  │──seleção──▶│      │         │          │          │          │         │         │
  │         │───▶│      │         │          │          │          │         │         │
  │         │      │─────job────▶│          │          │          │         │         │
  │         │      │         │    │────────fetch data────────▶│          │         │         │
  │         │      │         │    │◀───────dados OHLCV───────│          │         │         │
  │         │      │         │    │─────────────────▶│         │         │         │
  │         │      │         │    │◀────────────────features──│         │         │         │
  │         │      │         │    │──────────────────────────▶│         │         │
  │         │      │         │    │◀─────────────────result───│         │         │
  │         │      │         │    │────────────────────────────────────▶│         │
  │         │      │         │    │◀───────────────────predições─────────│         │
  │         │      │         │    │───────────────────────────────────────────────▶│
  │         │      │         │    │◀────────────────────métricas validadas─────────│
  │         │      │◀────────│────│───────────────resultados agregados─────────────│
  │◀────────│◀─────│         │    │          │          │         │         │
```

---

## 5. Stack Tecnológico

### 5.1 Matriz de Tecnologias por Camada

| Camada | Tecnologia | Versão | Justificativa Técnica |
|--------|------------|--------|----------------------|
| **Linguagem Base** | Python | 3.10+ | Ecossistema maduro para dados e ML; compatibilidade com todas as libs financeiras |
| **Linguagem EA** | MQL4/MQL5 | - | Padrão de mercado para MT4/MT5; necessário para exportação de estratégias |
| **Frontend** | React + TypeScript | 18+ | Componentização, tipagem forte, ecossistema rico de visualização |
| **API Gateway** | FastAPI | 0.100+ | Alto desempenho async, auto-documentação OpenAPI, validação Pydantic |
| **Task Queue** | Redis + RQ | 7.0+ | Simplicidade, persistência, integração nativa com Python |
| **Database - TS** | TimescaleDB | 2.11+ | Extensão PostgreSQL otimizada para séries temporais; SQL familiar |
| **Database - Meta** | PostgreSQL | 15+ | ACID compliance, JSON support, extensibilidade |
| **Cache** | Redis | 7.0+ | Baixa latência, estruturas de dados ricas, pub/sub |
| **Container** | Docker | 24+ | Reprodutibilidade de ambiente, isolamento de dependências |
| **Orchestration** | Docker Compose | 2.20+ | Simplifica desenvolvimento local e deployment single-node |

### 5.2 Stack de Dados e Feature Engineering

| Componente | Tecnologia | Justificativa |
|------------|------------|---------------|
| **DataFrame Engine** | pandas 2.0+ | Padrão da indústria; integração com todo ecossistema |
| **Indicadores Técnicos** | ta-lib 0.4+ | 130+ indicadores em C (performance); binding Python maduro |
| **Indicadores Modernos** | pandas-ta 0.3+ | API pandas-native; 100+ indicadores adicionais |
| **Processamento Numérico** | NumPy 1.24+ | Backend vetorizado para operações matemáticas |
| **Dados Financeiros** | yfinance, MetaTrader5 | Acesso direto a fontes de dados |
| **Formato Storage** | Parquet | Compressão eficiente, schema evolution, leitura colunar |

### 5.3 Stack de Backtesting

| Engine | Tecnologia | Caso de Uso | Justificativa |
|--------|------------|-------------|---------------|
| **Exploratório** | VectorBT 0.25+ | Varredura de 10k+ combinações | Vetorização NumPy; 1M ordens em ~100ms |
| **Detalhado** | Backtrader 1.9+ | Validação com execução realista | Event-driven; slippage, commission, order types |
| **Alternativo** | Backtesting.py | Backtest rápido com detalhes | Balance entre velocidade e realismo |
| **Bot Completo** | Freqtrade 2023+ | Estratégias prontas para produção | Hyperopt, FreqAI, integração exchanges |

### 5.4 Stack de Machine Learning

| Tipo | Tecnologia | Justificativa |
|------|------------|---------------|
| **Classificação** | XGBoost 2.0+ | Estado da arte para tabular; feature importance nativo |
| **Classificação Alt.** | LightGBM 4.0+ | Treinamento mais rápido; menor memória; similar performance |
| **Deep Learning** | TensorFlow 2.13+ / PyTorch 2.0+ | LSTM para séries temporais; flexibilidade arquitetural |
| **Regime Detection** | hmmlearn 0.3+ | HMM implementação robusta; bem documentada |
| **Pré-processamento** | scikit-learn 1.3+ | Pipeline, scaling, encoding, métricas |
| **Otimização** | Optuna 3.3+ | Hyperparameter tuning Bayesiano; pruning inteligente |
| **Tracking** | MLflow 2.8+ | Versionamento de modelos, métricas, artifacts |

### 5.5 Stack de Validação Estatística

| Componente | Tecnologia | Justificativa |
|------------|------------|---------------|
| **WFA** | Custom + scikit-learn | Implementação específica para financeiro |
| **CPCV** | Custom (Lopez de Prado) | Purging e embargo para evitar leakage |
| **Monte Carlo** | NumPy + SciPy | Simulação de cenários; distribuições estatísticas |
| **Métricas** | pyfolio, empyrical | Sharpe, Sortino, Calmar, Max Drawdown, etc. |
| **Testes Estatísticos** | scipy.stats | Testes de significância, estacionariedade |

### 5.6 Stack de Visualização

| Componente | Tecnologia | Justificativa |
|------------|------------|---------------|
| **Dashboards Interativos** | Plotly 5.15+ | Gráficos financeiros interativos; candlestick nativo |
| **Visualização Estática** | matplotlib 3.7+ | Gráficos para relatórios PDF |
| **Tabelas Avançadas** | ag-grid | Performance com grandes datasets; filtros avançados |
| **UI Components** | shadcn/ui + Tailwind | Design system consistente; acessibilidade |

### 5.7 Resumo de Dependências Críticas

```yaml
# Core
dependencias_core:
  - python: ">=3.10"
  - pandas: ">=2.0.0"
  - numpy: ">=1.24.0"
  
# Dados
dependencias_dados:
  - MetaTrader5: ">=5.0.45"
  - yfinance: ">=0.2.0"
  - requests: ">=2.31.0"
  
# Indicadores
dependencias_indicadores:
  - TA-Lib: ">=0.4.28"
  - pandas-ta: ">=0.3.14"
  
# Backtest
dependencias_backtest:
  - vectorbt: ">=0.25.0"
  - backtrader: ">=1.9.78"
  - backtesting: ">=0.3.3"
  
# ML
dependencias_ml:
  - xgboost: ">=2.0.0"
  - lightgbm: ">=4.0.0"
  - scikit-learn: ">=1.3.0"
  - hmmlearn: ">=0.3.0"
  - tensorflow: ">=2.13.0"
  
# Validação
dependencias_validacao:
  - scipy: ">=1.11.0"
  - empyrical: ">=0.5.5"
```

---

## 6. Requisitos Funcionais

### RF-01: Conexão Multi-Fonte de Dados

| Atributo | Descrição |
|----------|-----------|
| **Descrição** | O sistema deve permitir conexão a múltiplas fontes de dados financeiros, incluindo MetaTrader 4/5, arquivos CSV locais, e APIs de brokers (Dukascopy, Darwinex). |
| **Critérios de Aceitação** | 1. Conector MT5 com autenticação automática via terminal<br>2. Suporte a arquivos CSV com schema configurável (OHLCV, tick)<br>3. APIs REST/WS para fontes externas com retry e backoff exponencial<br>4. Fallback automático entre fontes quando disponível<br>5. Cache local de dados para operação offline |
| **Prioridade** | **Alta** (P0) |
| **Dependências** | - |

### RF-02: Extração de Dados OHLCV e Tick

| Atributo | Descrição |
|----------|-----------|
| **Descrição** | O sistema deve extrair dados históricos em formato OHLCV (candles) e tick (trades individuais) para qualquer símbolo e timeframe disponível na fonte de dados. |
| **Critérios de Aceitação** | 1. Download de candles para timeframes: M1, M5, M15, M30, H1, H4, D1, W1, MN<br>2. Download de dados tick com volume e informação de agressão<br>3. Range de datas configurável (start, end)<br>4. Chunking automático para grandes períodos (evitar timeout)<br>5. Validação de consistência (gaps, duplicatas, valores nulos) |
| **Prioridade** | **Alta** (P0) |
| **Dependências** | RF-01 |

### RF-03: Geração de Indicadores Técnicos e Features

| Atributo | Descrição |
|----------|-----------|
| **Descrição** | O sistema deve gerar automaticamente mais de 130 indicadores técnicos e features derivadas a partir dos dados brutos, permitindo também customização de indicadores próprios. |
| **Critérios de Aceitação** | 1. Biblioteca base: ta-lib (150+ indicadores) + pandas-ta (100+ indicadores)<br>2. Categorias: Tendência, Momentum, Volatilidade, Volume, Ciclicidade<br>3. Features derivadas: razões, diferenças, estatísticas móveis, ranks<br>4. Pipeline configurável via YAML/JSON<br>5. Feature importance integrada com modelos ML<br>6. Versionamento de features (hash do pipeline) |
| **Prioridade** | **Alta** (P0) |
| **Dependências** | RF-02 |

### RF-04: Backtest Vetorizado de Alta Velocidade

| Atributo | Descrição |
|----------|-----------|
| **Descrição** | O sistema deve executar backtests vetorizados de milhares de combinações de parâmetros em segundos, permitindo exploração eficiente do espaço de estratégias. |
| **Critérios de Aceitação** | 1. Engine base: VectorBT com processamento NumPy<br>2. Throughput: 10.000+ combinações em <30 segundos (1 ativo, 1 timeframe)<br>3. Suporte a múltiplos ativos simultâneos (portfolio backtest)<br>4. Paralelização multi-core automática<br>5. Cache de resultados intermediários<br>6. Progress tracking com estimativa de tempo |
| **Prioridade** | **Alta** (P0) |
| **Dependências** | RF-03 |

### RF-05: Validações Estatísticas Avançadas

| Atributo | Descrição |
|----------|-----------|
| **Descrição** | O sistema deve executar validações estatísticas rigorosas incluindo Walk-Forward Analysis (WFA), Combinatorial Purged Cross-Validation (CPCV) e simulações Monte Carlo. |
| **Critérios de Aceitação** | 1. **WFA**: Janelas rolantes com train/test split configurável<br>2. **CPCV**: Implementação com purging (k obs) e embargo (h obs)<br>3. **Monte Carlo**: 10.000+ simulações de cenários alternativos<br>4. Métricas calculadas: Sharpe, Sortino, Calmar, Max Drawdown, Profit Factor, Win Rate<br>5. Testes de estacionariedade e aleatoriedade<br>6. Relatório de confiança estatística para cada estratégia |
| **Prioridade** | **Alta** (P0) |
| **Dependências** | RF-04 |

### RF-06: Treinamento de Modelos ML

| Atributo | Descrição |
|----------|-----------|
| **Descrição** | O sistema deve treinar modelos de machine learning para classificação de sinais, detecção de regimes de mercado e predição temporal usando LSTM. |
| **Critérios de Aceitação** | 1. **Classificação**: XGBoost/LightGBM com hyperparameter tuning (Optuna)<br>2. **Regimes**: HMM com número de estados configurável (2-5)<br>3. **Temporal**: LSTM com arquitetura configurável (camadas, unidades, dropout)<br>4. Feature selection automática (importance, correlation, mutual info)<br>5. Cross-validation temporal com prevenção de lookahead bias<br>6. Model registry com versionamento e métricas de performance |
| **Prioridade** | **Alta** (P1) |
| **Dependências** | RF-03, RF-05 |

### RF-07: Recomendação de Top K Estratégias

| Atributo | Descrição |
|----------|-----------|
| **Descrição** | O sistema deve retornar as K melhores estratégias recomendadas com base em métricas OOS (Out-of-Sample), incluindo configurações otimizadas e justificativa da seleção. |
| **Critérios de Aceitação** | 1. Ranking multi-critério (Sharpe, Drawdown, Profit Factor, Consistency)<br>2. Filtros aplicáveis: min Sharpe, max drawdown, min trades<br>3. Para cada estratégia: parâmetros, métricas IS/OOS, equity curve, trades<br>4. Justificativa ML: contribuição de features, regime favorável<br>5. Exportação em múltiplos formatos (JSON, YAML, MQL)<br>6. Comparação lado-a-lado de estratégias selecionadas |
| **Prioridade** | **Alta** (P0) |
| **Dependências** | RF-04, RF-05, RF-06 |

### RF-08: Exportação para MQL4/5 e Configurações

| Atributo | Descrição |
|----------|-----------|
| **Descrição** | O sistema deve exportar estratégias validadas para código MQL4/5 (Expert Advisors) ou arquivos de parâmetros (JSON/YAML) para uso em outras plataformas. |
| **Critérios de Aceitação** | 1. Geração de EA MQL4/5 com estrutura completa (OnInit, OnTick, OnDeinit)<br>2. Templates configuráveis para diferentes tipos de estratégia<br>3. Set files (.set) compatíveis com MT4/5 Strategy Tester<br>4. JSON/YAML com parâmetros otimizados e metadados<br>5. Documentação inline no código gerado<br>6. Validação sintática do código MQL antes de exportar |
| **Prioridade** | **Média** (P1) |
| **Dependências** | RF-07 |

### RF-09: Histórico de Backtests com Reprodutibilidade

| Atributo | Descrição |
|----------|-----------|
| **Descrição** | O sistema deve armazenar histórico completo de todos os backtests executados com metadados de reprodutibilidade, permitindo auditoria e re-execução idêntica. |
| **Critérios de Aceitação** | 1. Manifest por backtest: seed, dataset hash, versão de código, dependências<br>2. Storage de: parâmetros, resultados, equity curves, trades individuais<br>3. Busca e filtro por: ativo, timeframe, data, estratégia, métricas<br>4. Re-execução idêntica a partir do manifest<br>5. Comparação entre runs históricas<br>6. Retenção configurável (TTL) com arquivamento para cold storage |
| **Prioridade** | **Média** (P1) |
| **Dependências** | RF-04 |

### RF-10: API Interna para Integração

| Atributo | Descrição |
|----------|-----------|
| **Descrição** | O sistema deve prover API interna (REST/GraphQL) para integração com outros serviços, permitindo automação e extensão de funcionalidades. |
| **Critérios de Aceitação** | 1. Endpoints RESTful para todas as operações CRUD<br>2. GraphQL opcional para queries flexíveis<br>3. Autenticação via JWT ou API keys<br>4. Rate limiting configurável<br>5. Documentação OpenAPI/Swagger automática<br>6. Webhooks para eventos (backtest complete, alertas)<br>7. SDK Python para facilitar integração |
| **Prioridade** | **Média** (P2) |
| **Dependências** | RF-01 a RF-09 |

### 6.1 Matriz de Prioridades

```
Prioridade  │ Requisitos
────────────┼────────────────────────────────────────
P0 (Alta)   │ RF-01, RF-02, RF-03, RF-04, RF-05, RF-07
P1 (Média)  │ RF-06, RF-08, RF-09
P2 (Baixa)  │ RF-10
```

---

## 7. Requisitos Não Funcionais

### 7.1 Performance

| ID | Requisito | Métrica | Critério de Aceitação |
|----|-----------|---------|----------------------|
| **RNF-PERF-01** | Tempo de backtest exploratório | Latência | ≤ 30 segundos para 10.000 combinações (1 ativo, 1 timeframe, 5 anos de dados) |
| **RNF-PERF-02** | Throughput de dados | Volume | Processamento de 1M+ candles/segundo em operação vetorizada |
| **RNF-PERF-03** | Tempo de carregamento de dados | Latência | ≤ 5 segundos para carregar 5 anos de dados M1 do cache local |
| **RNF-PERF-04** | Tempo de treinamento ML | Latência | ≤ 10 minutos para modelo XGBoost com 100k amostras e 50 features |
| **RNF-PERF-05** | Concorrência de jobs | Capacidade | Suporte a 10+ jobs de backtest em paralelo sem degradação >20% |
| **RNF-PERF-06** | Tempo de resposta da API | Latência | P95 < 200ms para endpoints de consulta; P95 < 5s para endpoints de execução |

### 7.2 Reprodutibilidade

| ID | Requisito | Implementação | Critério de Aceitação |
|----|-----------|---------------|----------------------|
| **RNF-REPR-01** | Seed determinística | Configuração | Toda operação aleatória (ML, Monte Carlo) usa seed configurável |
| **RNF-REPR-02** | Versionamento de datasets | Hashing | Cada dataset tem hash SHA-256 armazenado no manifest |
| **RNF-REPR-03** | Versionamento de código | Git | Cada backtest registra commit hash e branch |
| **RNF-REPR-04** | Manifest completo | JSON | Todo backtest gera manifest com: seed, dataset hash, código hash, versões de libs, parâmetros |
| **RNF-REPR-05** | Re-execução idêntica | Pipeline | Possibilidade de re-executar qualquer backtest histórico com resultados idênticos (±0.01%) |
| **RNF-REPR-06** | Ambiente containerizado | Docker | Dockerfile e docker-compose versionados para reprodutibilidade de ambiente |

#### Estrutura do Manifest de Reprodutibilidade

```json
{
  "manifest_version": "1.0",
  "run_id": "uuid-v4",
  "timestamp": "2024-01-15T10:30:00Z",
  "reproducibility": {
    "seed": 42,
    "dataset_hash": "sha256:a1b2c3...",
    "code_hash": "git:abc123...",
    "branch": "main",
    "python_version": "3.10.12",
    "dependencies_hash": "sha256:x9y8z7..."
  },
  "environment": {
    "os": "Ubuntu 22.04",
    "cpu": "AMD Ryzen 9 5900X",
    "ram_gb": 64,
    "docker_image": "trading-app:v1.2.3"
  },
  "configuration": {
    "symbol": "EURUSD",
    "timeframe": "H1",
    "date_range": ["2019-01-01", "2024-01-01"],
    "strategy": "MACD_Crossover",
    "parameters": {...}
  }
}
```

### 7.3 Escalabilidade

| ID | Requisito | Arquitetura | Critério de Aceitação |
|----|-----------|-------------|----------------------|
| **RNF-SCAL-01** | Fila de jobs distribuída | Redis + RQ | Suporte a fila persistente com retry e dead letter |
| **RNF-SCAL-02** | Workers horizontais | Stateless | Adição de workers sem reconfiguração (scale-out) |
| **RNF-SCAL-03** | Particionamento de dados | Sharding | Dados históricos particionáveis por símbolo/timeframe |
| **RNF-SCAL-04** | Cache distribuído | Redis Cluster | Cache compartilhado entre múltiplas instâncias |
| **RNF-SCAL-05** | Database read replicas | PostgreSQL | Réplicas de leitura para queries analíticas |
| **RNF-SCAL-06** | Auto-scaling de workers | Kubernetes | Escala automática baseada em tamanho da fila |

#### Arquitetura de Escalabilidade

```
                    ┌─────────────────┐
                    │   Load Balancer │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        ┌─────────┐    ┌─────────┐    ┌─────────┐
        │ API     │    │ API     │    │ API     │
        │ Instance│    │ Instance│    │ Instance│
        └────┬────┘    └────┬────┘    └────┬────┘
             │              │              │
             └──────────────┼──────────────┘
                            │
                    ┌───────┴───────┐
                    │  Redis Queue  │
                    └───────┬───────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
   ┌─────────┐        ┌─────────┐        ┌─────────┐
   │ Worker  │        │ Worker  │        │ Worker  │
   │   1     │        │   2     │        │   N     │
   └────┬────┘        └────┬────┘        └────┬────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                    ┌───────┴───────┐
                    │  Data Layer   │
                    │ (TimescaleDB) │
                    └───────────────┘
```

### 7.4 Experiência do Usuário (UX)

| ID | Requisito | Público-Alvo | Critério de Aceitação |
|----|-----------|--------------|----------------------|
| **RNF-UX-01** | Interface no-code | Traders não-técnicos | 80% das operações possíveis sem escrever código |
| **RNF-UX-02** | Wizard de estratégia | Iniciantes | Fluxo guiado para criação de estratégia em <5 passos |
| **RNF-UX-03** | Visualização de equity | Todos | Gráfico de equity interativo com zoom e anotações |
| **RNF-UX-04** | Progresso de operações | Todos | Barra de progresso com ETA para operações >5s |
| **RNF-UX-05** | Tooltips explicativos | Todos | Todo indicador e métrica tem tooltip com explicação |
| **RNF-UX-06** | Templates de estratégia | Todos | 10+ templates pré-configurados (MACD, RSI, Bollinger, etc.) |
| **RNF-UX-07** | Responsividade | Web users | Interface funcional em telas ≥1366px |
| **RNF-UX-08** | Dark/Light mode | Preferência | Toggle de tema com persistência |

### 7.5 Segurança

| ID | Requisito | Mecanismo | Critério de Aceitação |
|----|-----------|-----------|----------------------|
| **RNF-SEC-01** | Criptografia de dados locais | AES-256 | Dados sensíveis (credenciais, trades) criptografados em repouso |
| **RNF-SEC-02** | Separação de credenciais | Environment | Credenciais de broker em variáveis de ambiente, nunca no código |
| **RNF-SEC-03** | Autenticação de API | JWT | Tokens com expiração configurável; refresh token support |
| **RNF-SEC-04** | Rate limiting | Middleware | 100 req/min por IP; 1000 req/min por usuário autenticado |
| **RNF-SEC-05** | Sanitização de inputs | Validação | Todo input validado via Pydantic; SQL injection prevention |
| **RNF-SEC-06** | Logs de auditoria | Immutable | Logs de acesso e operações críticas append-only |
| **RNF-SEC-07** | Backup criptografado | GPG | Backups automáticos criptografados antes de upload |

### 7.6 Disponibilidade e Confiabilidade

| ID | Requisito | Estratégia | Critério de Aceitação |
|----|-----------|------------|----------------------|
| **RNF-AVAI-01** | Uptime do sistema | Redundância | 99.5% uptime para API (exceto manutenção programada) |
| **RNF-AVAI-02** | Graceful degradation | Fallback | Operação parcial mesmo com falha de componentes secundários |
| **RNF-AVAI-03** | Recuperação de jobs | Checkpoint | Jobs de longa duração salvam progresso a cada 10% |
| **RNF-AVAI-04** | Health checks | Monitoring | Endpoints /health e /ready para orquestração |

### 7.7 Manutenibilidade

| ID | Requisito | Prática | Critério de Aceitação |
|----|-----------|---------|----------------------|
| **RNF-MAINT-01** | Cobertura de testes | pytest | ≥80% cobertura de código; 100% em core business logic |
| **RNF-MAINT-02** | Documentação de código | Docstrings | Todas as classes e métodos públicos documentados |
| **RNF-MAINT-03** | Documentação de API | OpenAPI | Especificação OpenAPI 3.0 completa e atualizada |
| **RNF-MAINT-04** | Logging estruturado | JSON | Logs em formato JSON com correlation ID |
| **RNF-MAINT-05** | CI/CD | GitHub Actions | Pipeline de build, teste e deploy automatizado |

---

## 8. Apêndice: Glossário

| Termo | Definição |
|-------|-----------|
| **OHLCV** | Open, High, Low, Close, Volume - formato padrão de dados de candles |
| **Tick** | Registro individual de trade (preço, volume, timestamp) |
| **WFA** | Walk-Forward Analysis - validação com janelas temporais rolantes |
| **CPCV** | Combinatorial Purged Cross-Validation - validação cruzada para séries temporais |
| **OOS** | Out-of-Sample - dados não vistos durante treinamento/otimização |
| **IS** | In-Sample - dados usados para treinamento/otimização |
| **HMM** | Hidden Markov Model - modelo estatístico para detecção de regimes |
| **LSTM** | Long Short-Term Memory - arquitetura de rede neural recorrente |
| **EA** | Expert Advisor - programa automatizado para MT4/MT5 |
| **Sharpe Ratio** | Retorno ajustado ao risco (retorno / desvio padrão) |
| **Max Drawdown** | Maior queda do pico até o vale no equity curve |

---

*Documento gerado para especificação técnica do Sistema de Backtesting e Otimização de Estratégias de Trading*
*Versão: 1.0 | Data: 2024*
