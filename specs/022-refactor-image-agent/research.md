# Research Log: Refactor agente_imagem Structure

## Decision: Reutilizar nomenclatura de nodes existente e introduzir `prepare_image`
- **Rationale**: O catálogo `graph-nodes-patterns.md` define `validate_input`, `invoke_model` e `format_response` para etapas equivalentes. A tarefa T6 em `langgraph-tasks.md` exige aderência a esses nomes e acrescenta `prepare_image` para encapsular validação/encoding de imagens antes da chamada ao LLM.
- **Alternatives considered**: Manter nomes atuais (`validate_and_encode`, `parse_llm_response`) implicaria desalinhamento com os padrões e violaria o Princípio XXIII.

## Decision: Centralizar configuração em `config.py` inspirando-se em `agente_simples`
- **Rationale**: `langgraph-tasks.md` (T3) orienta mover `load_dotenv` e leitura da API key para uma `AppConfig`, garantindo mensagens de erro consistentes e permitindo reutilização com a CLI e `create_app()`.
- **Alternatives considered**: Continuar carregando variáveis diretamente em `main.py` manteria duplicação e dificultaria pré-checagens, além de impedir reutilização no CLI.

## Decision: Separar utilidades de IO de imagem em `utils/io.py` com exceções específicas
- **Rationale**: As tarefas T2 e T5 pedem uma estrutura modular com utilidades explícitas para leitura/gravação e tratamento de erros. Isso facilita testes unitários e logging consistente.
- **Alternatives considered**: Deixar funções em `utils.py` único não ofereceria especialização nem mensagens claras para falhas na leitura da imagem.

## Decision: Padronizar logging via `utils/logging.py`
- **Rationale**: T12 requer abandonar `logging.basicConfig` e replicar o padrão de `agente_simples`, assegurando handlers únicos por logger e formato consistente.
- **Alternatives considered**: Configurar logging diretamente em cada módulo aumentaria o risco de handlers duplicados e mensagens divergentes.

## Decision: Implementar CLI dedicada e expor `create_app()`
- **Rationale**: T7–T9 e T11 determinam que o grafo seja compilado em `graph.py` e exposto via `create_app`, com CLI alinhada ao padrão existente e integração com LangGraph CLI.
- **Alternatives considered**: Manter execução exclusiva por script impediria uso do `langgraph run` e violaria a meta do spec.

## Decision: Estratégia de testes com mocks de Gemini
- **Rationale**: T13 especifica criação de testes determinísticos para caminhos de sucesso e falha. Mockar `ChatGoogleGenerativeAI.invoke` e usar fixtures locais mantém testes previsíveis e alinhados ao Princípio III.
- **Alternatives considered**: Invocar o serviço real tornaria os testes não determinísticos e lentos, contrariando as diretrizes.

## Decision: Atualização incremental de `langgraph.json`
- **Rationale**: T11 e o Princípio XXII exigem apenas adicionar a nova entrada para `agente_imagem`, preservando os demais registros.
- **Alternatives considered**: Reescrever o arquivo inteiro ou remover entradas existentes não é permitido e poderia quebrar agentes já registrados.
