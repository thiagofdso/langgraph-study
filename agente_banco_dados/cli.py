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

    metadata = result.get("metadata", {})
    processed = metadata.get("processed_records", result.get("processed_records"))
    latency = metadata.get("llm_latency_seconds", result.get("llm_latency_seconds"))
    data_source = metadata.get("data_source")
    print("\nResumo da execução:")
    if processed is not None:
        print(f"- Registros processados: {processed}")
    if latency is not None:
        print(f"- Latência da chamada ao LLM: {latency:.2f} s")
    if data_source:
        print(f"- Fonte dos dados: {data_source}")
    print(f"- Gerado em: {metadata.get('generated_at', 'desconhecido')}")


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
