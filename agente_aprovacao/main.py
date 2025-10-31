"""Entry point for the approval-gated LangGraph workflow."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from textwrap import dedent
from typing import Any, Callable, Dict, Iterable, List, Literal, Optional, Tuple, TypedDict

from dotenv import load_dotenv
from langchain.tools import Tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

VALIDATION_ATTEMPT_LIMIT = 3
THREAD_ID = "agente-aprovacao"


class ValidatedSubmission(TypedDict, total=False):
    """Normalized user submission after validation."""

    prompt: str
    metadata: Dict[str, str]


class ApprovalOutcome(TypedDict, total=False):
    """Record of the human approval decision."""

    approved: bool
    reason: str
    timestamp: str


class SearchHit(TypedDict, total=False):
    """Structure for Tavily search results."""

    title: str
    url: str
    snippet: str


class ApprovalSessionState(TypedDict, total=False):
    """LangGraph state passed between nodes."""

    question: str
    validated_input: Optional[ValidatedSubmission]
    validation_errors: List[str]
    validation_attempts: int
    approval_required: bool
    approval_decision: Optional[ApprovalOutcome]
    search_results: List[SearchHit]
    response_text: str
    response_stage: Literal["initial", "final"]
    notes: List[str]


@dataclass(slots=True)
class WorkflowResources:
    """Resources shared across graph nodes."""

    model: ChatGoogleGenerativeAI
    search_tool: Tool
    run_search: Callable[[str], List[SearchHit]]


def validate_question(question: str) -> Tuple[Optional[ValidatedSubmission], List[str]]:
    """Return normalized submission and validation errors, if any."""

    errors: List[str] = []
    normalized = question.strip()

    if not normalized:
        errors.append("A pergunta não pode ser vazia.")

    if errors:
        return None, errors

    submission: ValidatedSubmission = {
        "prompt": normalized,
        "metadata": {"channel": "cli", "language": "pt-BR"},
    }
    return submission, []


def try_evaluate_math(expression: str) -> Optional[str]:
    """Attempt to evaluate simple arithmetic expressions safely."""

    import ast
    import operator

    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod,
    }

    class SafeEvaluator(ast.NodeVisitor):
        def visit(self, node):  # type: ignore[override]
            if isinstance(node, ast.Expression):
                return self.visit(node.body)
            if isinstance(node, ast.BinOp):
                if type(node.op) not in allowed_operators:
                    raise ValueError("Operador não permitido.")
                left = self.visit(node.left)
                right = self.visit(node.right)
                return allowed_operators[type(node.op)](left, right)
            if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
                operand = self.visit(node.operand)
                return +operand if isinstance(node.op, ast.UAdd) else -operand
            if isinstance(node, ast.Num):  # type: ignore[deprecated-ast]
                return node.n
            raise ValueError("Expressão contém elementos não suportados.")

    sanitized = expression.replace(",", ".")
    try:
        tree = ast.parse(sanitized, mode="eval")
        result = SafeEvaluator().visit(tree)
    except Exception:
        return None

    if isinstance(result, float) and result.is_integer():
        result = int(result)
    return f"O resultado é {result}."


def compose_final_response(state: ApprovalSessionState, resources: WorkflowResources) -> str:
    """Use Gemini to produce the final message for the requester."""

    prompt = state.get("validated_input", {}).get("prompt") or state.get("question", "")
    notes = state.get("notes", [])
    approval = state.get("approval_decision")
    search_results = state.get("search_results", [])

    context_lines: List[str] = [
        f"Pergunta do usuário: {prompt}",
        f"Aprovação humana: {'aprovada' if approval and approval.get('approved') else 'negada ou não executada'}",
    ]

    if approval and approval.get("reason"):
        context_lines.append(f"Justificativa da decisão humana: {approval['reason']}")

    if notes:
        context_lines.append("Observações do agente:")
        context_lines.extend(f"- {item}" for item in notes)

    if search_results:
        context_lines.append("Resultados da pesquisa aprovados:")
        for index, hit in enumerate(search_results, start=1):
            title = hit.get("title", "Sem título")
            url = hit.get("url", "Sem URL")
            snippet = hit.get("snippet", "Sem resumo disponível.")
            context_lines.append(
                dedent(
                    f"""
                    Fonte {index}:
                    Título: {title}
                    URL: {url}
                    Resumo: {snippet}
                    """
                ).strip()
            )
    else:
        context_lines.append(
            "Nenhum resultado externo foi utilizado; a resposta deve ser baseada apenas no conhecimento interno."
        )

    system_prompt = (
        "Você é um agente que deve responder em português, explicar se a pesquisa externa foi utilizada e"
        " indicar próximos passos quando necessário."
    )

    message = "\n\n".join(context_lines)
    try:
        response = resources.model.invoke(
            [SystemMessage(content=system_prompt), HumanMessage(content=message)]
        )
        if isinstance(response.content, str):
            return response.content.strip()
        return "".join(segment for segment in response.content if isinstance(segment, str)).strip()
    except Exception as exc:  # pragma: no cover - dependências externas
        fallback = [
            "Não foi possível gerar uma resposta automática devido a um erro no modelo.",
            f"Detalhes: {exc}",
            "Resumo manual do contexto:",
            message,
        ]
        return "\n".join(fallback)


def build_graph(resources: WorkflowResources) -> StateGraph[ApprovalSessionState]:
    """Configure the LangGraph workflow with validation, approval, and search nodes."""

    def gerar_resposta(state: ApprovalSessionState) -> ApprovalSessionState:
        state.setdefault("validation_errors", [])
        state.setdefault("validation_attempts", 0)
        state.setdefault("notes", [])
        state.setdefault("response_text", "")

        if state.get("response_stage", "initial") == "final":
            if not state["response_text"]:
                state["response_text"] = compose_final_response(state, resources)
            return state

        submission, errors = validate_question(state.get("question", ""))
        if errors:
            state["validation_attempts"] += 1
            state["validation_errors"] = errors
            if state["validation_attempts"] >= VALIDATION_ATTEMPT_LIMIT:
                note = (
                    "Limite de tentativas de validação excedido. Resposta final gerada sem consultar ferramentas."
                )
                if note not in state["notes"]:
                    state["notes"].append(note)
                state["response_stage"] = "final"
                state["approval_required"] = False
                return state

            correction = interrupt(
                {
                    "type": "validation",
                    "errors": errors,
                    "attempt": state["validation_attempts"],
                    "max_attempts": VALIDATION_ATTEMPT_LIMIT,
                    "previous_question": state.get("question", ""),
                }
            )
            state["validation_errors"] = []
            new_question = correction.get("question")
            if isinstance(new_question, str) and new_question.strip():
                state["question"] = new_question.strip()
            new_metadata = correction.get("metadata")
            if isinstance(new_metadata, dict):
                state.setdefault("validated_input", {})  # type: ignore[assignment]
                state["validated_input"] = {
                    "prompt": state.get("question", ""),
                    "metadata": {str(k): str(v) for k, v in new_metadata.items()},
                }
            else:
                state["validated_input"] = None
            return state

        state["validated_input"] = submission
        state["validation_errors"] = []
        state["response_stage"] = "initial"
        math_answer = try_evaluate_math(submission["prompt"])
        if math_answer is not None:
            state["response_text"] = math_answer
            note = "Resposta fornecida internamente sem uso de ferramentas externas."
            if note not in state["notes"]:
                state["notes"].append(note)
            state["approval_required"] = False
            state["response_stage"] = "final"
            return state

        state["approval_required"] = True
        planning_note = "Ferramenta de pesquisa solicitada para complementar a resposta."
        if planning_note not in state["notes"]:
            state["notes"].append(planning_note)
        return state

    def aprovacao_humana(state: ApprovalSessionState) -> ApprovalSessionState:
        question = state.get("validated_input", {}).get("prompt") or state.get("question", "")
        approval_payload = interrupt(
            {
                "type": "approval",
                "question": question,
                "action": "Executar pesquisa na internet com Tavily",
                "notes": state.get("notes", []),
            }
        )

        approved = bool(approval_payload.get("approved"))
        reason = approval_payload.get("reason") or ""
        state["approval_decision"] = {
            "approved": approved,
            "reason": reason,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        }
        state["approval_required"] = False

        if not approved:
            note = reason or "Pesquisa externa não autorizada pelo aprovador."
            if note not in state["notes"]:
                state["notes"].append(note)
            state["search_results"] = []
            state["response_stage"] = "final"
        return state

    def busca_internet(state: ApprovalSessionState) -> ApprovalSessionState:
        prompt = state.get("validated_input", {}).get("prompt") or state.get("question", "")
        results: List[SearchHit] = []
        try:
            results = resources.run_search(prompt)
            if not results:
                state["notes"].append("Pesquisa aprovada, porém nenhum resultado relevante foi retornado.")
        except Exception as exc:  # pragma: no cover - dependências externas
            state["notes"].append(f"Erro ao consultar Tavily: {exc}")

        state["search_results"] = results
        state["response_stage"] = "final"
        return state

    def avancar_de_gerar(state: ApprovalSessionState) -> str:
        if state.get("response_stage") == "final":
            return "final"
        return "aprovar"

    def rota_pos_aprovacao(state: ApprovalSessionState) -> str:
        decision = state.get("approval_decision")
        if decision and decision.get("approved"):
            return "buscar"
        return "final"

    graph = StateGraph(ApprovalSessionState)
    graph.add_node("gerar_resposta", gerar_resposta)
    graph.add_node("aprovacao_humana", aprovacao_humana)
    graph.add_node("busca_internet", busca_internet)

    graph.add_edge(START, "gerar_resposta")
    graph.add_conditional_edges(
        "gerar_resposta",
        avancar_de_gerar,
        {"aprovar": "aprovacao_humana", "final": END},
    )
    graph.add_conditional_edges(
        "aprovacao_humana",
        rota_pos_aprovacao,
        {"buscar": "busca_internet", "final": "gerar_resposta"},
    )
    graph.add_edge("busca_internet", "gerar_resposta")

    return graph.compile(checkpointer=InMemorySaver())


def ensure_credentials() -> None:
    """Ensure required API keys are present."""

    missing = [name for name in ("GEMINI_API_KEY", "TAVILY_API_KEY") if not os.getenv(name)]
    if missing:
        joined = ", ".join(missing)
        print(f"[Erro] Defina as variáveis de ambiente: {joined} em agente_aprovacao/.env", file=sys.stderr)
        sys.exit(1)


def instantiate_resources() -> WorkflowResources:
    """Create shared LangChain resources."""

    gemini_key = os.environ["GEMINI_API_KEY"].strip()
    tavily_key = os.environ["TAVILY_API_KEY"].strip()
    os.environ.setdefault("GOOGLE_API_KEY", gemini_key)
    os.environ.setdefault("TAVILY_API_KEY", tavily_key)

    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=gemini_key)
    search_client = TavilySearch(max_results=5, topic="general")

    def run_search(query: str) -> List[SearchHit]:
        payload = search_client.invoke({"query": query})
        hits: List[SearchHit] = []
        for item in payload.get("results", []):
            hits.append(
                {
                    "title": item.get("title", "Sem título"),
                    "url": item.get("url", ""),
                    "snippet": item.get("content") or item.get("text") or "",
                }
            )
        return hits

    search_tool = Tool.from_function(
        func=run_search,
        name="web_search",
        description="Buscar fontes públicas relevantes utilizando Tavily.",
        return_direct=True,
    )

    return WorkflowResources(model=model, search_tool=search_tool, run_search=run_search)


def handle_validation_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Collect corrected input from the console after validation failure."""

    errors = payload.get("errors", [])
    attempt = payload.get("attempt", 0)
    max_attempts = payload.get("max_attempts", VALIDATION_ATTEMPT_LIMIT)

    print("-" * 72)
    print("Entrada inválida detectada:")
    for item in errors:
        print(f"- {item}")
    print(f"Tentativa {attempt} de {max_attempts}.")
    corrected = input("Forneça uma nova pergunta (ou pressione Enter para repetir a anterior): ").strip()
    if not corrected:
        corrected = payload.get("previous_question", "")
    return {"question": corrected}


def handle_approval_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Request human approval to continue with the external search tool."""

    question = payload.get("question", "")
    action = payload.get("action", "Executar a ferramenta solicitada.")
    notes = payload.get("notes") or []

    print("-" * 72)
    print("Solicitação de aprovação humana")
    print(f"Ação proposta: {action}")
    if question:
        print(f"Pergunta do usuário: {question}")
    if notes:
        print("Notas atuais do fluxo:")
        for item in notes:
            print(f"- {item}")

    while True:
        decision = input("Autorizar execução da ferramenta? (s/n): ").strip().lower()
        if decision in {"s", "n", "sim", "nao", "não"}:
            break
        print("Resposta inválida. Digite 's' para sim ou 'n' para não.")

    approved = decision in {"s", "sim"}
    reason = "Aprovado pelo aprovador." if approved else "Uso da ferramenta negado pelo aprovador."
    return {"approved": approved, "reason": reason}


def drive_workflow(graph, initial_state: ApprovalSessionState) -> ApprovalSessionState:
    """Execute the workflow, handling interrupts for validation and approvals."""

    config = {"configurable": {"thread_id": THREAD_ID}}
    next_input: Any = initial_state
    use_command = False

    while True:
        stream: Iterable[Dict[str, Any]]
        if use_command:
            stream = graph.stream(Command(resume=next_input), config=config)
        else:
            stream = graph.stream(next_input, config=config)
            use_command = True  # subsequent iterations use Command

        interrupted = False
        for event in stream:
            interrupt_events = event.get("__interrupt__")
            if interrupt_events:
                payload = interrupt_events[0].value
                payload_type = payload.get("type")
                if payload_type == "validation":
                    next_input = handle_validation_payload(payload)
                elif payload_type == "approval":
                    next_input = handle_approval_payload(payload)
                else:
                    raise ValueError(f"Tipo de interrupção desconhecido: {payload_type}")
                interrupted = True
                break

        if interrupted:
            continue

        final_state = graph.get_state(config).values  # type: ignore[assignment]
        return final_state


def format_search_results(results: List[SearchHit]) -> str:
    """Create a readable list of search references."""

    if not results:
        return "(Nenhum resultado externo foi utilizado.)"

    lines = []
    for index, hit in enumerate(results, start=1):
        title = hit.get("title", "Sem título")
        url = hit.get("url", "")
        lines.append(f"{index}. {title} -> {url}")
    return "\n".join(lines)


def main() -> None:
    """Run the approval workflow CLI."""

    load_dotenv(dotenv_path="agente_aprovacao/.env")
    ensure_credentials()
    resources = instantiate_resources()
    graph = build_graph(resources)

    question = input("Digite a solicitação do usuário: ").strip()
    if not question:
        print("Nenhuma pergunta fornecida. Encerrando.")
        sys.exit(0)

    initial_state: ApprovalSessionState = {
        "question": question,
        "validated_input": None,
        "validation_errors": [],
        "validation_attempts": 0,
        "approval_required": False,
        "approval_decision": None,
        "search_results": [],
        "response_text": "",
        "response_stage": "initial",
        "notes": [],
    }

    final_state = drive_workflow(graph, initial_state)

    print("\n=== Resumo da Execução ===")
    print(f"Resposta final:\n{final_state.get('response_text', '(sem resposta)')}")
    decision = final_state.get("approval_decision")
    if decision:
        print(
            f"\nDecisão humana: {'aprovada' if decision.get('approved') else 'negada'} "
            f"({decision.get('reason', 'Sem justificativa')})"
        )
    print("\nNotas registradas:")
    for note in final_state.get("notes", []) or ["(nenhuma)"]:
        print(f"- {note}")
    print("\nResultados pesquisados:")
    print(format_search_results(final_state.get("search_results", [])))


if __name__ == "__main__":
    main()
