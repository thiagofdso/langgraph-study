# CLI Contract: agente_imagem

## Command: Python Module Entry Point
- **Executable**: `python -m agente_imagem.cli`
- **Arguments**:
  - `--image <path>` *(optional, default: `folder_map.png`)* – caminho do arquivo PNG a ser processado.
- **Environment Requirements**:
  - `GOOGLE_API_KEY` (obrigatório) – chave para invocar `gemini-2.5-flash`.
  - Opções adicionais reutilizam variáveis de `agente_simples` (`GEMINI_MODEL`, `GEMINI_TEMPERATURE`).
- **Input Contract**:
  - O arquivo deve ser uma imagem legível pelo Pillow; se inexistente, o agente criará uma imagem dummy mantendo compatibilidade histórica (T15).
- **Output Contract**:
  - `stdout`: markdown hierárquico retornado pelo LLM quando a validação é bem sucedida.
  - `stderr`: logs estruturados caso erros ocorram.
  - Código de saída 0 em sucesso; 1 quando ocorrer exceção não tratada.

## Command: LangGraph CLI
- **Executable**: `langgraph run agente-imagem`
- **Arguments**:
  - `--input '{"image_path": "..."}'` – JSON com caminho opcional para a imagem.
  - `--config '{"configurable": {"thread_id": "..."}}'` – (opcional) quando fluxo exigir isolamento.
- **Dependencies**:
  - `langgraph.json` deve conter registro `"agente-imagem": "agente_imagem/graph.py:create_app"` (T11).
- **Output Contract**:
  - `markdown_output` no estado final; erros retornam `status="error"` e `markdown_output=null` preservando mensagens anteriores.
