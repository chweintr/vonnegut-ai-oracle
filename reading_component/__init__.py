from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import streamlit.components.v1 as components

_component_func = components.declare_component(
    "interactive_reading_pane",
    path=str(Path(__file__).parent / "frontend"),
)


def interactive_reading_pane(
    *,
    text_content: str,
    key: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Render the interactive reading pane component and return selection payload."""

    safe_text = text_content or ""
    return _component_func(text_content=safe_text, key=key, default=None)


__all__ = ["interactive_reading_pane"]
