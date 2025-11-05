# Quickstart — Relatório de Vendas com Insights Gemini

## Pré-requisitos
- Python 3.12.3 com `venv` ativado (`source venv/bin/activate`).
- Dependências instaladas (`pip install -r requirements.txt`).
- Banco SQLite inicializado pelo CLI (`agente_banco_dados/db_init.py` é chamado automaticamente).
- Variáveis de ambiente:
  - `GEMINI_API_KEY` com credencial válida.
  - Opcional: `GEMINI_MODEL=gemini-2.5-flash`, `GEMINI_TEMPERATURE=0.25`.

## Executando o agente
```bash
python -m agente_banco_dados.cli
```

Saída esperada:
1. Mensagem confirmando preparo do banco (`Database ready with ...`).
2. Aviso de que o relatório usa somente o SQLite local.
3. Markdown contendo:
   - Tabelas de produtos e vendedores.
   - Seção “## Insights gerados pela IA” com três blocos (tendências, riscos, recomendações) referenciando números concretos.
   - Rodapé com carimbo `generated_at` em UTC e resumo de metadados quando disponível.
4. Resumo textual com registros processados, latência aproximada da chamada ao LLM, fonte dos dados e timestamp.

## Tratamento de erros
- Se `GEMINI_API_KEY` estiver ausente ou inválido, a execução informa o erro e orienta a configurar a chave.
- Quaisquer falhas do serviço Gemini resultam em mensagem amigável e registro do motivo em `metadata.llm_error`.

## Testes recomendados
```bash
pytest agente_banco_dados/tests
```
- Utilize `monkeypatch` para substituir a chamada à IA e validar que os insights aparecem corretamente.
- Simule ausência de credencial para confirmar mensagens de erro pedagógicas.
