# Checklist de Teste Manual – agente_tarefas

Execute sempre após alterações relevantes e utilize o comando:
```
venv/bin/langgraph dev --config langgraph.json --host 0.0.0.0
```

## Cenário 1 – Adicionar e remover
1. Inicie com lista vazia.
2. Envie: `Adicione estudar e comprar mantimentos, depois remova lavar louça`.
3. Verifique:
   - Resumo cita tarefas adicionadas/removidas.
   - Lista final contém `estudar`, `comprar mantimentos`.
   - `operation_report.log_entry` inclui `added=2` e `removed=1`.

## Cenário 2 – Listar sem alterações
1. Com tarefas existentes, envie `Liste minhas tarefas`.
2. Esperado:
   - Mensagem “Você solicitou apenas listar...”.
   - Nenhuma alteração na lista.
   - `log_entry` contém `action=list`.

## Cenário 3 – Deletar inexistente
1. Envie `Remova tarefa fantasma`.
2. Esperado:
   - Resumo informa “Não encontrei”.
   - Lista permanece igual.
   - `log_entry` inclui `missing=1:tarefa fantasma`.

## Cenário 4 – Erro de formato
1. Envie `faça algo`.
2. Esperado:
   - Mensagem explica o formato JSON correto.
   - Nenhuma alteração aplicada.
   - `log_entry` começa com `error=`.

Registre qualquer desvio ou regressão antes do deploy.
