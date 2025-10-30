# Data Model – Iterative Reflection Agent Guidance

## Entities

### RunConfiguration
- **Description**: Parameters governing a single execution of the reflection agent.
- **Fields**:
  - `iteration_limit` (int, default 3): Number of generate→reflect cycles to execute.
  - `question` (str, constant): Fixed prompt “O que é importante para um programador aprender”.
  - `timestamp_started` (datetime, optional): Recorded when execution begins for logging.
  - `timestamp_completed` (datetime, optional): Recorded when execution ends.
- **Validation Rules**:
  - `iteration_limit` MUST be ≥ 1.
  - `question` MUST match the fixed question; deviations should abort execution.

### DraftResponse
- **Description**: Captures each version of the answer produced by the generator node.
- **Fields**:
  - `iteration_index` (int): 0 for initial draft, increments after each reflection cycle.
  - `content` (str): Full text of the draft response.
  - `improvements_applied` (list[str]): Summary of revisions made after reflection.
  - `source_reflection_id` (str, optional): Identifier of the reflection that informed this draft.
- **Validation Rules**:
  - `iteration_index` MUST be sequential with no gaps.
  - `content` MUST contain at least four distinct learning priorities in the final draft.

### ReflectionNote
- **Description**: Structured critique emitted by the reflector node.
- **Fields**:
  - `reflection_id` (str): Unique identifier per reflection cycle.
  - `iteration_index` (int): Index of the draft being critiqued.
  - `strengths` (list[str]): Positive observations.
  - `gaps` (list[str]): Missing or weak points.
  - `action_items` (list[str]): Specific improvements the generator must address.
  - `reuse_flag` (bool): True when no new improvements are suggested.
- **Validation Rules**:
  - `iteration_index` MUST match the draft under review.
  - `action_items` MUST be non-empty unless `reuse_flag` is True.

### RunLog
- **Description**: Aggregated output summarizing each draft and reflection for reviewers.
- **Fields**:
  - `drafts` (list[DraftResponse]): Ordered history of drafts including the final answer.
  - `reflections` (list[ReflectionNote]): Ordered list of critiques.
  - `final_answer` (DraftResponse): Reference to the concluding draft.
- **Validation Rules**:
  - Length of `drafts` MUST equal `iteration_limit`.
  - Length of `reflections` MUST equal `iteration_limit` - 1 (no reflection before first draft).
