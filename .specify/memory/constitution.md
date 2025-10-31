<!--
Sync Impact Report:
Version change: 1.3.0 -> 1.4.0
List of modified principles: XVI. Clarifying Requirements During /speckit.specify (added), XVII. Clarifying Technical Scope During /speckit.plan (added), XVIII. Clarifying Task Details During /speckit.tasks (added), XIX. Checkpoints During /speckit.implement (added)
Added sections: XVI. Clarifying Requirements During /speckit.specify, XVII. Clarifying Technical Scope During /speckit.plan, XVIII. Clarifying Task Details During /speckit.tasks, XIX. Checkpoints During /speckit.implement
Removed sections: None
Templates requiring updates:
- .specify/templates/plan-template.md ✅ reviewed (guidance consistent)
- .specify/templates/spec-template.md ✅ reviewed (guidance consistent)
- .specify/templates/tasks-template.md ✅ reviewed (guidance consistent)
- Command templates (n/a) — no files present
Follow-up TODOs: None
-->
# Langgraph Agent Development Constitution

## Core Principles

### I. Main File for Testing
Every project's `main` file MUST serve as an executable entry point for demonstrating and testing the core functionality of the agent.

### II. Continuous Learning & Best Practices
Developers MUST actively research and apply best practices for libraries and frameworks, leveraging internet resources to ensure high-quality and efficient solutions.

### III. Focused Testing Strategy
Tests SHOULD NOT be created for the non-deterministic functionalities of LLMs and agents themselves. Instead, focus on testing the integration, data flow, and deterministic components of the agent system.

### IV. Standard LLM Model
All agents MUST utilize `gemini-2.5-flash` as the default Large Language Model for consistency and performance.

### V. Standard Agent Framework
`langgraph` MUST be used as the primary framework for agent development and orchestration.

### VI. Code Simplicity
Code MUST be kept simple, readable, and maintainable, adhering to the YAGNI (You Ain't Gonna Need It) principle.

### VII. Documentation & Comments
Code MUST be adequately documented and commented, explaining *why* certain decisions were made, especially for complex logic.

### VIII. Python Development Standards
All development MUST be in Python, utilizing `venv` for virtual environments. Dependencies MUST be managed via `requirements.txt`, avoiding version pinning where possible and refraining from removing dependencies without explicit justification.

### IX. Change Approval Process
Approval MUST be sought for significant changes during the implementation phase, especially those impacting scope, architecture, or user experience.

### X. Project Module Structure
Avoid nested module folders within projects. Instead, leverage `PYTHONPATH` to include project roots for module resolution (e.g., `PYTHONPATH=./my_project python my_project/main.py`).

### XI. Relative Path Usage
Relative paths SHOULD be preferred over absolute paths for file and module references to enhance portability and maintainability.

### XII. Environment Configuration
New projects MUST copy the `.env` file from the `agente_simples` folder to ensure consistent environment variable management.

### XIII. Preferred Research Tools
`mcp` (Context7) SHOULD be used for documentation lookup, and `perplexity` for general internet research. `google_web_search` and `web_fetch` serve as fallback tools.

### XIV. Specification-Driven Development
All features MUST be developed using a specification-driven approach, leveraging the `.specify` framework for clear requirements, planning, and task generation.

### XV. Project Catalog Updates
Upon completing implementation of any new project (e.g., `agente_*`, `multi_agentes_*`, or similar study artifacts), teams MUST record the feature in `PROJETOS.md`, documenting both its user-facing functionality and the technical approach used to satisfy the requirements. This ensures the catalog stays current for future learning and governance reviews.

### XVI. Clarifying Requirements During `/speckit.specify`
While running `/speckit.specify`, developers MUST avoid assuming user goals or requirements. Whenever intent, scope, or success measures are unclear, the developer MUST ask explicit clarifying questions before proceeding, ensuring the generated specification reflects the user's expectations.

### XVII. Clarifying Technical Scope During `/speckit.plan`
During `/speckit.plan`, developers MUST resolve ambiguities in architecture, tooling, or delivery scope before finalizing the implementation plan. Missing technical definitions require explicit questions to the user, and the resulting plan MUST document a complete, unambiguous scope.

### XVIII. Clarifying Task Details During `/speckit.tasks`
When executing `/speckit.tasks`, developers MUST request additional details from the user whenever task breakdown decisions depend on unspecified requirements. Task lists MUST capture the clarified scope so execution can proceed without hidden assumptions.

### XIX. Checkpoints During `/speckit.implement`
While using `/speckit.implement`, developers MUST provide checkpoints after completing key requirements—especially complex activities—summarizing the work done, proposing next steps, and confirming direction with the user. If tests fail repeatedly, developers MUST pause, explain the situation, suggest remediation options, and ask how the user wishes to proceed before continuing.

## Development Guidelines

All development activities should adhere to the principles outlined above, ensuring consistency and quality across all projects.

## Workflow and Approvals

Significant changes require approval. The process for seeking approval will be defined as part of the project's overall workflow documentation.

## Governance

This Constitution supersedes all other practices. Amendments require documentation, approval, and a migration plan. All pull requests and code reviews MUST verify compliance with these principles. Complexity MUST be justified.

**Version**: 1.4.0 | **Ratified**: 2025-10-28 | **Last Amended**: 2025-10-31
