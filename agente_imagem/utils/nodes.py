"""StateGraph node implementations for the imagem agent refactor."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Dict

from langchain_core.messages import HumanMessage

from agente_imagem.config import config
from agente_imagem.state import (
    GraphState,
    STATUS_ERROR,
    STATUS_FORMATTED,
    STATUS_INVOKED,
    STATUS_PREPARED,
    STATUS_VALIDATED,
)
from agente_imagem.utils.io import ImageLoadError, ensure_sample_image, image_to_base64, verify_image
from agente_imagem.utils.logging import get_logger

logger = get_logger(__name__)

LLM_PROMPT = (
    "Analyze this mind map image and extract its hierarchical structure. "
    "Represent the structure as a markdown string, using headings and lists to show hierarchy. "
    "Only include node text and hierarchical level. If the image is not a mind map or is unclear, "
    "respond with 'INVALID_IMAGE'."
)


def validate_input_node(state: GraphState) -> Dict[str, object]:
    """Determine the target image path and initialise metadata."""

    provided_path = state.get("image_path")
    if provided_path:
        image_path = Path(provided_path)
    else:
        image_path = Path(config.default_image)
        ensure_sample_image(image_path)

    metadata = dict(state.get("metadata", {}))
    metadata.setdefault("started_at", time.time())
    metadata["image_path"] = str(image_path)

    logger.info("Imagem selecionada para análise", extra={"image_path": str(image_path)})

    return {
        "image_path": str(image_path),
        "metadata": metadata,
        "status": STATUS_VALIDATED,
    }


def prepare_image_node(state: GraphState) -> Dict[str, object]:
    """Validate and encode the image into base64 for downstream consumption."""

    image_path = Path(state.get("image_path", config.default_image))

    if not image_path.exists():
        logger.error("Image file not found: %s", image_path)
        return {
            "base64_image": None,
            "status": STATUS_ERROR,
            "error": f"Image file not found: {image_path}",
        }

    try:
        verify_image(image_path)
        encoded = image_to_base64(image_path)
    except ImageLoadError as exc:
        logger.error("Error opening or verifying image %s: %s", image_path, exc)
        return {
            "base64_image": None,
            "status": STATUS_ERROR,
            "error": str(exc),
        }

    logger.info("Imagem validada e codificada", extra={"image_path": str(image_path)})

    return {
        "base64_image": encoded,
        "status": STATUS_PREPARED,
    }


def invoke_model_node(state: GraphState) -> Dict[str, object]:
    """Call Gemini with the encoded image and capture the response."""

    base64_image = state.get("base64_image")
    if not base64_image:
        logger.warning("Fluxo interrompido por imagem inválida ou ausente.")
        return {"llm_response": None, "status": STATUS_ERROR}

    llm = config.create_llm()
    payload = HumanMessage(
        content=[
            {"type": "text", "text": LLM_PROMPT},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}},
        ]
    )

    logger.info("Invocando Gemini com imagem codificada.")

    try:
        response = llm.invoke([payload])
        content = getattr(response, "content", None)
    except Exception as exc:  # pragma: no cover - defensive path for provider errors
        logger.error("Erro durante invocação do LLM", extra={"error": str(exc)})
        content = None

    return {"llm_response": content, "status": STATUS_INVOKED if content else STATUS_ERROR}


def format_response_node(state: GraphState) -> Dict[str, object]:
    """Transform the LLM output into the final agent response."""

    response = state.get("llm_response")
    metadata = state.get("metadata", {})

    if not response:
        logger.warning("Sem resposta válida do LLM; retornando sem markdown.")
        return {"markdown_output": None, "status": STATUS_ERROR}

    if "INVALID_IMAGE" in response:
        logger.warning("LLM sinalizou imagem inválida.")
        return {"markdown_output": None, "status": STATUS_ERROR}

    duration = None
    started_at = metadata.get("started_at")
    if started_at is not None:
        duration = max(time.time() - started_at, 0.0)

    logger.info("Markdown gerado com sucesso.")

    update: Dict[str, object] = {
        "markdown_output": response,
        "status": STATUS_FORMATTED,
    }

    if duration is not None:
        update["duration_seconds"] = duration

    return update
