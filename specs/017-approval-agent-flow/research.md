# Phase 0 Research — Agente com Aprovação Humana

## Decision 1: Aprovação humana com `interrupt` e retomada via `Command`
- **Decision**: Utilizar `interrupt` no nó de aprovação para suspender o grafo e aguardar decisão humana, retomando com `Command(resume=...)` após a revisão.
- **Rationale**: A documentação oficial detalha que `interrupt` pausa a execução, devolve o controle ao operador e requer um checkpointer para continuar, exatamente o padrão necessário para aprovações antes de executar ferramentas. citeturn0search0
- **Reference pattern**: `agente_perguntas/main.py` já usa `interrupt` para aprovação humana de respostas FAQ; vamos replicar a coleta de inputs e a retomada usando `graph.stream(Command(resume=...))`.

## Decision 2: Condicionais para retornar ao nó inicial após validação reprovada
- **Decision**: Adicionar um campo de estado (`validation_attempts` + `is_valid`) e uma condicional que, ao detectar falha, redirecione o grafo de volta ao nó de geração inicial após a intervenção humana.
- **Rationale**: O guia de human-in-the-loop mostra que múltiplas interrupções podem validar entradas sequenciais, permitindo que o fluxo recomece do ponto de validação depois de ajustes humanos. citeturn0search2

## Decision 3: Sequência com nó de geração condicional
- **Decision**: Implementar um nó `gerar_resposta` que identifica se é a primeira execução. Na primeira passagem, ele avança para validação/aprovação; na segunda, entrega a resposta e finaliza.
- **Rationale**: O requisito explicita que o nó de geração deve direcionar primeiro à aprovação humana e depois finalizar. Estruturar a condicional no próprio nó simplifica o fluxo e evita loops extras, atendendo à restrição de não criar loop de interação.

## Decision 4: Reaproveitar ferramenta Tavily do `agente_web`
- **Decision**: Importar/configurar a mesma ferramenta Tavily usada em `agente_web/main.py` para garantir consistência de parâmetros e reaproveitar `.env` existente.
- **Rationale**: O projeto já garante variáveis de ambiente e experimento validado com Tavily; replicar evita novas dependências e atende ao pedido de "adicionar a ferramenta do projeto agente_web".

## Decision 5: Checkpointer `InMemorySaver` e estado tipado
- **Decision**: Compilar o grafo com `InMemorySaver` e um `TypedDict` que agrega mensagens/decisões, mantendo histórico necessário para retomadas e encerramentos.
- **Rationale**: A documentação reforça que interrupções exigem checkpointer para retomar do ponto correto. citeturn0search3
