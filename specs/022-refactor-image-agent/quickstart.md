# Quickstart: Refactor agente_imagem Structure

## Pré-requisitos
1. Python 3.12.3 com o ambiente virtual do repositório (`venv/`).
2. Dependências instaladas: `pip install -r requirements.txt` (já inclui langgraph, langchain-core, langchain_google_genai, Pillow).
3. Variáveis de ambiente configuradas: copiar `agente_simples/.env.example` para `agente_imagem/.env` e ajustar `GOOGLE_API_KEY`.

## Passo a Passo
1. **Congelar comportamento atual (opcional, T1)**
   ```bash
   python agente_imagem/main.py > artefatos/baseline_output.txt
   ```
   > `main.py` agora delega para o CLI, preservando o fluxo legado.
2. **Executar o agente via CLI dedicada**
   ```bash
   python -m agente_imagem.cli --image folder_map.png
   ```
3. **Executar via LangGraph CLI**
   ```bash
   langgraph run agente-imagem --input '{"image_path": "folder_map.png"}'
   ```
4. **Rodar testes automatizados**
   ```bash
   pytest -k agente_imagem -q
   ```

## Resultados Esperados
- Saída em markdown idêntica ao comportamento anterior para `folder_map.png`.
- Logs estruturados informam criação de imagem dummy e status de cada etapa.
- Testes unitários passam sem acessar o serviço real do Gemini (mocks garantem determinismo).
