import os
import sys
import uuid
from typing import Annotated, List, Literal, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages

load_dotenv(dotenv_path="agente_tarefas/.env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Erro: defina GEMINI_API_KEY no arquivo agente_tarefas/.env antes de executar o agente.")
    sys.exit(1)

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    api_key=GEMINI_API_KEY,
)


class TaskItem(TypedDict):
    id: int
    description: str
    status: Literal["pending", "completed"]
    source_round: Literal["round1", "round3"]


class TimelineEntry(TypedDict, total=False):
    round_id: Literal["round1", "round2", "round3"]
    user_input: str
    agent_response: str
    notes: str


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    tasks: List[TaskItem]
    completed_ids: List[int]
    timeline: List[TimelineEntry]


workflow = StateGraph(AgentState)


def agent_node(state: AgentState):
    """Single LangGraph node: forwards accumulated mensagens to Gemini."""
    response = model.invoke(state["messages"])
    return {"messages": [response]}


workflow.add_node("agent", agent_node)
workflow.set_entry_point("agent")
workflow.add_edge("agent", END)

# Checkpointer baseado em memória mantém histórico entre as três rodadas.
memory = InMemorySaver()
app = workflow.compile(checkpointer=memory)


SYSTEM_PROMPT = (
    "Você é um assistente que atua em português brasileiro ajudando o usuário a gerenciar"
    " tarefas em uma sessão de três rodadas. Sempre responda de forma clara, curta e"
    " numerada quando solicitado, liste totais no encerramento e nunca faça mais perguntas"
    " após a terceira rodada. Use um tom encorajador e objetivo."
)


def invoke_agent(new_messages: List[BaseMessage], state: AgentState, thread_id: str) -> AgentState:
    """Helper centralizando o invoke para manter memória por thread."""
    config = {"configurable": {"thread_id": thread_id}}
    payload: AgentState = {
        "messages": new_messages,
        "tasks": state["tasks"],
        "completed_ids": state["completed_ids"],
        "timeline": state["timeline"],
    }
    return app.invoke(payload, config=config)


def split_tasks(raw: str) -> List[str]:
    fragments = [segment.strip() for segment in raw.replace("\n", ",").split(",")]
    return [fragment for fragment in fragments if fragment]


def build_initial_tasks(raw_items: List[str]) -> List[TaskItem]:
    return [
        {
            "id": index + 1,
            "description": item,
            "status": "pending",
            "source_round": "round1",
        }
        for index, item in enumerate(raw_items)
    ]


def build_round1_prompt(tasks: List[TaskItem]) -> str:
    task_lines = "\n".join(f"{task['id']}. {task['description']}" for task in tasks)
    return (
        "Rodada 1: Confirmar tarefas recebidas.\n"
        "Liste cada tarefa numerada e incentive o usuário a continuar para a segunda rodada.\n"
        "Tarefas informadas:\n"
        f"{task_lines}"
    )


def build_round2_prompt(tasks: List[TaskItem], completed_id: int) -> str:
    lines = []
    for task in tasks:
        status = "concluída" if task["status"] == "completed" else "pendente"
        marker = "✅" if task["status"] == "completed" else "🕒"
        lines.append(f"{task['id']}. {task['description']} ({status}) {marker}")
    rendered = "\n".join(lines)
    return (
        "Rodada 2: Confirmar a tarefa marcada como concluída e orientar o usuário para a última rodada.\n"
        f"Tarefa concluída: {completed_id}.\n"
        "Situação atual das tarefas:\n"
        f"{rendered}"
    )


def build_round3_prompt(tasks: List[TaskItem], duplicate_notes: List[str]) -> str:
    completed = [task for task in tasks if task["status"] == "completed"]
    pending = [task for task in tasks if task["status"] == "pending"]
    completed_lines = "\n".join(f"- {task['description']}" for task in completed) or "- (nenhuma)"
    pending_lines = "\n".join(f"- {task['description']}" for task in pending) or "- (nenhuma)"
    notes_section = "\n".join(f"- {note}" for note in duplicate_notes) or "- Nenhum aviso sobre duplicatas"
    return (
        "Rodada 3: Encerrar a sessão.\n"
        "Produza um resumo final destacando tarefas concluídas, tarefas pendentes e totais.\n"
        "Inclua orientações breves para reiniciar a sessão e registre decisões sobre duplicatas.\n"
        f"Tarefas concluídas:\n{completed_lines}\n"
        f"Tarefas pendentes:\n{pending_lines}\n"
        "Observações sobre duplicatas:\n"
        f"{notes_section}"
    )


def request_confirmation(message: str) -> bool:
    answer = input(message).strip().lower()
    print(f"Usuário: {answer}")
    return answer in {"s", "sim"}


def round_one(tasks_state: List[TaskItem]) -> str:
    while True:
        user_entry = input(
            "Rodada 1 – informe tarefas separadas por vírgula (ex.: Estudar, Lavar louça): "
        ).strip()
        print(f"Usuário: {user_entry}")
        parsed = split_tasks(user_entry)
        if not parsed:
            print("Agente: Preciso de pelo menos uma tarefa. Digite novamente por favor.")
            continue
        new_tasks = build_initial_tasks(parsed)
        tasks_state.clear()
        tasks_state.extend(new_tasks)
        return user_entry


def round_two(tasks_state: List[TaskItem], completed_ids: List[int]) -> int:
    while True:
        selection_raw = input(
            "Rodada 2 – informe o número da tarefa concluída: "
        ).strip()
        print(f"Usuário: {selection_raw}")
        if not selection_raw:
            print("Agente: Informe um número válido para continuar.")
            continue
        if not selection_raw.isdigit():
            print("Agente: Utilize apenas números correspondentes à lista apresentada.")
            continue
        selection = int(selection_raw)
        if selection < 1 or selection > len(tasks_state):
            print("Agente: Esse número não está na lista. Tente novamente.")
            continue
        if selection in completed_ids:
            print("Agente: Essa tarefa já foi concluída anteriormente. Escolha outra.")
            continue
        for task in tasks_state:
            if task["id"] == selection:
                task["status"] = "completed"
                break
        completed_ids.append(selection)
        return selection


def round_three(
    tasks_state: List[TaskItem],
    duplicate_notes: List[str],
) -> tuple[str, List[str]]:
    while True:
        user_entry = input(
            "Rodada 3 – adicione novas tarefas separadas por vírgula (ou Enter para finalizar): "
        ).strip()
        print(f"Usuário: {user_entry}")
        if not user_entry:
            if request_confirmation("Confirmar finalização sem novas tarefas? (s/n): "):
                return "Nenhuma tarefa adicionada", duplicate_notes
            print("Agente: Sem problemas, você pode informar novas tarefas agora.")
            continue
        parsed = split_tasks(user_entry)
        if not parsed:
            print("Agente: As entradas estavam vazias após limpeza. Tente novamente.")
            continue
        existing_descriptions = {task["description"].casefold() for task in tasks_state}
        next_id = len(tasks_state) + 1
        added_descriptions: List[str] = []
        for item in parsed:
            lowered = item.casefold()
            if lowered in existing_descriptions:
                keep = request_confirmation(
                    f"A tarefa '{item}' já existe. Deseja mantê-la duplicada? (s/n): "
                )
                decision = "mantida" if keep else "ignorada"
                duplicate_notes.append(f"Duplicata '{item}' foi {decision} pelo usuário")
                if not keep:
                    print("Agente: Duplicata ignorada. Informe outras se desejar.")
                    continue
            tasks_state.append(
                {
                    "id": next_id,
                    "description": item,
                    "status": "pending",
                    "source_round": "round3",
                }
            )
            existing_descriptions.add(lowered)
            added_descriptions.append(item)
            next_id += 1
        if not added_descriptions:
            print("Agente: Nenhuma nova tarefa foi adicionada. Você pode tentar novamente ou finalizar.")
            continue
        return ", ".join(added_descriptions), duplicate_notes


def main() -> None:
    thread_id = f"agente-tarefas-{uuid.uuid4()}"
    tasks_state: List[TaskItem] = []
    completed_ids: List[int] = []
    timeline: List[TimelineEntry] = []
    duplicate_notes: List[str] = []

    # Rodada 1
    user_text_round1 = round_one(tasks_state)
    initial_state: AgentState = {
        "messages": [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=build_round1_prompt(tasks_state)),
        ],
        "tasks": tasks_state,
        "completed_ids": completed_ids,
        "timeline": timeline,
    }
    result_round1 = invoke_agent(initial_state["messages"], initial_state, thread_id)
    agent_reply_round1 = result_round1["messages"][-1].content
    print(f"Agente: {agent_reply_round1}")
    timeline.append(
        {
            "round_id": "round1",
            "user_input": user_text_round1,
            "agent_response": agent_reply_round1,
        }
    )

    # Rodada 2
    selected_task = round_two(tasks_state, completed_ids)
    state_round2: AgentState = {
        "messages": [HumanMessage(content=build_round2_prompt(tasks_state, selected_task))],
        "tasks": tasks_state,
        "completed_ids": completed_ids,
        "timeline": timeline,
    }
    result_round2 = invoke_agent(state_round2["messages"], state_round2, thread_id)
    agent_reply_round2 = result_round2["messages"][-1].content
    print(f"Agente: {agent_reply_round2}")
    timeline.append(
        {
            "round_id": "round2",
            "user_input": str(selected_task),
            "agent_response": agent_reply_round2,
        }
    )

    # Rodada 3
    round3_summary, duplicate_notes = round_three(tasks_state, duplicate_notes)
    state_round3: AgentState = {
        "messages": [HumanMessage(content=build_round3_prompt(tasks_state, duplicate_notes))],
        "tasks": tasks_state,
        "completed_ids": completed_ids,
        "timeline": timeline,
    }
    result_round3 = invoke_agent(state_round3["messages"], state_round3, thread_id)
    agent_reply_round3 = result_round3["messages"][-1].content
    print(f"Agente: {agent_reply_round3}")
    timeline.append(
        {
            "round_id": "round3",
            "user_input": round3_summary,
            "agent_response": agent_reply_round3,
            "notes": "; ".join(duplicate_notes) if duplicate_notes else "",
        }
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAgente: Sessão interrompida pelo usuário.")
