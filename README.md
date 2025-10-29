# Web Search Agent (Projeto de Estudo)

Este repositório reúne agentes simples feitos com LangGraph. O projeto atual, `agente_web`, demonstra como combinar Tavily (busca na web) com o modelo Gemini (`gemini-2.5-flash`) para gerar um resumo rápido sobre a pergunta "Como pesquisar arquivos no linux?".

## Pré-requisitos

1. **Python 3.12** (use o `venv/` já incluído ou crie um novo virtualenv).
2. **Chaves de API**:
   - `GEMINI_API_KEY`
   - `TAVILY_API_KEY`
3. **Dependências** instaladas com:
   ```bash
   pip install -r requirements.txt
   ```

## Configuração do `.env`

O arquivo `.env` na raiz deve conter pelo menos:
```bash
GEMINI_API_KEY="sua-chave"
TAVILY_API_KEY="sua-chave"
```
As variáveis são carregadas automaticamente por `agente_web/main.py`.

## Executando o agente

```bash
python agente_web/main.py
```

A execução:
- Consulta a Tavily usando a pergunta padrão.
- Gera um resumo curto com Gemini.
- Exibe avisos (ex.: falta de resultados) e a lista de fontes encontradas.
- Salva o relatório em `agente_web/smoke_test_output.txt` (já ignorado pelo Git).

## Estrutura relevante

```
agente_web/
  main.py                 # fluxo LangGraph completo (buscar → resumir)
  smoke_test_output.txt   # relatório gerado após a execução (ignorado pelo Git)
```

Para explorar outros agentes de estudo, consulte as pastas `agente_simples/`, `agente_tool/`, etc., cada uma com seu próprio `main.py`.
