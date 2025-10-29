# Agente Banco de Dados

Projeto de estudo que cria um agente LangGraph simples. Ele inicializa um banco SQLite local com dados de produtos, vendedores e vendas, e gera um relatório em Markdown com os destaques.

## Pré-requisitos
- Python 3.12 (utilize o `venv/` já presente no repositório)
- Dependências instaladas com `pip install -r requirements.txt`
- Arquivo `.env` copiado de `agente_simples/.env` para `agente_banco_dados/.env`

## Como executar
1. Ative o ambiente virtual do repositório.
2. Na raiz do projeto execute:
   ```bash
   python agente_banco_dados/main.py
   ```
3. A execução irá:
   - Criar (ou reutilizar) `agente_banco_dados/data/sales.db` com dados de exemplo.
   - Executar o fluxo do LangGraph para consultar apenas o banco local.
   - Exibir no terminal um relatório em Markdown destacando os produtos mais vendidos e os melhores vendedores.

> O agente não faz chamadas de rede nem consultas externas: todo o conteúdo é derivado do banco local.

## Estrutura principal
- `db_init.py`: criação de esquema e inserção idempotente de dados.
- `reporting.py`: consultas agregadas e formatação do relatório em Markdown.
- `main.py`: ponto de entrada que inicializa o banco, executa o LangGraph e imprime o relatório.
- `data/`: diretório para o arquivo SQLite gerado.

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
```

A execução completa leva apenas alguns segundos e pode ser repetida quantas vezes quiser para estudo.
