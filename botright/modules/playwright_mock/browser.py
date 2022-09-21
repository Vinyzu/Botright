from . import page
from .. import hcaptcha


async def new_browser(botright, proxy, faker, **launch_arguments) -> "PlaywrightContext":
    # Spawning a new Context for more options
    browser = await botright.main_browser.new_context(
        locale="en-US",  # self.faker.locale
        geolocation={'longitude': proxy.longitude,
                     'latitude': proxy.latitude, "accuracy": 0.7},
        timezone_id=proxy.timezone,
        permissions=['geolocation'],
        screen={"width": faker.avail_width,
                "height": faker.avail_height},
        user_agent=faker.useragent,
        viewport={"width": faker.width,
                  "height": faker.height},
        proxy=proxy.browser_proxy,
        http_credentials={
            "username": proxy.username, "password": proxy.password} if proxy.username else None,
        **launch_arguments,
    )

    await mock_browser(botright, browser, proxy, faker)
    botright.stopable.append(browser)
    return browser


async def mock_browser(botright, browser, proxy, faker) -> None:
    async def get_hcaptcha_mocker(sitekey="00000000-0000-0000-0000-000000000000", rqdata=None):
        return await hcaptcha.get_hcaptcha(browser, sitekey=sitekey, rqdata=rqdata)
    browser.get_hcaptcha = get_hcaptcha_mocker

    async def page_mocker(**launch_arguments):
        return await page.new_page(botright, browser, proxy, faker, **launch_arguments)
    browser._new_page = browser.new_page
    browser.new_page = page_mocker
