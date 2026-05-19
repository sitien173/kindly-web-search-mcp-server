"""Optional output compression via caveman-compression."""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

try:
    from caveman_compression import compress_text as _cc_compress  # type: ignore[import-untyped]
except ImportError:
    _cc_compress = None

_enabled: bool = os.environ.get("KINDLY_COMPRESS_OUTPUT", "").strip().lower() in (
    "true",
    "1",
    "yes",
)

_warned_missing = False
_logged_backend = False


def maybe_compress(text: str) -> str:
    """Return *text* compressed if enabled and available, otherwise unchanged."""
    global _warned_missing, _logged_backend

    if not _enabled:
        return text

    if _cc_compress is None:
        if not _warned_missing:
            logger.warning(
                "KINDLY_COMPRESS_OUTPUT is enabled but caveman-compression is not installed. "
                "Install with: pip install caveman-compression"
            )
            _warned_missing = True
        return text

    result = _cc_compress(text)

    if isinstance(result, tuple):
        compressed = result[0]
    else:
        compressed = result

    if not _logged_backend:
        logger.info("Caveman compression active (auto-detected backend)")
        _logged_backend = True

    return compressed
