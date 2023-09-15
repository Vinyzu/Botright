from __future__ import annotations

from playwright.async_api import BrowserContext, Page
from botright.modules import ProxyManager, Faker

from . import page

async def new_browser(botright, proxy: ProxyManager, faker: Faker, **launch_arguments) -> BrowserContext:
    parsed_launch_arguments = {"user_agent": faker.useragent, "locale": "en-US",
                               "timezone_id": proxy.timezone, "geolocation": {"longitude": proxy.longitude, "latitude": proxy.latitude, "accuracy": 0.7},
                               "permissions": ["geolocation"], "ignore_https_errors": True,
                               "screen": {"width": faker.avail_width, "height": faker.avail_height}, "viewport": {"width": faker.width, "height": faker.height},
                               "proxy": proxy.browser_proxy,
                               "http_credentials": {"username": proxy.username, "password": proxy.password} if proxy.username else None,
                               **launch_arguments}  # self.faker.locale

    # Spawning a new Context for more options
    if proxy.browser_proxy:
        browser = await botright.proxy_main_browser.new_context(**parsed_launch_arguments)
    else:
        browser = await botright.main_browser.new_context(**parsed_launch_arguments)

    await mock_browser(botright, browser, faker)
    botright.stoppable.append(browser)
    return browser

async def mock_browser(botright, browser: BrowserContext, faker: Faker) -> None:
    async def page_mocker(**launch_arguments) -> Page:
        return await page.new_page(botright, browser, faker)

    browser._new_page = browser.new_page
    browser.new_page = page_mocker
