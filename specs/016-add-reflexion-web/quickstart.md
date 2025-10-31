# Quickstart — Reflexion Web Evidence Agent

## Pré-requisitos
- Python 3.12.3 utilizando o `venv` do repositório (`source venv/bin/activate`).
- Variáveis `GEMINI_API_KEY` e `TAVILY_API_KEY` configuradas no `.env` do agente (copiado de `agente_web`).
- Acesso à internet para consultas Tavily e chamadas ao Gemini.

## Passo a passo
1. Copie o arquivo `.env` existente em `agente_web/.env` para `agente_reflexao_web/.env` sem modificações.
2. Garanta que o ambiente virtual esteja ativo e com dependências atualizadas (`pip install -r requirements.txt` se necessário).
3. Execute o agente:
   ```bash
   python agente_reflexao_web/main.py
   ```
4. Observe no console:
   - Evidências coletadas (com título e URL).
   - Até três iterações de rascunho/reflexão com críticas fundamentadas.
   - Resposta final em português com citações numeradas e seção de referências.

## Resultado Esperado
- O script encerra após consolidar a resposta (sem loops interativos).
- Arquivo `.env` permanece idêntico ao copiado.
- Nenhum teste automatizado ou parâmetros adicionais são gerados.
