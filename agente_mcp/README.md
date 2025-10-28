# Agente MCP

Este projeto implementa um agente que utiliza o MultiServerMCPClient para interagir com múltiplos servidores MCP (Multi-Agent Communication Protocol). Atualmente, o agente está configurado para usar um servidor de matemática e um servidor de clima.

## Estrutura do Projeto

```
agente_mcp/
├── __init__.py
├── main.py
├── agent_graph.py
├── common.py
├── mcp_servers/
│   ├── math_server.py
│   └── weather_server.py
└── README.md
```

## Configuração

1.  **Variáveis de Ambiente**: Crie um arquivo `.env` dentro da pasta `agente_mcp/` e adicione sua chave de API do Gemini:

    ```
    GEMINI_API_KEY=sua_chave_api_aqui
    ```

2.  **Instalação de Dependências**: Certifique-se de ter um ambiente virtual Python configurado e ativado. Instale as dependências listadas no `requirements.txt` do projeto principal:

    ```bash
    source venv/bin/activate
    pip install -r requirements.txt
    ```

## Como Executar

Para executar o agente, siga os passos abaixo:

1.  **Inicie o Servidor de Clima (Weather Server)**: O servidor de clima precisa ser executado em segundo plano, pois o agente se conecta a ele via HTTP (SSE).

    ```bash
    python agente_mcp/mcp_servers/weather_server.py &
    ```
    Anote o PID do processo, caso precise encerrá-lo manualmente.

2.  **Execute o Agente**: O agente `main.py` irá se conectar ao servidor de clima em execução e iniciará o servidor de matemática via `stdio`.

    ```bash
    PYTHONPATH=. python agente_mcp/main.py
    ```

    O agente fará duas perguntas predefinidas: uma para o servidor de matemática e outra para o servidor de clima, e exibirá as respostas.

## Exemplo de Saída

```
User: quanto é 150 vezes 3?
Assistant: "450.0"
Assistant: 150 vezes 3 é 450.
------------------------------
User: qual o clima em Nova York?
Assistant: "It's always sunny in New York"
Assistant: O clima em Nova York está sempre ensolarado.
```

## Encerrando o Servidor de Clima

Se você iniciou o servidor de clima em segundo plano, pode encerrá-lo usando o comando `kill` com o PID do processo (substitua `[PID]` pelo número real):

```bash
kill [PID]
```