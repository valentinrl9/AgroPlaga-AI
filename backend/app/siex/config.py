"""Configuración módulo NEXO SIEX."""

import os

SIEX_PREVIEW_OPEN = os.getenv("SIEX_PREVIEW_OPEN", "false").strip().lower() in ("1", "true", "yes")
