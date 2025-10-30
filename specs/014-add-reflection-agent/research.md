# Phase 0 Research – Iterative Reflection Agent Guidance

## Decision 1: Use LangGraph `StateGraph` to orchestrate generate/reflect nodes

- **Rationale**: `StateGraph` lets us define explicit state (messages, iteration counter, logs) while still benefiting from LangGraph's checkpointing and edge routing. This matches the official documentation guidance for typed state workflows that need conditional edges and persistent memory.
- **Alternatives considered**:
  - `MessageGraph`: convenient for simple message pipelines, but it hides iteration counters and complicates storing structured run logs alongside messages.
  - Functional API (`@entrypoint`/`@task`): good for fan-out tasks, yet adds async overhead without simplifying this linear critique loop.

## Decision 2: Track drafts/reflections directly in graph state

- **Rationale**: Keeping `drafts` and `reflections` lists inside the graph state ensures every iteration emits structured data ready for reporting, avoiding post-processing of raw message transcripts.
- **Alternatives considered**:
  - Deriving logs from message history: fragile when prompts or output formats change and harder to unit-test.
  - External logging outside LangGraph: risks desync between control flow and recorded history.

## Decision 3: Prompt reflector with JSON schema enforcing actionable feedback

- **Rationale**: A strict JSON response (summary, strengths, gaps, action_items, reuse_previous) guarantees the generator receives concrete instructions and that we can detect no-op reflections (`reuse_previous = true`).
- **Alternatives considered**:
  - Free-form critique text: harder to parse for actionable steps.
  - External evaluation tools: unnecessary for baseline agent and would introduce configuration overhead.

## Decision 4: Enforce iteration cap using deterministic edge routing

- **Rationale**: Routing from `generate` either to `reflect` or `END` based on an iteration counter honors the fixed-loop requirement without adding user prompts or environment parameters.
- **Alternatives considered**:
  - CLI flag to change iteration count: violates the "sem novos parâmetros" requirement.
  - Human-in-the-loop continue prompt: introduces interactive loops the spec forbids.

## Decision 5: Keep Gemini 2.5 Flash as the sole LLM

- **Rationale**: Aligns with the Langgraph constitution (Principle IV) and existing agents, simplifying `.env` reuse and ensuring consistent output tone across generate and reflect steps.
- **Alternatives considered**:
  - Dedicated reflection model: adds provisioning complexity and diverges from project standards.
  - Switching models per iteration: increases latency and tuning effort without clear benefit for this scope.
