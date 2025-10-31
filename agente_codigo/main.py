import contextlib
import io
import os
import re
import traceback
from typing import Annotated, List, Optional, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

MODEL_NAME = "gemini-2.5-flash"
MAX_ITERATIONS = 5
DEFAULT_THREAD_ID = "code-generator-thread"

INITIAL_PROMPT = (
    "Desenvolva um script didático em Python que explore as principais estruturas "
    "de dados (listas, tuplas, conjuntos, dicionários, pilhas, filas e lista "
    "encadeada) em um único arquivo.\n\n"
    "Requisitos:\n"
    "- Implemente classes ou funções para cada estrutura quando fizer sentido.\n"
    "- Inclua exemplos de uso demonstrando inserção, remoção, busca e exibição "
    "dos dados.\n"
    "- Adicione comentários explicativos destacando conceitos chave.\n"
    "- Forneça exercícios em forma de TODOs comentados para que estudantes possam "
    "expandir o conteúdo.\n"
    '- Exponha uma função `main()` que execute todos os exemplos e chame essa '
    'função em `if __name__ == "__main__"`.'
)


# -----------------------------------------------------------------------------
# State definition
# -----------------------------------------------------------------------------


class ExecutionResult(TypedDict, total=False):
    stdout: str
    stderr: str
    exception: str
    return_code: int


class AgentState(TypedDict, total=False):
    messages: Annotated[List[BaseMessage], add_messages]
    iteration_count: int
    code: Optional[str]
    execution_result: Optional[ExecutionResult]
    reflection_feedback: Optional[str]
    status: str
    decision: Optional[str]


# -----------------------------------------------------------------------------
# Graph node placeholders (implemented in later phases)
# -----------------------------------------------------------------------------


def _build_generation_instruction(
    iteration: int, reflection_feedback: Optional[str]
) -> str:
    if iteration == 1:
        iteration_message = (
            f"Você está na iteração {iteration} de {MAX_ITERATIONS}. "
            "Gere o script Python completo conforme o prompt original.\n\n"
        )
        intro_action = "Gere o script Python completo conforme o prompt original."
    else:
        iteration_message = (
            f"Você está na iteração {iteration} de {MAX_ITERATIONS}. "
            "Gere novamente o script Python completo incorporando os ajustes necessários.\n\n"
        )
        intro_action = (
            "Atualize o script Python completo conforme o prompt original, "
            "corrigindo os problemas detectados na execução anterior."
        )

    instruction = (
        iteration_message
        + f"{intro_action}\n\n"
        "Regras:\n"
        "1. Retorne apenas o código Python final sem explicações.\n"
        "2. Certifique-se de que `main()` exista e seja chamado em "
        "`if __name__ == \"__main__\"`.\n"
        "3. Inclua comentários didáticos e TODOs conforme solicitado.\n"
    )
    if reflection_feedback:
        instruction += (
            "\nFeedback da execução anterior (incorpore as correções necessárias):\n"
            f"{reflection_feedback}\n"
        )
    return instruction


def _message_to_text(message: BaseMessage) -> str:
    content = message.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                parts.append(item.get("text", ""))
            else:
                parts.append(str(item))
        return "".join(parts)
    return str(content)


CODE_BLOCK_PATTERN = re.compile(
    r"```(?:python)?\s*(?P<body>[\s\S]*?)```", flags=re.IGNORECASE
)


def _extract_code(text: str) -> str:
    """Return the main code content, stripping Markdown code fences when present."""
    match = CODE_BLOCK_PATTERN.search(text)
    if match:
        return match.group("body").strip()
    return text.strip()


def generation_node(state: AgentState, *, model: ChatGoogleGenerativeAI) -> AgentState:
    """Produce candidate code using the LLM and increment the iteration counter."""
    iteration = state.get("iteration_count", 0) + 1
    reflection_feedback = state.get("reflection_feedback")

    generation_instruction = _build_generation_instruction(iteration, reflection_feedback)

    history = list(state.get("messages", []))
    history.append(HumanMessage(content=generation_instruction))
    ai_response = model.invoke(history)

    code_text = _extract_code(_message_to_text(ai_response))

    return {
        "messages": [HumanMessage(content=generation_instruction), ai_response],
        "iteration_count": iteration,
        "code": code_text,
        "execution_result": None,
        "status": "running",
        "decision": None,
        "reflection_feedback": None,
    }


def execution_node(state: AgentState) -> AgentState:
    """Execute the generated code in-memory and capture outputs."""
    code = state.get("code")
    if not code:
        error_message = "Nenhum código disponível para execução."
        result: ExecutionResult = {
            "stdout": "",
            "stderr": error_message,
            "return_code": 1,
        }
        return {
            "execution_result": result,
            "status": "error",
            "decision": "end",
        }

    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    exception_text: Optional[str] = None
    return_code = 0

    # Use isolated namespace to avoid leaking globals between iterations.
    namespace: dict = {}
    try:
        with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(
            stderr_buffer
        ):
            exec(code, namespace, namespace)
    except Exception as exc:  # noqa: BLE001 - capture all runtime errors
        return_code = 1
        exception_text = "".join(traceback.format_exception(exc.__class__, exc, exc.__traceback__))

    exec_result: ExecutionResult = {
        "stdout": stdout_buffer.getvalue(),
        "stderr": stderr_buffer.getvalue(),
        "return_code": return_code,
    }
    if exception_text:
        exec_result["exception"] = exception_text

    status = "running" if return_code == 0 else "error"

    return {
        "execution_result": exec_result,
        "status": status,
        "decision": None,
    }


def _build_reflection_prompt(code: str, result: ExecutionResult) -> str:
    error_sections = []
    stderr = result.get("stderr") or ""
    if stderr.strip():
        error_sections.append(f"STDERR:\n{stderr.strip()}")
    exception_text = result.get("exception") or ""
    if exception_text.strip():
        error_sections.append(f"TRACEBACK:\n{exception_text.strip()}")
    if not error_sections:
        error_sections.append("Nenhuma saída de erro capturada.")
    error_report = "\n\n".join(error_sections)

    prompt = (
        "Você é responsável por revisar um script Python que acabou de falhar na execução.\n"
        "Analise a mensagem de erro e forneça uma lista de correções claras que o próximo "
        "ciclo de geração deve aplicar. Seja objetivo e aponte seções específicas do código "
        "que precisam de ajustes.\n\n"
        "Código atual:\n"
        "```python\n"
        f"{code.strip()}\n"
        "```\n\n"
        "Relatório de erro:\n"
        f"{error_report}\n\n"
        "Responda em português com um breve resumo seguido de passos numerados."
    )
    return prompt


def reflection_node(state: AgentState, *, model: ChatGoogleGenerativeAI) -> AgentState:
    """Generate feedback based on the latest error to guide the next attempt."""
    code = state.get("code") or ""
    exec_result = state.get("execution_result") or {}
    prompt = _build_reflection_prompt(code, exec_result)
    response = model.invoke([HumanMessage(content=prompt)])
    feedback = _message_to_text(response)

    print("\n--- Reflexão do modelo ---")
    print(feedback)
    print("--- Fim da reflexão ---\n")

    return {
        "reflection_feedback": feedback,
        "status": "running",
        "decision": None,
    }


def _format_execution_summary(result: Optional[ExecutionResult]) -> str:
    if not result:
        return "Nenhuma execução registrada."
    parts = []
    stdout = result.get("stdout") or ""
    if stdout.strip():
        parts.append(f"STDOUT:\n{stdout.strip()}")
    stderr = result.get("stderr") or ""
    if stderr.strip():
        parts.append(f"STDERR:\n{stderr.strip()}")
    exception = result.get("exception") or ""
    if exception.strip():
        parts.append(f"EXCEPTION:\n{exception.strip()}")
    return "\n\n".join(parts) if parts else "Sem saídas visíveis."


def decision_node(state: AgentState) -> AgentState:
    """Determine whether to finish, reflect, or continue looping."""
    iteration = state.get("iteration_count", 0)
    exec_result = state.get("execution_result")
    return_code = exec_result.get("return_code") if exec_result else None

    if return_code == 0:
        print(f"[Iteração {iteration}] Execução bem-sucedida. Encerrando loop.")
        return {
            "status": "success",
            "decision": "end",
        }

    if iteration >= MAX_ITERATIONS:
        print(
            f"[Iteração {iteration}] Limite de tentativas ({MAX_ITERATIONS}) alcançado. "
            "Encerrando loop."
        )
        summary = _format_execution_summary(exec_result)
        print("Resumo da última execução:\n", summary)
        return {
            "status": "limit_reached",
            "decision": "end",
        }

    print(
        f"[Iteração {iteration}] Erro detectado. Enviando para reflexão antes da "
        "próxima tentativa."
    )
    summary = _format_execution_summary(exec_result)
    print("Resumo da execução com erro:\n", summary)
    return {
        "status": "running",
        "decision": "reflect",
    }


def _print_final_summary(state: AgentState) -> None:
    status = state.get("status", "desconhecido")
    iteration = state.get("iteration_count", 0)
    code = state.get("code") or ""
    print("\n===== Resumo Final =====")
    print(f"Status: {status}")
    print(f"Iterações executadas: {iteration}")
    if code:
        print("\n--- Código final ---")
        print(code)
        print("--- Fim do código final ---")
    else:
        print("Nenhum código final disponível.")




# -----------------------------------------------------------------------------
# Graph assembly
# -----------------------------------------------------------------------------


def build_app(model: ChatGoogleGenerativeAI):
    workflow = StateGraph(AgentState)

    workflow.add_node("generate", lambda state: generation_node(state, model=model))
    workflow.add_node("execute", execution_node)
    workflow.add_node("decide", decision_node)
    workflow.add_node("reflect", lambda state: reflection_node(state, model=model))

    workflow.set_entry_point("generate")
    workflow.add_edge("generate", "execute")
    workflow.add_edge("execute", "decide")
    workflow.add_conditional_edges(
        "decide",
        lambda state: state.get("decision", "end"),
        {
            "reflect": "reflect",
            "continue": "generate",
            "end": END,
        },
    )
    workflow.add_edge("reflect", "generate")

    memory = InMemorySaver()
    return workflow.compile(checkpointer=memory)


# -----------------------------------------------------------------------------
# Entry point
# -----------------------------------------------------------------------------


def main() -> None:
    load_dotenv(dotenv_path="agente_codigo/.env")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY não configurada. Defina a variável antes de executar o agente.")
        return

    model = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=0.0,
        api_key=api_key,
    )

    app = build_app(model)
    config = {"configurable": {"thread_id": DEFAULT_THREAD_ID}}

    initial_state: AgentState = {
        "messages": [HumanMessage(content=INITIAL_PROMPT)],
        "iteration_count": 0,
        "code": None,
        "execution_result": None,
        "reflection_feedback": None,
        "status": "running",
        "decision": None,
    }

    try:
        final_state = app.invoke(initial_state, config=config)
    except Exception as exc:  # noqa: BLE001
        print("Erro inesperado durante a execução do agente:", exc)
        raise
    else:
        _print_final_summary(final_state)


if __name__ == "__main__":
    main()
