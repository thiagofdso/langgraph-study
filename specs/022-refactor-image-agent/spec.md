# Feature Specification: Refactor agente_imagem Structure

**Feature Branch**: `022-refactor-image-agent`  
**Created**: 2025-11-05  
**Status**: Draft  
**Input**: User description: "O proximo spec number é o 022, quero que seja refatorado o projeto agente_imagem seguindo boas praticas de langgraph, o objetivo é organizar o projeto em arquivos espeficicos semelhante ao agente_simples, não deve ser alterada funcionalidade, o objetivo é apenas estrutura o projeto usando boas praticas sem mudar a funcionalidade. Deve manter tambem o teste. Deve ter um def create_app() conforme o agente_simples para funcionar no langgraph cli."

**Note**: This specification is an integral part of the specification-driven development process, generated and managed using the `.specify` framework, ensuring clear requirements and alignment with project goals.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Standardized Project Layout (Priority: P1)

As a maintainer, I need `agente_imagem` organized in the same modular structure used by `agente_simples` so that the codebase is discoverable, reviewable, and easier to extend.

**Why this priority**: Without a standardized layout, onboarding new contributors is slow and mistakes creep in because shared tooling assumes common folders and entry points.

**Independent Test**: Walk through the repository tree and README to confirm that each responsibility (configuration, state, workflow, CLI entry point, utilities, tests, docs) has a dedicated module that mirrors the reference agent, then run the baseline sample flow to verify nothing broke.

**Acceptance Scenarios**:

1. **Given** the reorganized repository, **When** a maintainer inspects the documentation, **Then** they can locate distinct modules for configuration, workflow graph, state handling, CLI entry point, utilities, and tests that match the naming and responsibilities described for other LangGraph agents.
2. **Given** the preserved workflow behavior, **When** the sample image-to-markdown flow is run after restructuring, **Then** the markdown output matches the pre-refactor baseline for the same inputs.

---

### User Story 2 - CLI Friendly Entry Point (Priority: P2)

As an operator using the LangGraph CLI, I need a `create_app()` factory so I can run `agente_imagem` through the same commands used for the other agents without editing source files.

**Why this priority**: CLI parity keeps operational workflows consistent; without it, this agent becomes an exception that increases support load.

**Independent Test**: Execute the LangGraph CLI command that targets `agente_imagem`, confirm it discovers `create_app()`, and verify the run succeeds end-to-end with the standard sample image.

**Acceptance Scenarios**:

1. **Given** the reorganized project, **When** the LangGraph CLI looks for `create_app()` in the package, **Then** it resolves the factory without custom configuration and runs the agent successfully.
2. **Given** the CLI execution, **When** the operator provides an image path through the documented mechanism, **Then** the workflow completes and returns the same markdown structure that `main.py` produced before refactoring.

---

### User Story 3 - Regression Confidence (Priority: P3)

As a QA engineer, I need automated coverage for the critical image-analysis path so I can verify the refactor preserved behavior without manual regression checks.

**Why this priority**: The agent relies on external services; a fast regression signal prevents shipping a broken structure that silently fails in production.

**Independent Test**: Run the targeted automated tests for `agente_imagem` in isolation and confirm they pass using the updated module layout with no changes to expected outcomes.

**Acceptance Scenarios**:

1. **Given** the updated file structure, **When** the automated tests covering default success and failure paths are executed, **Then** they pass on the first run and verify both a valid image and an invalid configuration scenario.
2. **Given** the refactored modules, **When** QA reviews logging for an invalid image input, **Then** the same error and warning messages appear as in the pre-refactor build.

### Edge Cases

- Running the agent without `GOOGLE_API_KEY` must still surface a clear configuration error rather than silently failing.
- Providing a missing or unreadable image path must return the same failure response and logs that the legacy script emitted.
- Invoking the agent through the CLI with no explicit image path must keep the documented fallback flow (auto-creating or referencing the default sample image).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The `agente_imagem` project MUST adopt the shared LangGraph agent layout, with discrete modules for configuration, state definition, workflow assembly, CLI entry point, utilities, docs, and tests that mirror the structure documented for `agente_simples`.
- **FR-002**: The package MUST expose a `create_app()` factory at the package level that returns the compiled workflow object currently exposed as `app`, ensuring compatibility with the LangGraph CLI.
- **FR-003**: The refactor MUST preserve all existing behaviors for valid and invalid image processing, including logging, fallback image creation, and markdown output so that baseline runs produce identical results.
- **FR-004**: Automated tests covering the primary success path and at least one failure path for `agente_imagem` MUST exist and pass without requiring updates to expected values after the restructure.
- **FR-005**: Project documentation (README and any quick-start instructions) MUST be updated to describe the new layout, how to invoke the agent through the CLI, and how to run its automated tests.
- **FR-006**: Packaging metadata (e.g., `langgraph.json` or equivalent project manifest) MUST be updated so tooling and the CLI locate the agent without manual path adjustments.

### Key Entities *(include if feature involves data)*

- **Image Analysis Request**: Represents the user-provided image context, including the source path, any generated base64 encoding, and metadata required to validate or load the asset.
- **Image Analysis Result**: Captures the workflow output, covering the raw LLM response, the derived markdown hierarchy, and any error indicators surfaced back to operators.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: When executing the standard sample image flow post-refactor, the produced markdown output matches the pre-refactor baseline with 100% string equality for at least two representative images.
- **SC-002**: The LangGraph CLI launches `agente_imagem` with the standard command on the first attempt, completing the workflow end-to-end without manual patching or code edits.
- **SC-003**: All automated tests covering `agente_imagem` pass on the first run (`pytest` exit code 0), confirming both success and failure paths behave as before.
- **SC-004**: During peer review, maintainers confirm (via checklist or sign-off) that each required module documented in FR-001 is present and described, with no gaps compared to the reference agent layout.

## Assumptions

- The existing prompt logic, logging configuration, and environment variable handling from `main.py` remain the source of truth for expected behavior.
- The LangGraph CLI uses the same discovery conventions as in `agente_simples`, so matching that structure is sufficient for compatibility.
- Team reviewers have access to the current `agente_imagem` outputs to establish the baseline for regression checks.

## Dependencies

- Access to the Google Generative AI API key remains necessary to exercise the full success path.
- LangGraph CLI tooling must already be installed in the development environment to validate the `create_app()` integration.
