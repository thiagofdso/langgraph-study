"""Command-line interface for the imagem agent refactor."""

from __future__ import annotations

import argparse
from typing import List

from agente_imagem import preflight_config_check
from agente_imagem.config import config
from agente_imagem.graph import app
from agente_imagem.state import GraphState, STATUS_ERROR
from agente_imagem.utils import get_logger

logger = get_logger(__name__)


def _handle_preflight() -> bool:
    """Run configuration diagnostics and display actionable guidance."""

    checks: List[dict] = preflight_config_check()
    failures = [check for check in checks if check["result"] == "fail"]
    warnings = [check for check in checks if check["result"] == "warn"]

    for warning in warnings:
        print(f"⚠ {warning['message']}")

    if failures:
        for failure in failures:
            print(f"✗ {failure['message']}")
        logger.error("Falha de configuração detectada", extra={"failures": failures})
        return False

    return True


def main() -> None:
    """Parse CLI arguments, run the agent, and print the markdown result."""

    parser = argparse.ArgumentParser(description="Executa o agente de análise de mapas mentais.")
    parser.add_argument(
        "--image",
        default=config.default_image,
        help=f"Caminho para a imagem a ser analisada (padrão: {config.default_image})",
    )
    args = parser.parse_args()

    if not _handle_preflight():
        return

    initial_state: GraphState = {"image_path": args.image}
    result = app.invoke(initial_state)

    markdown = result.get("markdown_output")
    status = result.get("status", STATUS_ERROR)

    if markdown:
        logger.info("Execução concluída com sucesso", extra={"status": status, "image": args.image})
        print(markdown)
    else:
        logger.error("Execução concluída sem markdown", extra={"status": status, "image": args.image})
        print("Failed to generate markdown from the image.")


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
