# Documento de Tarefa: Reorganização do Agente Simples

## 1. Análise Atual

### 1.1 Estado Atual
- **Estrutura do projeto**: `agente_simples/` contém apenas `main.py`, um `__init__.py` vazio e instruções básicas no `README`. Não há separação entre state, nós, configuração ou utilidades.
- **State Schema**: Usa um `TypedDict` minimalista diretamente em `main.py` (`GraphState`) sem reducers ou validação.
- **Nodes/Tasks**: Todo o fluxo reside na função `agent` dentro de `main.py`; não há modularização, handlers ou reutilização.
- **Middleware / Observabilidade**: Inexistente. Não há logging estruturado, métricas ou mensagens de diagnóstico.
- **Performace / Resiliência**: O agente chama `ChatGoogleGenerativeAI` diretamente com `temperature=0`, sem timeout explícito, retry ou tratamento de exceções.
- **API utilizada**: Graph API (StateGraph) com um único node e fluxo linear, compilado sem checkpointer.

### 1.2 Impacto da Mudança
- **Componentes afetados**: Arquitetura de pastas do `agente_simples`, criação de novos módulos (`state.py`, `config.py`, `utils/`, `graph.py`), ajustes no entrypoint CLI e documentação. Testes e scripts precisam acompanhar a nova estrutura.
- **Riscos identificados**:
  - Interrupção temporária do comando CLI se o entrypoint não for atualizado corretamente.
  - Possível quebra do fluxo se variáveis de ambiente mudarem (necessário `.env.example` consistente).
  - Falta de testes automatizados atuais exige atenção manual após reorganização.

## 2. Requisitos & Objetivos

### 2.1 Objetivo Principal
Disponibilizar um guia passo a passo para reorganizar o `agente_simples` seguindo boas práticas de estruturação de projetos LangGraph, garantindo modularidade, facilidade de manutenção e prontidão para expansão (middleware, logging, testes e deployment).

### 2.2 Escolha de API
- **Manter Graph API (StateGraph)**: O fluxo continua simples, mas o StateGraph permite evolução futura (múltiplos nodes, condicionais, fan-out). Functional API seria redundante neste estágio e `create_agent` não oferece o mesmo controle fino desejado para um exemplo didático.

### 2.3 Estrutura do Projeto
- **Estrutura recomendada**: Modelo **Básico (Single Agent)**, com pacote isolado, módulos dedicados para state, config, nodes, ferramentas/utilidades e testes. Adequado para equipe pequena mas com planejamento para crescimento incremental.

## 3. Organização de Arquivos

### 3.1 Estrutura Base Planejada
```
agente_simples/
├── __init__.py
├── config.py              # Configurações centralizadas / AppConfig
├── graph.py               # Construção e compilação do graph
├── state.py               # Schema do state (TypedDict ou Pydantic)
├── cli.py                 # Entry point CLI separado (invoca o app)
├── utils/
│   ├── __init__.py
│   ├── nodes.py           # Implementação dos nodes
│   ├── prompts.py         # Mensagens ou templates (quando aplicável)
│   └── logging.py         # Setup de logging estruturado
├── tests/
│   ├── __init__.py
│   ├── test_nodes.py
│   └── test_graph.py
├── docs/
│   └── operations.md      # Notas de operação/troubleshooting
├── __main__.py            # Permite `python -m agente_simples`
└── README.md              # Atualizado para refletir nova estrutura
```

### 3.2 Padrões de Importação
- Sempre agrupar imports por categoria: Stdlib → Terceiros → Locais.
- Evitar `import *` e apelidos obscuros; usar nomes explícitos (`from agente_simples.state import GraphState`).
- Para nodes e ferramentas, expor apenas o necessário no `utils/__init__.py`.

## 4. Implementação Detalhada

### 4.1 State & Config
1. **Criar `state.py`**:
   - Definir `GraphState` como `TypedDict` com reducers (`messages`, `metadata`, `status`).
   - Adicionar um `DialogueState` em Pydantic (opcional) para validação de entrada.
   - Exemplo inicial:
     ```python
     # agente_simples/state.py
     from typing import Annotated
     from typing_extensions import TypedDict
     from langgraph.graph.message import add_messages
     from pydantic import BaseModel, Field

     class DialogueInput(BaseModel):
         """Validação de entrada do CLI."""
         pergunta: str = Field(..., min_length=5, description="Pergunta em português")

     class GraphState(TypedDict, total=False):
         """Estado compartilhado entre nodes do agente simples."""
         messages: Annotated[list, add_messages]
         metadata: dict
         status: str
         resposta: str
     ```
2. **Criar `config.py`**:
   - Implementar `AppConfig` com `dataclass`, leitura de `.env` e fallback seguro.
   - Expor propriedades para modelo, temperatura, checkpointer e diretórios de log.
   - Incluir método `create_model()` para encapsular provider instantiation.
   - Exemplo inicial:
     ```python
     # agente_simples/config.py
     import os
     from dataclasses import dataclass
     from dotenv import load_dotenv
     from langgraph.checkpoint.memory import MemorySaver
     from langchain_google_genai import ChatGoogleGenerativeAI

     load_dotenv()

     @dataclass
     class AppConfig:
         """Configurações do agente simples."""
         model_name: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
         temperature: float = float(os.getenv("GEMINI_TEMPERATURE", "0.0"))
         timeout_seconds: int = int(os.getenv("AGENT_TIMEOUT_SECONDS", "30"))
         locale: str = os.getenv("AGENT_LOCALE", "pt-BR")

         def create_llm(self) -> ChatGoogleGenerativeAI:
             return ChatGoogleGenerativeAI(
                 model=self.model_name,
                 temperature=self.temperature,
                 api_key=os.getenv("GEMINI_API_KEY"),
             )

         def create_checkpointer(self):
             return MemorySaver()

     config = AppConfig()
     ```
3. **Centralizar constantes** (como timeout e idioma padrão) em `config.py` ou `utils/constants.py` se necessário.

### 4.2 Nodes / Utilidades
1. **Criar `utils/nodes.py`**:
   - Separar funções: `validate_question_node`, `invoke_model_node`, `format_answer_node`.
   - Cada node deve retornar dicionário parcial, respeitando imutabilidade do state.
   - Incluir tratamento de exceções com mensagens amigáveis (em português) e logging.
   - Exemplo inicial:
     ```python
     # agente_simples/utils/nodes.py
     from langchain_core.messages import HumanMessage
     from agente_simples.config import config
     from agente_simples.state import GraphState, DialogueInput
     from agente_simples.utils.logging import get_logger

     logger = get_logger()

     def validate_question_node(state: GraphState) -> dict:
         """Garante que a pergunta seja válida antes de chamar o LLM."""
         raw_question = state.get("resposta") or state["messages"][-1].content
         dialogue = DialogueInput(pergunta=raw_question)
         logger.debug("Pergunta validada", extra={"pergunta": dialogue.pergunta})
         return {"metadata": {"question": dialogue.pergunta}}

     def invoke_model_node(state: GraphState) -> dict:
         """Chama o modelo Gemini com tratamento de erros."""
         llm = config.create_llm()
         question = state["metadata"]["question"]
         try:
             resposta = llm.invoke(question).content
         except Exception as exc:
             logger.exception("Erro ao chamar modelo", extra={"question": question})
             resposta = (
                 "Não consegui obter uma resposta agora. "
                 "Verifique sua conexão ou tente novamente mais tarde."
             )
         return {"resposta": resposta}

     def format_answer_node(state: GraphState) -> dict:
         """Formata a resposta final para exibição amigável."""
         resposta = state.get("resposta", "")
         retorno = f"Resposta do agente: {resposta.strip()}"
         logger.info("Resposta gerada com sucesso")
         return {"resposta": retorno, "status": "completed"}
     ```
2. **Adicionar `utils/logging.py`**:
   - Configurar logger padrão (stdout + arquivo em `logs/`), níveis e formatação.
   - Garantir que nodes utilizem logger injetado ou global configurado.
   - Exemplo inicial:
     ```python
     # agente_simples/utils/logging.py
     import logging
     from pathlib import Path

     LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
     LOG_DIR.mkdir(exist_ok=True)

     def get_logger() -> logging.Logger:
         logger = logging.getLogger("agente_simples")
         if not logger.handlers:
             logger.setLevel(logging.INFO)
             formatter = logging.Formatter(
                 "%(asctime)s %(levelname)s %(name)s %(message)s"
             )
             stream_handler = logging.StreamHandler()
             stream_handler.setFormatter(formatter)

             file_handler = logging.FileHandler(LOG_DIR / "agent.log")
             file_handler.setFormatter(formatter)

             logger.addHandler(stream_handler)
             logger.addHandler(file_handler)
         return logger
     ```
3. **Opcional**: `utils/prompts.py` para armazenar prompt system/contexto padrão.
   ```python
   # agente_simples/utils/prompts.py
   SYSTEM_PROMPT = (
       "Você é um assistente organizado que responde em português brasileiro, "
       "com foco em objetividade e cordialidade."
   )
   ```
4. **Criar `cli.py`**:
   - Responsável por carregar config, preparar state inicial, chamar `graph.invoke`.
   - Implementar prompts de entrada e exibir respostas/erros formatados.
   - Exemplo inicial:
     ```python
     # agente_simples/cli.py
     from agente_simples.graph import app
     from agente_simples.utils.logging import get_logger

     logger = get_logger()

     def main() -> None:
         pergunta = input("Faça sua pergunta em português: ").strip()
         if not pergunta:
             print("Pergunta vazia. Tente novamente com mais detalhes.")
             return
         result = app.invoke({"messages": [{"role": "user", "content": pergunta}]})
         resposta = result.get("resposta")
         logger.info("Execução concluída", extra={"question": pergunta})
         print(resposta)
     ```
5. **Atualizar `__main__.py`**:
   - Permitir execução via `python -m agente_simples` chamando `cli.main()`.
   - Exemplo inicial:
     ```python
     # agente_simples/__main__.py
     from agente_simples.cli import main

     if __name__ == "__main__":
         main()
     ```

### 4.3 Construção do Graph
1. **Criar `graph.py`**:
   - Importar `StateGraph`, `START`, `END` e `GraphState`.
   - Adicionar nodes nomeados (`"validate_input"`, `"invoke_model"`, `"format_response"`).
   - Configurar edges (`START` → validate → invoke → format → `END`).
   - Incluir checkpointer (ex.: `MemorySaver` para dev) usando `config.create_checkpointer()`.
   - Expor `graph` ou `app` compilado e função `create_app()` para testes.
   - Exemplo inicial:
     ```python
     # agente_simples/graph.py
     from langgraph.graph import StateGraph, START, END
     from agente_simples.config import config
     from agente_simples.state import GraphState
     from agente_simples.utils import nodes

     def create_app():
         builder = StateGraph(GraphState)
         builder.add_node("validate_input", nodes.validate_question_node)
         builder.add_node("invoke_model", nodes.invoke_model_node)
         builder.add_node("format_response", nodes.format_answer_node)

         builder.add_edge(START, "validate_input")
         builder.add_edge("validate_input", "invoke_model")
         builder.add_edge("invoke_model", "format_response")
         builder.add_edge("format_response", END)

         return builder.compile(checkpointer=config.create_checkpointer())

     app = create_app()
     ```
2. **Remover lógica de graph de `main.py`**:
   - `main.py` passa a apenas delegar para `cli.main()` ou ser substituído por `cli.py`.

## 5. Testing Strategy

### 5.1 Unit Tests
- `tests/test_nodes.py`: Validar nodes isoladamente (inputs vazios, erros do provedor, tempo de resposta).
  ```python
  # agente_simples/tests/test_nodes.py
  import pytest
  from agente_simples.utils import nodes
  from agente_simples.state import GraphState

  def test_format_answer_node_formats_response():
      state: GraphState = {"resposta": "Olá!"}
      result = nodes.format_answer_node(state)
      assert "Resposta do agente" in result["resposta"]

  def test_validate_question_node_rejects_short_question():
      state: GraphState = {"messages": [{"role": "user", "content": "Oi"}]}
      with pytest.raises(Exception):
          nodes.validate_question_node(state)
  ```
- `tests/test_state.py`: Garantir reducers e validações do state (quando houver Pydantic).
  ```python
  # agente_simples/tests/test_state.py
  import pytest
  from agente_simples.state import DialogueInput

  def test_dialogue_input_accepts_valid_question():
      payload = DialogueInput(pergunta="Qual é a capital do Brasil?")
      assert payload.pergunta.startswith("Qual")

  def test_dialogue_input_rejects_short_question():
      with pytest.raises(ValueError):
          DialogueInput(pergunta="Oi")
  ```

### 5.2 Integration Tests
- `tests/test_graph.py`: Executar o graph completo com mock do LLM (fixtures com `ChatGoogleGenerativeAI` fake).
  ```python
  # agente_simples/tests/test_graph.py
  from unittest.mock import patch
  from agente_simples.graph import create_app

  @patch("agente_simples.utils.nodes.config.create_llm")
  def test_graph_flow_returns_answer(mock_create_llm):
      mock_llm = mock_create_llm.return_value
      mock_llm.invoke.return_value.content = "O Brasil tem 26 estados."

      app = create_app()
      result = app.invoke({"messages": [{"role": "user", "content": "Quantos estados tem o Brasil?"}]})

      assert "Resposta do agente" in result["resposta"]
      mock_llm.invoke.assert_called_once()
  ```
- `tests/test_cli.py` (opcional): Verificar interação CLI usando `pytest` + `capsys`.
  ```python
  # agente_simples/tests/test_cli.py
  from unittest.mock import patch
  from agente_simples import cli

  @patch("builtins.input", return_value="Qual é a capital do Brasil?")
  @patch("agente_simples.cli.app.invoke", return_value={"resposta": "Resposta do agente: Brasília"})
  def test_cli_main_happy_path(mock_invoke, mock_input, capsys):
      cli.main()
      captured = capsys.readouterr()
      assert "Brasília" in captured.out
      mock_invoke.assert_called_once()
  ```
- Adicionar workflow de testes em `Makefile` / `pyproject.toml` com `pytest`.

## 6. Deployment & Monitoring

### 6.1 Estrutura Final
- Confirmar existência de `.env.example`, `.gitignore` atualizado, `langgraph.json` apontando para `agente_simples/graph.py:create_app` (ou `graph` compilado).
- Documentação (`README.md` e `docs/operations.md`) descreve setup, variáveis, comandos de teste e troubleshooting.
- Incluir seção de futuros aprimoramentos (middleware, LangSmith, checkpointer persistente) para guiar evolução.

### 6.2 Checklist
- [ ] Script de reorganização executado (pastas criadas conforme blueprint).
- [ ] `config.py` carrega e valida variáveis necessárias (`GEMINI_API_KEY`, idioma, temperatura).
- [ ] `graph.py` e nodes seguem a convenção de imutabilidade e logging.
- [ ] `cli.py` lida com erros e mensagens amigáveis em português.
- [ ] Tests unitários e de integração implementados e documentados.
- [ ] `.env.example`, `.gitignore`, `langgraph.json` e `README.md` atualizados.
- [ ] Logs acessíveis e limpos após execução (`logs/`).
- [ ] Pronto para integração futura com LangSmith/LangGraph Studio (configuração documentada).

#### Exemplos de Arquivos de Suporte
- `.env.example`:
  ```dotenv
  GEMINI_API_KEY="coloque_sua_chave_aqui"
  GEMINI_MODEL="gemini-2.5-flash"
  GEMINI_TEMPERATURE=0.0
  AGENT_TIMEOUT_SECONDS=30
  AGENT_LOCALE="pt-BR"
  ```
- `langgraph.json`:
  ```json
  {
    "dependencies": ["."],
    "graphs": {
      "agente-simples": "agente_simples/graph.py:create_app"
    },
    "env": ".env"
  }
  ```
- `README.md` (trecho sugerido):
  ```markdown
  ## Uso Rápido

  1. Crie a virtualenv e instale dependências:
     ```bash
     python -m venv venv
     source venv/bin/activate
     pip install -r requirements.txt
     ```
  2. Copie `.env.example` para `.env` e preencha `GEMINI_API_KEY`.
  3. Execute o agente:
     ```bash
     python -m agente_simples
     ```
  ```
