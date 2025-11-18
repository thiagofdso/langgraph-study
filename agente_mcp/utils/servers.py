"""Server profile primitives and validation helpers."""
from __future__ import annotations

from dataclasses import dataclass, field
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Literal, Mapping, Sequence

VALID_TRANSPORTS = {"stdio", "sse"}
AGENT_ROOT = Path(__file__).resolve().parent.parent


class ServerProfileError(ValueError):
    """Raised when a server profile configuration is invalid."""


@dataclass(slots=True)
class ServerProfile:
    """Declarative metadata describing an MCP server."""

    name: str
    transport: Literal["stdio", "sse"]
    endpoint: str
    auto_start: bool = True
    env: Mapping[str, str] = field(default_factory=dict)
    timeout_seconds: int = 30

    def as_client_payload(self) -> Dict[str, object]:
        """Return a structure compatible with MultiServerMCPClient expectations."""

        payload: Dict[str, object] = {"transport": self.transport}
        if self.transport == "stdio":
            payload.update(
                {
                    "command": sys.executable,
                    "args": [self.endpoint],
                }
            )
            if self.env:
                payload["env"] = dict(self.env)
        else:
            payload.update({"url": self.endpoint})
        return payload


def _normalize_name(name: str) -> str:
    normalized = name.strip()
    if not normalized:
        raise ServerProfileError("name não pode estar vazio")
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789_")
    lowered = normalized.lower()
    if any(char not in allowed for char in lowered):
        raise ServerProfileError(
            "name deve usar snake_case (apenas letras minúsculas, números e underline)"
        )
    return lowered


def validate_profile(profile: ServerProfile) -> ServerProfile:
    """Validate a single profile instance, returning the same object for chaining."""

    profile.name = _normalize_name(profile.name)
    if profile.transport not in VALID_TRANSPORTS:
        raise ServerProfileError(
            f"Transporte '{profile.transport}' não suportado. Use um destes: {VALID_TRANSPORTS}."
        )
    endpoint = profile.endpoint.strip()
    if not endpoint:
        raise ServerProfileError("endpoint não pode estar vazio")
    profile.endpoint = endpoint
    if profile.transport == "stdio":
        script_path = Path(endpoint)
        if not script_path.exists():
            raise ServerProfileError(f"Arquivo do servidor não encontrado: {script_path}")
    if profile.timeout_seconds <= 0:
        raise ServerProfileError("timeout_seconds deve ser positivo")
    return profile


def validate_profiles(profiles: Iterable[ServerProfile]) -> List[ServerProfile]:
    """Validate multiple profiles ensuring uniqueness by name."""

    validated: List[ServerProfile] = []
    seen: set[str] = set()
    for profile in profiles:
        current = validate_profile(profile)
        if current.name in seen:
            raise ServerProfileError(f"Perfil duplicado detectado: {current.name}")
        seen.add(current.name)
        validated.append(current)
    return validated


def builtin_server_profiles() -> List[ServerProfile]:
    """Return the default math + weather profiles used across the repo."""

    math_script = AGENT_ROOT / "mcp_servers" / "math_server.py"
    weather_url = "http://localhost:8000/sse"
    defaults = [
        ServerProfile(
            name="math",
            transport="stdio",
            endpoint=str(math_script),
            auto_start=True,
            timeout_seconds=30,
        ),
        ServerProfile(
            name="weather",
            transport="sse",
            endpoint=weather_url,
            auto_start=False,
            timeout_seconds=30,
        ),
    ]
    return validate_profiles(defaults)


DEFAULT_SERVER_PROFILES = tuple(builtin_server_profiles())


def load_server_profiles(
    source: Sequence[ServerProfile] | None = None,
) -> List[ServerProfile]:
    """Load server profiles from the provided sequence or fall back to defaults."""

    if source is None:
        return list(DEFAULT_SERVER_PROFILES)
    return validate_profiles(source)


def build_connection_map(
    profiles: Sequence[ServerProfile],
) -> Dict[str, Dict[str, object]]:
    """Convert profiles into the structure accepted by MultiServerMCPClient."""

    return {profile.name: profile.as_client_payload() for profile in profiles}


__all__ = [
    "DEFAULT_SERVER_PROFILES",
    "ServerProfile",
    "ServerProfileError",
    "builtin_server_profiles",
    "build_connection_map",
    "load_server_profiles",
    "validate_profile",
    "validate_profiles",
]
