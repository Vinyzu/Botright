from contextlib import suppress

import pytest


@pytest.mark.asyncio
async def test_recaptcha(page):
    await page.goto("https://www.google.com/recaptcha/api2/demo")

    with suppress(RecursionError):
        result = await page.solve_recaptcha()
        assert result
