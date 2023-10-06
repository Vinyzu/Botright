from __future__ import annotations

from playwright.async_api import Browser, BrowserContext, Page
from botright.modules import ProxyManager, Faker

from . import page

async def new_browser(main_browser: Browser, proxy: ProxyManager, faker: Faker, mask_fingerprint: bool, **launch_arguments) -> BrowserContext:
    """
    Create a new browser context with custom configurations.

    Args:
        main_browser (Browser): The main browser instance (e.g., Chromium).
        proxy (ProxyManager): An instance of ProxyManager for configuring proxy settings.
        faker (Faker): An instance of Faker for generating fake user agent and other details.
        **launch_arguments: Additional launch arguments for configuring the browser context. See https://playwright.dev/python/docs/api/class-browser#browser-new-context.

    Returns:
        BrowserContext: A new browser context with the specified configurations.
    """
    if mask_fingerprint:
        parsed_launch_arguments = {"user_agent": faker.useragent, "locale": "en-US",
                                   "timezone_id": proxy.timezone, "geolocation": {"longitude": proxy.longitude, "latitude": proxy.latitude, "accuracy": 0.7},
                                   "permissions": ["geolocation"], "ignore_https_errors": True,
                                   "screen": {"width": faker.width, "height": faker.height}, "viewport": {"width": faker.avail_width, "height": faker.avail_height},
                                   "color_scheme": "dark",
                                   "proxy": proxy.browser_proxy,
                                   "http_credentials": {"username": proxy.username, "password": proxy.password} if proxy.username else None,
                                   **launch_arguments}  # self.faker.locale
    else:
        parsed_launch_arguments = {"locale": "en-US",
                                   "timezone_id": proxy.timezone, "geolocation": {"longitude": proxy.longitude, "latitude": proxy.latitude, "accuracy": 0.7},
                                   "ignore_https_errors": True,
                                   "color_scheme": "dark",
                                   "proxy": proxy.browser_proxy,
                                   "http_credentials": {"username": proxy.username, "password": proxy.password} if proxy.username else None,
                                   **launch_arguments}  # self.faker.locale

    # Spawning a new Context for more options
    browser = await main_browser.new_context(**parsed_launch_arguments)

    await mock_browser(browser, faker)

    return browser

async def mock_browser(browser: BrowserContext, faker: Faker) -> None:
    """
    Mock the browser context to override the default `new_page` method with a custom page mocker.

    Args:
        browser (BrowserContext): The browser context to be mocked.
        faker (Faker): An instance of Faker for generating fake user agent and other details.
    """
    async def page_mocker(**launch_arguments) -> Page:
        """
        Args:
            **launch_arguments: Dont use! PlaywrightBrowserContext.new_page() doesn't take any args. Only used to prevent errors.

        Returns:
            Page: A new Page instance.
        """
        return await page.new_page(browser, faker)

    browser._new_page = browser.new_page
    browser.new_page = page_mocker
