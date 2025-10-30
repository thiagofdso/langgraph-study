## Como fazer um agente LangGraph criar pastas, ler, escrever e atualizar arquivos, e executar código Python

Um agente LangGraph pode realizar operações com arquivos e executar código Python através de **ferramentas customizadas** (tools). Estas tools são funções Python que o agente invoca para completar tarefas.[1][2]

### Conceitos Fundamentais

Um agente LangGraph com capacidades de manipulação de arquivos é composto por três componentes principais:[2]

1. **Model (LLM)** - O modelo de linguagem que decide qual tool usar
2. **Tools** - Funções que o agente pode chamar para executar ações
3. **Graph** - O fluxo de orquestração que conecta o model aos tools

### Implementação Completa

Aqui está um exemplo prático mostrando como implementar todas as funcionalidades solicitadas:

```python
import os
import json
import subprocess
from typing import Annotated, Any, Literal
from langchain_core.tools import tool
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from langchain_core.messages import AnyMessage
from typing_extensions import TypedDict
import operator

# ============ DEFINIÇÃO DAS TOOLS ============

@tool
def create_folder(path: str) -> str:
    """
    Cria uma pasta/diretório no caminho especificado.
    Se pastas intermediárias não existirem, elas também serão criadas.
    
    Args:
        path: Caminho da pasta a ser criada (ex: 'dados/projeto/config')
    
    Returns:
        Mensagem de sucesso ou erro
    """
    try:
        os.makedirs(path, exist_ok=True)
        return f"✓ Pasta criada com sucesso: {path}"
    except Exception as e:
        return f"✗ Erro ao criar pasta: {str(e)}"


@tool
def write_file(path: str, content: str) -> str:
    """
    Escreve conteúdo em um arquivo. Cria o arquivo se não existir.
    Se o diretório não existir, ele será criado automaticamente.
    
    Args:
        path: Caminho do arquivo (ex: 'dados/dados.txt')
        content: Conteúdo a ser escrito
    
    Returns:
        Mensagem de sucesso ou erro
    """
    try:
        # Garante que o diretório existe
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"✓ Arquivo escrito com sucesso: {path}"
    except Exception as e:
        return f"✗ Erro ao escrever arquivo: {str(e)}"


@tool
def read_file(path: str) -> str:
    """
    Lê o conteúdo completo de um arquivo.
    
    Args:
        path: Caminho do arquivo (ex: 'dados/dados.txt')
    
    Returns:
        Conteúdo do arquivo ou mensagem de erro
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return f"✗ Arquivo não encontrado: {path}"
    except Exception as e:
        return f"✗ Erro ao ler arquivo: {str(e)}"


@tool
def update_file(path: str, content: str, mode: str = "overwrite") -> str:
    """
    Atualiza um arquivo existente. Pode sobrescrever ou anexar conteúdo.
    
    Args:
        path: Caminho do arquivo
        content: Novo conteúdo ou conteúdo a anexar
        mode: "overwrite" para substituir, "append" para anexar
    
    Returns:
        Mensagem de sucesso ou erro
    """
    try:
        if mode == "overwrite":
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"✓ Arquivo atualizado (sobrescrito): {path}"
        elif mode == "append":
            with open(path, 'a', encoding='utf-8') as f:
                f.write(content)
            return f"✓ Arquivo atualizado (anexado): {path}"
        else:
            return "✗ Modo inválido. Use 'overwrite' ou 'append'"
    except Exception as e:
        return f"✗ Erro ao atualizar arquivo: {str(e)}"


@tool
def execute_python(code: str) -> str:
    """
    Executa código Python em um ambiente isolado usando subprocess.
    O código é executado em um processo separado para segurança.
    
    Args:
        code: Código Python a ser executado (como string)
    
    Returns:
        Output do código ou mensagem de erro
    """
    try:
        # Executa o código em um processo separado
        result = subprocess.run(
            ["python", "-c", code],
            capture_output=True,
            text=True,
            timeout=30  # Timeout de 30 segundos
        )
        
        if result.returncode == 0:
            # Sucesso
            output = result.stdout.strip()
            return output if output else "✓ Código executado com sucesso (sem output)"
        else:
            # Erro na execução
            error = result.stderr.strip()
            return f"✗ Erro ao executar código:\n{error}"
    
    except subprocess.TimeoutExpired:
        return "✗ Erro: Execução expirou (timeout > 30s)"
    except Exception as e:
        return f"✗ Erro ao executar código: {str(e)}"


# Alternativa: Execute Python com acesso a variáveis (menos seguro, mas mais flexível)
@tool
def execute_python_with_context(code: str) -> str:
    """
    Executa código Python com contexto compartilhado.
    Use quando precisar de variáveis entre múltiplas execuções.
    NOTA: Menos seguro que execute_python.
    
    Args:
        code: Código Python a ser executado
    
    Returns:
        Output do código ou mensagem de erro
    """
    try:
        # Cria um contexto de execução
        exec_globals = {}
        exec_locals = {}
        
        exec(code, exec_globals, exec_locals)
        
        # Tenta capturar output se houver variável 'result'
        if 'result' in exec_locals:
            return str(exec_locals['result'])
        else:
            return "✓ Código executado com sucesso"
    
    except Exception as e:
        return f"✗ Erro ao executar código: {str(e)}"


# ============ DEFINIÇÃO DO AGENTE ============

# Define o state do agente
class State(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

# Cria o modelo
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Define as tools
tools = [
    create_folder,
    write_file,
    read_file,
    update_file,
    execute_python,
]

# Vincula as tools ao modelo
model_with_tools = model.bind_tools(tools)

# Define o nó que executa o modelo
def call_model(state: State):
    messages = state["messages"]
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}

# Define o nó que executa as tools
tool_node = ToolNode(tools)

# Define lógica condicional
def should_continue(state: State):
    messages = state["messages"]
    last_message = messages[-1]
    
    # Se há tool_calls, vai para executar tools
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    # Caso contrário, termina
    return END

# Cria o graph
graph_builder = StateGraph(State)

# Adiciona os nós
graph_builder.add_node("model", call_model)
graph_builder.add_node("tools", tool_node)

# Adiciona as edges
graph_builder.add_edge(START, "model")
graph_builder.add_conditional_edges("model", should_continue, ["tools", END])
graph_builder.add_edge("tools", "model")

# Compila o graph
graph = graph_builder.compile()

# ============ USANDO O AGENTE ============

if __name__ == "__main__":
    from langchain_core.messages import HumanMessage
    
    # Exemplo 1: Criar pasta e escrever arquivo
    print("=" * 60)
    print("EXEMPLO 1: Criar pasta e escrever arquivo")
    print("=" * 60)
    
    response = graph.invoke({
        "messages": [HumanMessage(content="""
        Crie uma pasta chamada 'projeto_dados' e dentro dela crie um arquivo 'dados.json'
        com o seguinte conteúdo JSON:
        {
            "nome": "João",
            "idade": 30,
            "email": "joao@example.com"
        }
        """)]
    })
    
    print("\nÚltima resposta do agente:")
    print(response["messages"][-1].content)
    
    
    # Exemplo 2: Ler arquivo
    print("\n" + "=" * 60)
    print("EXEMPLO 2: Ler arquivo")
    print("=" * 60)
    
    response = graph.invoke({
        "messages": [HumanMessage(content="Leia o arquivo projeto_dados/dados.json e me mostre o conteúdo")]
    })
    
    print("\nÚltima resposta do agente:")
    print(response["messages"][-1].content)
    
    
    # Exemplo 3: Executar código Python
    print("\n" + "=" * 60)
    print("EXEMPLO 3: Executar código Python")
    print("=" * 60)
    
    response = graph.invoke({
        "messages": [HumanMessage(content="""
        Execute código Python que:
        1. Cria uma lista com números de 1 a 5
        2. Calcula a soma
        3. Imprime o resultado
        """)]
    })
    
    print("\nÚltima resposta do agente:")
    print(response["messages"][-1].content)
    
    
    # Exemplo 4: Atualizar arquivo
    print("\n" + "=" * 60)
    print("EXEMPLO 4: Atualizar arquivo")
    print("=" * 60)
    
    response = graph.invoke({
        "messages": [HumanMessage(content="""
        Anexe as seguintes linhas ao arquivo projeto_dados/dados.json:
        ,
        "ativo": true,
        "cidade": "São Paulo"
        }
        """)]
    })
    
    print("\nÚltima resposta do agente:")
    print(response["messages"][-1].content)
```

### Recursos Importantes

**Segurança ao executar código Python:**[3][4]

Para executar código não confiável de forma segura, existem alternativas:

- **Sandbox com Pyodide**: Use `langchain-sandbox` para WebAssembly
- **Subprocess com timeout**: Limite tempo de execução (como no exemplo acima)
- **Allowlist de comandos**: Restrinja operações permitidas

**Tratamento de Erro em Tools:**[2]

As tools devem sempre retornar strings com feedback claro sobre sucesso ou erro. O agente usa essa informação para decidir próximos passos.

**Estado Compartilhado:**[5]

Se precisar de variáveis compartilhadas entre múltiplas execuções de código Python, use `execute_python_with_context()` ou armazene dados em arquivos.

### Instalação de Dependências

```bash
pip install langgraph langchain langchain-openai langchain-experimental
```

Este exemplo fornece uma base sólida e segura para agentes LangGraph com manipulação completa de arquivos e execução de código Python. Você pode expandir adicionando mais validações, logging, ou integrações com sistemas de armazenamento em nuvem conforme necessário.[6][7][8][1][2]

[1](https://www.datacamp.com/pt/tutorial/langgraph-agents)
[2](https://docs.langchain.com/oss/python/langgraph/graph-api)
[3](https://developer.nvidia.com/blog/create-your-own-bash-computer-use-agent-with-nvidia-nemotron-in-one-hour/)
[4](https://github.com/langchain-ai/langchain-sandbox)
[5](https://www.getzep.com/ai-agents/langgraph-tutorial/)
[6](https://analisemacro.com.br/inteligencia-artificial/automatizando-a-construcao-de-codigos-em-python-com-langgraph/)
[7](https://hub.asimov.academy/blog/langgraph/)
[8](https://langchain-ai.github.io/langgraph/how-tos/tool-calling/)
[9](https://www.youtube.com/watch?v=f4ID3ZxRG1A)
[10](https://translate.google.com/translate?u=https%3A%2F%2Fmedium.com%2Fpythoneers%2Fbuilding-ai-agent-systems-with-langgraph-9d85537a6326&hl=pt&sl=en&tl=pt&client=srp)
[11](https://docs.langchain.com/oss/python/langchain/agents)
[12](https://deployapps.dev/blog/data-analyst-agent-langgraph-genezio/)
[13](https://www.datacamp.com/pt/tutorial/building-langchain-agents-to-automate-tasks-in-python)
[14](https://github.com/langchain-ai/langgraph)
[15](https://github.com/jakenolan/langgraph-custom-tools)
[16](https://www.youtube.com/watch?v=swXFdmF4EZw)
[17](https://github.com/ju-bezdek/langchain-decorators)
[18](https://www.reddit.com/r/learnpython/comments/wgzx2w/create_file_if_it_doesnt_exist_as_well_as_its/)
[19](https://docs.langchain.com/oss/python/langchain/structured-output)
[20](https://docs.langchain.com/oss/python/langchain/tools)
[21](https://api.python.langchain.com/en/latest/experimental/tools/langchain_experimental.tools.python.tool.PythonREPLTool.html)
[22](https://stackoverflow.com/questions/77744941/load-tool-does-not-recognize-python-repl-in-langchain)