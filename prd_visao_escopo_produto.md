# Product Requirements Document (PRD)
## Sistema de Análise e Recomendação de Estratégias de Trading

---

# 1. Visão do Produto

## 1.1 Declaração de Visão

> **Para** traders quantitativos, desenvolvedores e traders discrecionários avançados **que** precisam identificar padrões de mercado e otimizar estratégias de trading, **o** Sistema de Análise e Recomendação de Estratégias **é uma** plataforma desktop/web **que** conecta-se ao MetaTrader 4/5 via Python, executa backtests robustos em múltiplas estratégias e utiliza Machine Learning para reconhecer padrões recorrentes. **Diferentemente de** plataformas tradicionais de backtesting ou otimizadores de EA, **nosso produto** oferece recomendações inteligentes de configurações de estratégia validadas por técnicas anti-overfitting (WFA, CPCV, Monte Carlo), gerando automaticamente EAs parametrizados prontos para deploy.

## 1.2 Objetivos do Produto

| Objetivo | Descrição | Métrica de Sucesso |
|----------|-----------|-------------------|
| **OBJ-001** | Automatizar a descoberta de padrões recorrentes em ativos/timeframes | >80% de precisão na identificação de regimes de mercado |
| **OBJ-002** | Reduzir tempo de desenvolvimento de estratégias viáveis | De semanas para <30 minutos por ativo/timeframe |
| **OBJ-003** | Eliminar overfitting através de validação estatística rigorosa | <5% de degradação de performance entre treino e teste |
| **OBJ-004** | Democratizar acesso a técnicas quantitativas avançadas | Usuários sem background de programação conseguem operar |
| **OBJ-005** | Gerar EAs exportáveis diretamente para MT4/MT5 | 100% das estratégias aprovadas exportáveis em MQL4/MQL5 |

## 1.3 Proposta de Valor

### Valor Principal
**"Um trader experiente analisando seu gráfico 24/7"**

O produto simula a experiência de ter um trader sênior analisando o mercado, identificando padrões, sugerindo setups, calibrando parâmetros e validando estratégias - tudo de forma automatizada e baseada em dados.

### Pilares de Valor

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

## 1.4 Diferenciais Competitivos

| Diferencial | Descrição | Concorrência |
|-------------|-----------|--------------|
| **Reconhecimento de Padrões com ML** | Algoritmos de ML identificam regimes de mercado e padrões recorrentes automaticamente | Ferramentas tradicionais usam apenas indicadores técnicos fixos |
| **Validação Anti-Overfitting Integrada** | WFA, CPCV e Monte Carlo embutidos no pipeline de validação | Requerem implementação manual ou ferramentas separadas |
| **Geração Automática de EA** | Exportação direta para MQL4/MQL5 com parâmetros otimizados | Geralmente requer programação manual do EA |
| **Integração Python + MT4/MT5** | Ponte nativa entre ecossistema Python e MetaTrader | Soluções fragmentadas ou limitadas |
| **Artefatos Acessíveis** | Código, logs, CSVs e notebooks disponíveis para usuários avançados | Caixa-preta na maioria das soluções |
| **Dual Interface** | Tanto visual (GUI) quanto programática (API/CLI) | Foco exclusivo em uma das abordagens |

## 1.5 Posicionamento no Mercado

```
                    COMPLEXIDADE TÉCNICA
                    Baixa ◄─────────────────► Alta
                    
    ┌─────────────────────────────────────────────────────┐
    │                                                     │
Alta│  TradingView        │   ████████████████           │
    │  (Análise Visual)   │   Nosso Produto              │
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

# 2. Personas

## 2.1 Persona 1: Ricardo "Quant" Silva

| Atributo | Descrição |
|----------|-----------|
| **Nome** | Ricardo Silva |
| **Apelido** | Quant Dev |
| **Idade** | 32 anos |
| **Formação** | Engenharia/Ciência da Computação ou Física |
| **Experiência** | 5+ anos em trading quantitativo |
| **Localização** | São Paulo/SP ou remoto |

### Perfil
Ricardo é um desenvolvedor quantitativo que trabalha em mesa de trading ou de forma independente. Ele prefere ter controle total sobre seu pipeline de análise e valoriza a capacidade de inspecionar, modificar e estender o código. Usa Python diariamente e está familiarizado com bibliotecas como pandas, numpy, scikit-learn e backtrader.

### Objetivos
- Iterar rapidamente em novas ideias de estratégias
- Ter acesso aos artefatos brutos (código, logs, CSVs, notebooks)
- Integrar o sistema com seu pipeline existente de ML
- Automatizar completamente o workflow de descoberta de alpha
- Publicar papers ou artigos baseados em suas análises

### Frustrações
- Plataformas que funcionam como "caixa-preta" sem acesso ao código
- Ferramentas que limitam a customização de algoritmos
- Necessidade de reimplementar validações estatísticas manualmente
- Dificuldade em reproduzir resultados entre diferentes ambientes
- Interfaces visuais que não permitem scripting ou batch processing

### Necessidades
- [ ] API REST/GraphQL completa
- [ ] Acesso ao código-fonte dos algoritmos de ML
- [ ] Exportação de notebooks Jupyter com análises
- [ ] CLI para automação e scripts
- [ ] Documentação técnica detalhada
- [ ] Possibilidade de injetar estratégias customizadas em Python

### Citação Típica
> *"Eu preciso ver o código por trás das recomendações. Se não consigo reproduzir e modificar, não serve para o meu workflow."*

---

## 2.2 Persona 2: Marina Torres

| Atributo | Descrição |
|----------|-----------|
| **Nome** | Marina Torres |
| **Apelido** | Trader Discrecionário Avançado |
| **Idade** | 41 anos |
| **Formação** | Administração/Economia ou autodidata |
| **Experiência** | 8+ anos em trading, migração para quant |
| **Localização** | Curitiba/PR |

### Perfil
Marina é uma trader experiente que começou no trading discrecionário e agora busca incorporar análise quantitativa em seu processo. Ela entende bem de análise técnica, price action e gerenciamento de risco, mas não tem background de programação. Valoriza visualização clara e interpretabilidade das recomendações.

### Objetivos
- Identificar padrões no gráfico sem precisar programar
- Receber sugestões de setup com explicação do racional
- Validar suas intuições de trading com dados estatísticos
- Aprender conceitos quantitativos de forma prática
- Tomar decisões informadas baseadas em backtests robustos

### Frustrações
- Cursos e ferramentas que exigem conhecimento de programação
- Resultados de backtests que parecem "bons demais para ser verdade"
- Falta de transparência sobre como as recomendações são geradas
- Interfaces complexas e sobrecarregadas de informações
- Dificuldade em confiar em estratégias geradas automaticamente

### Necessidades
- [ ] Interface visual intuitiva com gráficos interativos
- [ ] Padrões marcados diretamente no gráfico
- [ ] Explicação em linguagem natural das recomendações
- [ ] Métricas de performance claras e interpretáveis
- [ ] Alertas e notificações sobre oportunidades
- [ ] Tutoriais e tooltips educacionais

### Citação Típica
> *"Eu quero ver o padrão no gráfico, entender por que essa estratégia foi sugerida e ter confiança nos números - sem precisar escrever uma linha de código."*

---

## 2.3 Persona 3: Carlos Mendes

| Atributo | Descrição |
|----------|-----------|
| **Nome** | Carlos Mendes |
| **Apelido** | Trader de Robôs |
| **Idade** | 38 anos |
| **Formação** | Engenharia ou TI |
| **Experiência** | 6+ anos operando EAs no MT4/MT5 |
| **Localização** | Florianópolis/SC |

### Perfil
Carlos opera exclusivamente com Expert Advisors (EAs) no MetaTrader. Ele tem conhecimento básico de MQL4/MQL5 e consegue fazer ajustes simples em EAs existentes, mas prefere não desenvolver estratégias do zero. Sua principal preocupação é a robustez e a validação estatística das estratégias antes de colocá-las em produção.

### Objetivos
- Transformar recomendações em EAs funcionais rapidamente
- Validar estratégias com testes rigorosos antes de operar
- Otimizar parâmetros de EAs existentes
- Gerenciar múltiplas estratégias em diferentes ativos
- Minimizar tempo entre ideia e deploy em conta real

### Frustrações
- Processo manual e demorado de otimização de parâmetros
- Dificuldade em identificar overfitting em backtests
- Necessidade de múltiplas ferramentas no workflow
- Problemas de compatibilidade entre plataformas
- Falta de confiança em estratégias não validadas estatisticamente

### Necessidades
- [ ] Exportação direta para MQL4/MQL5
- [ ] Arquivos de configuração JSON/YAML
- [ ] Relatórios de validação prontos para auditoria
- [ ] Comparação lado-a-lado de múltiplas estratégias
- [ ] Integração direta com MT4/MT5 para forward testing
- [ ] Alertas de degradação de performance em tempo real

### Citação Típica
> *"Eu quero clicar em 'exportar para EA' e ter um arquivo MQL pronto para compilar e rodar no meu MT5, com a certeza de que passou nos testes estatísticos."*

---

## 2.4 Resumo Comparativo das Personas

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

# 3. Casos de Uso

## 3.1 UC-001: Descoberta Automática de Estratégias Viáveis

| Campo | Descrição |
|-------|-----------|
| **ID** | UC-001 |
| **Nome** | Descoberta Automática de Estratégias Viáveis |
| **Ator Principal** | Ricardo (Quant Dev) / Marina (Trader Discrecionária) |
| **Atores Secundários** | Sistema de ML, MT4/MT5 Connector |
| **Frequência** | Alta (diária/semanal) |
| **Prioridade** | Alta |

### Descrição
O usuário seleciona um símbolo (ativo) e timeframe, e o sistema realiza automaticamente o download de dados históricos, gera features técnicas, executa backtests massivos em múltiplas estratégias candidatas e retorna um ranking das estratégias mais viáveis para aquele contexto de mercado.

### Pré-condições
1. Usuário está autenticado no sistema
2. Conexão com MT4/MT5 está configurada e ativa OU dados históricos estão disponíveis localmente
3. Bibliotecas Python necessárias estão instaladas
4. Configurações de risco e capital estão definidas

### Fluxo Principal

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

### Fluxos Alternativos

**FA-001: Dados indisponíveis**
- Se os dados não estiverem disponíveis no MT4/MT5, o sistema tenta fontes alternativas (Yahoo Finance, broker APIs)
- Se nenhuma fonte disponível, notifica usuário com instruções

**FA-002: Nenhuma estratégia viável encontrada**
- Sistema expande automaticamente o espaço de busca
- Notifica usuário sobre ajustes sugeridos nos critérios

### Pós-condições
1. Ranking de estratégias está disponível para visualização
2. Dados e resultados estão salvos no banco de dados/histórico
3. Estratégias podem ser selecionadas para validação aprofundada
4. Artefatos (CSVs, logs) disponíveis para download

### Requisitos Funcionais Relacionados
- RF-001, RF-002, RF-003, RF-004, RF-005

---

## 3.2 UC-002: Análise de Padrões e Regimes de Mercado

| Campo | Descrição |
|-------|-----------|
| **ID** | UC-002 |
| **Nome** | Análise de Padrões e Regimes de Mercado |
| **Ator Principal** | Marina (Trader Discrecionária) |
| **Atores Secundários** | Sistema de ML, Visualizador de Gráficos |
| **Frequência** | Alta (diária) |
| **Prioridade** | Alta |

### Descrição
O usuário acessa a tela "Histórico & Padrões" onde visualiza o gráfico do ativo com padrões detectados pelo ML marcados visualmente, regimes de mercado identificados (trending, ranging, volatile), e recebe sugestões de estratégias com parâmetros otimizados para o contexto atual.

### Pré-condições
1. Dados históricos do ativo/timeframe estão disponíveis
2. Modelos de ML para detecção de padrões estão treinados/carregados
3. Análise de regimes (HMM) foi executada previamente

### Fluxo Principal

| Passo | Ator | Ação |
|-------|------|------|
| 1 | Usuário | Navega para tela "Histórico & Padrões" |
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

### Fluxos Alternativos

**FA-001: Padrão não reconhecido**
- Usuário pode marcar manualmente um padrão
- Sistema aprende com feedback para futuras detecções

**FA-002: Regime em transição**
- Sistema indica probabilidade de mudança de regime
- Alerta sobre incerteza nas recomendações

### Pós-condições
1. Visualização do gráfico com anotações está disponível
2. Sugestões de estratégias foram apresentadas
3. Histórico de análise foi salvo
4. Usuário pode exportar imagem ou relatório

### Requisitos Funcionais Relacionados
- RF-006, RF-007, RF-008, RF-009

---

## 3.3 UC-003: Validação Anti-Overfitting de Estratégia

| Campo | Descrição |
|-------|-----------|
| **ID** | UC-003 |
| **Nome** | Validação Anti-Overfitting de Estratégia |
| **Ator Principal** | Carlos (Trader de Robôs) / Ricardo (Quant Dev) |
| **Atores Secundários** | Motor de Validação Estatística |
| **Frequência** | Média (semanal) |
| **Prioridade** | Alta |

### Descrição
O usuário seleciona uma estratégia candidata do ranking e executa o pipeline completo de validação anti-overfitting, incluindo Walk-Forward Analysis (WFA), Combinatorial Purged Cross-Validation (CPCV) e testes de Monte Carlo. Estratégias aprovadas são salvas como "modelos aprovados".

### Pré-condições
1. Estratégia candidata foi previamente identificada (UC-001)
2. Dados históricos suficientes para validação (mínimo 2 anos recomendado)
3. Parâmetros de validação configurados

### Fluxo Principal

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

### Critérios de Aprovação

| Teste | Critério Mínimo | Critério Ideal |
|-------|-----------------|----------------|
| WFA | CAGR > 0 no out-of-sample | CAGR out > 70% CAGR in |
| CPCV | Média Sharpe > 1 | Média Sharpe > 1.5 |
| Monte Carlo | 95% dos cenários lucrativos | 99% dos cenários lucrativos |
| PBO | < 50% | < 20% |

### Pós-condições
1. Relatório de validação completo está disponível
2. Estratégia foi classificada como aprovada/reprovada
3. Se aprovada, estratégia entra no catálogo de modelos aprovados
4. Artefatos de validação salvos para auditoria futura

### Requisitos Funcionais Relacionados
- RF-010, RF-011, RF-012, RF-013

---

## 3.4 UC-004: Exportação para EA MT4/MT5

| Campo | Descrição |
|-------|-----------|
| **ID** | UC-004 |
| **Nome** | Exportação para EA MT4/MT5 |
| **Ator Principal** | Carlos (Trader de Robôs) |
| **Atores Secundários** | Gerador de Código MQL, Sistema de Arquivos |
| **Frequência** | Média (semanal) |
| **Prioridade** | Alta |

### Descrição
O usuário exporta uma estratégia aprovada para um Expert Advisor (EA) funcional em MQL4 ou MQL5, pronto para compilação e execução no MetaTrader. Alternativamente, pode exportar arquivo de configuração JSON/YAML para integração com EAs existentes.

### Pré-condições
1. Estratégia foi aprovada no pipeline de validação (UC-003)
2. Tipo de exportação foi selecionado (MQL4/MQL5/JSON/YAML)
3. Diretório de destino está configurado ou acessível

### Fluxo Principal

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

### Formatos de Exportação

| Formato | Conteúdo | Caso de Uso |
|---------|----------|-------------|
| **MQL4** | EA completo em MQL4 | Deploy direto no MT4 |
| **MQL5** | EA completo em MQL5 | Deploy direto no MT5 |
| **JSON** | Parâmetros estruturados | Integração com EA existente |
| **YAML** | Parâmetros + metadados | Versionamento e CI/CD |

### Pós-condições
1. Arquivo exportado está disponível no diretório especificado
2. Código gerado passou em validação sintática
3. Registro de exportação foi salvo
4. Instruções de uso foram apresentadas

### Requisitos Funcionais Relacionados
- RF-014, RF-015, RF-016

---

## 3.5 UC-005: Consulta Rápida de Recomendação

| Campo | Descrição |
|-------|-----------|
| **ID** | UC-005 |
| **Nome** | Consulta Rápida de Recomendação |
| **Ator Principal** | Marina (Trader Discrecionária) / Carlos (Trader de Robôs) |
| **Atores Secundários** | MT4/MT5 Connector, Sistema de ML |
| **Frequência** | Muito Alta (múltiplas vezes ao dia) |
| **Prioridade** | Média |

### Descrição
No modo "consulta rápida", o usuário está analisando um gráfico no MT4/MT5, clica no app e recebe instantaneamente uma recomendação de estratégia para o ativo/timeframe atual, sem necessidade de navegar por múltiplas telas ou configurar parâmetros.

### Pré-condições
1. App está em execução (em segundo plano ou minimizado)
2. MT4/MT5 está aberto com gráfico ativo
3. Conexão entre app e MT4/MT5 está estabelecida
4. Dados do ativo/timeframe atual são detectáveis

### Fluxo Principal

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

### Fluxos Alternativos

**FA-001: Análise em cache**
- Se análise recente existe em cache, retorna imediatamente
- Indica ao usuário a idade da análise

**FA-002: Ativo não suportado**
- Notifica usuário sobre limitação
- Sugere ativos similares disponíveis

### Tempo de Resposta Esperado

| Cenário | Tempo Máximo |
|---------|--------------|
| Cache hit | < 1 segundo |
| Cache miss | < 10 segundos |
| Análise completa | < 30 segundos |

### Pós-condições
1. Recomendação foi apresentada ao usuário
2. Interação foi registrada
3. Se aceita, estratégia pode ser validada/exportada
4. Feedback do usuário foi coletado (implícito ou explícito)

### Requisitos Funcionais Relacionados
- RF-017, RF-018, RF-019

---

## 3.6 Matriz de Prioridade dos Casos de Uso

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

# 8. Roadmap do Produto

## 8.1 Visão Geral das Fases

```
    2024 Q4        2025 Q1        2025 Q2        2025 Q3        2025 Q4
    ├──────────────┼──────────────┼──────────────┼──────────────┤
    │   FASE 1     │   FASE 2     │   FASE 3     │   FASE 4     │
    │   POC CLI    │   Dev-Focus  │  Trader-Friendly  │  Live Assist │
    │              │              │              │              │
    │  v0.1.0      │  v0.5.0      │  v1.0.0      │  v2.0.0      │
    └──────────────┴──────────────┴──────────────┴──────────────┘
```

---

## 8.2 Fase 1: POC CLI (v0.1.0) - Q4 2024

### Objetivo
Validar a viabilidade técnica do pipeline core: conexão MT4/MT5, backtesting, ML básico e geração de código.

### Funcionalidades

| ID | Funcionalidade | Descrição |
|----|----------------|-----------|
| F1.1 | Conector MT5 Python | Biblioteca para comunicação com MT5 via ZeroMQ |
| F1.2 | Downloader de Dados | Download OHLCV de múltiplos ativos/timeframes |
| F1.3 | Engine de Backtest | Backtest simples com métricas básicas (Profit Factor, Sharpe) |
| F1.4 | Estratégias Template | 3 estratégias de exemplo (média móvel, RSI, Bollinger) |
| F1.5 | Otimizador de Parâmetros | Grid search simples para otimização |
| F1.6 | CLI Básico | Interface de linha de comando para execução |
| F1.7 | Export CSV | Exportação de resultados para CSV |

### Critérios de Sucesso

| Critério | Métrica | Target |
|----------|---------|--------|
| CS1.1 | Tempo de backtest (1 ano H1) | < 5 segundos |
| CS1.2 | Precisão de execução vs MT5 | > 99% |
| CS1.3 | Cobertura de testes | > 70% |
| CS1.4 | Documentação CLI | Completa |

### Entregáveis
- [ ] Repositório GitHub público
- [ ] Pacote pip instalável
- [ ] Documentação técnica
- [ ] 3 notebooks de exemplo

---

## 8.3 Fase 2: App Dev-Focused (v0.5.0) - Q1 2025

### Objetivo
Evoluir para aplicação desktop/web com foco em desenvolvedores quantitativos, adicionando ML, validação estatística e API.

### Funcionalidades

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

### Critérios de Sucesso

| Critério | Métrica | Target |
|----------|---------|--------|
| CS2.1 | Usuários beta ativos | > 10 quants |
| CS2.2 | Tempo de análise completa | < 10 minutos |
| CS2.3 | Precisão regime detection | > 75% |
| CS2.4 | Uptime API | > 99% |
| CS2.5 | NPS dos usuários beta | > 50 |

### Entregáveis
- [ ] Aplicativo instalável (Windows/Mac/Linux)
- [ ] API documentada (Swagger/OpenAPI)
- [ ] 10+ estratégias de exemplo
- [ ] Tutorial em vídeo

---

## 8.4 Fase 3: App Trader-Friendly (v1.0.0) - Q2 2025

### Objetivo
Tornar o produto acessível a traders não-programadores com interface visual rica, explicações intuitivas e fluxo simplificado.

### Funcionalidades

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

### Critérios de Sucesso

| Critério | Métrica | Target |
|----------|---------|--------|
| CS3.1 | Usuários ativos mensais | > 500 |
| CS3.2 | Taxa de conversão trial→pago | > 15% |
| CS3.3 | Tempo até primeira análise | < 5 minutos |
| CS3.4 | Satisfação geral (CSAT) | > 4.0/5.0 |
| CS3.5 | Taxa de churn mensal | < 10% |

### Entregáveis
- [ ] Versão 1.0 estável
- [ ] Site com planos de assinatura
- [ ] Programa de afiliados
- [ ] Suporte via chat/email

---

## 8.5 Fase 4: Live Assist (v2.0.0) - Q3 2025

### Objetivo
Adicionar recursos de tempo real, integração profunda com MT4/MT5 e assistência ativa durante o trading.

### Funcionalidades

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

### Critérios de Sucesso

| Critério | Métrica | Target |
|----------|---------|--------|
| CS4.1 | Usuários pagantes | > 2.000 |
| CS4.2 | MRR (Monthly Recurring Revenue) | > $50k |
| CS4.3 | Tempo de resposta consulta rápida | < 3 segundos |
| CS4.4 | Estratégias compartilhadas | > 1.000 |
| CS4.5 | NPS geral | > 70 |

### Entregáveis
- [ ] Plataforma completa SaaS
- [ ] App móvel (iOS/Android)
- [ ] Marketplace de estratégias
- [ ] API pública para desenvolvedores

---

## 8.6 Resumo do Roadmap

| Fase | Versão | Período | Foco Principal | Persona Target |
|------|--------|---------|----------------|----------------|
| **1** | v0.1.0 | Q4 2024 | Viabilidade técnica | Ricardo (Validação) |
| **2** | v0.5.0 | Q1 2025 | Automação + ML | Ricardo (Principal) |
| **3** | v1.0.0 | Q2 2025 | Usabilidade + Export | Marina + Carlos |
| **4** | v2.0.0 | Q3 2025 | Tempo real + Cloud | Todas as personas |

---

## 8.7 Dependências entre Fases

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

*Documento gerado em: 2024*
*Versão: 1.0*
*Status: Rascunho para revisão*
