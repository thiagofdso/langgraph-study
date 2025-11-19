# agente_tarefas

Agente CLI em três rodadas construído com LangGraph seguindo o template v2.3. O fluxo mantém o mesmo comportamento anterior:

1. **Rodada 1** – coleta tarefas iniciais e confirma recebimento.
2. **Rodada 2** – usuário marca uma tarefa como concluída.
3. **Rodada 3** – adiciona novas tarefas opcionais e recebe o resumo final.

## Estrutura

```
agente_tarefas/
├── cli.py              # fluxo interativo
├── config.py           # carregamento do .env e fábrica de LLM/checkpointer
├── graph.py            # construção do StateGraph
├── state.py            # TypedDicts e fábrica de estado
├── utils/
│   ├── prompts.py      # SYSTEM_PROMPT + builders
│   ├── rounds.py       # parsing/validação das três rodadas
│   └── timeline.py     # helpers de logging
├── docs/operations.md  # procedimentos operacionais
├── tests/              # pytest cobrindo rounds/graph/cli
├── logs/.gitkeep       # diretório padrão para saídas futuras
├── __main__.py         # habilita `python -m agente_tarefas`
└── main.py             # compatibilidade com import legado
```

## Pré-requisitos
- Python 3.12.3 via virtualenv do repositório (`source venv/bin/activate`).
- Dependências globais do projeto instaladas (`pip install -r requirements.txt`).
- Arquivo `.env` nesta pasta com `GEMINI_API_KEY` válido (as demais chaves seguem o padrão dos outros agentes).

## Como executar
```bash
python -m agente_tarefas
```

O CLI imprime as falas como `Usuário:` e `Agente:` para acompanhar a conversa. O `thread_id` usa o prefixo configurável `AGENT_THREAD_PREFIX` e mantém a sessão intacta durante as três rodadas.

## Testes
```bash
pytest agente_tarefas/tests -q
```

Os testes validam validações de entrada (`utils/rounds.py`), a compilação do grafo (`graph.py`) e o fluxo feliz do CLI com um modelo fake.
