from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Settings:
    """Runtime configuration (env-first).

    Note: keep this module lightweight; it is imported by tests.
    """

    serper_api_key: str = os.environ.get("SERPER_API_KEY", "")
    browser_engine: str = os.environ.get("KINDLY_BROWSER_ENGINE", "chromium")
    lightpanda_host: str = os.environ.get("KINDLY_LIGHTPANDA_HOST", "127.0.0.1")
    lightpanda_port: int = int(os.environ.get("KINDLY_LIGHTPANDA_PORT", "9222"))

settings = Settings()