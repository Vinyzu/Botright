from __future__ import annotations

from typing import Optional
import os
import logging

import hcaptcha_challenger as solver
from async_class import AsyncObject
from playwright.async_api import async_playwright, BrowserContext
import browsers

from .modules import Faker, ProxyManager
from .modules.playwright_mock import browser

logging.getLogger("websockets").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

class Botright(AsyncObject):
    async def __ainit__(self,
                        headless: Optional[bool] = False,
                        block_images: Optional[bool] = False,
                        cache_responses: Optional[bool] = False,
                        user_action_layer: Optional[bool] = True,
                        scroll_into_view: Optional[bool] = True,
                        disable_canvas: Optional[bool] = True) -> None:
        # Init local-side of the ModelHub
        solver.install(upgrade=True)
        # solver.install(flush_yolo=True, upgrade=True)

        # Setting Values
        self.block_images = block_images
        self.cache_responses = cache_responses
        self.scroll_into_view = scroll_into_view
        self.user_action_layer = user_action_layer
        self.cache = {}
        self.flags = ['--accept-lang=en-US', '--lang=en-US', '--incognito', '--no-pings', '--no-zygote', '--mute-audio', '--no-first-run', '--no-default-browser-check', '--disable-software-rasterizer', '--disable-cloud-import', '--disable-gesture-typing', '--disable-offer-store-unmasked-wallet-cards', '--disable-offer-upload-credit-cards', '--disable-print-preview', '--disable-voice-input', '--disable-wake-on-wifi', '--disable-cookie-encryption', '--ignore-gpu-blocklist', '--enable-async-dns', '--enable-simple-cache-backend', '--enable-tcp-fast-open', '--prerender-from-omnibox=disabled', '--enable-web-bluetooth', '--disable-features=AudioServiceOutOfProcess,IsolateOrigins,site-per-process,TranslateUI,BlinkGenPropertyTrees', '--aggressive-cache-discard', '--disable-extensions', '--disable-blink-features', '--disable-blink-features=AutomationControlled', '--disable-ipc-flooding-protection', '--enable-features=NetworkService,NetworkServiceInProcess,TrustTokens,TrustTokensAlwaysAllowIssuance', '--disable-component-extensions-with-background-pages', '--disable-default-apps', '--disable-breakpad'] #, '--disable-component-update', '--disable-domain-reliability', '--disable-sync', '--disable-client-side-phishing-detection', '--disable-hang-monitor', '--disable-popup-blocking', '--disable-prompt-on-repost', '--metrics-recording-only', '--safebrowsing-disable-auto-update', '--password-store=basic', '--autoplay-policy=no-user-gesture-required', '--use-mock-keychain', '--force-webrtc-ip-handling-policy=default_public_interface_only', '--disable-session-crashed-bubble', '--disable-crash-reporter', '--disable-dev-shm-usage', '--force-color-profile=srgb', '--disable-translate', '--disable-background-networking', '--disable-background-timer-throttling', '--disable-backgrounding-occluded-windows', '--disable-infobars', '--hide-scrollbars', '--disable-renderer-backgrounding', '--font-render-hinting=none', '--disable-logging', '--enable-surface-synchronization', '--run-all-compositor-stages-before-draw', '--disable-threaded-animation', '--disable-threaded-scrolling', '--disable-checker-imaging', '--disable-new-content-rendering-timeout', '--disable-image-animation-resync', '--disable-partial-raster', '--blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4']

        # Collecting items that can be stopped
        self.stoppable = []
        self.temp_user_data_dirs = []

        # Extensions
        path_to_extension = rf"{os.path.dirname(os.path.abspath(__file__))}\WebRTC-Leak-Shield"
        self.flags.append(f"--disable-extensions-except={path_to_extension}")
        self.flags.append(f"--load-extension={path_to_extension}")

        if disable_canvas:
            self.flags.append('--disable-reading-from-canvas')

        # Starting Playwright
        self.playwright = await async_playwright().start()
        self.browser = self.get_browser_engine()

        # Launching Firefox with Human Emulation and Prevent WebRTC leakage
        self.main_browser = await self.playwright.chromium.launch(headless=headless, executable_path=self.browser["path"], proxy=None, args=self.flags)
        self.proxy_main_browser = await self.playwright.chromium.launch(headless=headless, executable_path=self.browser["path"], proxy={"server": 'http://per-context'}, args=self.flags)
        self.stoppable.append(self.main_browser)

    async def new_browser(self,
                          proxy: Optional[str] = None,
                          stealth_page: Optional[bool] = True,
                          **launch_arguments) -> BrowserContext:

        # Calling ProxyManager and Faker to get necessary information for Botright
        _proxy = await ProxyManager(self, proxy)
        _faker = await Faker(self, _proxy)

        _browser = await browser.new_browser(self, _proxy, _faker, **launch_arguments)
        _browser.proxy = _proxy
        _browser.faker = _faker
        _browser.stealth_page = stealth_page

        await _browser.grant_permissions(["notifications", "geolocation"])
        self.stoppable.append(_browser)
        self.stoppable.append(_browser)

        return _browser

    async def __adel__(self) -> None:
        """This method will be called when object will be closed"""
        for obj in self.stoppable:
            try:
                await obj.close()
            except Exception:
                pass

        try:
            await self.playwright.stop()
        except Exception:
            pass

    @staticmethod
    def get_browser_engine() -> browsers.Browser:
        # Get a browser on the system based on Chromium (for cdp)
        # Chrome preferred (much stealthier)
        if chrome := browsers.get("chrome"):
            return chrome

        not_supported = ["firefox", "msie", "opera", "chrome", "msedge", "opera"]
        for browser_engine in browsers.browsers():
            if browser_engine["browser_type"] not in not_supported:
                return browser_engine

        raise EnvironmentError("No Chromium based browser found")
