import pytest


@pytest.mark.asyncio
@pytest.mark.xfail
async def test_recaptcha(page):
    await page.goto("https://www.google.com/recaptcha/api2/demo")

    result = await page.solve_recaptcha()
    assert result
