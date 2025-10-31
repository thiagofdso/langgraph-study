## Casos de Uso Avançados para Estudar LangGraph

**Reflexion Pattern**: Implemente na pasta agente_reflexao_web o padrão Reflexion completo onde o agente não só reflete, mas fundamenta suas críticas em dados externos (como resultados de ferramentas de busca) e gera citações explícitas. O agente deve responder a pergunta "Como funciona o Google Agent Development Kit?" O próximo requisito é o de número 016.

[1]

Use langgraph, consulte a documentação do langgraph external_docs/langgraph_docs.md sobre praticas de uso do framework. Se baseie no projeto agente_web para consultar a internet, no projeto agente_reflexao_basica para realizar o processo de reflexão, use um limite de 3 iterações de reflexão e no projeto agente_memoria para usar memoria no nó de geração da resposta. Adicione as referências usadas na reflexão na resposta para o agente que elaborou a resposta inicial. Não adicione parametros. Não crie um loop de interação, não crie teste unitários ou testes de integração. Teste a aplicação executando o main.py, copie o .env de agente_web e não altere o .env copiado.

### **Padrões de Roteamento e Controle de Fluxo**

**Human-in-the-Loop com Validação**: Crie na pasta agente_aprovacao um workflow onde o agente pausa para aprovação humana antes de executar ferramentas, valida a entrada do usuário, e pode retornar ao loop se a validação falhar.[6][7]

Use langgraph, consulte a documentação do langgraph external_docs/langgraph_docs.md sobre praticas de uso do framework. Não adicione parametros. Não crie um loop de interação, não crie teste unitários ou testes de integração. Teste a aplicação executando o main.py, não altere o .env copiado. Consulte o projeto na pasta agente_perguntas/main.py para verificar a forma de inserir a aprovação humana, use a mesma forma para aprovar uso de uma tool. Adicione a ferramenta do projeto agente_tool/main.py. Consulte a documentação https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/ para detalhes do funcionamento do human-in-the-loop. Pesquise na internet como retornar ao loop em caso de falha na validação, salve sua consulta na pasta research.


**Roteamento com Fallback Estratégico**: Implemente um sistema que tenta diferentes estratégias sequencialmente se a primeira falhar, com lógica de fallback inteligente.[4]

### **Padrões de Execução Paralela**

**Execução Paralela de Ferramentas com Gestão de Erros**: Crie agente_error_handling um agente que executa múltiplas ferramentas assincronamente em paralelo usando `asyncio.gather`, com tratamento robusto de erros e métricas de performance.[10]

### **Padrões de Streaming e Feedback em Tempo Real**

**Streaming de Múltiplos Modos**: Implemente na pasta agente_multiplos_modos streaming usando diferentes modos (`values`, `updates`, `messages`, `custom`) para fornecer feedback granular do progresso do agente.[11][12]

**Streaming com Atualizações Customizadas**: Crie um agente na pasta agente_evento_customizado que emite eventos customizados durante a execução (como "Processando 50/100 registros") usando o modo de streaming `custom`.[13][11]

**Streaming de Tokens LLM de Subgrafos**: Implemente na pasta agente_streaming_subgrafos streaming de tokens não apenas do grafo principal, mas também de subgrafos aninhados.[11]

### **Padrões RAG Avançados**

**RAG Agêntico com Decisão de Retrieval**: Crie um agente na pasta agentic_rag que decide autonomamente se precisa buscar contexto adicional ou se pode responder diretamente, usando routing condicional.[14][15]

**Corrective RAG (CRAG)**: Implemente CRAG na pasta agente_crag onde o agente avalia a relevância dos documentos recuperados, pode reescrever a query se a recuperação falhar, e verifica se a resposta gerada faz sentido.[16][17]

**Self-RAG**: Implemente Self-RAG na pasta agente_self_rag com loops de feedback internos que filtram documentos ruins e auto-corrigem a geração.[17][18]

### **Padrões de Subgrafos e Modularidade**

**Subgrafos com Transformação de Estado**: Implemente na pasta agente_multiplos_schemas subgrafos onde o estado do grafo pai e do subgrafo têm schemas diferentes, exigindo transformação de estado na entrada e saída.[19][20]

**Subgrafos Aninhados para Multi-Agente Complexo**: Crie na pasta multi_agentes_aninhados uma  hierarquia de subgrafos onde diferentes times de agentes têm seus próprios estados isolados mas se comunicam através de chaves compartilhadas.[20][21]

**Subgrafos Reutilizáveis**: Desenvolva na pasta agentes_modulares subgrafos modulares que podem ser reutilizados em múltiplos workflows diferentes.[20]

### **Padrões de Retry e Tratamento de Erros**

**Retry com Política Customizada**: Implemente na pasta agente_retry políticas de retry automáticas para erros transientes (problemas de rede, rate limits) usando `RetryPolicy`.[22][23][24]

**Categorização e Roteamento de Erros**: Crie na pasta agente_roteamoento_erros um sistema que categoriza erros (transientes, recuperáveis por LLM, recuperáveis por humano, fatais) e roteia para diferentes handlers.[23][24]

**Circuit Breaker Pattern**: Implemente na pasta agente_circuit_breaker um padrão circuit breaker que para o loop após muitas falhas consecutivas, com backoff exponencial.[5]

### **Padrões de Time-Travel e Debugging**

**Time-Travel para Debugging**: Implemente na pasta agente_time_travel funcionalidade para navegar pelo histórico de checkpoints, visualizar estados passados, e retomar execução de pontos específicos.[25][26][27]

**Forking de Execução**: Crie na pasta agente_forking workflows onde você pode "forkar" a execução de um checkpoint passado com estado modificado para explorar caminhos alternativos.[26][28]

**Replay de Execuções**: Implemente agente_replay replay eficiente de execuções anteriores aproveitando checkpoints sem re-executar nós já processados.[28][25]

### **Padrões de Planning e Multi-Step Reasoning**

**Plan-and-Execute Agent**: Implemente agente_planejador um agente que primeiro cria um plano completo de ações, depois executa cada passo sequencialmente, com capacidade de replanejamento se algo falhar.

**Tree of Thoughts com LATS**: Implemente na pasta agente_lats Language Agent Tree Search (LATS) que explora múltiplos caminhos de raciocínio em paralelo, avalia cada caminho, e usa busca em árvore para encontrar a melhor solução.[1]

### **Padrões Avançados de ReAct**

**ReAct com Tool Calling Paralelo**: Implemente na pasta agente_tool_paralela um agente ReAct que pode executar múltiplas ferramentas em paralelo quando apropriado.[29][30][31]

**ReAct com Seleção Dinâmica de Tools**: Crie na pasta agente_tool_dinamica um agente que pode adicionar ou remover ferramentas dinamicamente durante a execução baseado no contexto.

**ReAct com Hierarchical Planning**: Combine na pasta agente_planejamento_dinamico ReAct com planning hierárquico onde o agente pode delegar sub-tarefas para agentes especializados.

### **Projetos Práticos Complexos**

**Sistema de Atendimento ao Cliente Multi-Camada**: Combine classificação de intenção, roteamento, RAG, human-in-the-loop para aprovações, e múltiplos agentes especializados.

**Assistente de Pesquisa Científica**: Implemente busca paralela em múltiplas fontes, sumarização map-reduce, reflexão para validar qualidade, e geração de relatório final.

**Code Review Agent com Auto-Correção**: Crie um agente que analisa código, executa testes, identifica problemas, sugere correções, aplica correções automaticamente, e re-testa.

**Sistema de Análise Financeira**: Implemente agentes paralelos para coletar dados de diferentes fontes, análise com ferramentas especializadas, validação de resultados, e geração de insights.

Esses casos de uso vão desde conceitos intermediários até padrões muito avançados, permitindo que você explore progressivamente as capacidades completas do LangGraph.[9][21][32][33][34][35][36][37][38][39][2][8][1]

[1](https://blog.langchain.com/reflection-agents/)
[2](https://learnopencv.com/langgraph-self-correcting-agent-code-generation/)
[3](https://langchain-ai.github.io/langgraph/tutorials/code_assistant/langgraph_code_assistant/)
[4](https://aiproduct.engineer/tutorials/langgraph-tutorial-implementing-advanced-conditional-routing-unit-13-exercise-4)
[5](https://www.swarnendu.de/blog/langgraph-best-practices/)
[6](https://langchain-ai.github.io/langgraphjs/concepts/human_in_the_loop/)
[7](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/)
[8](https://python.langchain.com/docs/versions/migrating_chains/map_reduce_chain/)
[9](https://langchain-ai.github.io/langgraphjs/how-tos/map-reduce/)
[10](https://aiproduct.engineer/tutorials/langgraph-tutorial-parallel-tool-execution-unit-23-exercise-4)
[11](https://langchain-ai.github.io/langgraph/concepts/streaming/)
[12](https://dev.to/jamesli/two-basic-streaming-response-techniques-of-langgraph-ioo)
[13](https://www.youtube.com/watch?v=a9B1POjAs9c)
[14](https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_agentic_rag/)
[15](https://www.elastic.co/search-labs/blog/build-rag-workflow-langgraph-elasticsearch)
[16](https://www.datacamp.com/tutorial/corrective-rag-crag)
[17](https://www.datacamp.com/tutorial/self-rag)
[18](https://blog.langchain.com/agentic-rag-with-langgraph/)
[19](https://langchain-ai.github.io/langgraphjs/how-tos/subgraph/)
[20](https://dev.to/sreeni5018/langgraph-subgraphs-a-guide-to-modular-ai-agents-development-31ob)
[21](https://langchain-ai.github.io/langgraph/concepts/agentic_concepts/)
[22](https://www.linkedin.com/posts/erdeepak-patidar_langgraph-langchain-aiworkflow-activity-7339294189043535872-dP83)
[23](https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph)
[24](https://aiproduct.engineer/tutorials/langgraph-tutorial-error-handling-patterns-unit-23-exercise-6)
[25](https://dragonforest.in/time-travel-in-langgraph/)
[26](https://langchain-ai.github.io/langgraph/concepts/time-travel/)
[27](https://docs.langchain.com/oss/python/langgraph/use-time-travel)
[28](https://langchain-ai.github.io/langgraphjs/concepts/time-travel/)
[29](https://github.com/langchain-ai/react-agent)
[30](https://langchain-ai.github.io/langgraph/how-tos/react-agent-from-scratch/)
[31](https://neo4j.com/blog/developer/react-agent-langgraph-mcp/)
[32](https://www.youtube.com/watch?v=1w5cCXlh7JQ)
[33](https://www.projectpro.io/article/langgraph-projects-and-examples/1124)
[34](https://www.ibm.com/think/tutorials/build-agentic-workflows-langgraph-granite)
[35](https://www.designveloper.com/blog/what-is-langgraph/)
[36](https://langchain-ai.github.io/langgraph/tutorials/workflows/)
[37](https://dev.to/jamesli/advanced-langgraph-implementing-conditional-edges-and-tool-calling-agents-3pdn)
[38](https://www.scalablepath.com/machine-learning/langgraph)
[39](https://pub.towardsai.net/agentic-design-patterns-with-langgraph-5fe7289187e6)
[40](https://www.datacamp.com/tutorial/langgraph-agents)
[41](https://langchain-ai.github.io/langgraph/concepts/why-langgraph/)
[42](https://docs.langchain.com/oss/python/langgraph/workflows-agents)
[43](https://www.linkedin.com/pulse/exploring-frontiers-ai-top-5-use-cases-langchain-dileep-kumar-pandiya-hos3e)
[44](https://www.gettingstarted.ai/langgraph-tutorial-with-example/)
[45](https://blog.langchain.com/top-5-langgraph-agents-in-production-2024/)
[46](https://latenode.com/blog/langgraph-tutorial-complete-beginners-guide-to-getting-started)
[47](https://edzor.com/blogs/langgraph-ai-applications-beginners/)
[48](https://www.youtube.com/watch?v=jGg_1h0qzaM)
[49](https://cognitiveclass.ai/courses/agentic-ai-workflow-design-patterns-with-langgraph)
[50](https://latenode.com/blog/langgraph-multi-agent-systems-complete-tutorial-examples)
[51](https://www.reddit.com/r/LangChain/comments/1g3i734/langgraph_101_tutorial_with_practical_example/)
[52](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)
[53](https://docs.langchain.com/oss/python/langgraph/use-subgraphs)
[54](https://www.youtube.com/watch?v=YmAaKKlDy7k)
[55](https://python.langchain.com/docs/how_to/output_parser_retry/)
[56](https://github.com/langchain-ai/langgraph/discussions/981)
[57](https://blog.langchain.com/making-it-easier-to-build-human-in-the-loop-agents-with-interrupt/)
[58](https://github.com/langchain-ai/langgraph/discussions/1175)
[59](https://www.youtube.com/watch?v=52oj4SPUHRA)
[60](https://www.langchain.com/langgraph)
[61](https://github.com/langchain-ai/langchain/discussions/24695)
[62](https://github.com/langchain-ai/langgraph/issues/1252)
[63](https://auth0.com/blog/async-ciba-python-langgraph-auth0/)
[64](https://veritasanalytica.ai/langgraph-ultimate-guide/)
[65](https://dev.to/vdrosatos/building-a-retrieval-augmented-generation-rag-system-with-langchain-langgraph-tavily-and-langsmith-in-typescript-mef)
[66](https://www.youtube.com/watch?v=hMHyPtwruVs)
[67](https://ai.google.dev/gemini-api/docs/langgraph-example)
[68](https://github.com/ranguy9304/LangGraphRAG)
[69](https://python.langchain.com/docs/concepts/streaming/)
[70](https://docs.langchain.com/langsmith/use-stream-react)
[71](https://python.langchain.com/docs/tutorials/rag/)
[72](https://docs.langchain.com/oss/python/langgraph/streaming)
[73](https://www.reddit.com/r/LangChain/comments/1nf6jos/react_agent_implementations_langgraph_vs_other/)
[74](https://langchain-ai.github.io/langgraph/how-tos/streaming/)
[75](https://milvus.io/blog/get-started-with-langgraph-up-react-a-practical-langgraph-template.md)
[76](https://www.youtube.com/watch?v=Zmh1X94xJKw)
[77](https://langchain-ai.github.io/langgraph/how-tos/graph-api/)
[78](https://www.reddit.com/r/LangChain/comments/1cthrqz/agents_working_in_parallel_with_langgraph/)
[79](https://langchain-ai.github.io/langgraph/concepts/low_level/)
[80](https://github.com/langchain-ai/langgraph/discussions/2212)
[81](https://forum.langchain.com/t/parallel-execution-with-supervisor-pattern/1665)
[82](https://github.com/langchain-ai/langgraph/discussions/1340)
[83](https://docs.langchain.com/langsmith/studio)
[84](https://forum.langchain.com/t/parallel-tool-calling-in-langgraph/439)
[85](https://arize.com/docs/phoenix/cookbook/agent-workflow-patterns/langgraph)
[86](https://developer.couchbase.com/tutorial-langgraph-persistence-checkpoint/)
[87](https://github.com/junfanz1/LangGraph-Reflection-Researcher)
[88](https://blog.gopenai.com/deep-dive-into-the-self-correcting-coding-assistant-with-langchain-and-langgraph-03bd6698c4fd)
[89](https://www.youtube.com/watch?v=rBWrjNyVyCA)
[90](https://www.youtube.com/watch?v=GMPFt-LrOWc)
[91](https://www.youtube.com/watch?v=JQznvlSatPQ)
[92](https://blog.langchain.com/tag/agents/)
[93](https://stackoverflow.com/questions/78959005/double-nesting-map-reduce-in-langgraph)
[94](https://towardsdatascience.com/langgraph-101-lets-build-a-deep-research-agent/)
[95](https://activewizards.com/blog/a-deep-dive-into-langgraph-for-self-correcting-ai-agents)
[96](https://github.com/langchain-ai/langgraph/discussions/609)
[97](https://www.linkedin.com/posts/suparna-guha_from-theory-to-code-mastering-agentic-workflows-activity-7372694333906534400-jbL-)


## Middlewares Disponíveis em LangGraph e Casos de Uso para Estudo

Com base na documentação oficial, o LangGraph possui um sistema robusto de middlewares que permite controlar o loop de execução dos agentes. Aqui estão todos os middlewares disponíveis e projetos práticos para você implementar e aprender.[1][2][3][4][5]

### **Middlewares Built-in Disponíveis**

#### **1. SummarizationMiddleware**
Sumariza automaticamente o histórico de conversação quando se aproxima dos limites de tokens.[2][3][1]

**Casos de uso para implementar:**
- **Chatbot de Atendimento Prolongado**: Crie um agente que mantém conversas longas e sumariza automaticamente mensagens antigas quando ultrapassar 4000 tokens
- **Assistente de Documentação**: Implemente um agente que processa documentação extensa e mantém contexto sumarizado das seções anteriores
- **Agente de Reuniões**: Desenvolva um sistema que acompanha reuniões longas e sumariza pontos anteriores periodicamente

#### **2. HumanInTheLoopMiddleware**
Pausa a execução do agente para aprovação, edição ou rejeição de chamadas de ferramentas antes da execução.[3][4][1][2]

**Casos de uso para implementar:**
- **Agente de Email Corporativo**: Sistema que pede aprovação humana antes de enviar emails mas auto-aprova leitura de emails
- **Gerenciador de Banco de Dados**: Agente que requer aprovação para operações de DELETE/UPDATE mas permite SELECT livremente
- **Sistema de Compras**: Assistente que pede confirmação humana para compras acima de determinado valor
- **Agente DevOps**: Sistema que requer aprovação para deploy em produção mas permite deploy automático em ambientes de teste

#### **3. AnthropicPromptCachingMiddleware**
Reduz custos através de cache de prefixos de prompts repetitivos com modelos Anthropic.[4][2][3]

**Casos de uso para implementar:**
- **Assistente com System Prompt Longo**: Implemente um agente com um system prompt extenso (documentação, regras de negócio) e meça a economia de tokens
- **Agente de Análise de Contratos**: Sistema que usa templates longos de análise legal repetidamente
- **Chatbot com Knowledge Base Grande**: Agente que injeta contexto extenso sobre produtos/serviços em cada chamada

#### **4. ModelCallLimitMiddleware**
Limita o número de chamadas ao modelo para prevenir loops infinitos ou custos excessivos.[3][4]

**Casos de uso para implementar:**
- **Agente com Budget**: Crie um agente limitado a 5 chamadas por execução e 20 por thread
- **Sistema de Testes**: Implemente um agente que testa funcionalidades mas tem limite de chamadas para evitar custos
- **Agente de Demonstração**: Sistema para demos que tem limites para evitar abusos

#### **5. ToolCallLimitMiddleware**
Limita chamadas a ferramentas específicas ou todas as ferramentas.[4][3]

**Casos de uso para implementar:**
- **Controle de API Externa**: Limite chamadas a uma API de busca web a 3 por execução
- **Gerenciador de Custos**: Implemente limites diferentes para ferramentas caras vs baratas
- **Rate Limiter Inteligente**: Sistema que distribui limites entre múltiplas ferramentas

#### **6. ModelFallbackMiddleware**
Fallback automático para modelos alternativos quando o modelo primário falha.[3][4]

**Casos de uso para implementar:**
- **Sistema Resiliente Multi-Provider**: Agente que tenta GPT-4, depois GPT-4-mini, depois Claude se houver falhas
- **Otimização de Custos Dinâmica**: Sistema que usa modelo caro mas faz fallback para modelo barato em caso de erro
- **Multi-Region Failover**: Agente que tenta diferentes regiões/providers automaticamente

#### **7. PIIMiddleware**
Detecta e trata informações pessoalmente identificáveis (PII) em conversações.[5][4][3]

**Casos de uso para implementar:**
- **Chatbot de Healthcare**: Sistema que detecta e mascara CPF, emails, números de telefone antes de enviar ao modelo
- **Sistema de Compliance LGPD**: Agente que bloqueia execução se detectar dados sensíveis não permitidos
- **Logger Seguro**: Sistema que redacta PII antes de fazer logging das conversas
- **Assistente Financeiro**: Agente que mascara números de cartão de crédito mas mantém últimos 4 dígitos

#### **8. TodoListMiddleware (PlanningMiddleware)**
Adiciona capacidades de gerenciamento de lista de tarefas para tarefas multi-step complexas.[3]

**Casos de uso para implementar:**
- **Assistente de Projeto**: Agente que quebra solicitações complexas em lista de todos e marca como completo conforme executa
- **Gerenciador de Refatoração de Código**: Sistema que cria plano de refatoração e executa passo a passo
- **Planejador de Eventos**: Agente que divide organização de eventos em sub-tarefas

#### **9. LLMToolSelectorMiddleware**
Usa LLM para selecionar ferramentas relevantes antes de chamar o modelo principal.[4][3]

**Casos de uso para implementar:**
- **Agente com Muitas Ferramentas**: Sistema com 20+ ferramentas que usa modelo barato para selecionar apenas 3 relevantes
- **Otimização de Contexto**: Agente que reduz tamanho do prompt filtrando ferramentas irrelevantes
- **Permissão Dinâmica**: Sistema que filtra ferramentas baseado em contexto do usuário

#### **10. ToolRetryMiddleware**
Retry automático de chamadas de ferramentas falhas com backoff exponencial configurável.[4][3]

**Casos de uso para implementar:**
- **Sistema Resiliente a Falhas de Rede**: Agente que retenta automaticamente chamadas de API que falharam por timeout
- **Gerenciador de APIs Instáveis**: Sistema com retry inteligente e backoff exponencial
- **Handler de Rate Limits**: Agente que detecta erros de rate limit e retenta com delays apropriados

#### **11. LLMToolEmulatorMiddleware**
Emula execução de ferramentas usando LLM para testes, substituindo chamadas reais por respostas geradas por IA.[3]

**Casos de uso para implementar:**
- **Ambiente de Testes**: Sistema que emula APIs caras ou indisponíveis durante desenvolvimento
- **Prototipagem Rápida**: Agente para testar workflows antes de implementar ferramentas reais
- **Demo Mode**: Sistema que simula integrações para demonstrações

#### **12. ContextEditingMiddleware**
Gerencia contexto de conversação através de trimming, sumarização ou limpeza de uso de ferramentas.[3]

**Casos de uso para implementar:**
- **Limpeza de Tentativas Falhas**: Sistema que remove tool calls falhos do contexto
- **Gerenciamento de Contexto Customizado**: Agente com estratégias personalizadas de limpeza de histórico
- **Otimização de Tokens**: Sistema que mantém apenas N últimas execuções de ferramentas

### **Middlewares Customizados - Padrões para Implementar**

#### **Decorators Disponíveis**[2][3]

**Node-style (executam em pontos específicos):**
- `@before_agent` - Antes do agente iniciar
- `@before_model` - Antes de cada chamada ao modelo
- `@after_model` - Após cada resposta do modelo
- `@after_agent` - Após agente completar

**Wrap-style (interceptam execução):**
- `@wrap_model_call` - Envolve chamadas ao modelo
- `@wrap_tool_call` - Envolve chamadas a ferramentas

**Convenience:**
- `@dynamic_prompt` - Gera prompts dinâmicos

#### **Casos de Uso para Middlewares Customizados**

**Middleware de Logging e Observabilidade:**
- Sistema que registra todas as chamadas ao modelo com timestamps e custos
- Agente que envia métricas para sistema de monitoramento (Prometheus/Grafana)
- Sistema que faz tracing distribuído de execuções

**Middleware de Autenticação e Autorização:**[6][7][8]
- Sistema que valida JWT tokens antes de permitir execução
- Agente que filtra ferramentas baseado em permissões do usuário
- Sistema multi-tenant com isolamento de recursos por usuário

**Middleware de Rate Limiting:**
- Sistema que implementa rate limiting por usuário
- Agente com throttling baseado em janelas de tempo
- Sistema com quotas diferentes por tier de usuário

**Middleware de Validação de Entrada:**
- Sistema que valida e sanitiza inputs antes de processar
- Agente que bloqueia prompts maliciosos ou injection attempts
- Sistema com validação de schema Pydantic

**Middleware de Transformação de Contexto:**
- Sistema que traduz mensagens automaticamente
- Agente que injeta contexto adicional de bases de dados
- Sistema que enriquece prompts com informações do usuário

**Middleware de Circuit Breaker:**
- Sistema que para execução após N falhas consecutivas
- Agente com degradação graciosa quando serviços externos falham
- Sistema com health checks antes de chamadas

**Middleware de Cache:**
- Sistema que cacheia respostas idênticas
- Agente com cache distribuído (Redis)
- Sistema com invalidação inteligente de cache

**Middleware de A/B Testing:**
- Sistema que roteia para diferentes modelos baseado em experimentos
- Agente que coleta métricas para comparação de modelos
- Sistema com feature flags para funcionalidades experimentais

**Middleware de Custo e Budget:**
- Sistema que rastreia custos por usuário/sessão
- Agente que alerta quando atingir limites de budget
- Sistema que muda para modelos mais baratos quando necessário

**Middleware de Segurança Avançada:**[8][9]
- Sistema com Content Security Policy para outputs
- Agente que detecta e previne prompt injection
- Sistema com sanitização de outputs sensíveis

### **Projetos Práticos Combinando Múltiplos Middlewares**

**1. Sistema Empresarial Completo:**
Combine autenticação, rate limiting, PII detection, human-in-the-loop, e logging em um sistema corporativo seguro.

**2. Assistente de Custos Otimizado:**
Use model fallback, call limits, tool selector, e prompt caching para minimizar custos.

**3. Agente de Compliance:**
Integre PII middleware, context editing, logging avançado e human approval para conformidade regulatória.

**4. Sistema Resiliente de Produção:**
Combine retry middleware, fallback, circuit breaker, e monitoring para alta disponibilidade.

**5. Plataforma Multi-Tenant:**
Implemente autenticação, autorização, rate limiting por tenant, e isolamento de dados.


https://blog.langchain.com/tag/case-studies/

Esses middlewares oferecem controle granular sobre cada etapa do loop de execução dos agentes, permitindo que você construa sistemas robustos, seguros e eficientes.[1][5][2][4][3]

[1](https://www.linkedin.com/pulse/mastering-langchain-middleware-unlocking-fine-tuned-ummadisetti-acyvc)
[2](https://docs.langchain.com/oss/python/langchain/middleware?ajs_aid=9d45355d-0fd5-4ae7-9af2-0fe2c6095284)
[3](https://docs.langchain.com/oss/python/langchain/middleware)
[4](https://colinmcnamara.com/blog/langchain-middleware-v1-alpha-guide)
[5](https://blog.langchain.com/langchain-langgraph-1dot0/)
[6](https://langchain-ai.github.io/langgraphjs/concepts/auth/)
[7](https://github.com/langchain-ai/custom-auth)
[8](https://towardsai.net/p/artificial-intelligence/securing-ai-workflows-authentication-security-for-langgraph-fastapi-part-2)
[9](https://pub.towardsai.net/securing-ai-workflows-authentication-security-for-langgraph-fastapi-part-2-8427f2aa9d20)
[10](https://milvus.io/blog/langchain-vs-langgraph.md)
[11](https://www.langchain.com/langchain)
[12](https://www.youtube.com/watch?v=r5Z_gYZb4Ns)
[13](https://langchain-ai.github.io/langgraphjs/how-tos/http/custom_middleware/)
[14](https://langchain-5e9cc07a-preview-an07au-1754595026-9c8a87e.mintlify.app/langgraph-platform/custom-middleware)
[15](https://github.com/von-development/awesome-LangGraph)
[16](https://docs.langchain.com/oss/python/langchain/runtime)
[17](https://www.ibm.com/think/topics/langgraph)
[18](https://docs.langchain.com/langsmith/custom-middleware)
[19](https://caistack.com/blog/using-langgraph-heres-why-teams-run-their-agents-on-caistack-ai-middleware/)
[20](https://www.langchain.com/langgraph)
[21](https://github.com/langchain-ai/langgraph-101)
[22](https://github.com/langchain-ai/langgraph/discussions/2527)
[23](https://langchain-ai.github.io/langgraphjs/how-tos/)
[24](https://www.youtube.com/watch?v=AZ6257Ya_70)
[25](https://docs.langchain.com/oss/python/deepagents/middleware)
[26](https://langchain-5e9cc07a-preview-brodyd-1754591744-fac1b99.mintlify.app/labs/swe/setup/authentication)
[27](https://www.youtube.com/watch?v=4Z2uBtIfmfE)
[28](https://auth0.com/blog/genai-tool-calling-build-agent-that-calls-gmail-securely-with-langgraph-vercelai-nextjs/)