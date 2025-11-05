"""Command-line interface for executing the SQLite sales report agent."""

from __future__ import annotations

from agente_banco_dados.db_init import initialize_database
from agente_banco_dados.graph import app


def main() -> None:
    """Prepare the SQLite dataset and print the generated Markdown report."""

    counts = initialize_database()
    print(
        "Database ready with "
        f"{counts['products']} products, "
        f"{counts['sellers']} sellers, "
        f"{counts['sales']} sales records."
    )
    print("Relatório gerado exclusivamente a partir do banco SQLite local.")
    result = app.invoke({})
    print(result["report_markdown"])


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
