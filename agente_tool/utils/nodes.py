"""Node implementations for the agente_tool LangGraph workflow."""

from __future__ import annotations

import math
import time
from typing import Any, Dict, List, Optional

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)

from agente_tool.config import AppConfig, ConfigurationError, config as default_config
from agente_tool.state import GraphState, ToolPlan
from agente_tool.utils.logging import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """
# MISSÃO
Você é um assistente matemático e sua única função é resolver problemas numéricos utilizando a ferramenta `calculator`. Você se comunica exclusivamente em português.

---

# REGRAS CRÍTICAS
1.  **USO OBRIGATÓRIO DA FERRAMENTA**: Para QUALQUER operação matemática, desde as mais simples (ex: 2 + 2) até as mais complexas, você DEVE OBRIGATORIAMENTE chamar a ferramenta `calculator`. Esta regra é inquebrável, pois a ferramenta audita todos os cálculos. NÃO realize nenhum cálculo diretamente.
2.  **FORMATO DA EXPRESSÃO**: A ferramenta aceita um único argumento `expression`, que deve ser uma string contendo a operação matemática em notação infixa (ex: `(100 / 5) * 2`).
3.  **TRANSPARÊNCIA ZERO**: NUNCA mencione a ferramenta `calculator` ou o processo de cálculo em sua resposta ao usuário. Aja como se você tivesse calculado o resultado instantaneamente.
4.  **MANUSEIO DE ERROS**: Se a ferramenta `calculator` retornar um erro, NÃO invente um resultado. Informe ao usuário que a operação não pôde ser realizada e peça para que ele reformule a pergunta com dados claros e válidos.
5.  **FOCO EXCLUSIVO**: Se a pergunta do usuário não contiver um problema matemático calculável (ex: "Qual a história da matemática?"), informe educadamente que sua especialidade é resolver cálculos e que você não pode atender a essa solicitação.
6. **VALORES ABSOLUTOS**: Exiba os resultados absolutos, exemplo 1/2 =0,5

---

# FLUXO DE TRABALHO
1.  **Analisar**: O usuário faz uma pergunta.
2.  **Formular**: Se contiver um cálculo, traduza-o para uma expressão matemática em string.
3.  **Executar**: Chame a ferramenta `calculator` com a expressão.
4.  **Responder**: Após receber o resultado da ferramenta:
    -   Inicie com uma breve explicação do raciocínio ou dos passos do cálculo.
    -   Apresente o **resultado final** de forma clara.

---

# EXEMPLOS

**Exemplo 1: Cálculo Simples**
-   **Usuário**: "Quanto é 300 dividido por 4?"
-   **Sua Ação**: Chamar `calculator(expression='300 / 4')`
-   **Resposta Final (após receber '75')**: "Para calcular 300 dividido por 4, realizamos a divisão simples. O resultado é **75**."

**Exemplo 2: Cálculo Complexo**
-   **Usuário**: "Eu tinha R$ 1.500, paguei uma conta de R$ 350 e depois recebi 20% do valor que sobrou. Com quanto fiquei?"
-   **Sua Ação**: Chamar `calculator(expression='(1500 - 350) * 1.20')`
-   **Resposta Final (após receber '1380')**: "Primeiro, subtraímos a conta de R$ 350 do valor inicial de R$ 1.500, restando R$ 1.150. Em seguida, calculamos um acréscimo de 20% sobre esse valor. O montante final é **R$ 1.380,00**."

**Exemplo 3: Pergunta Não-Matemática**
-   **Usuário**: "Qual a sua cor favorita?"
-   **Sua Ação**: Não chamar a ferramenta.
-   **Resposta Final**: "Minha especialidade é resolver operações matemáticas. Não consigo responder a perguntas sobre preferências pessoais."
"""


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
        return {
            "selected_tool": None,
            "tool_plan": None,
            "pending_tool_calls": [],
        }
    last_message = ai_messages[-1]
    tool_calls = getattr(last_message, "tool_calls", None) or []
    if not tool_calls:
        logger.info("Modelo não solicitou ferramentas nesta rodada.")
        return {
            "selected_tool": None,
            "tool_plan": None,
            "pending_tool_calls": [],
        }

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
            "pending_tool_calls": [],
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

    pending_calls: List[Dict[str, Any]] = [
        {
            "name": tool_name,
            "args": call.get("args", {}),
            "call_id": call.get("id"),
        }
        for call in tool_calls
    ]

    logger.info(
        "Plano de ferramenta detectado",
        extra={"tool": tool_name, "tool_args": plan["args"]},
    )
    return {
        "selected_tool": tool_name,
        "tool_plan": plan,
        "pending_tool_calls": pending_calls,
    }


def handle_tool_result(state: GraphState) -> Dict[str, Any]:
    """Process the latest ToolNode output and update the agent state accordingly."""

    messages = state.get("messages") or []
    tool_messages = [msg for msg in messages if isinstance(msg, ToolMessage)]
    if not tool_messages:
        logger.error(
            "ToolNode executado, mas nenhuma mensagem de ferramenta foi encontrada."
        )
        return {
            "status": STATUS_ERROR,
            "resposta": (
                "Não consegui processar essa expressão matemática. "
                "Revise a operação e tente novamente."
            ),
        }

    last_tool_message = tool_messages[-1]
    content = _clean_content(last_tool_message)
    plan: Optional[ToolPlan] = state.get("tool_plan")
    tool_name = last_tool_message.name or (plan or {}).get("name") or _TOOL_NAME
    expression = (plan or {}).get("args", {}).get("expression")

    metadata = dict(state.get("metadata", {}))
    metadata["last_tool_result"] = content
    metadata["last_tool_expression"] = expression
    metadata["last_tool_name"] = tool_name
    metadata["last_tool_call_id"] = getattr(last_tool_message, "tool_call_id", None)

    run_record = {
        "name": tool_name,
        "args": (plan or {}).get("args", {}),
        "result": content,
        "call_id": getattr(last_tool_message, "tool_call_id", None),
    }

    update: Dict[str, Any] = {
        "metadata": metadata,
        "selected_tool": tool_name,
        "tool_plan": None,
        "pending_tool_calls": [],
        "tool_call": run_record,
        "last_tool_run": run_record,
    }

    if content.strip().lower().startswith("error"):
        logger.warning(
            "Ferramenta retornou erro controlado.",
            extra={"tool": tool_name, "result": content},
        )
        update["status"] = STATUS_ERROR
        update["resposta"] = (
            "Não consegui processar essa expressão matemática. "
            "Revise a operação e tente novamente."
        )
        update["tool_call"]["error"] = content
    else:
        logger.info(
            "Ferramenta executada com sucesso",
            extra={"tool": tool_name, "result": content},
        )
        update["status"] = STATUS_VALIDATED
        update["resposta"] = content

    return update


def _build_conversation(
    state: GraphState,
    *,
    include_system_prompt: bool = True,
) -> List[BaseMessage]:
    """Compose the conversation to send to the model."""

    conversation: List[BaseMessage] = []
    system_prompt = state.get("metadata", {}).get("system_prompt")
    if include_system_prompt and system_prompt:
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

    app_config or default_config
    if llm is None:
        logger.error("Modelo não fornecido ao invocar o LLM.")
        return {
            "status": STATUS_ERROR,
            "resposta": (
                "Modelo não configurado. Execute a inicialização do agente antes de enviar perguntas."
            ),
        }

    model = llm

    metadata = dict(state.get("metadata", {}))
    invoke_runs = metadata.get("invoke_model_runs", 0)
    conversation = _build_conversation(
        state,
        include_system_prompt=invoke_runs == 0,
    )
    if invoke_runs >= 1:
        conversation.append(HumanMessage(content="Continue gerando sua resposta."))
    metadata["invoke_model_runs"] = invoke_runs + 1

    try:
        response = model.invoke(conversation)
        print("Resposta do modelo:")
        print(response)
    except ConfigurationError as exc:
        logger.error(
            "Erro de configuração ao invocar modelo", extra={"error": str(exc)}
        )
        return {"status": STATUS_ERROR, "resposta": str(exc), "metadata": metadata}
    except Exception:  # pragma: no cover - trajetória de exceção logada
        logger.exception("Falha inesperada ao chamar o modelo")
        return {
            "status": STATUS_ERROR,
            "resposta": (
                "Encontrei um problema ao consultar o modelo agora. "
                "Tente novamente em alguns instantes."
            ),
            "metadata": metadata,
        }

    raw_content = _clean_content(response)

    update: Dict[str, Any] = {
        "messages": [response],
        "status": STATUS_RESPONDED,
        "metadata": metadata,
    }

    if raw_content:
        logger.info("Resposta obtida do modelo.")
        update["resposta"] = raw_content
        return update

    logger.info("Modelo retornou chamada de ferramenta ou conteúdo vazio.")
    return update


def finalize_response(
    state: GraphState,
    *,
    llm: Any | None = None,
    app_config: AppConfig | None = None,
) -> Dict[str, Any]:
    """Ask the model to produce the final answer after tool execution."""

    app_config or default_config
    if llm is None:
        logger.error("Modelo não fornecido para gerar resposta final.")
        return {
            "status": STATUS_ERROR,
            "resposta": (
                "Modelo não configurado. Tente novamente após inicializar o agente."
            ),
        }

    model = llm

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
    "handle_tool_result",
    "finalize_response",
    "format_response",
    "invoke_model",
    "plan_tool_usage",
    "validate_input",
]
