# Product Requirements Document (PRD)
## TradeStrategist - Sistema de Análise e Recomendação de Estratégias de Trading
### Versão 1.0 | Data: Janeiro 2025

---

## Sumário Executivo

O **TradeStrategist** é uma plataforma inovadora que combina análise técnica avançada, Machine Learning e validação estatística rigorosa para auxiliar traders na descoberta, otimização e deploy de estratégias de trading. Desenvolvido para atender desde desenvolvedores quantitativos até traders discrecionários, o sistema oferece uma ponte única entre o ecossistema Python e as plataformas MetaTrader 4/5.

A proposta de valor central do produto é funcionar como "um trader experiente analisando o mercado 24/7" - identificando padrões recorrentes, sugerindo setups otimizados, calibrando parâmetros e validando estratégias de forma completamente automatizada e baseada em dados. Diferentemente de plataformas tradicionais que operam como "caixa-preta", o TradeStrategist oferece total transparência com acesso a código-fonte, logs, artefatos e notebooks reprodutíveis.

Este documento consolida todas as especificações do produto, abrangendo desde a visão estratégica e personas até a arquitetura técnica, requisitos detalhados, fluxos de navegação e especificações de interface.

---

## 1. Visão do Produto

### 1.1 Declaração de Visão

> **Para** traders quantitativos, desenvolvedores e traders discrecionários avançados **que** precisam identificar padrões de mercado e otimizar estratégias de trading, **o** TradeStrategist **é uma** plataforma desktop/web **que** conecta-se ao MetaTrader 4/5 via Python, executa backtests robustos em múltiplas estratégias e utiliza Machine Learning para reconhecer padrões recorrentes. **Diferentemente de** plataformas tradicionais de backtesting ou otimizadores de EA, **nosso produto** oferece recomendações inteligentes de configurações de estratégia validadas por técnicas anti-overfitting (WFA, CPCV, Monte Carlo), gerando automaticamente EAs parametrizados prontos para deploy.

### 1.2 Objetivos do Produto

| Objetivo | Descrição | Métrica de Sucesso |
|----------|-----------|-------------------|
| **OBJ-001** | Automatizar a descoberta de padrões recorrentes em ativos/timeframes | >80% de precisão na identificação de regimes de mercado |
| **OBJ-002** | Reduzir tempo de desenvolvimento de estratégias viáveis | De semanas para <30 minutos por ativo/timeframe |
| **OBJ-003** | Eliminar overfitting através de validação estatística rigorosa | <5% de degradação de performance entre treino e teste |
| **OBJ-004** | Democratizar acesso a técnicas quantitativas avançadas | Usuários sem background de programação conseguem operar |
| **OBJ-005** | Gerar EAs exportáveis diretamente para MT4/MT5 | 100% das estratégias aprovadas exportáveis em MQL4/MQL5 |

### 1.3 Proposta de Valor

#### Valor Principal
**"Um trader experiente analisando seu gráfico 24/7"**

O produto simula a experiência de ter um trader sênior analisando o mercado, identificando padrões, sugerindo setups, calibrando parâmetros e validando estratégias - tudo de forma automatizada e baseada em dados.

#### Pilares de Valor

```
┌─────────────────────────────────────────────────────────────────┐
│                    PROPOSTA DE VALOR                            │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   VELOCIDADE    │   PRECISÃO      │      CONFIANÇA              │
│                 │                 │                             │
│ • Análise em    │ • ML para       │ • Validação estatística     │
│   minutos, não  │   reconhecimento│   rigorosa (WFA/CPCV/MC)    │
│   dias          │   de padrões    │                             │
│ • Backtests     │ • Features      │ • Transparência total       │
│   massivos      │   engineering   │   nos resultados            │
│   automatizados │   avançado      │ • Reprodutibilidade         │
│                 │                 │   garantida                 │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

### 1.4 Diferenciais Competitivos

| Diferencial | Descrição | Concorrência |
|-------------|-----------|--------------|
| **Reconhecimento de Padrões com ML** | Algoritmos de ML identificam regimes de mercado e padrões recorrentes automaticamente | Ferramentas tradicionais usam apenas indicadores técnicos fixos |
| **Validação Anti-Overfitting Integrada** | WFA, CPCV e Monte Carlo embutidos no pipeline de validação | Requerem implementação manual ou ferramentas separadas |
| **Geração Automática de EA** | Exportação direta para MQL4/MQL5 com parâmetros otimizados | Geralmente requer programação manual do EA |
| **Integração Python + MT4/MT5** | Ponte nativa entre ecossistema Python e MetaTrader | Soluções fragmentadas ou limitadas |
| **Artefatos Acessíveis** | Código, logs, CSVs e notebooks disponíveis para usuários avançados | Caixa-preta na maioria das soluções |
| **Dual Interface** | Tanto visual (GUI) quanto programática (API/CLI) | Foco exclusivo em uma das abordagens |

### 1.5 Posicionamento no Mercado

```
                    COMPLEXIDADE TÉCNICA
                    Baixa ◄─────────────────► Alta
                    
    ┌─────────────────────────────────────────────────────┐
    │                                                     │
Alta│  TradingView        │   ████████████████           │
    │  (Análise Visual)   │   TradeStrategist            │
    │                     │   (Análise + Automação)      │
    │  ┌─────────┐        │   ┌─────────────────┐        │
    │  │ MT4/5   │        │   │ Python + ML     │        │
    │  │ Built-in│        │   │ + Anti-Overfit  │        │
    │  │ Tester  │        │   │ + Auto EA Gen   │        │
    │  └─────────┘        │   └─────────────────┘        │
Baixa│                     │                              │
    │  ┌─────────┐        │   ┌─────────────────┐        │
    │  │ EA      │        │   │ Zipline/        │        │
    │  │ Builders│        │   │ Backtrader      │        │
    │  │ (Drag   │        │   │ (Frameworks)    │        │
    │  │ & Drop) │        │   │                 │        │
    │  └─────────┘        │   └─────────────────┘        │
    └─────────────────────────────────────────────────────┘
    
    LEGENDA: ████ = Posição do nosso produto
```

---

## 2. Personas

### 2.1 Persona 1: Ricardo "Quant" Silva

| Atributo | Descrição |
|----------|-----------|
| **Nome** | Ricardo Silva |
| **Apelido** | Quant Dev |
| **Idade** | 32 anos |
| **Formação** | Engenharia/Ciência da Computação ou Física |
| **Experiência** | 5+ anos em trading quantitativo |
| **Localização** | São Paulo/SP ou remoto |

#### Perfil
Ricardo é um desenvolvedor quantitativo que trabalha em mesa de trading ou de forma independente. Ele prefere ter controle total sobre seu pipeline de análise e valoriza a capacidade de inspecionar, modificar e estender o código. Usa Python diariamente e está familiarizado com bibliotecas como pandas, numpy, scikit-learn e backtrader.

#### Objetivos
- Iterar rapidamente em novas ideias de estratégias
- Ter acesso aos artefatos brutos (código, logs, CSVs, notebooks)
- Integrar o sistema com seu pipeline existente de ML
- Automatizar completamente o workflow de descoberta de alpha
- Publicar papers ou artigos baseados em suas análises

#### Frustrações
- Plataformas que funcionam como "caixa-preta" sem acesso ao código
- Ferramentas que limitam a customização de algoritmos
- Necessidade de reimplementar validações estatísticas manualmente
- Dificuldade em reproduzir resultados entre diferentes ambientes
- Interfaces visuais que não permitem scripting ou batch processing

#### Necessidades
- [x] API REST/GraphQL completa
- [x] Acesso ao código-fonte dos algoritmos de ML
- [x] Exportação de notebooks Jupyter com análises
- [x] CLI para automação e scripts
- [x] Documentação técnica detalhada
- [x] Possibilidade de injetar estratégias customizadas em Python

#### Citação Típica
> *"Eu preciso ver o código por trás das recomendações. Se não consigo reproduzir e modificar, não serve para o meu workflow."*

---

### 2.2 Persona 2: Marina Torres

| Atributo | Descrição |
|----------|-----------|
| **Nome** | Marina Torres |
| **Apelido** | Trader Discrecionário Avançado |
| **Idade** | 41 anos |
| **Formação** | Administração/Economia ou autodidata |
| **Experiência** | 8+ anos em trading, migração para quant |
| **Localização** | Curitiba/PR |

#### Perfil
Marina é uma trader experiente que começou no trading discrecionário e agora busca incorporar análise quantitativa em seu processo. Ela entende bem de análise técnica, price action e gerenciamento de risco, mas não tem background de programação. Valoriza visualização clara e interpretabilidade das recomendações.

#### Objetivos
- Identificar padrões no gráfico sem precisar programar
- Receber sugestões de setup com explicação do racional
- Validar suas intuições de trading com dados estatísticos
- Aprender conceitos quantitativos de forma prática
- Tomar decisões informadas baseadas em backtests robustos

#### Frustrações
- Cursos e ferramentas que exigem conhecimento de programação
- Resultados de backtests que parecem "bons demais para ser verdade"
- Falta de transparência sobre como as recomendações são geradas
- Interfaces complexas e sobrecarregadas de informações
- Dificuldade em confiar em estratégias geradas automaticamente

#### Necessidades
- [x] Interface visual intuitiva com gráficos interativos
- [x] Padrões marcados diretamente no gráfico
- [x] Explicação em linguagem natural das recomendações
- [x] Métricas de performance claras e interpretáveis
- [x] Alertas e notificações sobre oportunidades
- [x] Tutoriais e tooltips educacionais

#### Citação Típica
> *"Eu quero ver o padrão no gráfico, entender por que essa estratégia foi sugerida e ter confiança nos números - sem precisar escrever uma linha de código."*

---

### 2.3 Persona 3: Carlos Mendes

| Atributo | Descrição |
|----------|-----------|
| **Nome** | Carlos Mendes |
| **Apelido** | Trader de Robôs |
| **Idade** | 38 anos |
| **Formação** | Engenharia ou TI |
| **Experiência** | 6+ anos operando EAs no MT4/MT5 |
| **Localização** | Florianópolis/SC |

#### Perfil
Carlos opera exclusivamente com Expert Advisors (EAs) no MetaTrader. Ele tem conhecimento básico de MQL4/MQL5 e consegue fazer ajustes simples em EAs existentes, mas prefere não desenvolver estratégias do zero. Sua principal preocupação é a robustez e a validação estatística das estratégias antes de colocá-las em produção.

#### Objetivos
- Transformar recomendações em EAs funcionais rapidamente
- Validar estratégias com testes rigorosos antes de operar
- Otimizar parâmetros de EAs existentes
- Gerenciar múltiplas estratégias em diferentes ativos
- Minimizar tempo entre ideia e deploy em conta real

#### Frustrações
- Processo manual e demorado de otimização de parâmetros
- Dificuldade em identificar overfitting em backtests
- Necessidade de múltiplas ferramentas no workflow
- Problemas de compatibilidade entre plataformas
- Falta de confiança em estratégias não validadas estatisticamente

#### Necessidades
- [x] Exportação direta para MQL4/MQL5
- [x] Arquivos de configuração JSON/YAML
- [x] Relatórios de validação prontos para auditoria
- [x] Comparação lado-a-lado de múltiplas estratégias
- [x] Integração direta com MT4/MT5 para forward testing
- [x] Alertas de degradação de performance em tempo real

#### Citação Típica
> *"Eu quero clicar em 'exportar para EA' e ter um arquivo MQL pronto para compilar e rodar no meu MT5, com a certeza de que passou nos testes estatísticos."*

---

### 2.4 Resumo Comparativo das Personas

| Aspecto | Ricardo (Quant Dev) | Marina (Discrecionária) | Carlos (Trader de Robôs) |
|---------|---------------------|------------------------|--------------------------|
| **Prioridade #1** | Acesso ao código | Visualização intuitiva | Exportação para EA |
| **Prioridade #2** | Automação total | Interpretabilidade | Validação estatística |
| **Prioridade #3** | Customização | Facilidade de uso | Deploy rápido |
| **Interface Preferida** | CLI / API / Notebook | GUI Visual | GUI + Export |
| **Nível Técnico** | Alto | Médio | Médio |
| **Tempo Disponível** | Dedicação total | Tempo limitado | Tempo limitado |
| **Principal Medo** | Caixa-preta | Complexidade excessiva | Overfitting não detectado |

---

## 3. Casos de Uso

### 3.1 UC-001: Descoberta Automática de Estratégias Viáveis

| Campo | Descrição |
|-------|-----------|
| **ID** | UC-001 |
| **Nome** | Descoberta Automática de Estratégias Viáveis |
| **Ator Principal** | Ricardo (Quant Dev) / Marina (Trader Discrecionária) |
| **Atores Secundários** | Sistema de ML, MT4/MT5 Connector |
| **Frequência** | Alta (diária/semanal) |
| **Prioridade** | Alta |

#### Descrição
O usuário seleciona um símbolo (ativo) e timeframe, e o sistema realiza automaticamente o download de dados históricos, gera features técnicas, executa backtests massivos em múltiplas estratégias candidatas e retorna um ranking das estratégias mais viáveis para aquele contexto de mercado.

#### Pré-condições
1. Usuário está autenticado no sistema
2. Conexão com MT4/MT5 está configurada e ativa OU dados históricos estão disponíveis localmente
3. Bibliotecas Python necessárias estão instaladas
4. Configurações de risco e capital estão definidas

#### Fluxo Principal

| Passo | Ator | Ação |
|-------|------|------|
| 1 | Usuário | Seleciona símbolo (ex: EURUSD) e timeframe (ex: H1) |
| 2 | Usuário | Define período de análise (ex: últimos 2 anos) |
| 3 | Usuário | Configura parâmetros de busca (opcional): tipos de estratégias, restrições de risco |
| 4 | Sistema | Valida parâmetros e verifica disponibilidade de dados |
| 5 | Sistema | Baixa dados históricos do MT4/MT5 ou cache local |
| 6 | Sistema | Executa pipeline de feature engineering |
| 7 | Sistema | Identifica regimes de mercado usando HMM |
| 8 | Sistema | Executa backtests em paralelo nas estratégias candidatas |
| 9 | Sistema | Calcula métricas de performance para cada estratégia |
| 10 | Sistema | Aplica filtros de viabilidade (profit factor, drawdown, etc.) |
| 11 | Sistema | Gera ranking ordenado das estratégias aprovadas |
| 12 | Sistema | Apresenta resultados com métricas detalhadas |

#### Fluxos Alternativos

**FA-001: Dados indisponíveis**
- Se os dados não estiverem disponíveis no MT4/MT5, o sistema tenta fontes alternativas (Yahoo Finance, broker APIs)
- Se nenhuma fonte disponível, notifica usuário com instruções

**FA-002: Nenhuma estratégia viável encontrada**
- Sistema expande automaticamente o espaço de busca
- Notifica usuário sobre ajustes sugeridos nos critérios

#### Pós-condições
1. Ranking de estratégias está disponível para visualização
2. Dados e resultados estão salvos no banco de dados/histórico
3. Estratégias podem ser selecionadas para validação aprofundada
4. Artefatos (CSVs, logs) disponíveis para download

#### Requisitos Funcionais Relacionados
- RF-001, RF-002, RF-003, RF-004, RF-005, RF-007

---

### 3.2 UC-002: Análise de Padrões e Regimes de Mercado

| Campo | Descrição |
|-------|-----------|
| **ID** | UC-002 |
| **Nome** | Análise de Padrões e Regimes de Mercado |
| **Ator Principal** | Marina (Trader Discrecionária) |
| **Atores Secundários** | Sistema de ML, Visualizador de Gráficos |
| **Frequência** | Alta (diária) |
| **Prioridade** | Alta |

#### Descrição
O usuário acessa a tela "Histórico & Estratégia Ideal" onde visualiza o gráfico do ativo com padrões detectados pelo ML marcados visualmente, regimes de mercado identificados (trending, ranging, volatile), e recebe sugestões de estratégias com parâmetros otimizados para o contexto atual.

#### Pré-condições
1. Dados históricos do ativo/timeframe estão disponíveis
2. Modelos de ML para detecção de padrões estão treinados/carregados
3. Análise de regimes (HMM) foi executada previamente

#### Fluxo Principal

| Passo | Ator | Ação |
|-------|------|------|
| 1 | Usuário | Navega para tela "Histórico & Estratégia Ideal" |
| 2 | Usuário | Seleciona ativo e timeframe |
| 3 | Sistema | Carrega dados e executa análise de padrões |
| 4 | Sistema | Renderiza gráfico candlestick interativo |
| 5 | Sistema | Sobrepõe marcações de padrões detectados |
| 6 | Sistema | Coloriza regimes de mercado (ex: verde=trend up, cinza=ranging) |
| 7 | Sistema | Exibe painel lateral com estatísticas de regimes |
| 8 | Sistema | Gera sugestões de estratégias para regime atual |
| 9 | Sistema | Apresenta explicação em linguagem natural |
| 10 | Usuário | Interage com gráfico (zoom, pan, clique em padrões) |
| 11 | Sistema | Atualiza informações contextuais conforme interação |

#### Fluxos Alternativos

**FA-001: Padrão não reconhecido**
- Usuário pode marcar manualmente um padrão
- Sistema aprende com feedback para futuras detecções

**FA-002: Regime em transição**
- Sistema indica probabilidade de mudança de regime
- Alerta sobre incerteza nas recomendações

#### Pós-condições
1. Visualização do gráfico com anotações está disponível
2. Sugestões de estratégias foram apresentadas
3. Histórico de análise foi salvo
4. Usuário pode exportar imagem ou relatório

#### Requisitos Funcionais Relacionados
- RF-006, RF-007

---

### 3.3 UC-003: Validação Anti-Overfitting de Estratégia

| Campo | Descrição |
|-------|-----------|
| **ID** | UC-003 |
| **Nome** | Validação Anti-Overfitting de Estratégia |
| **Ator Principal** | Carlos (Trader de Robôs) / Ricardo (Quant Dev) |
| **Atores Secundários** | Motor de Validação Estatística |
| **Frequência** | Média (semanal) |
| **Prioridade** | Alta |

#### Descrição
O usuário seleciona uma estratégia candidata do ranking e executa o pipeline completo de validação anti-overfitting, incluindo Walk-Forward Analysis (WFA), Combinatorial Purged Cross-Validation (CPCV) e testes de Monte Carlo. Estratégias aprovadas são salvas como "modelos aprovados".

#### Pré-condições
1. Estratégia candidata foi previamente identificada (UC-001)
2. Dados históricos suficientes para validação (mínimo 2 anos recomendado)
3. Parâmetros de validação configurados

#### Fluxo Principal

| Passo | Ator | Ação |
|-------|------|------|
| 1 | Usuário | Seleciona estratégia candidata do ranking |
| 2 | Usuário | Inicia processo de validação aprofundada |
| 3 | Sistema | Apresenta configurações de validação (editáveis) |
| 4 | Usuário | Confirma ou ajusta parâmetros |
| 5 | Sistema | Executa Walk-Forward Analysis (WFA) |
| 6 | Sistema | Executa Combinatorial Purged Cross-Validation (CPCV) |
| 7 | Sistema | Executa simulações de Monte Carlo |
| 8 | Sistema | Calcula probabilidade de overfitting (PBO) |
| 9 | Sistema | Gera relatório consolidado de validação |
| 10 | Sistema | Apresenta resultados com gráficos de análise |
| 11 | Usuário | Revisa resultados e decide aprovação |
| 12 | Usuário | Salva estratégia como "modelo aprovado" (se aprovada) |

#### Critérios de Aprovação

| Teste | Critério Mínimo | Critério Ideal |
|-------|-----------------|----------------|
| WFA | CAGR > 0 no out-of-sample | CAGR out > 70% CAGR in |
| CPCV | Média Sharpe > 1 | Média Sharpe > 1.5 |
| Monte Carlo | 95% dos cenários lucrativos | 99% dos cenários lucrativos |
| PBO | < 50% | < 20% |

#### Pós-condições
1. Relatório de validação completo está disponível
2. Estratégia foi classificada como aprovada/reprovada
3. Se aprovada, estratégia entra no catálogo de modelos aprovados
4. Artefatos de validação salvos para auditoria futura

#### Requisitos Funcionais Relacionados
- RF-005, RF-009

---

### 3.4 UC-004: Exportação para EA MT4/MT5

| Campo | Descrição |
|-------|-----------|
| **ID** | UC-004 |
| **Nome** | Exportação para EA MT4/MT5 |
| **Ator Principal** | Carlos (Trader de Robôs) |
| **Atores Secundários** | Gerador de Código MQL, Sistema de Arquivos |
| **Frequência** | Média (semanal) |
| **Prioridade** | Alta |

#### Descrição
O usuário exporta uma estratégia aprovada para um Expert Advisor (EA) funcional em MQL4 ou MQL5, pronto para compilação e execução no MetaTrader. Alternativamente, pode exportar arquivo de configuração JSON/YAML para integração com EAs existentes.

#### Pré-condições
1. Estratégia foi aprovada no pipeline de validação (UC-003)
2. Tipo de exportação foi selecionado (MQL4/MQL5/JSON/YAML)
3. Diretório de destino está configurado ou acessível

#### Fluxo Principal

| Passo | Ator | Ação |
|-------|------|------|
| 1 | Usuário | Seleciona estratégia aprovada do catálogo |
| 2 | Usuário | Clica em "Exportar" |
| 3 | Sistema | Apresenta opções de formato (MQL4/MQL5/JSON/YAML) |
| 4 | Usuário | Seleciona formato desejado |
| 5 | Sistema | Gera código/configuração correspondente |
| 6 | Sistema | Valida sintaxe do código gerado |
| 7 | Sistema | Apresenta preview do código/arquivo |
| 8 | Usuário | Confirma ou solicita ajustes |
| 9 | Sistema | Salva arquivo no diretório especificado |
| 10 | Sistema | Fornece instruções de instalação no MT4/MT5 |
| 11 | Sistema | Registra exportação no histórico |

#### Formatos de Exportação

| Formato | Conteúdo | Caso de Uso |
|---------|----------|-------------|
| **MQL4** | EA completo em MQL4 | Deploy direto no MT4 |
| **MQL5** | EA completo em MQL5 | Deploy direto no MT5 |
| **JSON** | Parâmetros estruturados | Integração com EA existente |
| **YAML** | Parâmetros + metadados | Versionamento e CI/CD |

#### Pós-condições
1. Arquivo exportado está disponível no diretório especificado
2. Código gerado passou em validação sintática
3. Registro de exportação foi salvo
4. Instruções de uso foram apresentadas

#### Requisitos Funcionais Relacionados
- RF-008

---

### 3.5 UC-005: Consulta Rápida de Recomendação

| Campo | Descrição |
|-------|-----------|
| **ID** | UC-005 |
| **Nome** | Consulta Rápida de Recomendação |
| **Ator Principal** | Marina (Trader Discrecionária) / Carlos (Trader de Robôs) |
| **Atores Secundários** | MT4/MT5 Connector, Sistema de ML |
| **Frequência** | Muito Alta (múltiplas vezes ao dia) |
| **Prioridade** | Média |

#### Descrição
No modo "consulta rápida", o usuário está analisando um gráfico no MT4/MT5, clica no app e recebe instantaneamente uma recomendação de estratégia para o ativo/timeframe atual, sem necessidade de navegar por múltiplas telas ou configurar parâmetros.

#### Pré-condições
1. App está em execução (em segundo plano ou minimizado)
2. MT4/MT5 está aberto com gráfico ativo
3. Conexão entre app e MT4/MT5 está estabelecida
4. Dados do ativo/timeframe atual são detectáveis

#### Fluxo Principal

| Passo | Ator | Ação |
|-------|------|------|
| 1 | Usuário | Está visualizando gráfico no MT4/MT5 |
| 2 | Usuário | Atalho de teclado ou clica no ícone do app |
| 3 | Sistema | Detecta ativo e timeframe atuais do MT4/MT5 |
| 4 | Sistema | Verifica cache de análises recentes |
| 5 | Sistema | Se não houver cache, executa análise rápida |
| 6 | Sistema | Identifica regime de mercado atual |
| 7 | Sistema | Recupera estratégias recomendadas para contexto |
| 8 | Sistema | Apresenta recomendação em overlay/janela flutuante |
| 9 | Sistema | Exibe: setup sugerido, parâmetros, confiança |
| 10 | Usuário | Pode aceitar, descartar ou solicitar detalhes |
| 11 | Sistema | Registra interação para aprendizado |

#### Fluxos Alternativos

**FA-001: Análise em cache**
- Se análise recente existe em cache, retorna imediatamente
- Indica ao usuário a idade da análise

**FA-002: Ativo não suportado**
- Notifica usuário sobre limitação
- Sugere ativos similares disponíveis

#### Tempo de Resposta Esperado

| Cenário | Tempo Máximo |
|---------|--------------|
| Cache hit | < 1 segundo |
| Cache miss | < 10 segundos |
| Análise completa | < 30 segundos |

#### Pós-condições
1. Recomendação foi apresentada ao usuário
2. Interação foi registrada
3. Se aceita, estratégia pode ser validada/exportada
4. Feedback do usuário foi coletado (implícito ou explícito)

#### Requisitos Funcionais Relacionados
- RF-010

---

### 3.6 Matriz de Prioridade dos Casos de Uso

```
     IMPACTO NO NEGÓCIO
     Baixo ◄─────────────► Alto
     
Alto ┌─────────────────────────────────────┐
     │  UC-001    UC-003                   │
     │  (Busca)   (Validação)              │
     │                                     │
     │              ★ UC-002               │
     │             (Padrões)               │
     │                                     │
     │  UC-005                             │
     │  (Consulta                          │
     │   Rápida)   UC-004                  │
     │             (Export)                │
Baixo└─────────────────────────────────────┘

★ = Caso de uso principal (core)
```

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
  │         │      │         │    │◀────────────────features──│         │         │
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

## 8. Roadmap do Produto

### 8.1 Visão Geral das Fases

```
    2024 Q4        2025 Q1        2025 Q2        2025 Q3        2025 Q4
    ├──────────────┼──────────────┼──────────────┼──────────────┤
    │   FASE 1     │   FASE 2     │   FASE 3     │   FASE 4     │
    │   POC CLI    │   Dev-Focus  │  Trader-Friendly  │  Live Assist │
    │              │              │              │              │
    │  v0.1.0      │  v0.5.0      │  v1.0.0      │  v2.0.0      │
    └──────────────┴──────────────┴──────────────┴──────────────┘
```

### 8.2 Fase 1: POC CLI (v0.1.0) - Q4 2024

#### Objetivo
Validar a viabilidade técnica do pipeline core: conexão MT4/MT5, backtesting, ML básico e geração de código.

#### Funcionalidades

| ID | Funcionalidade | Descrição |
|----|----------------|-----------|
| F1.1 | Conector MT5 Python | Biblioteca para comunicação com MT5 via ZeroMQ |
| F1.2 | Downloader de Dados | Download OHLCV de múltiplos ativos/timeframes |
| F1.3 | Engine de Backtest | Backtest simples com métricas básicas (Profit Factor, Sharpe) |
| F1.4 | Estratégias Template | 3 estratégias de exemplo (média móvel, RSI, Bollinger) |
| F1.5 | Otimizador de Parâmetros | Grid search simples para otimização |
| F1.6 | CLI Básico | Interface de linha de comando para execução |
| F1.7 | Export CSV | Exportação de resultados para CSV |

#### Critérios de Sucesso

| Critério | Métrica | Target |
|----------|---------|--------|
| CS1.1 | Tempo de backtest (1 ano H1) | < 5 segundos |
| CS1.2 | Precisão de execução vs MT5 | > 99% |
| CS1.3 | Cobertura de testes | > 70% |
| CS1.4 | Documentação CLI | Completa |

#### Entregáveis
- [ ] Repositório GitHub público
- [ ] Pacote pip instalável
- [ ] Documentação técnica
- [ ] 3 notebooks de exemplo

### 8.3 Fase 2: App Dev-Focused (v0.5.0) - Q1 2025

#### Objetivo
Evoluir para aplicação desktop/web com foco em desenvolvedores quantitativos, adicionando ML, validação estatística e API.

#### Funcionalidades

| ID | Funcionalidade | Descrição |
|----|----------------|-----------|
| F2.1 | GUI Desktop (Electron/Tauri) | Interface gráfica multiplataforma |
| F2.2 | Feature Engineering Avançado | 50+ features técnicas automatizadas |
| F2.3 | Detecção de Regimes (HMM) | Hidden Markov Models para classificação de mercado |
| F2.4 | Reconhecimento de Padrões | ML para identificar padrões de candlestick |
| F2.5 | Walk-Forward Analysis | Implementação WFA básica |
| F2.6 | API REST | Endpoints para integração externa |
| F2.7 | Jupyter Integration | Exportação de análises para notebooks |
| F2.8 | Sistema de Plugins | Arquitetura para estratégias customizadas |
| F2.9 | Logging Avançado | Logs detalhados de todas as operações |
| F2.10 | Cache de Dados | Sistema de cache para dados históricos |

#### Critérios de Sucesso

| Critério | Métrica | Target |
|----------|---------|--------|
| CS2.1 | Usuários beta ativos | > 10 quants |
| CS2.2 | Tempo de análise completa | < 10 minutos |
| CS2.3 | Precisão regime detection | > 75% |
| CS2.4 | Uptime API | > 99% |
| CS2.5 | NPS dos usuários beta | > 50 |

#### Entregáveis
- [ ] Aplicativo instalável (Windows/Mac/Linux)
- [ ] API documentada (Swagger/OpenAPI)
- [ ] 10+ estratégias de exemplo
- [ ] Tutorial em vídeo

### 8.4 Fase 3: App Trader-Friendly (v1.0.0) - Q2 2025

#### Objetivo
Tornar o produto acessível a traders não-programadores com interface visual rica, explicações intuitivas e fluxo simplificado.

#### Funcionalidades

| ID | Funcionalidade | Descrição |
|----|----------------|-----------|
| F3.1 | Dashboard Visual | Interface drag-and-drop para configuração |
| F3.2 | Gráficos Interativos | Charting avançado com marcações de padrões |
| F3.3 | Explicações em Linguagem Natural | Tradução de recomendações para texto compreensível |
| F3.4 | CPCV Completo | Combinatorial Purged Cross-Validation |
| F3.5 | Monte Carlo Avançado | Simulações com múltiplos cenários |
| F3.6 | Gerador de EA MQL4/MQL5 | Exportação automática de EAs funcionais |
| F3.7 | Ranking de Estratégias | Sistema de pontuação e comparação |
| F3.8 | Alertas e Notificações | Notificações desktop/email de oportunidades |
| F3.9 | Modo Tutorial | Onboarding guiado para novos usuários |
| F3.10 | Relatórios PDF | Geração de relatórios profissionais |
| F3.11 | Gestão de Portfolio | Acompanhamento de múltiplas estratégias |

#### Critérios de Sucesso

| Critério | Métrica | Target |
|----------|---------|--------|
| CS3.1 | Usuários ativos mensais | > 500 |
| CS3.2 | Taxa de conversão trial→pago | > 15% |
| CS3.3 | Tempo até primeira análise | < 5 minutos |
| CS3.4 | Satisfação geral (CSAT) | > 4.0/5.0 |
| CS3.5 | Taxa de churn mensal | < 10% |

#### Entregáveis
- [ ] Versão 1.0 estável
- [ ] Site com planos de assinatura
- [ ] Programa de afiliados
- [ ] Suporte via chat/email

### 8.5 Fase 4: Live Assist (v2.0.0) - Q3 2025

#### Objetivo
Adicionar recursos de tempo real, integração profunda com MT4/MT5 e assistência ativa durante o trading.

#### Funcionalidades

| ID | Funcionalidade | Descrição |
|----|----------------|-----------|
| F4.1 | Modo Consulta Rápida | Atalho global para recomendação instantânea |
| F4.2 | Sincronização MT em Tempo Real | Conexão persistente com MT4/MT5 |
| F4.3 | Alertas de Mudança de Regime | Notificação quando mercado muda de regime |
| F4.4 | Degradação de Performance | Monitoramento de estratégias em produção |
| F4.5 | Reinicialização Automática | Sugestão de reotimização quando necessário |
| F4.6 | Cloud Sync | Sincronização de configurações entre dispositivos |
| F4.7 | Comunidade/Sharing | Compartilhamento de estratégias entre usuários |
| F4.8 | Backtesting Distribuído | Processamento em nuvem para análises pesadas |
| F4.9 | Mobile Companion | App móvel para acompanhamento |
| F4.10 | Machine Learning Contínuo | Retreinamento automático dos modelos |

#### Critérios de Sucesso

| Critério | Métrica | Target |
|----------|---------|--------|
| CS4.1 | Usuários pagantes | > 2.000 |
| CS4.2 | MRR (Monthly Recurring Revenue) | > $50k |
| CS4.3 | Tempo de resposta consulta rápida | < 3 segundos |
| CS4.4 | Estratégias compartilhadas | > 1.000 |
| CS4.5 | NPS geral | > 70 |

#### Entregáveis
- [ ] Plataforma completa SaaS
- [ ] App móvel (iOS/Android)
- [ ] Marketplace de estratégias
- [ ] API pública para desenvolvedores

### 8.6 Resumo do Roadmap

| Fase | Versão | Período | Foco Principal | Persona Target |
|------|--------|---------|----------------|----------------|
| **1** | v0.1.0 | Q4 2024 | Viabilidade técnica | Ricardo (Validação) |
| **2** | v0.5.0 | Q1 2025 | Automação + ML | Ricardo (Principal) |
| **3** | v1.0.0 | Q2 2025 | Usabilidade + Export | Marina + Carlos |
| **4** | v2.0.0 | Q3 2025 | Tempo real + Cloud | Todas as personas |

### 8.7 Dependências entre Fases

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   FASE 1    │────▶│   FASE 2    │────▶│   FASE 3    │────▶│   FASE 4    │
│   POC CLI   │     │  Dev-Focus  │     │   Trader    │     │ Live Assist │
└─────────────┘     └─────────────┘     │  Friendly   │     └─────────────┘
                                        └─────────────┘
     │                    │                  │               │
     ▼                    ▼                  ▼               ▼
┌─────────┐         ┌─────────┐        ┌─────────┐      ┌─────────┐
│Conector │         │  GUI    │        │  UX/UI  │      │  Cloud  │
│  MT5    │         │ Desktop │        │Polished │      │  Infra  │
└─────────┘         └─────────┘        └─────────┘      └─────────┘
     │                    │                  │               │
┌─────────┐         ┌─────────┐        ┌─────────┐      ┌─────────┐
│ Backtest│         │   ML    │        │  Gerador│      │  Real   │
│  Básico │         │  HMM    │        │   EA    │      │  Time   │
└─────────┘         └─────────┘        └─────────┘      └─────────┘
```

---

## 9. Fluxo de Navegação

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

## 10. Especificação da Tela "Histórico & Estratégia Ideal"

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

## 11. Design System

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

## Apêndice A: Glossário

| Termo | Definição |
|-------|-----------|
| **Backtest** | Simulação de execução de uma estratégia de trading em dados históricos para avaliar sua performance |
| **CAGR** | Compound Annual Growth Rate - taxa de crescimento anual composta |
| **CPCV** | Combinatorial Purged Cross-Validation - validação cruzada para séries temporais com purging e embargo |
| **Drawdown** | Queda percentual do valor de pico até o vale em uma série de retornos |
| **EA** | Expert Advisor - programa automatizado para execução de estratégias no MT4/MT5 |
| **Feature** | Variável de entrada utilizada por modelos de machine learning |
| **Feature Engineering** | Processo de criação e seleção de variáveis relevantes para modelos ML |
| **HMM** | Hidden Markov Model - modelo estatístico para detecção de regimes de mercado |
| **IS** | In-Sample - dados usados para treinamento/otimização |
| **LSTM** | Long Short-Term Memory - arquitetura de rede neural recorrente para séries temporais |
| **Max Drawdown** | Maior queda do pico até o vale no equity curve |
| **OHLCV** | Open, High, Low, Close, Volume - formato padrão de dados de candles |
| **OOS** | Out-of-Sample - dados não vistos durante treinamento/otimização |
| **Overfitting** | Ajuste excessivo do modelo aos dados de treino, prejudicando generalização |
| **PBO** | Probability of Backtest Overfitting - probabilidade de overfitting em backtests |
| **Profit Factor** | Razão entre ganhos brutos e perdas brutas |
| **Regime de Mercado** | Estado característico do mercado (tendência, range, volatilidade) |
| **Sharpe Ratio** | Retorno ajustado ao risco (retorno / desvio padrão) |
| **Sortino Ratio** | Variante do Sharpe que considera apenas desvio negativo |
| **Tick** | Registro individual de trade (preço, volume, timestamp) |
| **Timeframe** | Intervalo temporal dos candles (M1, H1, D1, etc.) |
| **WFA** | Walk-Forward Analysis - validação com janelas temporais rolantes |
| **WFE** | Walk-Forward Efficiency - métrica de robustez da estratégia |

---

## Apêndice B: Referências

### Documentação Técnica

| Recurso | URL | Descrição |
|---------|-----|-----------|
| VectorBT | https://vectorbt.dev/ | Framework de backtesting vetorizado |
| Backtrader | https://www.backtrader.com/ | Framework event-driven de backtesting |
| pandas-ta | https://github.com/twopirllc/pandas-ta | Biblioteca de indicadores técnicos |
| XGBoost | https://xgboost.readthedocs.io/ | Framework de gradient boosting |
| LightGBM | https://lightgbm.readthedocs.io/ | Framework de gradient boosting (Microsoft) |
| hmmlearn | https://hmmlearn.readthedocs.io/ | Implementação de HMM |
| Optuna | https://optuna.org/ | Framework de otimização de hiperparâmetros |

### Livros e Papers

| Referência | Autor | Tópico |
|------------|-------|--------|
| "Advances in Financial Machine Learning" | Marcos Lopez de Prado | ML em finanças, CPCV |
| "Machine Learning for Algorithmic Trading" | Stefan Jansen | ML para trading |
| "Evidence-Based Technical Analysis" | David Aronson | Validação estatística |

### APIs e Integrações

| Serviço | Documentação | Uso |
|---------|--------------|-----|
| MetaTrader 5 | https://www.mql5.com/ | Conexão e execução |
| Yahoo Finance | https://pypi.org/project/yfinance/ | Dados históricos |
| Dukascopy | https://www.dukascopy.com/ | Dados tick |

### Ferramentas de Desenvolvimento

| Categoria | Ferramenta | URL |
|-----------|------------|-----|
| Container | Docker | https://docs.docker.com/ |
| Orquestração | Docker Compose | https://docs.docker.com/compose/ |
| Cache | Redis | https://redis.io/documentation |
| Database | TimescaleDB | https://docs.timescale.com/ |
| API | FastAPI | https://fastapi.tiangolo.com/ |

---

*Documento gerado em: Janeiro 2025*
*Versão: 1.0*
*Status: Documento Consolidado Final*

**Arquivos Fonte:**
- Seção 1-3, 8: `/mnt/okcomputer/output/prd_visao_escopo_produto.md`
- Seção 4-7: `/mnt/okcomputer/output/PRD_Arquitetura_Requisitos_Tecnicos.md`
- Seção 9-11: `/mnt/okcomputer/output/PRD_Interface_Estrategia_Ideal.md`
