import pytest

from botright.extended_typing import Page


@pytest.mark.asyncio
async def test_browserleaks(page: Page):
    await page.goto("https://browserleaks.com/webrtc")
    await page.wait_for_timeout(2000)

    leak_check = await page.locator("[id='rtc-leak']").text_content()
    assert "No Leak" in leak_check


@pytest.mark.asyncio
async def test_expressvpn(page: Page):
    await page.goto("https://www.expressvpn.com/en/webrtc-leak-test")
    await page.wait_for_timeout(2000)

    leak_checks = page.locator("[class='title green']")
    leak_check0 = await leak_checks.nth(0).is_visible()
    leak_check1 = await leak_checks.nth(1).is_visible()
    print(leak_check0, leak_check1)
    assert leak_check0 or leak_check1


@pytest.mark.asyncio
async def test_surfshark(page: Page):
    await page.goto("https://surfshark.com/en/webrtc-leak-test")
    await page.wait_for_timeout(2000)

    leak_check = await page.locator("[data-test='webrtc-leak-test-checker']").inner_html()
    assert "No WebRTC leaks detected" in leak_check


@pytest.mark.asyncio
async def test_hide_me(page: Page):
    await page.goto("https://hide.me/en/webrtc-leak-test")
    await page.wait_for_timeout(2000)

    leak_check = await page.locator("[data-type='webrtc']").inner_html()
    assert "WebRTC is disabled" in leak_check


@pytest.mark.skip(reason="Hidemyass is maight maight detect wrong / detect js instead of webrtc")
@pytest.mark.asyncio
async def test_hidemyass(page: Page):
    await page.goto("https://www.hidemyass.com/webrtc-leak-test?nogeoip")
    await page.wait_for_timeout(2000)

    leak_check = page.locator("[class *= 'header-message protected']")
    assert await leak_check.is_visible()


@pytest.mark.asyncio
async def test_ovpn(page: Page):
    await page.goto("https://www.ovpn.com/en/webrtc-leak-test")
    await page.wait_for_timeout(2000)

    leak_check = await page.locator("[class='protected-wrapper protected']").text_content()
    assert leak_check == "No IP leak"


@pytest.mark.asyncio
async def test_browserscan(page: Page):
    await page.goto("https://www.browserscan.net/webrtc")
    await page.wait_for_timeout(2000)

    leak_checks = page.locator("[class *= '_webrtc__item__ip']")
    for leak_check in await leak_checks.all_text_contents():
        assert leak_check.lower() == "disabled"
