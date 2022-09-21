
from async_class import AsyncObject
from playwright.async_api import async_playwright

from .modules import Faker, ProxyManager
from .modules.playwright_mock import browser
from .modules.hcaptcha_challenger.update import update_ai


class Botright(AsyncObject):
    async def __ainit__(self, headless=False) -> None:
        # Updating AI
        update_ai()

        # Collecting items that can be stopped
        self.stopable = []
        # Starting Playwright
        self.playwright = await async_playwright().start()
        # Launching Firefox with Human Emulation and Prevent WebRTC leakage
        self.main_browser = await self.playwright.firefox.launch(headless=headless, proxy=None, firefox_user_prefs={"media.peerconnection.enabled": False, "media.navigator.enabled": False})
        self.stopable.append(self.main_browser)

    async def new_browser(self, proxy=None, **launch_arguments) -> "PlaywrightContext":
        # Calling ProxyManager and Faker to get neccessary informations for Botright
        _proxy = await ProxyManager(self, proxy)
        _faker = await Faker(self, _proxy)

        _browser = await browser.new_browser(self, _proxy, _faker, **launch_arguments)
        _browser.proxy = _proxy
        _browser.faker = _faker

        return _browser

    async def __adel__(self) -> None:
        """ This method will be called when object will be closed """
        for obj in self.stopable:
            try:
                await obj.close()
            except:
                pass

        try:
            await self.playwright.stop()
        except:
            pass
