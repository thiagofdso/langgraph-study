"""Node implementations for the agente_tool LangGraph workflow."""

from __future__ import annotations

import math
import time
from typing import Any, Callable, Dict, List

from langchain_core.messages import AIMessage, BaseMessage, SystemMessage, ToolMessage

from agente_tool.config import AppConfig, ConfigurationError, config as default_config
from agente_tool.state import GraphState, ToolPlan
from agente_tool.utils.logging import get_logger
from agente_tool.utils.tools import calculator, CalculatorError

logger = get_logger(__name__)

SYSTEM_PROMPT = (
    "Você é um assistente matemático especializado em resolver operações numéricas usando a ferramenta `calculator`. "
    "Sempre responda em português. Sempre que a pergunta exigir qualquer cálculo "
    "aritmético ou algébrico, chame a ferramenta `calculator` informando "
    "um único campo `expression` com a operação em notação infixa (ex.: '300 / 4'). "
    "Faça isso mesmo caso entenda que pode fazer o calculo sózinho."
    "Ela é necessária para auditar todos calculos feitos."
    "Após receber o resultado da ferramenta, explique de forma breve o raciocínio e "
    "apresente o valor final. Se a pergunta não envolver contas, responda normalmente. "
    "Caso a ferramenta retorne erro, peça novos dados ao usuário em vez de inventar um valor."
    "Não mencione a chamada da ferramenta calculator nem seu funcionamento durante sua resposta."
    "Caso entenda que não é possível usar a ferramenta explique-se."
)

STATUS_VALIDATED = "validated"
STATUS_RESPONDED = "responded"
STATUS_COMPLETED = "completed"
STATUS_ERROR = "error"

_QUESTION_MIN_LENGTH = 5
_TOOL_NAME = "calculator"


def _clean_content(message: BaseMessage | Dict[str, Any]) -> str:
    """Return the textual content from the provided message-like object."""

    if isinstance(message, BaseMessage):
        content = getattr(message, "content", "")
    elif isinstance(message, dict):
        content = str(message.get("content", ""))
    else:
        content = ""

    if isinstance(content, list):
        parts: List[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text")
                if text:
                    parts.append(str(text))
        content = "".join(parts)

    if content is None:
        return ""

    return str(content).strip()


def _ensure_question(state: GraphState) -> str:
    """Extract the current question text from the state."""

    messages = state.get("messages") or []
    if not messages:
        return ""
    last_message = messages[-1]
    return _clean_content(last_message)


def _initial_metadata(question: str) -> Dict[str, Any]:
    """Build metadata dictionary seeded with the current question."""

    return {
        "question": question,
        "system_prompt": SYSTEM_PROMPT,
        "started_at": time.perf_counter(),
    }


def validate_input(state: GraphState) -> Dict[str, Any]:
    """Validate user input and prepare metadata for downstream nodes."""

    question = _ensure_question(state)
    metadata = _initial_metadata(question)

    if len(question) < _QUESTION_MIN_LENGTH:
        logger.warning("Pergunta inválida: muito curta", extra={"question": question})
        return {
            "metadata": metadata,
            "status": STATUS_ERROR,
            "resposta": (
                "Preciso de mais detalhes para ajudar. Informe uma operação matemática completa."
            ),
        }

    logger.info("Pergunta validada", extra={"question": question})
    return {
        "metadata": metadata,
        "status": STATUS_VALIDATED,
    }


def plan_tool_usage(state: GraphState) -> Dict[str, Any]:
    """Inspect the latest model output and prepare a tool plan if requested."""

    messages = state.get("messages") or []
    ai_messages = [message for message in messages if isinstance(message, AIMessage)]
    if not ai_messages:
        logger.info(
            "Nenhuma saída do modelo disponível para planejamento de ferramentas."
        )
        return {"selected_tool": None, "tool_plan": None}
    last_message = ai_messages[-1]
    tool_calls = getattr(last_message, "tool_calls", None) or []
    if not tool_calls:
        logger.info("Modelo não solicitou ferramentas nesta rodada.")
        return {"selected_tool": None, "tool_plan": None}

    call = tool_calls[0]
    tool_name = call.get("name")
    if tool_name != _TOOL_NAME:
        logger.warning(
            "Ferramenta desconhecida solicitada pelo modelo",
            extra={"tool": tool_name},
        )
        return {
            "selected_tool": tool_name,
            "tool_plan": None,
            "status": STATUS_ERROR,
            "resposta": (
                "Recebi uma solicitação para uma ferramenta desconhecida. "
                "Tente novamente com uma operação matemática simples."
            ),
        }

    plan: ToolPlan = {
        "name": tool_name,
        "args": call.get("args", {}),
        "call_id": call.get("id"),
    }

    logger.info(
        "Plano de ferramenta detectado",
        extra={"tool": tool_name, "tool_args": plan["args"]},
    )
    return {
        "selected_tool": tool_name,
        "tool_plan": plan,
    }


def execute_tools(
    state: GraphState,
    *,
    calculator_fn: Callable[[str], Any] | None = None,
) -> Dict[str, Any]:
    """Execute the planned tool and attach the result to the message history."""

    plan = state.get("tool_plan")
    if not plan:
        return {}

    tool_name = plan.get("name")
    if tool_name != _TOOL_NAME:
        logger.error("Ferramenta planejada não suportada", extra={"tool": tool_name})
        return {
            "status": STATUS_ERROR,
            "resposta": (
                "A ferramenta solicitada não está disponível. Utilize apenas operações matemáticas simples."
            ),
        }

    expression = plan.get("args", {}).get("expression")
    if not expression:
        logger.error(
            "Plano de ferramenta sem expressão definida.", extra={"plan": plan}
        )
        return {
            "status": STATUS_ERROR,
            "resposta": "A ferramenta calculadora não recebeu uma expressão válida.",
        }

    runner = calculator_fn or (lambda expr: calculator.invoke({"expression": expr}))

    try:
        raw_result = runner(expression)
        result = str(raw_result)
        logger.info(
            "Ferramenta executada com sucesso",
            extra={"tool": tool_name, "expression": expression, "result": result},
        )
    except CalculatorError as exc:
        logger.warning("Erro controlado da calculadora", extra={"error": str(exc)})
        return {
            "status": STATUS_ERROR,
            "resposta": str(exc),
        }
    except Exception as exc:  # pragma: no cover - proteção adicional
        logger.exception(
            "Falha inesperada ao executar ferramenta",
            extra={"expression": expression},
        )
        return {
            "status": STATUS_ERROR,
            "resposta": (
                "Não consegui processar essa expressão matemática. "
                "Revise a operação e tente novamente."
            ),
            "tool_call": {
                "name": tool_name,
                "args": plan.get("args", {}),
                "error": str(exc),
            },
        }

    tool_message = ToolMessage(
        tool_call_id=plan.get("call_id") or f"{tool_name}-call",
        name=tool_name,
        content=result,
    )

    metadata = dict(state.get("metadata", {}))
    metadata["last_tool_result"] = result
    metadata["last_tool_expression"] = expression

    return {
        "messages": [tool_message],
        "status": STATUS_VALIDATED,
        "selected_tool": tool_name,
        "tool_call": {
            "name": tool_name,
            "args": plan.get("args", {}),
            "result": result,
        },
        "metadata": metadata,
        "resposta": result,
    }


def _build_conversation(state: GraphState) -> List[BaseMessage]:
    """Compose the conversation to send to the model."""

    conversation: List[BaseMessage] = []
    system_prompt = state.get("metadata", {}).get("system_prompt")
    if system_prompt:
        conversation.append(SystemMessage(content=system_prompt))
    conversation.extend(state.get("messages", []))
    return conversation


def invoke_model(
    state: GraphState,
    *,
    llm: Any | None = None,
    app_config: AppConfig | None = None,
) -> Dict[str, Any]:
    """Call the configured LLM with accumulated messages."""

    question = state.get("metadata", {}).get("question", "")
    if not question:
        logger.error("Pergunta ausente ao chamar o modelo.")
        return {
            "status": STATUS_ERROR,
            "resposta": "Não consegui identificar a pergunta. Tente novamente com mais detalhes.",
        }

    cfg = app_config or default_config
    model = llm

    if model is None:
        try:
            model = cfg.create_llm()
        except ConfigurationError as exc:
            logger.error(
                "Configuração inválida ao instanciar LLM", extra={"error": str(exc)}
            )
            return {"status": STATUS_ERROR, "resposta": str(exc)}

    conversation = _build_conversation(state)

    try:
        response = model.invoke(conversation)
        print(response)
    except ConfigurationError as exc:
        logger.error(
            "Erro de configuração ao invocar modelo", extra={"error": str(exc)}
        )
        return {"status": STATUS_ERROR, "resposta": str(exc)}
    except Exception:  # pragma: no cover - trajetória de exceção logada
        logger.exception("Falha inesperada ao chamar o modelo")
        return {
            "status": STATUS_ERROR,
            "resposta": (
                "Encontrei um problema ao consultar o modelo agora. "
                "Tente novamente em alguns instantes."
            ),
        }

    raw_content = _clean_content(response)
    if raw_content:
        logger.info("Resposta obtida do modelo.")
        return {
            "messages": [response],
            "resposta": raw_content,
            "status": STATUS_RESPONDED,
        }

    logger.info("Modelo retornou chamada de ferramenta ou conteúdo vazio.")
    return {
        "messages": [response],
        "status": STATUS_RESPONDED,
    }


def finalize_response(
    state: GraphState,
    *,
    llm: Any | None = None,
    app_config: AppConfig | None = None,
) -> Dict[str, Any]:
    """Ask the model to produce the final answer after tool execution."""

    cfg = app_config or default_config
    model = llm

    if model is None:
        try:
            model = cfg.create_llm()
        except ConfigurationError as exc:
            logger.error(
                "Configuração inválida ao instanciar LLM na etapa final",
                extra={"error": str(exc)},
            )
            return {"status": STATUS_ERROR, "resposta": str(exc)}

    conversation = _build_conversation(state)

    try:
        response = model.invoke(conversation)
    except Exception:  # pragma: no cover - proteção extra para etapa final
        logger.exception("Falha inesperada ao gerar resposta final")
        return {
            "status": STATUS_ERROR,
            "resposta": (
                "Não consegui concluir a resposta após executar a ferramenta. "
                "Tente novamente em instantes."
            ),
        }

    tool_calls = getattr(response, "tool_calls", None) or []
    if tool_calls:
        logger.warning(
            "Modelo solicitou nova ferramenta na etapa final",
            extra={"tool_calls": tool_calls},
        )
        return {
            "status": STATUS_ERROR,
            "resposta": (
                "Não consegui concluir a resposta após executar a ferramenta. "
                "Tente novamente."
            ),
        }

    content = _clean_content(response) or "Não consegui gerar uma resposta no momento."
    logger.info("Resposta final obtida do modelo.")

    return {
        "messages": [AIMessage(content=content)],
        "resposta": content,
        "status": STATUS_RESPONDED,
    }


def format_response(state: GraphState) -> Dict[str, Any]:
    """Format the final answer, recording execution duration."""

    base_response = state.get("resposta")
    if not base_response:
        messages = state.get("messages", [])
        base_response = _clean_content(messages[-1]) if messages else ""

    base_response = base_response or "Sem resposta disponível no momento."
    formatted = f"Resposta do agente: {base_response.strip()}"

    metadata = state.get("metadata", {})
    started_at = metadata.get("started_at")
    duration = None
    if started_at is not None:
        duration = max(time.perf_counter() - started_at, 0.0)

    status = state.get("status")
    if status == STATUS_ERROR:
        logger.warning("Fluxo concluído com erro controlado.")
        final_status = STATUS_ERROR
    else:
        logger.info("Fluxo concluído com sucesso.")
        final_status = STATUS_COMPLETED

    update: Dict[str, Any] = {
        "resposta": formatted,
        "status": final_status,
    }
    if duration is not None and math.isfinite(duration):
        update["duration_seconds"] = duration

    return update


__all__ = [
    "SYSTEM_PROMPT",
    "STATUS_COMPLETED",
    "STATUS_ERROR",
    "STATUS_RESPONDED",
    "STATUS_VALIDATED",
    "execute_tools",
    "finalize_response",
    "format_response",
    "invoke_model",
    "plan_tool_usage",
    "validate_input",
]
