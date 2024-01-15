import pytest


@pytest.mark.asyncio
@pytest.mark.skip(reason="Geetest currently not supported")  # @pytest.mark.xfail
async def test_intelligent_captcha(page):
    await page.goto("https://www.geetest.com/en/adaptive-captcha-demo")

    result = await page.solve_geetest()
    assert result


@pytest.mark.asyncio
@pytest.mark.skip(reason="Geetest currently not supported")  # @pytest.mark.xfail
async def test_slider_captcha(page):
    await page.goto("https://www.geetest.com/en/adaptive-captcha-demo")

    checkbox = page.locator('[class="tab-item tab-item-1"]')
    await checkbox.click()

    await page.wait_for_timeout(2000)

    result = await page.solve_geetest()
    assert result


@pytest.mark.asyncio
@pytest.mark.skip(reason="Geetest currently not supported")  # @pytest.mark.xfail
async def test_icon_captcha(page):
    await page.goto("https://www.geetest.com/en/adaptive-captcha-demo")

    checkbox = page.locator('[class="tab-item tab-item-2"]')
    await checkbox.click()

    await page.wait_for_timeout(2000)

    result = await page.solve_geetest(mode="canny")
    assert result


@pytest.mark.asyncio
@pytest.mark.skip(reason="Geetest currently not supported")  # @pytest.mark.xfail
async def test_gobang_captcha(page):
    await page.goto("https://www.geetest.com/en/adaptive-captcha-demo")

    checkbox = page.locator('[class="tab-item tab-item-3"]')
    await checkbox.click()

    await page.wait_for_timeout(2000)

    result = await page.solve_geetest()
    assert result


@pytest.mark.asyncio
@pytest.mark.skip(reason="Geetest currently not supported")  # @pytest.mark.xfail
async def test_iconcrush_captcha(page):
    await page.goto("https://www.geetest.com/en/adaptive-captcha-demo")

    checkbox = page.locator('[class="tab-item tab-item-4"]')
    await checkbox.click()

    await page.wait_for_timeout(2000)

    result = await page.solve_geetest()
    assert result
