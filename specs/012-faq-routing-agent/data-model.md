# Data Model: FAQ Routing Agent

## Entities

### Interaction Record
- **Attributes**: `user_question` (str), `matched_faq` (optional[str]), `confidence` (float 0-1), `status` (enum: `resolved` | `human`), `notes` (str)
- **Usage**: Stored in memory for the session to build the final summary.

### Escalation Summary
- **Attributes**: `pending_questions` (list[str]), `timestamp`/`order` (int), `reason` (str)
- **Usage**: Populated when an interaction is routed to human support; displayed in console summary.

## Relationships
- Escalation Summary aggregates Interaction Records where status == `human`.

## Validation Rules
- Similarity threshold (default 0.7) determines status.
- FAQ permanece como texto estático no prompt; quaisquer ajustes exigem atualização manual do arquivo `prompt.py`.
- At least three demo interactions must exist: two resolved, one escalated.
