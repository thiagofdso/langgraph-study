# Feature Specification: SQLite Sales Agent

**Feature Branch**: `[011-sqlite-sales-agent]`  
**Created**: 2025-10-29  
**Status**: Draft  
**Input**: User description: "Quero um projeto para estudo. Crie na pasta agente_banco_dados um agente que responde exclusivamente baseado em uma base de dados local SQLLite sem acesso externo. Ele deve criar uma base local com registros de vendas, vendedor, produtos. Ele deve gerar um relatório dos produtos mais vendidos e dos melhores vendedores para teste. O proximo requisito é 011."

**Note**: This specification is an integral part of the specification-driven development process, generated and managed using the `.specify` framework, ensuring clear requirements and alignment with project goals.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Seed local sales database (Priority: P1)

As a learner configuring the study project, I can run the agent once to create a local SQLite database with sample data for products, sellers, and sales so that later insights are available without any external dependencies.

**Why this priority**: Without a populated local database, the agent has no information to reference, so this is the foundation for every other interaction.

**Independent Test**: Execute the agent from a clean workspace and confirm that the SQLite file, required tables, and a minimum set of seed records (at least 5 products, 3 sellers, and 20 sales rows) are created automatically.

**Acceptance Scenarios**:

1. **Given** no existing database file, **When** the agent runs, **Then** it creates the SQLite database with tables for products, sellers, and sales and confirms the record counts.
2. **Given** an existing database with the expected schema, **When** the agent runs again, **Then** it preserves existing data without duplicating the seed entries.

---

### User Story 2 - Summarize sales insights locally (Priority: P2)

As a learner exploring the dataset, I can trigger the agent to read only from the local database and receive a concise report of the top-selling products and highest-performing sellers so I can understand the sample sales trends offline.

**Why this priority**: The reporting output is the tangible learning outcome—without it the dataset is unused.

**Independent Test**: Run the agent after the database exists and verify that the console output lists the top products and sellers sorted by sales volume and revenue, clearly sourced from the local data.

**Acceptance Scenarios**:

1. **Given** the seeded database, **When** the agent generates the report, **Then** it prints the three products with the highest total quantity sold and the three sellers with the highest total revenue, stating that the results come from the local SQLite database.

---

### Edge Cases

- Agent runs without write permissions for the target directory—how is the user notified that the database cannot be created?
- Database file exists but schema is missing or corrupted—how does the agent repair or recreate it without data loss surprises?
- Learner deletes all rows in one of the tables—does the report clearly state that no data is available instead of failing silently?
- Agent is run repeatedly in quick succession—does it avoid duplicating seed data and still respond quickly?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The agent MUST create (if absent) a local SQLite database file inside `agente_banco_dados` with tables for products, sellers, and sales before answering any request.
- **FR-002**: The agent MUST seed the database with at least 5 products, 3 sellers, and 20 sales records, ensuring referential integrity between tables.
- **FR-003**: The agent MUST generate a console report that lists the top three products by quantity sold and the top three sellers by total revenue, sourced exclusively from the local database.
- **FR-004**: The agent MUST disclose in its output that insights are derived from the local database and MUST NOT attempt any external network access while running.
- **FR-005**: The agent MUST handle reruns idempotently by reusing the existing database without duplicating seed data, and it MUST warn the user if the schema or data is missing.

### Key Entities *(include if feature involves data)*

- **Product**: Represents an item being sold; key attributes include identifier, name, optional category, and unit price.
- **Seller**: Represents a salesperson; key attributes include identifier, name, and optional region.
- **Sale**: Represents a transaction; key attributes include identifier, product reference, seller reference, sale date, quantity, and total amount. Each sale links one product to one seller.

## Assumptions & Constraints

- The study project will run on a local machine with Python and SQLite available; no cloud or external services are expected.
- Sample data can be fictional and hard-coded because the goal is to practice local data handling.
- Reports can be delivered via standard console output; no GUI or API layer is required.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On a clean checkout, a single agent run completes database creation and seeding in under 10 seconds and confirms table counts in the console.
- **SC-002**: When the report action runs, the top three products and sellers are displayed in descending order with their aggregate metrics every time, even after multiple executions.
- **SC-003**: All agent responses explicitly state that insights are sourced from the local study database, without referencing any external data sources.
- **SC-004**: If required tables or data are missing, the agent emits a clear warning message guiding the learner to reseed the database within one execution.
