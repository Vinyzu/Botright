import pytest


@pytest.mark.asyncio
@pytest.mark.xfail
async def test_solve_hcaptcha(page):
    await page.goto("https://accounts.hcaptcha.com/demo?sitekey=00000000-0000-0000-0000-000000000000")

    result = await page.solve_hcaptcha()
    assert result


@pytest.mark.asyncio
@pytest.mark.xfail
async def test_get_hcaptcha(page):
    result = await page.get_hcaptcha()
    assert result
