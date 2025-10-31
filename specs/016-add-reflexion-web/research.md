# Phase 0 Research — Reflexion Web Evidence Agent

## Decision 1: Fluxo principal com LangGraph StateGraph e agregação de mensagens
- **Decision**: Usar `StateGraph` com `TypedDict` e agregadores `add_messages` para compor o histórico de mensagens dentro da execução, além de campos para evidências e status do ciclo.
- **Rationale**: A documentação oficial mostra que `add_messages` funciona como um **reducer** para anexar novas mensagens ao estado compartilhado enquanto o grafo executa, o que é distinto do checkpointer (`InMemorySaver`) que apenas persiste o estado entre invocações. Sem o agregador, cada nó sobrescreveria o array de mensagens e perderíamos o histórico da rodada atual (`external_docs/langgraph_docs.md:149-190`). Nos agentes existentes (`agente_reflexao_basica`, `agente_memoria`), o agregador convive com o checkpointer para garantir tanto acumulação local quanto memória entre chamadas.
- **Alternatives considered**: Tentar depender apenas do `InMemorySaver` foi rejeitado porque ele não agrega mensagens automaticamente; ele salva o dicionário inteiro conforme fornecido. Confiar unicamente no checkpointer faria com que cada nó precisasse reimplementar manualmente a lógica de concatenação, aumentando o risco de inconsistências.

## Decision 2: Memória curta com InMemorySaver e thread estático
- **Decision**: Instanciar `InMemorySaver` como checkpointer ao compilar o grafo e utilizar `config = {"configurable": {"thread_id": "reflexao-web"}}` para manter estado entre nós.
- **Rationale**: A documentação de LangGraph destaca `InMemorySaver` para fluxos locais de curto prazo. O projeto `agente_memoria` demonstra essa integração para preservar conversas; replicar abordagem garante que reflexões usem histórico sem depender de armazenamento externo.
- **Alternatives considered**: Implementar armazenamento customizado em disco ou memória global; rejeitado para evitar persistência desnecessária e porque a especificação requer operação em memória.

## Decision 3: Coleta de evidências com TavilySearch e normalização de citações
- **Decision**: Reaproveitar `langchain_tavily.TavilySearch` (como em `agente_web`) para buscar fontes e armazenar `title`, `url`, `content` em estrutura própria; as reflexões e resposta final citarão as evidências pelo índice de coleta.
- **Rationale**: Tavily já está configurada no projeto, possui API simples e entrega metadados necessários para citações. Alinhar o pipeline à implementação existente reduz risco e aproveita variáveis de ambiente existentes no `.env` copiado.
- **Alternatives considered**: Usar Requests com Google Custom Search ou outra API; descartado por demandar novas credenciais e fugir do padrão estabelecido no repositório.

## Decision 4: Limite de três reflexões com verificação explícita no grafo
- **Decision**: Controlar iterações via contador no estado (`reflection_count`) e edges condicionais que encerram o fluxo após três ciclos, garantindo que o nó de reflexão só execute quando houver novas evidências.
- **Rationale**: A documentação recomenda usar condicionais para encerrar loops (`StateGraph.add_conditional_edges`). O requisito do usuário veda loops indefinidos; contador explícito facilita testes manuais e logging.
- **Alternatives considered**: Configurar limite pelo número de mensagens agregadas (similar ao `MESSAGE_LIMIT` de `agente_reflexao_basica`); descartado por ser menos direto e exigir cálculos em função do histórico completo.
