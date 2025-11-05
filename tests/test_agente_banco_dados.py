from agente_banco_dados import create_app, initialize_database


def test_create_app_generates_report():
    """create_app must return a compiled graph capable of generating the Markdown report."""

    initialize_database()
    app = create_app()
    result = app.invoke({})

    assert "# Relatório de Vendas Baseado em SQLite" in result["report_markdown"]
    assert len(result["top_products"]) > 0
    assert len(result["top_sellers"]) > 0
