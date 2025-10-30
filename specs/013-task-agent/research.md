# Research Log – Terminal Task Session Agent

## Decision: Model orchestration with `StateGraph` + `InMemorySaver`
- **Rationale**: `external_docs/langgraph_docs.md` highlights `StateGraph` for deterministic node execution and checkpointing, and `agente_memoria/main.py` demonstrates the same pattern with `InMemorySaver` to preserve conversational state. Reusing this approach keeps memory management consistent and leverages proven repository code.
- **Alternatives considered**: LangGraph Functional API with `@entrypoint` was reviewed, but it introduces async futures complexity unnecessary for a linear three-step flow.

## Decision: Maintain task state inside TypedDict with annotated reducers
- **Rationale**: LangGraph docs recommend typed state schemas with reducers like `add_messages` for accumulating messages. Extending this by adding fields for `tasks`, `completed_index`, and `new_tasks` keeps conversation history and task data together and benefits from automatic state merging.
- **Alternatives considered**: Managing tasks outside LangGraph (pure Python variables) would bypass memory checkpoints and contradict the requirement to “use memória conforme exemplo”.

## Decision: Drive exactly three interactions via controlled invocations
- **Rationale**: The specification and user input forbid interaction loops. Running `app.invoke` separately for each round mirrors `agente_memoria` usage while allowing us to capture user prompts/agent replies explicitly in the terminal.
- **Alternatives considered**: Using `.stream()` with conditional edges could enforce flow internally, but it risks additional iterations if the LLM emits tool calls and complicates adherence to the three-round limit.

## Decision: Keep prompts in Portuguese with explicit echoing of user/agent turns
- **Rationale**: Requirements demand Portuguese interaction and visible input/output. Structuring prompts with clear context (task list summary, completion status, additions) ensures the LLM has all necessary information per round while keeping terminal output aligned with study goals.
- **Alternatives considered**: English prompts or hidden context might simplify development but would violate user instructions and reduce transparency for learners.
