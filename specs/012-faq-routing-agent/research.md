# Research: FAQ Routing Agent

## Decision 1: Embed FAQ directly in prompt builder
- **Decision**: Store the fictitious FAQ as structured text within `agente_perguntas/prompt.py`, loading it into the system prompt during graph initialization.
- **Rationale**: Keeps the project self-contained, aligns with the requirement to insert the FAQ directly in the prompt, and avoids additional file I/O. The prompt builder can surface the FAQ as markdown for deterministic retrieval cues.
- **Alternatives considered**:
  - Loading the FAQ from an external JSON/YAML file: rejected to honor the instruction of embedding directly in the prompt.
  - Generating embeddings + vector retrieval: unnecessary complexity for a study project and violates the simplicity principle.

## Decision 2: Use LangGraph interrupts for human escalation
- **Decision**: Represent escalation as a branch in the graph where low-confidence answers trigger an `interrupt` payload that captures question + suggested routing data. This follows the LangGraph documentation guidance on human-in-the-loop patterns (see `external_docs/langgraph_docs.md`, “Human-in-the-loop with interrupt”).
- **Rationale**: Interrupt pauses execution and hands control to an external reviewer, matching the requirement to identify questions that need a human. The technique is lightweight and keeps the graph small.
- **Alternatives considered**:
  - Custom state flag without interrupt: simpler but loses the explicit HITL semantics and recommended workflow for human approvals.
  - Multi-agent Send/Command handoff from Perplexity examples: noted as an option for future scaling, but overkill here because the project only needs to flag escalation, not hand control to a separate agent.

## Decision 3: Confidence heuristic via keyword overlap
- **Decision**: Implement a basic similarity score (keyword overlap / normalized token match) to decide if an FAQ answer is confident enough. Threshold documented (e.g., 0.7 match ratio) determines whether to answer or escalate.
- **Rationale**: Keeps implementation deterministic and testable without external tooling, satisfies requirement for two resolvable questions and one escalated example.
- **Alternatives considered**:
  - Semantic similarity using embeddings: heavier dependency footprint and unnecessary for the study scope.
  - Manual mapping only exact matches: would fail paraphrased acceptance scenario from spec.

## Decision 4: Demonstrate human handoff pathway in documentation
- **Decision**: Document a manual procedure for simulating human insertion (e.g., capturing interrupt payload from console) instead of automated tests. Reference Perplexity findings that mention using `Send()` to a human agent and explain how it would extend the project.
- **Rationale**: Meets user request to describe how human insertion could be tested without building full multi-agent support. Aligns with no-unit-tests requirement.
- **Alternatives considered**:
  - Implementing an actual human agent stub: adds extra complexity and files, deviating from the “one prompt file + main” requirement.
