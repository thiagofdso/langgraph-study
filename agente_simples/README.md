# Agente Simples (LangGraph)

O agente responde perguntas pontuais em português usando o modelo `gemini-2.5-flash`. A refatoração atual reorganiza o projeto em módulos independentes (state, config, graph, CLI) e adiciona validação, diagnósticos e logging estruturado.

## 1. Configuração Rápida
1. Ative o ambiente virtual do repositório:
   ```bash
   source venv/bin/activate
   ```
2. Copie o arquivo de exemplo de variáveis:
   ```bash
   cp agente_simples/.env.example agente_simples/.env
   ```
3. Preencha `agente_simples/.env` com `GEMINI_API_KEY` e ajustes opcionais (`GEMINI_MODEL`, `GEMINI_TEMPERATURE`, `AGENT_TIMEOUT_SECONDS`, `AGENT_LOCALE`).

> Dica: use `AGENTE_SIMPLES_LOG_DIR=/caminho/customizado` para gravar logs fora do diretório padrão `agente_simples/logs/`.

## 2. Executando o Agente
```bash
python -m agente_simples
```
- O agente executa checagens de configuração antes de chamar o modelo.
- Em caso de falha, instruções de correção são exibidas no terminal e a execução é interrompida.
- Perguntas válidas retornam uma resposta formatada e registram a execução nos logs.

## 3. Estrutura do Projeto
```text
agente_simples/
├── __init__.py
├── __main__.py          # permite `python -m agente_simples`
├── cli.py               # fluxo de linha de comando
├── config.py            # configuração centralizada + checagens
├── graph.py             # StateGraph compilado
├── state.py             # schema de estado e validações
├── utils/
│   ├── __init__.py
│   ├── logging.py
│   ├── nodes.py
│   └── prompts.py
├── tests/
│   ├── test_cli.py
│   ├── test_graph.py
│   └── test_nodes.py
└── docs/
    └── operations.md
```

## 4. Relatórios e Logs
- Logs ficam em `agente_simples/logs/agent.log` (ou no diretório definido pela variável `AGENTE_SIMPLES_LOG_DIR`).
- Cada execução registra a pergunta, status final (`completed` ou `error`) e a duração aproximada.
- Consulte `agente_simples/docs/operations.md` para procedimentos operacionais detalhados e troubleshooting.

## 5. Testes Automatizados
Rode a suíte dedicada com:
```bash
pytest agente_simples/tests -v
```
Cenários cobertos:
- Validação dos nodes e tratamento de erros (`test_nodes.py`).
- Fluxo completo do StateGraph, incluindo falha controlada do provedor (`test_graph.py`).
- Comportamento da CLI, pré-checagens e logging (`test_cli.py`).

## 6. Próximos Passos Sugeridos
- Integrar LangGraph Studio ou LangSmith para observabilidade ampliada.
- Automatizar execução periódica da suíte de testes para detectar regressões.
- Expandir prompts e instruções aproveitando o módulo `utils/prompts.py`.
