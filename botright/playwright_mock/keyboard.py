from __future__ import annotations

import random
from typing import TYPE_CHECKING, Optional

# from undetected_playwright.async_api import Keyboard as PlaywrightKeyboard
from playwright.async_api import Keyboard as PlaywrightKeyboard

if TYPE_CHECKING:
    from . import Page


class Keyboard(PlaywrightKeyboard):
    def __init__(self, keyboard: PlaywrightKeyboard, page: Page):
        super().__init__(keyboard)
        self._impl_obj = keyboard._impl_obj

        self._page = page
        self._origin_type = keyboard.type

    async def type(self, text: str, *, delay: Optional[float] = None) -> None:
        if not delay:
            delay = 100
        delay = int(delay)

        for char in text:
            await self._origin_type(text=char, delay=random.randint(delay - 50, delay + 50))
        await self._page.wait_for_timeout(random.randint(4, 8) * 100)
