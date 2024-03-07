from __future__ import annotations

import logging
import os
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Optional

import browsers
import hcaptcha_challenger as solver
import loguru
from async_class import AsyncObject
from chrome_fingerprints import AsyncFingerprintGenerator
from playwright.async_api import APIResponse, Playwright, async_playwright
from undetected_playwright.async_api import async_playwright as undetected_async_playwright

from botright.playwright_mock import browser

from .modules import Faker, ProxyManager
from .playwright_mock import BrowserContext

logging.getLogger("websockets").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
loguru.logger.disable("hcaptcha_challenger")


class Botright(AsyncObject):
    def __init__(
        self,
        headless: Optional[bool] = False,
        block_images: Optional[bool] = False,
        cache_responses: Optional[bool] = False,
        user_action_layer: Optional[bool] = False,
        scroll_into_view: Optional[bool] = True,
        spoof_canvas: Optional[bool] = True,
        mask_fingerprint: Optional[bool] = True,
        use_undetected_playwright: Optional[bool] = False,
    ) -> None:
        """
        Initialize a Botright instance with specified configurations.

        Args:
            headless (bool, optional): Whether to run the browser in headless mode. Defaults to False.
            block_images (bool, optional): Whether to block images in the browser. Defaults to False.
            cache_responses (bool, optional): Whether to cache HTTP responses. Defaults to False.
            user_action_layer (bool, optional): Whether to enable user action simulation layer. Defaults to False.
            scroll_into_view (bool, optional): Whether to scroll elements into view automatically. Defaults to True.
            spoof_canvas (bool, optional): Whether to disable canvas fingerprinting protection. Defaults to True.
            mask_fingerprint (bool, optional): Whether to mask the browser fingerprint. Defaults to True.
            use_undetected_playwright (bool, optional): Whether to use undetected_playwright (TEMP). Defaults to False.
        """
        # This Init Function is only for intellisense.
        super().__init__()

    async def __ainit__(
        self,
        headless: Optional[bool] = False,
        block_images: Optional[bool] = False,
        cache_responses: Optional[bool] = False,
        user_action_layer: Optional[bool] = False,
        scroll_into_view: Optional[bool] = True,
        spoof_canvas: Optional[bool] = True,
        mask_fingerprint: Optional[bool] = True,
        use_undetected_playwright: Optional[bool] = False,
    ) -> None:
        """
        Initialize a Botright instance with specified configurations.

        Args:
            headless (bool, optional): Whether to run the browser in headless mode. Defaults to False.
            block_images (bool, optional): Whether to block images in the browser. Defaults to False.
            cache_responses (bool, optional): Whether to cache HTTP responses. Defaults to False.
            user_action_layer (bool, optional): Whether to enable user action simulation layer. Defaults to False.
            scroll_into_view (bool, optional): Whether to scroll elements into view automatically. Defaults to True.
            spoof_canvas (bool, optional): Whether to disable canvas fingerprinting protection. Defaults to True.
            mask_fingerprint (bool, optional): Whether to mask the browser fingerprint. Defaults to True.
            use_undetected_playwright (bool, optional): Whether to use undetected_playwright . EXPERIMENTAL (TEMP). Defaults to False.
        """

        # Init local-side of the ModelHub
        solver.install(upgrade=True)
        # Starting Playwright
        if use_undetected_playwright:
            # (TODO: TEMP)
            self.playwright: Playwright = await undetected_async_playwright().start()  # type: ignore
        else:
            self.playwright = await async_playwright().start()

        # Getting Chromium based browser engine and deleting botright temp dirs
        self.browser = self.get_browser_engine()

        # Setting Values
        self.headless = headless
        self.block_images = block_images
        self.cache_responses = cache_responses
        self.scroll_into_view = scroll_into_view
        self.user_action_layer = user_action_layer
        self.mask_fingerprint = mask_fingerprint
        self.use_undetected_playwright = use_undetected_playwright
        self.cache: Dict[str, APIResponse] = {}

        # '--disable-gpu', '--incognito', '--disable-blink-features=AutomationControlled'
        # fmt: off
        self.flags = ['--incognito', '--accept-lang=en-US', '--lang=en-US', '--no-pings', '--mute-audio', '--no-first-run', '--no-default-browser-check', '--disable-cloud-import',
                      '--disable-gesture-typing', '--disable-offer-store-unmasked-wallet-cards', '--disable-offer-upload-credit-cards', '--disable-print-preview', '--disable-voice-input',
                      '--disable-wake-on-wifi', '--disable-cookie-encryption', '--ignore-gpu-blocklist', '--enable-async-dns', '--enable-simple-cache-backend', '--enable-tcp-fast-open',
                      '--prerender-from-omnibox=disabled', '--enable-web-bluetooth', '--disable-features=AudioServiceOutOfProcess,IsolateOrigins,site-per-process,TranslateUI,BlinkGenPropertyTrees',
                      '--aggressive-cache-discard', '--disable-extensions', '--disable-ipc-flooding-protection', '--disable-blink-features=AutomationControlled', '--test-type',
                      '--enable-features=NetworkService,NetworkServiceInProcess,TrustTokens,TrustTokensAlwaysAllowIssuance', '--disable-component-extensions-with-background-pages',
                      '--disable-default-apps', '--disable-breakpad', '--disable-component-update', '--disable-domain-reliability', '--disable-sync', '--disable-client-side-phishing-detection',
                      '--disable-hang-monitor', '--disable-popup-blocking', '--disable-prompt-on-repost', '--metrics-recording-only', '--safebrowsing-disable-auto-update', '--password-store=basic',
                      '--autoplay-policy=no-user-gesture-required', '--use-mock-keychain', '--force-webrtc-ip-handling-policy=disable_non_proxied_udp',
                      '--webrtc-ip-handling-policy=disable_non_proxied_udp', '--disable-session-crashed-bubble', '--disable-crash-reporter', '--disable-dev-shm-usage', '--force-color-profile=srgb',
                      '--disable-translate', '--disable-background-networking', '--disable-background-timer-throttling', '--disable-backgrounding-occluded-windows', '--disable-infobars',
                      '--hide-scrollbars', '--disable-renderer-backgrounding', '--font-render-hinting=none', '--disable-logging', '--enable-surface-synchronization',
                      '--run-all-compositor-stages-before-draw', '--disable-threaded-animation', '--disable-threaded-scrolling', '--disable-checker-imaging',
                      '--disable-new-content-rendering-timeout', '--disable-image-animation-resync', '--disable-partial-raster', '--blink-settings=primaryHoverType=2,availableHoverTypes=2,'
                      'primaryPointerType=4,availablePointerTypes=4', '--disable-layer-tree-host-memory-pressure']
        # fmt: on

        # Collecting items that can be stopped
        self.stoppable: List[Any] = []
        self.temp_dirs: List[TemporaryDirectory] = []  # type: ignore

        if spoof_canvas and self.mask_fingerprint:
            if self.browser["browser_type"] != "chromium":
                self.flags.append("--disable-reading-from-canvas")
            else:
                self.flags.append("--fingerprinting-canvas-image-data-noise")

        self.fingerprint_generator = AsyncFingerprintGenerator()

    async def new_browser(self, proxy: Optional[str] = None, **launch_arguments) -> BrowserContext:
        """
        Create a new Botright browser instance with specified configurations.

        Args:
            proxy (str, optional): Proxy server URL to use for the browser. Defaults to None.
            **launch_arguments: Additional launch arguments to the browser. See at `Playwright Docs <https://playwright.dev/python/docs/api/class-browsertype#browser-type-launch-persistent-context>`_.

        Returns:
            BrowserContext: A new browser context for web scraping or automation.
        """

        # Calling ProxyManager and Faker to get necessary information for Botright
        _proxy: ProxyManager = await ProxyManager(self, proxy)
        _faker: Faker = await Faker(self, _proxy)

        # Launching Main Browser
        if self.mask_fingerprint:
            flags = self.flags + [f"--user-agent={_faker.fingerprint.navigator.user_agent}"]
        else:
            flags = self.flags

        _browser = await browser.new_browser(self, _proxy, _faker, flags, **launch_arguments)
        _browser.proxy = _proxy
        _browser.faker = _faker
        _browser.user_action_layer = self.user_action_layer
        _browser.scroll_into_view = self.scroll_into_view
        _browser.mask_fingerprint = self.mask_fingerprint

        await _browser.grant_permissions(["notifications", "geolocation"])
        self.stoppable.append(_browser)

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

        for temp_dir in self.temp_dirs:
            if os.path.exists(temp_dir.name):
                try:
                    temp_dir.cleanup()
                except Exception:
                    pass

    @staticmethod
    def get_browser_engine() -> browsers.Browser:
        """
        Get the browser engine based on Chromium to use for Playwright based on system availability.
        If available, prefers Ungoogled Chromium for stealthier browsing.

        Returns:
            browsers.Browser: The selected browser engine.
        Raises:
            EnvironmentError: If no Chromium based browser is found on the system.
        """
        # Ungoogled Chromium preferred (most stealthy)
        if chromium := browsers.get("chromium"):
            return chromium
        print("\033[1;33;48m[WARNING] Ungoogled Chromium not found. Recommended for Canvas Manipulation. Download at https://ungoogled-software.github.io/ungoogled-chromium-binaries/ \033[0m")

        # Chrome preferred (much stealthier)
        if chrome := browsers.get("chrome"):
            return chrome

        not_supported = ["firefox", "msie", "opera", "msedge"]
        for browser_engine in browsers.browsers():
            if browser_engine["browser_type"] not in not_supported:
                return browser_engine

        raise EnvironmentError("No Chromium based browser found")
