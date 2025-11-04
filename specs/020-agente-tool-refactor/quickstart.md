# Quickstart – agente_tool refatorado

## Pré-requisitos
1. Python 3.12 instalado.
2. Ambiente virtual configurado (`python -m venv venv && source venv/bin/activate`).
3. Dependências instaladas: `pip install -r requirements.txt`.
4. Copiar `agente_tool/.env.example` para `agente_tool/.env` e preencher `GEMINI_API_KEY` (opcionalmente `DEFAULT_THREAD_ID`).

## Executando o agente
```bash
python -m agente_tool run "quanto é 300 dividido por 4?"
```
- Esperado: saída formatada `Resposta do agente: 75`.
- Logs informativos indicarão cada etapa (`validate_input`, `plan_tool_usage`, `execute_tools`, `invoke_model`, `format_response`).
- Para reutilizar memória in-memory, informe `--thread-id <identificador>`.
- Executando `python -m agente_tool` sem parâmetros, a CLI solicitará a pergunta interativamente.

## Rodando testes
```bash
pytest agente_tool/tests -v
```
- Inclui testes unitários dos nodes e teste de integração do grafo.

## Atualizando catálogo de nodes
Após adicionar novas responsabilidades, execute:
1. Editar `graph-nodes-patterns.md` adicionando linha para o novo node.
2. Revisar se entradas existentes continuam corretas.
