from __future__ import annotations

from typing import Optional
import os
import logging
import platform

import hcaptcha_challenger as solver
from async_class import AsyncObject
from playwright.async_api import async_playwright, BrowserContext
import browsers

from .modules import Faker, ProxyManager
from botright.playwright_mock import browser
from .fingerprint_generator import FingerprintGenerator

logging.getLogger("websockets").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

class Botright(AsyncObject):
    async def __ainit__(self,
                        headless: Optional[bool] = False,
                        block_images: Optional[bool] = False,
                        cache_responses: Optional[bool] = False,
                        user_action_layer: Optional[bool] = False,
                        scroll_into_view: Optional[bool] = True,
                        disable_canvas: Optional[bool] = True,
                        dont_mask_fingerprint: Optional[bool] = False) -> None:
        """
        Initialize a Botright instance with specified configurations.

        Args:
            headless (bool, optional): Whether to run the browser in headless mode. Defaults to False.
            block_images (bool, optional): Whether to block images in the browser. Defaults to False.
            cache_responses (bool, optional): Whether to cache HTTP responses. Defaults to False.
            user_action_layer (bool, optional): Whether to enable user action simulation layer. Defaults to False.
            scroll_into_view (bool, optional): Whether to scroll elements into view automatically. Defaults to True.
            disable_canvas (bool, optional): Whether to disable canvas fingerprinting protection. Defaults to True.
            dont_mask_fingerprint (bool, optional): Whether to mask the browser fingerprint. Defaults to False.
        """

        # Init local-side of the ModelHub
        solver.install(upgrade=True)
        # Starting Playwright
        self.playwright = await async_playwright().start()
        self.browser = self.get_browser_engine()

        # Setting Values
        self.headless = headless
        self.block_images = block_images
        self.cache_responses = cache_responses
        self.scroll_into_view = scroll_into_view
        self.user_action_layer = user_action_layer
        self.mask_fingerprint = not dont_mask_fingerprint
        self.cache = {}

        self.flags = ['--accept-lang=en-US', '--lang=en-US', '--incognito', '--no-pings', '--no-zygote', '--mute-audio', '--no-first-run', '--no-default-browser-check', '--disable-software-rasterizer', '--disable-cloud-import', '--disable-gesture-typing', '--disable-offer-store-unmasked-wallet-cards', '--disable-offer-upload-credit-cards', '--disable-print-preview', '--disable-voice-input', '--disable-wake-on-wifi', '--disable-cookie-encryption', '--ignore-gpu-blocklist', '--enable-async-dns', '--enable-simple-cache-backend', '--enable-tcp-fast-open', '--prerender-from-omnibox=disabled', '--enable-web-bluetooth', '--disable-features=AudioServiceOutOfProcess,IsolateOrigins,site-per-process,TranslateUI,BlinkGenPropertyTrees', '--aggressive-cache-discard', '--disable-extensions', '--disable-blink-features', '--disable-blink-features=AutomationControlled', '--disable-ipc-flooding-protection', '--enable-features=NetworkService,NetworkServiceInProcess,TrustTokens,TrustTokensAlwaysAllowIssuance', '--disable-component-extensions-with-background-pages', '--disable-default-apps', '--disable-breakpad', '--disable-component-update', '--disable-domain-reliability', '--disable-sync', '--disable-client-side-phishing-detection', '--disable-hang-monitor', '--disable-popup-blocking', '--disable-prompt-on-repost', '--metrics-recording-only', '--safebrowsing-disable-auto-update', '--password-store=basic', '--autoplay-policy=no-user-gesture-required', '--use-mock-keychain', '--force-webrtc-ip-handling-policy=default_public_interface_only', '--disable-session-crashed-bubble', '--disable-crash-reporter', '--disable-dev-shm-usage', '--force-color-profile=srgb', '--disable-translate', '--disable-background-networking', '--disable-background-timer-throttling', '--disable-backgrounding-occluded-windows', '--disable-infobars', '--hide-scrollbars', '--disable-renderer-backgrounding', '--font-render-hinting=none', '--disable-logging', '--enable-surface-synchronization', '--run-all-compositor-stages-before-draw', '--disable-threaded-animation', '--disable-threaded-scrolling', '--disable-checker-imaging', '--disable-new-content-rendering-timeout', '--disable-image-animation-resync', '--disable-partial-raster', '--blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4']

        # Collecting items that can be stopped
        self.stoppable = []
        self.temp_user_data_dirs = []

        if disable_canvas and self.browser["browser_type"] != "chromium":
            self.flags.append('--disable-reading-from-canvas')
        elif self.mask_fingerprint:
            self.flags.append('--fingerprinting-canvas-image-data-noise')

        os_dict = {"Darwin": "macos", "Windows": "windows", "Linux": "linux", "Java": "linux"}
        self.fingerprint_generator = FingerprintGenerator(os_dict[platform.system()])

    async def new_browser(self,
                          proxy: Optional[str] = None,
                          stealth_page: Optional[bool] = True,
                          **launch_arguments) -> BrowserContext:
        """
        Create a new Botright browser instance with specified configurations.

        Args:
            proxy (str, optional): Proxy server URL to use for the browser. Defaults to None.
            stealth_page (bool, optional): Whether to enable stealth mode for the browser page. Defaults to True.
            **launch_arguments: Additional launch arguments for the browser.

        Returns:
            BrowserContext: A new browser context for web scraping or automation.
        """

        # Calling ProxyManager and Faker to get necessary information for Botright
        _proxy = await ProxyManager(self, proxy)
        _faker = await Faker(self, _proxy)

        # Launching Main Browser
        if self.mask_fingerprint:
            flags = self.flags + [f"--user-agent={_faker.useragent}"]
        else:
            flags = self.flags
        if _proxy.browser_proxy:
            main_browser = await self.playwright.chromium.launch(headless=self.headless, executable_path=self.browser["path"], proxy={"server": 'http://per-context'}, args=flags)
        else:
            main_browser = await self.playwright.chromium.launch(headless=self.headless, executable_path=self.browser["path"], proxy=None, args=flags)

        _browser = await browser.new_browser(main_browser, _proxy, _faker, self.mask_fingerprint, **launch_arguments)
        _browser.proxy = _proxy
        _browser.faker = _faker
        _browser.stealth_page = stealth_page
        _browser.user_action_layer = self.user_action_layer
        _browser.scroll_into_view = self.scroll_into_view
        _browser.mask_fingerprint = self.mask_fingerprint

        await _browser.grant_permissions(["notifications", "geolocation"])
        self.stoppable.append(_browser)
        self.stoppable.append(main_browser)

        return _browser

    async def __adel__(self) -> None:
        """
        Cleanup method called when the Botright instance is closed.
        Closes all associated browser instances and stops the Playwright engine.
        """
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
        """
        Get the browser engine to use for Playwright based on system availability.
        If available, prefers Ungoogled Chromium for stealthier browsing.

        Returns:
            browsers.Browser: The selected browser engine.
        Raises:
            EnvironmentError: If no Chromium based browser is found on the system.
        """
        # Get a browser on the system based on Chromium (for cdp)
        # Ungoogled Chromium preferred (most stealthy)
        if chrome := browsers.get("chromium"):
            return chrome
        print("\033[1;33;48m[WARNING] Ungoogled Chromium not found. Recommended for stealthier botright and Canvas Manipulation. Download at https://ungoogled-software.github.io/ungoogled-chromium-binaries/ \033[0m")

        # Chrome preferred (much stealthier)
        if chrome := browsers.get("chrome"):
            return chrome

        not_supported = ["firefox", "msie", "opera", "msedge"]
        for browser_engine in browsers.browsers():
            if browser_engine["browser_type"] not in not_supported:
                return browser_engine

        raise EnvironmentError("No Chromium based browser found")
