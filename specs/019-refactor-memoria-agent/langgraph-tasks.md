# Documento de Tarefa: Refatorar agente_memoria

## 1. Análise Atual
### 1.1 Estado Atual
- **Project Structure**: Diretório `agente_memoria/` contém apenas `main.py`, `__init__.py` vazio e `README.md`. Não há separação entre configuração, estado, nós e CLI; toda a lógica está concentrada em `main.py`.
- **State Schema**: Define um `AgentState` via `TypedDict` apenas com `messages`, mas o próprio node altera a lista diretamente (mutação) e não adiciona metadados nem controle de fluxo.
- **Nodes/Tasks**: Existe um único node (`agent_node`) embutido em `main.py`; a invocação do modelo ocorre diretamente nele, sem camadas de validação, formatação ou tratamento de erros.
- **Middleware/Observability**: Ausência de logging estruturado, sem validações de configuração ou mensagens orientativas (diferente do agente_simples). Não há middleware nem interceptores.
- **Performance/Resiliência**: Usa `InMemorySaver`, mas o agente não expõe mecanismos para resetar threads, escolher identificadores ou lidar com falhas do provedor.
- **API Utilizada**: Graph API tradicional (StateGraph) com fluxo linear mínimo (`agent` -> END).

### 1.2 Impacto da Mudança
- **Componentes afetados**: Estrutura de diretórios, gestão de estado, criação do grafo, configuração de modelo, CLI, logging, documentação e testes.
- **Riscos identificados**:
  - Regressão em comportamento de memória se histórico não for preservado corretamente durante a extração para componentes separados.
  - Erros de configuração caso variáveis de ambiente sejam renomeadas sem atualizar documentação.
  - Possível quebra em scripts existentes se interface de execução (ex.: `python agente_memoria/main.py`) mudar sem oferecer nova entrada (`__main__.py` ou CLI dedicada).

## 2. Requisitos & Objetivos
### 2.1 Objetivo Principal
Refatorar `agente_memoria` para seguir boas práticas de organização LangGraph, garantindo memória persistente, diagnósticos claros e alinhamento estrutural ao padrão usado em `agente_simples`.

### 2.2 Escolha de API
- **Graph API (StateGraph)** permanecerá como base, pois o projeto já utiliza esse modelo e precisa de controle explícito de estado com checkpointer.
- Avaliar uso complementar da Functional API apenas se surgirem tarefas lineares adicionais (não prioritário neste refactor).

### 2.3 Estrutura do Projeto
- Adotar **Estrutura Básica** (Seção 0.5.1 do guia), expandida para incluir CLI e testes, espelhando padrões do `agente_simples`.
- Criar subpacotes para `config`, `state`, `graph`, `cli`/`main`, `utils` (nodes, prompts, logging) e `tests`.

## 3. Organização de Arquivos
### 3.1 Estrutura Base Proposta
```
agente_memoria/
├── __init__.py
├── cli.py                # Entrada CLI (similar ao agente_simples)
├── config.py             # AppConfig com validações e criação de LLM/checkpointer
├── docs/
│   └── operations.md     # Guia de operação e troubleshooting
├── graph.py              # Função create_app() compilando StateGraph
├── main.py               # Importa cli.main (compatibilidade)
├── prompts.py            # Prompts base (se necessários)
├── state.py              # GraphState com reducers e modelos de mensagem
├── utils/
│   ├── __init__.py
│   ├── logging.py        # Configuração de logs
│   └── nodes.py          # Nós separados (validação, invoke, format, memória)
└── tests/
    ├── __init__.py
    ├── test_nodes.py
    ├── test_graph.py
    └── fixtures.py
```
- Adicionar `.env.example`, `.gitignore` atualizado e `langgraph.json` no root do repositório se ainda não existir para este agente.

### 3.2 Padrões de Importação
- Ordenar importações: stdlib → third-party → locais.
- Evitar `from module import *`; expor funções necessárias via `__all__` em `utils/__init__.py`.
- Reutilizar utilitários do `agente_simples` quando fizer sentido (ex.: logger), mas preferir encapsular dependências específicas do agente de memória.

## 4. Implementação Detalhada
### 4.1 State & Config
1. **Criar `state.py`**:
   - Definir `GraphState` com `messages: Annotated[List[BaseMessage], add_messages]`, `metadata`, `status`, `resposta`, `thread_id`.
   - Incluir modelo Pydantic (`ThreadConfig`) para validação de identificadores informados pelo usuário.
2. **Criar `config.py`**:
   - Implementar `AppConfig` com leitura de `.env`, atributos `model_name`, `temperature`, `timeout`, `api_key`, `default_thread_id`.
   - Fornecer métodos `create_llm()` e `create_checkpointer()` (padrão InMemorySaver, permitindo substituição futura).
   - Implementar `preflight_config_check()` retornando lista de diagnósticos (pass/warn/fail), seguindo padrão do agente simples.

### 4.2 Nodes/Tasks/Middleware
1. **`utils/nodes.py`** (dividir responsabilidades):
   - `validate_question_node`: Validar entrada (mínimo 5 caracteres), normalizar idioma e anexar metadados (`started_at`, `thread_id`).
   - `load_history_node`: Carregar histórico existente do checkpointer ou store com base no `thread_id`.
   - `invoke_model_node`: Montar prompt combinando histórico, controlar exceções (credenciais, timeouts, indisponibilidade), retornar resposta e status.
   - `update_memory_node`: Aplicar reducer adicionando mensagem do agente, garantir que histórico não seja substituído.
   - `format_response_node`: Preparar saída final para CLI com tempo de execução e mensagens amigáveis.
2. **Tratamento de erros**:
   - Mapear categorias (configuração ausente, erro temporário, erro do provedor) e devolver mensagens orientativas.
   - Adicionar logs estruturados usando logger configurado em `utils/logging.py`.
3. **Prompts**:
   - Se necessário, mover prompt base para `prompts.py` com instruções específicas sobre uso de memória.

### 4.3 Graph Construction
1. **`graph.py`**:
   - Criar função `create_app()` que instancia `StateGraph(GraphState)`, adiciona nodes e edges:
     - START → `validate_input` → `load_history` → `invoke_model` → `update_memory` → `format_response` → END.
   - Compilar grafo com checkpointer proveniente de `config.create_checkpointer()`.
   - Expor `app = create_app()`.
2. **`cli.py`**:
   - Implementar fluxo semelhante ao `agente_simples`: rodar preflight, solicitar pergunta e opcionalmente thread id, interpretar comandos especiais (`/reset`, `/trocar-thread`).
   - Permitir injetar `thread_id` via argumento de linha de comando.
3. **`main.py`**:
   - Manter como proxy (importar `main` de `cli.py`) para compatibilidade com `python agente_memoria/main.py`.

### 4.4 Documentação & Scripts Auxiliares
1. Atualizar `README.md` com instruções alinhadas ao novo fluxo (setup, execução, reset de memória).
2. Criar `docs/operations.md` com troubleshooting (credenciais, network, latência, reset).
3. Gerar `.env.example` com variáveis utilizadas.
4. Adicionar `langgraph.json` apontando para `agente_memoria/graph.py:create_app`.

## 5. Testing Strategy
### 5.1 Unit Tests
- **`test_nodes.py`**: Validar cada node isoladamente (entrada vazia, erro de credencial simulado, resposta com memória).
- **`test_config.py`** (opcional): Garantir que `preflight_config_check` responde corretamente a variáveis ausentes.
- Mockar LLM (`ChatGoogleGenerativeAI`) para retornar respostas determinísticas.

### 5.2 Integration Tests
- **`test_graph.py`**: Invocar `app.invoke` com cenário multi-turno e verificar reaproveitamento de contexto.
- **Fluxo de erro**: Simular falta de API key e garantir mensagem de bloqueio amigável.
- **Reset de thread**: Validar que comando de reset limpa histórico e próxima interação não traz contexto anterior.

## 6. Deployment & Monitoring
### 6.1 Estrutura Final
- Confirmar que nova estrutura respeita checklist da Seção 0.5.10 (state/config separados, `.env.example`, `langgraph.json`, documentação).
- Garantir que `langgraph.json` permite execução via `langgraph dev` e integração com LangGraph Studio.

### 6.2 Checklist
- [ ] Código revisado com pareamento (code review).
- [ ] Testes automatizados e manuais passando.
- [ ] Logging e mensagens de erro verificados.
- [ ] `langgraph.json` atualizado/testado.
- [ ] Documentação (README + docs/operations.md) atualizada.
- [ ] `.env.example` fornece todas as variáveis necessárias.
- [ ] Plano de rollback documentado (possível reverter para versão anterior em caso de falha).
