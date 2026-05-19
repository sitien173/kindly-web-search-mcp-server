from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from kindly_web_search_mcp_server.settings import Settings
from kindly_web_search_mcp_server.scrape import chromium_pool


class TestBrowserEngine(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        chromium_pool._POOL = None
        chromium_pool._LIGHTPANDA_POOL = None
        chromium_pool._SHUTDOWN_REGISTERED = False

    def _apply_settings(self, *, engine: str = "chromium", host: str = "127.0.0.1", port: int = 9222) -> None:
        chromium_pool.settings = Settings.__new__(Settings)
        chromium_pool.settings.serper_api_key = ""
        chromium_pool.settings.browser_engine = engine
        chromium_pool.settings.lightpanda_host = host
        chromium_pool.settings.lightpanda_port = port

    async def test_get_browser_pool_returns_chromium_pool_by_default(self) -> None:
        self._apply_settings(engine="chromium")

        pool = await chromium_pool.get_browser_pool()

        self.assertIsInstance(pool, chromium_pool.ChromiumPool)

    async def test_get_browser_pool_returns_lightpanda_pool(self) -> None:
        self._apply_settings(engine="lightpanda")

        pool = await chromium_pool.get_browser_pool()

        self.assertIsInstance(pool, chromium_pool.LightPandaPool)
        self.assertEqual(pool.host, "127.0.0.1")
        self.assertEqual(pool.port, 9222)

    async def test_get_browser_pool_raises_on_unknown_engine(self) -> None:
        self._apply_settings(engine="invalid-engine")

        with self.assertRaises(RuntimeError):
            await chromium_pool.get_browser_pool()

    async def test_lightpanda_slot_terminate_is_noop(self) -> None:
        slot = chromium_pool.LightPandaSlot(slot_id=0, host="127.0.0.1", port=9222)

        await slot.terminate()
        slot.terminate_sync()

        self.assertEqual(slot.host, "127.0.0.1")
        self.assertEqual(slot.port, 9222)

    async def test_lightpanda_pool_acquire_release(self) -> None:
        self._apply_settings(engine="lightpanda")
        with patch(
            "kindly_web_search_mcp_server.scrape.nodriver_worker._wait_for_devtools_ready",
            new_callable=AsyncMock,
        ) as mock_wait:
            pool = await chromium_pool.get_lightpanda_pool()
            slot = await pool.acquire(user_agent="UA", diagnostics=None)

            self.assertIsNotNone(slot)
            assert slot is not None
            self.assertEqual(slot.host, "127.0.0.1")
            self.assertEqual(slot.port, 9222)
            mock_wait.assert_awaited_once()

            await pool.release(slot, diagnostics=None)
            reacquired = await pool.acquire(user_agent="UA", diagnostics=None)
            self.assertIsNotNone(reacquired)

    def test_settings_browser_engine_defaults(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            cfg = Settings()

        self.assertEqual(cfg.browser_engine, "chromium")
        self.assertEqual(cfg.lightpanda_host, "127.0.0.1")
        self.assertEqual(cfg.lightpanda_port, 9222)


if __name__ == "__main__":
    unittest.main()
