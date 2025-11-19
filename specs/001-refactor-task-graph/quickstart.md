# Quickstart: Graph-Managed Task Workflow

## 1. Pré-requisitos
1. Ative o virtualenv da raiz: `source venv/bin/activate`.
2. Garanta `.env` dentro de `agente_tarefas/` com `GEMINI_API_KEY` (mesmo formato dos outros agentes).
3. Instale dependências compartilhadas na raiz: `pip install -r requirements.txt`.

## 2. Executar o CLI tradicional
```bash
cd agente_tarefas
python -m agente_tarefas
```
- Observe três rodadas. O CLI apenas coleta entradas e encaminha ao grafo; todas as mutações são tratadas pelos nodes.
- Logs/timeline devem mostrar três entradas após a conclusão.

## 3. Executar testes automatizados
```bash
pytest agente_tarefas/tests -q
```
- Inclui testes novos de nodes, grafo e CLI, garantindo que o estado seja atualizado via LangGraph.

## 4. Smoke test do módulo principal
```bash
python agente_tarefas/main.py --smoke
```
- (Caso exista flag `--smoke`, usar; caso contrário execute `python agente_tarefas/main.py` e siga o fluxo padrão.)
- Confirme que o resumo final corresponde às alterações feitas pelos nodes.

## 5. LangGraph CLI manual
```bash
langgraph run agente-tarefas \
  --thread-id demo-thread \
  --input '{"messages": [{"role": "user", "content": "Rodada 1"}], "tasks": [], "completed_ids": [], "timeline": []}'
```
- Forneça inputs simulados para cada rodada (os testes manuais devem cobrir essa etapa conforme requisito do usuário).
- Verifique se `tasks`, `completed_ids` e `timeline` são atualizados apenas pelos nodes e se o output final bate com o CLI tradicional.

## 6. Checklist antes do merge
- CLI tradicional executa sem alterações manuais no estado local.
- Rodar `pytest` sem falhas.
- Registrar observações de LangGraph CLI manual no PR (incluindo comandos usados e comportamento observado).
- Atualizar `graph-nodes-patterns.md` caso novos nomes de nodes tenham sido introduzidos.
