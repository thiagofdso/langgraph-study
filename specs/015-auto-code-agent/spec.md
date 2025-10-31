# Feature Specification: Simplified Code Generation Loop

**Feature Branch**: `015-auto-code-agent`
**Created**: October 30, 2025
**Status**: Draft (Revised October 31, 2025)
**Input**: Desenvolver em `agente_codigo/main.py` um agente LangGraph inspirado no tutorial oficial do LangGraph Code Assistant. O agente deve operar inteiramente em memória, mantendo um histórico de mensagens e um contador de iterações. A cada ciclo ele gera código com o modelo `gemini-2.5-flash`, executa esse código, decide se deve refletir sobre erros e interrompe o loop quando obtiver sucesso ou alcançar o limite máximo de 5 tentativas. O código gerado permanece em variáveis (não salvar em disco) e o resultado final é impresso no console.

**Prompt de Teste Inicial**: A primeira execução do agente deve iniciar com o seguinte prompt para o nó de geração de código:
```
Desenvolva um script didático em Python que explore as principais estruturas de dados (listas, tuplas, conjuntos, dicionários, pilhas, filas e lista encadeada) em um único arquivo. 

Requisitos:
- Implemente classes ou funções para cada estrutura quando fizer sentido.
- Inclua exemplos de uso demonstrando inserção, remoção, busca e exibição dos dados.
- Adicione comentários explicativos destacando conceitos chave.
- Forneça exercícios em forma de TODOs comentados para que estudantes possam expandir o conteúdo.
- Exponha uma função `run_demo()` que execute todos os exemplos e chame essa função em `if __name__ == "__main__"`.

Formato de saída desejado:
- Código Python bem estruturado e comentado em uma string única.
- Seções separadas por comentários indicando cada estrutura de dados.
``` 

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Loop de Geração e Execução (Priority: P1)

Um instrutor executa `python agente_codigo/main.py` para iniciar o agente. O nó de geração cria o script, armazena o conteúdo no estado e incrementa o contador de iterações. O nó de execução roda o script em memória e registra o resultado no estado. Se o retorno for bem-sucedido, o nó de decisão finaliza o fluxo e o código final é impresso no console.

**Independent Test**: Executar o agente e verificar que, quando o script roda sem erros antes de atingir 5 tentativas, o processo encerra imediatamente exibindo o código final gerado.

### User Story 2 - Correção Orientada por Reflexão (Priority: P1)

Quando a execução falha (ex.: exceção em tempo de execução), o nó de decisão direciona a saída para o nó de reflexão. O nó de reflexão, usando `gemini-2.5-flash`, recebe o código atual e a mensagem de erro, produzindo um feedback separado do histórico principal. O nó de geração utiliza tanto o histórico de mensagens quanto o feedback da reflexão na próxima tentativa.

**Independent Test**: Forçar um erro (por exemplo, simulando uma exceção no script) e confirmar que o agente reutiliza o feedback de reflexão na próxima iteração, mantendo o contador correto.

### User Story 3 - Controle Seguro do Ciclo (Priority: P2)

Um operador ajusta as constantes internas de `agente_codigo/main.py` (com destaque para `MAX_ITERATIONS = 5`) e garante que nenhuma artefato em disco seja criado durante a execução. O nó de decisão encerra o fluxo quando o limite é atingido, imprimindo o motivo no console.

**Independent Test**: Definir o script para falhar consecutivamente, executar o agente e confirmar que após 5 iterações o processo encerra com status "limite atingido" e apenas o histórico em memória é utilizado.

### Edge Cases

- Ausência da variável `GEMINI_API_KEY` no ambiente ou falha ao carregar o `.env`.
- Exceções inesperadas durante a execução do script (ex.: erros de sintaxe ou loops infinitos).
- Resposta não estruturada do modelo (JSON inválido) exigindo novo prompt orientativo.
- Execução bem-sucedida na primeira tentativa (contador deve permanecer consistente e fluxo deve finalizar imediatamente).
- Reflexão retornando conteúdo vazio; a iteração seguinte deve prosseguir apenas com o histórico de mensagens.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O agente DEVE usar LangGraph com nós explícitos de geração, execução, decisão e reflexão conectados conforme o tutorial oficial.
- **FR-002**: O nó de geração DEVE utilizar `gemini-2.5-flash`, receber o histórico completo de mensagens e o resultado da reflexão, armazenar o código em memória e incrementar um contador de iterações no estado.
- **FR-003**: O nó de execução DEVE executar o código diretamente a partir da string mantida no estado, capturando stdout, stderr e exceções sem gravar arquivos.
- **FR-004**: O nó de decisão DEVE analisar o retorno da execução e o contador, finalizando o fluxo quando `return_code == 0` ou quando `iteration_count >= 5`; caso contrário, DEVE encaminhar para o nó de reflexão quando houver erro.
- **FR-005**: O nó de reflexão DEVE usar `gemini-2.5-flash` para produzir feedback textual a partir do código atual e da mensagem de erro, armazenando-o separadamente do histórico principal.
- **FR-006**: O agente DEVE imprimir no console o status de cada iteração e, ao final, exibir o código completo da última geração.
- **FR-007**: Nenhum arquivo DEVE ser criado, modificado ou lido fora de `agente_codigo/.env`; todo conteúdo permanece em variáveis em memória.
- **FR-008**: O agente DEVE manter memória de execução (similar ao `InMemorySaver` usado em `agente_memoria/main.py`) para preservar o histórico entre invocações dentro do mesmo thread.
- **FR-009**: A execução inicial DEVE utilizar o prompt definido em "Prompt de Teste Inicial" e oferecer meios de rodar novos prompts apenas ajustando o estado inicial.

### Success Criteria *(mandatory)*

- **SC-001**: Em 95% dos testes internos, o agente interrompe o loop antes ou exatamente na quinta iteração, respeitando o contador e as condições de saída.
- **SC-002**: Em 100% das execuções, o console mostra a sequência de iterações com status (sucesso, erro, limite) e o código final gerado.
- **SC-003**: Em 100% das execuções bem-sucedidas, o código impresso pode ser executado diretamente (por exemplo, via `python -c "..."`).
- **SC-004**: Em 100% das falhas consecutivas, o agente exibe claramente que o limite de 5 tentativas foi atingido e encerra sem criar arquivos.

## Assumptions

- `gemini-2.5-flash` permanecerá disponível e configurado via `GEMINI_API_KEY` em `agente_codigo/.env`.
- O ambiente possui Python 3.12 e bibliotecas `langgraph`, `langchain-core` e `langchain-google-genai` já instaladas.
- Os testes se concentram em validar o fluxo iterativo; não há persistência de logs, apenas impressão em console.
- A execução do código em memória utiliza `exec` ou mecanismo equivalente seguro para scripts provisórios.
- A funcionalidade poderá evoluir posteriormente para gravar artefatos em disco, mas esta iteração permanece estritamente em memória.
