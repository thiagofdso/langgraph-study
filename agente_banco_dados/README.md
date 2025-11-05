# Agente Banco de Dados

Projeto de estudo que cria um agente LangGraph simples. Ele inicializa um banco SQLite local com dados de produtos, vendedores e vendas, e gera um relatório em Markdown com os destaques.

## Pré-requisitos
- Python 3.12 (utilize o `venv/` já presente no repositório)
- Dependências instaladas com `pip install -r requirements.txt`
- Arquivo de variáveis de ambiente configurado:
  1. Copie `agente_banco_dados/.env.example` para `agente_banco_dados/.env`.
  2. Preencha `GEMINI_API_KEY` com uma chave válida do Gemini.
  3. Ajuste `GEMINI_MODEL` ou `GEMINI_TEMPERATURE` apenas se necessário.

## Como executar
1. Ative o ambiente virtual do repositório.
2. Na raiz do projeto execute:
   ```bash
   python agente_banco_dados/main.py
   ```
3. A execução irá:
   - Criar (ou reutilizar) `agente_banco_dados/data/sales.db` com dados de exemplo.
   - Construir métricas locais e enviar o contexto para o Gemini (`gemini-2.5-flash`) gerar insights.
   - Exibir no terminal um relatório em Markdown contendo tabelas de produtos e vendedores, bem como a seção `## Insights gerados pela IA`.
   - Informar o horário de geração (`generated_at`) e um resumo dos registros processados.

> A consulta aos dados permanece totalmente local. A única chamada externa é a invocação do modelo Gemini para produzir a narrativa.

### Executando com o LangGraph CLI
Após registrar o grafo no `langgraph.json`, o agente pode ser invocado sem o script principal:

```bash
langgraph run agente_banco_dados
```

### Uso programático do grafo
Você também pode importar a função `create_app()` para reutilizar o grafo em outros scripts:

```python
from agente_banco_dados import create_app, initialize_database

initialize_database()
app = create_app()
result = app.invoke({})
print(result["report_markdown"])
```

## Estrutura principal
- `config.py`: constantes e ajustes de limites para o seed.
- `db_init.py`: criação de esquema e inserção idempotente de dados.
- `reporting.py`: consultas agregadas e formatação do relatório em Markdown.
- `state.py`: contratos tipados compartilhados entre os nodes.
- `utils/nodes.py`: nós do LangGraph responsáveis por buscar métricas e renderizar o relatório.
- `graph.py`: definição e compilação do grafo (`create_app` e `app`).
- `cli.py`: orquestrador da linha de comando.
- `main.py`: entry point legacy que delega para `cli.main`.
- `tests/test_agente_banco_dados.py`: teste que garante a emissão do relatório via `create_app`.
- `data/`: diretório para o arquivo SQLite gerado.

## Arquitetura modular
- **Seed e configuração**: `db_init.py` e `config.py` continuam responsáveis por preparar e validar o banco local.
- **Camada de domínio**: `state.py` define o contrato de dados (`ReportState`, `ProductSummary`, `SellerSummary`) consumido pelos nodes.
- **Orquestração LangGraph**: `utils/nodes.py` encapsula as operações puras (`load_sales_metrics` e `render_sales_report`), enquanto `graph.py` monta o fluxo sequencial.
- **Interfaces de execução**: `cli.py` prepara o ambiente e imprime o relatório; `create_app()` permite uso programático e integração com LangGraph CLI; `main.py` delega para o CLI mantendo compatibilidade com o comando legado.

## Reinicializando os dados
Apague `agente_banco_dados/data/sales.db` e execute o comando novamente. O script recriará o banco com os dados de exemplo.

## Resultado esperado
Um trecho típico do relatório:

```markdown
# Relatório de Vendas Baseado em SQLite
*Fonte: banco de dados local agente_banco_dados/data/sales.db*

## Produtos mais vendidos
| Produto                     | Quantidade | Receita     |
| --------------------------- | ---------- | ----------- |
| Conference Speaker          | 34         | R$ 14280,00 |
| Noise-Cancelling Headphones | 28         | R$ 24920,00 |
| Smart Monitor               | 22         | R$ 34980,00 |

## Melhores vendedores
| Vendedor     | Região       | Quantidade | Receita     |
| ------------ | ------------ | ---------- | ----------- |
| Alice Alves  | São Paulo    | 36         | R$ 45650,00 |
| Carla Costa  | Minas Gerais | 38         | R$ 44370,00 |
| Daniela Dias | Paraná       | 28         | R$ 36390,00 |

## Insights gerados pela IA
1. Tendência: Produtos premium concentram maior receita (ex.: "Noise-Cancelling Headphones" com R$ 24920,00).
2. Risco: Queda recente no volume do "Smart Monitor" pode afetar margem de monitores.
3. Recomendação: Incentivar vendedores da região Sul com combos envolvendo "Conference Speaker".

*Gerado em 2025-11-05T14:23:11.123456+00:00*
```

A execução completa leva apenas alguns segundos e pode ser repetida quantas vezes quiser para estudo.
