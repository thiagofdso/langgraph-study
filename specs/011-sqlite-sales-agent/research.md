# Research: SQLite Sales Agent

## Decision 1: Idempotent SQLite setup via Python's `sqlite3`
- **Decision**: Use a dedicated `db_init.py` module that employs Python's built-in `sqlite3` library with parameterized queries to create tables and seed sample data. Schema creation will use `executescript` for readability, while data inserts will rely on `INSERT OR IGNORE` (or equivalent) to keep reruns idempotent.
- **Rationale**: Python's standard library ensures zero external dependencies and full control over transactions. Parameterized queries are explicitly recommended to avoid SQL injection, and `executescript` is appropriate for multi-statement schema initialization while keeping data seeding safe via individual `execute` calls.
- **Alternatives considered**:
  - Using an ORM such as SQLAlchemy for migrations was rejected as unnecessary complexity for a study project with a fixed schema.
  - Loading prebuilt `.sql` fixtures through shell commands was skipped to avoid platform-specific tooling.

Sources: citeturn1search0turn1search2

## Decision 2: Direct query node inside a minimal LangGraph StateGraph
- **Decision**: Build a compact `StateGraph` with two synchronous nodes: one to read aggregate metrics from SQLite and another to format a markdown report. The graph will operate without a toolchain that delegates SQL composition to the LLM; instead, deterministic Python functions will perform queries and pass structured results to the reporting node.
- **Rationale**: LangGraph's low-level node functions support direct data access, letting us keep the workflow deterministic and transparent—ideal for an offline study agent. Using the built-in SQL toolkit would give more flexibility but introduces risk of model-generated SQL and additional dependency setup that the specification does not require.
- **Alternatives considered**:
  - `SQLDatabaseToolkit` with a ReAct-style agent: rejected because it expects the LLM to compose SQL, increasing complexity and potential failure points for a beginner project.citeturn0search0turn0search7
  - Functional API with parallel tasks: unnecessary because the workflow is linear (initialize → query → report).

## Decision 3: Skip LangGraph checkpointing for now
- **Decision**: Run the graph without persistent checkpointing; rely on single-run execution since the agent's job is to produce one report per invocation.
- **Rationale**: The dataset is tiny and rebuilt on each run, so checkpoint persistence adds little value. Keeping the graph stateless avoids additional dependencies and configuration.
- **Alternatives considered**:
  - `langgraph-checkpoint-sqlite`: useful for resumable workflows, but adds setup overhead and a second SQLite file. We can document it as a future enhancement for longer-running agents.citeturn0search4

## Decision 4: Markdown report generation without extra libraries
- **Decision**: Format the "top products" and "top sellers" sections as markdown tables using small helper functions (string join) instead of external packages like `tabulate`.
- **Rationale**: Keeps the project dependency-light and reinforces manual control over the output format, which is important for a learning-focused repository.
- **Alternatives considered**:
  - Adding `tabulate` or `rich`: produces nicer tables but overcomplicates dependency management for the first iteration. Future iterations can revisit if presentation needs grow.
