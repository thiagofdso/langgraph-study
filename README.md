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

## Executando o LangGraph CLI e Dashboard

Para rodar o ambiente local com suporte ao dashboard do LangGraph:

1. Execute `langgraph dev --config langgraph.json --host 0.0.0.0` para iniciar o CLI local.
2. Gere um certificado SSL autoassinado e ajuste as variáveis de ambiente `SSL_PATH` (caminho do certificado/chave) e `NGINX_CONF_PATH` (arquivo de configuração do NGINX) para refletirem os caminhos corretos.
3. Rode o script `nginx/start.sh` para iniciar o proxy NGINX com o novo certificado.
4. Adicione a entrada `langgraph.local` ao arquivo de hosts do sistema:
   - Linux: `/etc/hosts`
   - Windows: `C:\\Windows\\System32\\drivers\\etc\\hosts`
5. No Windows, instale o certificado gerado em **Autoridades de Certificação Raiz Confiáveis** para evitar avisos de segurança.
6. Acesse `https://smith.langchain.com/studio/?baseUrl=https://langgraph.local` para visualizar o dashboard do LangGraph.
