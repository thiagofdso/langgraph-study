# Operações do agente_tarefas (LangGraph CLI)

O agente funciona exclusivamente via **LangGraph CLI** e interpreta cada mensagem do usuário como um conjunto de operações JSON. Use este guia como referência rápida durante manutenção ou QA.

## Como executar
```bash
venv/bin/langgraph dev --config langgraph.json --host 0.0.0.0
```
Com o servidor ativo, envie mensagens pelo painel/CLI integrado (não há mais `python -m agente_tarefas`).

## Contrato de operações JSON

Cada turno deve ser convertido em um array JSON ordenado, onde cada elemento contém:

| Campo | Obrigatório? | Valores | Observações |
|-------|--------------|---------|-------------|
| `op`  | Sim | `listar`, `add`, `del` | Define a ação |
| `tasks` | Sim apenas para `add`/`del` | Lista de strings únicas | Duplicatas são removidas ignorando maiúsculas/minúsculas |

Exemplos válidos:

```json
[{"op":"listar"}]
```

```json
[
  {"op":"add","tasks":["estudar","comprar mantimentos"]},
  {"op":"del","tasks":["estudar"]}
]
```

Regras principais:
1. **Sempre responda com um array** – mesmo para uma única operação.
2. **Limpeza automática** – espaços extras são removidos e tarefas vazias são rejeitadas.
3. **Listar não altera o estado** – `{ "op": "listar" }` pode ser usado isoladamente.
4. **Erros não aplicam mudanças** – JSON inválido ou operações incompletas geram mensagens orientativas e o estado permanece intacto.

## Resumo gerado pelo agente
- **Adições/remoções**: informadas por nome, na ordem executada.
- **Itens ausentes**: deletar algo que não existe apenas produz um alerta “não encontrei”.
- **Listagem pura**: resposta começa com “Você solicitou apenas listar…” e mostra a lista atual.
- **Erros de validação**: inclui dicas do formato correto `[{"op":"add","tasks":["..."]}]`.

## Logs operacionais
O nó `apply_operations` gera um `log_entry` textual em `operation_report.log_entry` para cada turno, com padrões como:
```
added=2:estudar,comprar mantimentos | removed=1:ler
action=list
error=invalid-json | reason=Não consegui interpretar as operações...
```
Use esse campo para instrumentação adicional ou exportação de métricas.

## Checklist de QA manual
1. **Adicionar/remover**: enviar “Adicione estudar e remova ler” → verificar lista final e log.
2. **Listar**: enviar “Liste minhas tarefas” → nenhuma alteração e mensagem “apenas listar”.
3. **Erro proposital**: enviar “faça algo” → mensagem orientando sobre JSON e log `error=invalid-json`.
4. **Deletar inexistente**: “Remova passear” quando não existe → alerta “Não encontrei”.

Registre os resultados em `docs/manual-test.md` sempre que fizer smoke tests.
