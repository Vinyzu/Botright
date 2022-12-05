import pytest


@pytest.mark.asyncio
async def test_hcaptcha(page):
    await page.goto("https://accounts.hcaptcha.com/demo")

    result = await page.solve_hcaptcha()
    print(result)
    assert result
