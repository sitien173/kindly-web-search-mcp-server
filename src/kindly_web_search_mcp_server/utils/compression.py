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

_backend: str | None = os.environ.get("KINDLY_COMPRESS_BACKEND", "").strip().lower() or None
_model: str | None = os.environ.get("KINDLY_COMPRESS_MODEL", "").strip() or None
_base_url: str | None = os.environ.get("KINDLY_COMPRESS_BASE_URL", "").strip() or None

_warned_missing = False
_warned_error = False
_logged_backend = False


def _build_kwargs() -> dict:
    kwargs: dict = {}
    if _backend:
        kwargs["backend"] = _backend
    if _model:
        kwargs["model"] = _model
    if _base_url:
        kwargs["base_url"] = _base_url
        kwargs["calculate_embeddings"] = False
    return kwargs


def maybe_compress(text: str) -> str:
    """Return *text* compressed if enabled and available, otherwise unchanged."""
    global _warned_missing, _warned_error, _logged_backend

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

    try:
        result = _cc_compress(text, **_build_kwargs())
    except Exception as exc:
        if not _warned_error:
            logger.warning("Caveman compression failed, returning uncompressed: %s", exc)
            _warned_error = True
        return text

    if isinstance(result, tuple):
        compressed = result[0]
    else:
        compressed = result

    if not _logged_backend:
        backend_label = _backend or "auto-detected"
        model_label = f", model={_model}" if _model else ""
        url_label = f", base_url={_base_url}" if _base_url else ""
        logger.info("Caveman compression active (backend=%s%s%s)", backend_label, model_label, url_label)
        _logged_backend = True

    return compressed
