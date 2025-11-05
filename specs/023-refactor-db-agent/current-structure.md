# Estrutura atual do `agente_banco_dados` (pré-refatoração)

```
agente_banco_dados/
├── .env                    # arquivo opcional com variáveis locais
├── README.md               # documentação do agente
├── __init__.py             # pacote vazio
├── __pycache__/            # artefatos compilados
├── config.py               # constantes e parâmetros do agente
├── data/
│   ├── README.md           # instruções sobre o banco
│   └── sales.db            # banco SQLite populado
├── db_init.py              # criação/seed do banco
├── main.py                 # ponto de entrada atual
└── reporting.py            # consultas SQL e formatação Markdown
```

> Observação: Não há diretórios dedicados para `state`, `graph`, `cli` ou `utils`; toda a lógica de orquestração reside em `main.py`.
