# Quickstart: agente_tool

## Pré-requisitos

1. **Criar/ativar ambiente virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variáveis de ambiente:**
   ```bash
   cp agente_tool/.env.example agente_tool/.env
   ```
   Atualize o arquivo copiado com `GEMINI_API_KEY` válido (e opcionalmente `DEFAULT_THREAD_ID`).

## Executando o agente

Utilize a CLI refatorada para disparar o fluxo:

```bash
python -m agente_tool run "quanto é 300 dividido por 4?"
```

- O comando executa checagens de configuração e registra logs tanto no console quanto em `agente_tool/logs/agent.log`.
- Para reutilizar o histórico em memória, informe `--thread-id` (padrão: `DEFAULT_THREAD_ID`).
- Também é possível executar somente `python -m agente_tool` e digitar a pergunta quando solicitado.

## Estrutura do projeto

- `config.py`: carregamento de `.env`, criação do LLM Gemini e `MemorySaver`.
- `state.py`: contratos `GraphState`, `ThreadConfig` e `ToolPlan`.
- `utils/`: nodes, ferramentas, logging e reexports.
- `graph.py`: montagem do `StateGraph` com roteamento condicional.
- `cli.py`: comando `run` que encapsula pré-checagens, execução e logging.
- `docs/`: baseline antes/depois e arquitetura textual.
- `tests/`: suíte `pytest` cobrindo nodes e fluxo completo.

## Testes

```bash
pytest agente_tool/tests -v
```

Os testes utilizam dublês de LLM e ferramenta para validar validação, planejamento, execução e formatação da resposta.
