import pytest


@pytest.mark.asyncio
async def test_recaptcha(page):
    await page.goto("https://www.google.com/recaptcha/api2/demo")

    result = await page.solve_recaptcha()
    print(result)
    assert result
