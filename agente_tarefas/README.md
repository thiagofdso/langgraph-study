# agente_tarefas

Agente de tarefas totalmente orientado ao **LangGraph CLI**. O fluxo não possui mais `python -m` nem `cli.py` interativo: toda a experiência acontece em um único turno do grafo, que interpreta a mensagem do usuário, mapeia operações JSON e devolve a lista atualizada ao final.

## Estrutura

```
agente_tarefas/
├── cli.py              # shim que direciona para o LangGraph CLI
├── config.py           # carregamento de .env e fábrica de LLM/checkpointer
├── graph.py            # StateGraph com nós parse/apply/summarize
├── state.py            # estado enxuto (lista de tarefas em memória)
├── utils/
│   ├── prompts.py      # instruções para o LLM produzir JSON
│   ├── nodes.py        # parse_operations, apply_operations, summarize_response
│   └── operations.py   # schema + validação `{ "op": ... }`
├── docs/               # notas operacionais
├── tests/              # pytest com cenários de nós e grafo
├── __main__.py         # preservado para alertar sobre o novo fluxo
└── main.py             # compatibilidade de import legado
```

## Pré-requisitos
- Python 3.12.3 via virtualenv do repositório (`source venv/bin/activate`).
- Dependências instaladas com `pip install -r requirements.txt`.
- `.env` com `GEMINI_API_KEY` (segue padrão dos demais agentes).

## Como executar (LangGraph CLI)
```bash
venv/bin/langgraph dev --config langgraph.json --host 0.0.0.0
```
Depois de iniciar o servidor, use o painel/CLI interativo para enviar mensagens como:

```text
Adicione estudar e fazer compras, depois remova lavar louça
```

O nó de parsing exige JSON estruturado e instrui o Gemini a responder algo como:
```json
[
  {"op": "add", "tasks": ["estudar", "fazer compras"]},
  {"op": "del", "tasks": ["lavar louça"]}
]
```
Os nós subsequentes aplicam as operações na ordem recebida e sempre respondem com a lista resultante. Para listar sem alterações envie apenas “Liste minhas tarefas” (gera `{ "op": "listar" }`).

## Testes
```bash
pytest agente_tarefas/tests -q
```
Os testes cobrem validação das operações, execução sequencial do grafo e respostas para cenários ambíguos. Após alterações de código, execute também o fluxo manual descrito acima para garantir que o LangGraph CLI apresenta o comportamento esperado.

## Documentação complementar
- `docs/operations.md`: contrato JSON completo, exemplos e instruções de log.
- `docs/manual-test.md`: checklist de QA manual (adicionar/remover/listar/erros).
