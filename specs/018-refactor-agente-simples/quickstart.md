# Quickstart: Refactor Simple Agent

## Pré-requisitos
- Python 3.12 instalado
- Ambiente virtual criado na raiz (`python -m venv venv && source venv/bin/activate`)
- Dependências do repositório instaladas (`pip install -r requirements.txt`)
- Credencial Gemini disponível para popular `.env`

## Setup do Projeto
1. Copie o template de variáveis:
   ```bash
   cp agente_simples/.env.example agente_simples/.env
   ```
2. Edite `agente_simples/.env` preenchendo `GEMINI_API_KEY` e demais overrides desejados (`GEMINI_MODEL`, `GEMINI_TEMPERATURE`, etc.).
3. Garanta que `PYTHONPATH` inclui a raiz do repositório ao executar scripts:
   ```bash
   export PYTHONPATH=.
   ```

## Estrutura Esperada Após Refatoração
```text
agente_simples/
├── __init__.py
├── __main__.py
├── cli.py
├── config.py
├── graph.py
├── state.py
├── utils/
│   ├── __init__.py
│   ├── logging.py
│   ├── nodes.py
│   └── prompts.py
├── tests/
│   ├── __init__.py
│   ├── test_nodes.py
│   ├── test_graph.py
│   └── test_cli.py
└── docs/
    └── operations.md
```

## Executando o Agente
```bash
python -m agente_simples
```
Ao solicitar a pergunta, forneça um texto em português (≥5 caracteres). A resposta virá formatada e também será registrada em `agente_simples/logs/agent.log`.

## Rodando Testes
```bash
pytest agente_simples/tests -v
```
Os testes unitários usam mocks para o LLM; nenhuma chamada real é feita à API da Gemini.

## Artefatos Gerados
- Logs rotacionados em `agente_simples/logs/`
- Histórico de execuções disponível pelo logger e via wrapper HTTP (`/agent/logs`) quando exposto.

## Próximos Passos
- Integrar `langgraph.json` ao fluxo de CI.
- Avaliar adoção de LangSmith para observabilidade e replays.
