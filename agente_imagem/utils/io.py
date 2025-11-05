"""Image IO helpers for the imagem agent refactor."""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Optional

from PIL import Image


class ImageLoadError(RuntimeError):
    """Raised when an image cannot be located or decoded."""


def image_to_base64(path: str | Path) -> str:
    """Return the base64 representation of the provided image."""

    file_path = Path(path)
    if not file_path.exists():
        raise ImageLoadError(f"Arquivo não encontrado: {file_path}")

    with file_path.open("rb") as handle:
        return base64.b64encode(handle.read()).decode("utf-8")


def base64_to_image(encoded: str, *, output_path: str | Path = "decoded_image.png") -> Path:
    """Decode a base64 string into an image file and return its path."""

    file_path = Path(output_path)
    file_path.write_bytes(base64.b64decode(encoded.encode("utf-8")))
    return file_path


def ensure_sample_image(default_path: Path) -> None:
    """Create a sample image for demonstration purposes if missing."""

    if default_path.exists():
        return

    default_path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (60, 30), color="red")
    image.save(default_path)


def verify_image(path: Path) -> None:
    """Validate that the target file is a readable image."""

    try:
        with Image.open(path) as img:
            img.verify()
    except Exception as exc:  # pragma: no cover - defensive logging occurs upstream
        raise ImageLoadError(f"Erro ao abrir ou validar imagem {path}: {exc}") from exc
