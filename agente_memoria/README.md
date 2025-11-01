# Agente de Memória

Este agente demonstra como usar o LangGraph para construir um agente conversacional com memória.

## Configuração

1.  **Crie um ambiente virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Crie um arquivo `.env`** no diretório `agente_memoria`. Você pode copiar o arquivo de exemplo:
    ```bash
    cp agente_memoria/.env.example agente_memoria/.env
    ```
    Em seguida, edite o arquivo `.env` e adicione sua chave de API do Gemini.

## Executando o Agente

Para executar o agente, execute o seguinte comando a partir do diretório raiz:

```bash
python -m agente_memoria.cli
```

Você também pode especificar um ID de tópico para manter conversas separadas:

```bash
python -m agente_memoria.cli --thread minha-conversa
```

### Comandos

Os seguintes comandos estão disponíveis na CLI:

- `/sair`: Sai do agente.
- `/reset`: Limpa o histórico do tópico atual, iniciando um novo tópico.
- `/thread <novo-id-topico>`: Muda para um novo tópico de conversa.

## Integração com LangGraph

Este agente está integrado à CLI do LangGraph. Você pode visualizar o grafo do agente com o seguinte comando:

```bash
langgraph dev --graph agente_memoria/graph.py:app
```