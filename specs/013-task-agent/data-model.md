# Data Model – Terminal Task Session Agent

## Entities

### Task Item
- **Description**: Single activity captured during the session and persisted in memory for subsequent rounds. Mirrors the learner’s wording.
- **Fields**:
  - `id` (int) – 1-based position shown to the learner; must remain stable across rounds.
  - `description` (str) – original text supplied by the learner; trimmed; minimum 1 non-whitespace character.
  - `status` (enum: `pending`, `completed`) – defaults to `pending`; transitions to `completed` exactly once.
  - `source_round` (enum: `round1`, `round3`) – indicates when the task entered the list for auditability.
- **Validation Rules**:
  - Reject duplicates in round 3 unless learner explicitly confirms inclusion (tracked separately via User Command result).
  - Prevent marking an already `completed` task again; surface warning instead.
- **State Transitions**:
  - `pending` → `completed` when round-2 selection matches `id`.
  - `completed` → (no further transitions).

### Session Timeline
- **Description**: Ordered log of interactions across the three rounds, supplying context to the LLM and final summary.
- **Fields**:
  - `round_id` (enum: `round1`, `round2`, `round3`)
  - `user_input` (str) – exact text typed by the learner (echoed in terminal).
  - `agent_response` (str) – formatted Portuguese reply rendered in terminal.
  - `timestamp` (datetime | optional) – local time of interaction; may be omitted if not required for demo.
- **Validation Rules**:
  - Preserve chronological order; do not append entries after session closes.
  - Ensure each round has exactly one entry.
- **Relationships**:
  - Linked to Task Items for context (IDs referenced in responses).

### User Command
- **Description**: Parsed interpretation of learner input per round, including validation state.
- **Fields**:
  - `round_id` (enum: `round1`, `round2`, `round3`)
  - `raw_text` (str) – verbatim terminal entry.
  - `parsed_action` (enum: `create_tasks`, `complete_task`, `add_tasks`, `confirm_duplicate`, `skip_duplicate`)
  - `valid` (bool) – indicates whether input satisfied round requirements.
  - `notes` (str | optional) – explanation shown when invalid or when duplicates encountered.
- **Validation Rules**:
  - Round 1 requires at least one parsed task; otherwise `valid=False` with retry prompt.
  - Round 2 requires integer within existing task range; invalid entries flagged with guidance.
  - Round 3 allows zero tasks only after explicit confirmation.
- **State Transitions**:
  - `valid=False` → `valid=True` after learner retries with acceptable input.

## Relationships & Derived Data

- Session Timeline entries reference Task Item IDs to narrate progress; final summary aggregates counts of `pending` vs `completed`.
- User Command outcomes drive Task Item updates and summary phrasing; duplicate-handling decisions recorded to explain final list composition.
- All entities live inside LangGraph state to benefit from memory checkpoints between invocations.
