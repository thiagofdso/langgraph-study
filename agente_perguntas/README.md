# Agente Perguntas

Agente em LangGraph responsável por responder perguntas frequentes a partir de um FAQ embutido e encaminhar dúvidas desconhecidas para atendimento humano (HITL). O projeto foi refatorado para seguir o padrão modular usado em outros agentes do repositório (`config.py`, `graph.py`, `cli.py`, `utils/`, `docs/`, `tests/`).

## Pré-requisitos

1. Python 3.12 instalado e o ambiente virtual padrão do repositório ativado:
   ```bash
   source venv/bin/activate
   ```
2. Dependências instaladas:
   ```bash
   pip install -r requirements.txt
   ```
3. Variáveis de ambiente configuradas a partir do template:
   ```bash
   cp agente_perguntas/.env.example agente_perguntas/.env
   ```
   Preencha `GEMINI_API_KEY` e ajuste opcionalmente `GEMINI_MODEL`, `GEMINI_TEMPERATURE`, `AGENTE_PERGUNTAS_CONFIDENCE` e `AGENTE_PERGUNTAS_LOG_DIR`.

## Como executar

### Modo demonstrativo
```bash
python -m agente_perguntas
```
- Executa as perguntas definidas em `agente_perguntas/utils/prompts.py` (três exemplos padrão).
- O terminal mostra para cada pergunta o status (`respondido automaticamente` ou `encaminhar para humano`).
- Se houver escalonamento, o CLI solicita mensagem e notas do especialista e retoma a execução automaticamente.

### Pergunta única
```bash
python -m agente_perguntas --pergunta "Vocês oferecem suporte 24 horas?"
```
- Útil para validar rapidamente perguntas específicas do FAQ.
- Opcional: `--thread-id <uuid>` para reutilizar checkpoints do LangGraph ao depurar sessões.

## Logs estruturados
- O diretório configurado em `AGENTE_PERGUNTAS_LOG_DIR` (padrão `agente_perguntas/logs`) recebe entradas JSON via `structlog`.
- Cada interação registra `question`, `status`, `confidence`, `notes` e um resumo da resposta.
- Consulte `agente_perguntas/utils/logging.py` para detalhes de formatação.

## Testes
Uma suíte dedicada cobre utilitários de similaridade, grafo (auto/HITL) e CLI. Execute:
```bash
pytest agente_perguntas/tests -v
```
Você deve ver todos os cenários como `PASSED` (tempo esperado < 1s em dev machines). Consulte `agente_perguntas/tests/` para adaptar ou adicionar casos.

## Documentação complementar
- `agente_perguntas/docs/quickstart.md`: passo a passo completo para configurar ambiente, rodar o demo, enviar pergunta única e validar testes.
- `agente_perguntas/docs/operations.md`: procedimentos operacionais, fluxo HITL, troubleshooting para ausência de `GEMINI_API_KEY` e orientações para revisar logs.
