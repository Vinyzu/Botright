from __future__ import annotations

import sys
import inspect
from tempfile import TemporaryDirectory
from typing import Optional, Pattern, Callable, Any, List, Dict, Union, TYPE_CHECKING, TypedDict

# from undetected_playwright._impl._async_base import AsyncEventContextManager
# from undetected_playwright.async_api import BrowserContext as PlaywrightBrowserContext, \
#     Route as PlaywrightRoute, \
#     Request as PlaywrightRequest, \
#     ConsoleMessage as PlaywrightConsoleMessage  # , \
from playwright._impl._async_base import AsyncEventContextManager
from playwright.async_api import BrowserContext as PlaywrightBrowserContext, \
    Page as PlaywrightPage, \
    Frame as PlaywrightFrame, \
    ElementHandle as PlaywrightElementHandle, \
    Route as PlaywrightRoute, \
    Request as PlaywrightRequest, \
    ConsoleMessage as PlaywrightConsoleMessage, \
    APIResponse


from ..modules import ProxyManager, Faker
from . import new_page, Page, Route, Request, Frame, JSHandle, ElementHandle

if TYPE_CHECKING:
    from botright import Botright


async def new_browser(botright: Botright, proxy: ProxyManager, faker: Faker, flags: List[str], **launch_arguments) -> BrowserContext:
    """
    Create a new browser context with custom configurations.

    Args:
        botright (Botright): The Botright Instance from the main thread.
        proxy (ProxyManager): An instance of ProxyManager for configuring proxy settings.
        faker (Faker): An instance of Faker for generating fake user agent and other details.
        flags (List[str]): The command line flags to pass into the Browser Instance.
        # browser_path (str): The path to the real browser executable.
        # headless (bool, optional): Whether to run the browser in headless mode. Defaults to False.
        # mask_fingerprint (bool, optional): Whether to mask the browser fingerprint. Defaults to True.
        # user_action_layer (bool, optional): Whether to enable user action simulation layer. Defaults to False.
        # scroll_into_view (bool, optional): Whether to scroll elements into view automatically. Defaults to True.
        **launch_arguments: Additional launch arguments for configuring the browser context. See https://playwright.dev/python/docs/api/class-browser#browser-new-context.

    Returns:
        BrowserContext: A new browser context with the specified configurations.
    """
    if botright.mask_fingerprint:
        fingerprint = faker.fingerprint
        parsed_launch_arguments = {"locale": "en-US",  "user_agent": fingerprint.navigator.user_agent,
                                   "timezone_id": proxy.timezone, "geolocation": {"longitude": proxy.longitude, "latitude": proxy.latitude, "accuracy": 0.7},
                                   "permissions": ["geolocation"], "ignore_https_errors": True,
                                   "screen": {"width": fingerprint.screen.width, "height": fingerprint.screen.height},
                                   "viewport": {"width": fingerprint.screen.avail_width, "height": fingerprint.screen.avail_height},
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

    if sys.version_info.minor >= 10:
        temp_dir = TemporaryDirectory(prefix="botright-", ignore_cleanup_errors=True)
    else:
        temp_dir = TemporaryDirectory(prefix="botright-")
    temp_dir_path = temp_dir.name
    botright.temp_dirs.append(temp_dir)

    # Spawning a new Context for more options
    if proxy.browser_proxy:
        _browser = await botright.playwright.chromium.launch_persistent_context(user_data_dir=temp_dir_path, headless=botright.headless, executable_path=botright.browser["path"], args=flags,
                                                                                **parsed_launch_arguments)
    else:
        _browser = await botright.playwright.chromium.launch_persistent_context(user_data_dir=temp_dir_path, headless=botright.headless, executable_path=botright.browser["path"], args=flags,
                                                                                **parsed_launch_arguments)

    browser = BrowserContext(_browser, proxy, faker, use_undetected_playwright=botright.use_undetected_playwright, cache=botright.cache,
                             user_action_layer=botright.user_action_layer, mask_fingerprint=botright.mask_fingerprint, scroll_into_view=botright.scroll_into_view)

    # Preprocessing to save computing resources
    if botright.block_images:
        await browser.block_images()

    if botright.cache_responses:
        await browser.cache_responses()

    return browser


class BrowserContext(PlaywrightBrowserContext):
    def __init__(self, browser: PlaywrightBrowserContext, proxy: ProxyManager, faker: Faker, use_undetected_playwright: Optional[bool], cache: Dict[str, APIResponse],
                 user_action_layer: Optional[bool], scroll_into_view: Optional[bool], mask_fingerprint: Optional[bool]):
        super().__init__(browser)
        self._impl_obj = browser._impl_obj
        self._browser = browser
        self._closed = False
        self._route_proxies: Dict[Union[Callable[[PlaywrightRoute], Any], Callable[[PlaywrightRoute, PlaywrightRequest], Any]],
                                  Union[Callable[[PlaywrightRoute], Any], Callable[[PlaywrightRoute, PlaywrightRequest], Any]]] = {}

        self.proxy = proxy
        self.faker = faker
        self.use_undetected_playwright = use_undetected_playwright

        self.cache = cache
        self.user_action_layer = user_action_layer
        self.scroll_into_view = scroll_into_view
        self.mask_fingerprint = mask_fingerprint

        self._origin_new_page = browser.new_page
        self._origin_close = browser.close
        self._origin_route = browser.route
        self._origin_unroute = browser.unroute
        self._origin_expect_console_message = browser.expect_console_message
        self._origin_expose_function = browser.expose_function
        self._origin_expose_binding = browser.expose_binding

        # Setting first page to be closed as it's the first empty about:blank page of the Persistent Context
        self.persistent_page = self.pages[0]

    def __eq__(self, obj):
        if isinstance(obj, BrowserContext):
            if (obj._browser == self._browser) and (obj.proxy == self.proxy) and (obj.faker == self.faker):
                return True
        return False

    @property
    def pages(self):
        if self._closed:
            return []

        pages: List[Page] = []
        for _page in self._browser.pages:
            page = Page(_page, self, self.faker)
            pages.append(page)
        return pages

    async def cache_responses(self):
        async def route_interceptor(route: PlaywrightRoute):
            request = route.request

            if request.resource_type in ("document", "stylesheet", "image", "media", "font", "manifest"):
                if request.url not in self.cache:
                    response = await route.fetch()
                    self.cache[request.url] = response
                else:
                    response = self.cache[request.url]
                await route.fulfill(response=response)
            else:
                await route.continue_()

        await self.route("**", route_interceptor)

    async def block_images(self):
        async def all_blocker(route: PlaywrightRoute):
            await route.abort(error_code="aborted")

        async def image_blocker(route: PlaywrightRoute):
            if route.request.resource_type == "image":
                await route.abort(error_code="aborted")
            else:
                await route.continue_()

        await self.route("**/*.{apng,avif,gif,jpg,jpeg,jfif,pjpeg,pjp,png,svg,webp}", all_blocker)
        await self.route("**", image_blocker)

    async def new_page(self, **launch_arguments) -> Page:
        """
        Args:
            **launch_arguments: Dont use! PlaywrightBrowserContext.new_page() doesn't take any args. Only used to prevent errors.

        Returns:
            Page: A new Page instance.
        """
        page = await new_page(self, self.faker)

        # Close first page it's the first empty about:blank page of the Persistent Context
        if not self.persistent_page.is_closed():
            await self.persistent_page.close()

        return page

    async def close(self, reason: Optional[str] = None):
        self._closed = True
        return await self._origin_close(reason=reason)

    async def route(self, url: Union[str, Pattern[str], Callable[[str], bool]], handler: Union[Callable[[PlaywrightRoute], Any], Callable[[PlaywrightRoute, PlaywrightRequest], Any]],
                    times: Optional[int] = None):
        if len(inspect.signature(handler).parameters) == 2:  # Checking how many parameters the callable expects
            def handler_proxy(route: PlaywrightRoute, request: PlaywrightRequest):
                page = request.frame.page

                route = Route(route, Page(page, self, self.faker))
                request = Request(request, Page(page, self, self.faker))
                return handler(route, request)  # type: ignore

            self._route_proxies[handler] = handler_proxy
            await self._origin_route(url=url, handler=handler_proxy, times=times)
        else:
            def handler_proxy_no_request(route: PlaywrightRoute):
                page = route.request.frame.page

                route = Route(route, Page(page, self, self.faker))
                return handler(route)  # type: ignore

            self._route_proxies[handler] = handler_proxy_no_request
            await self._origin_route(url=url, handler=handler_proxy_no_request, times=times)

    async def unroute(self, url: Union[str, Pattern[str], Callable[[str], bool]],
                      handler: Optional[Union[Callable[[PlaywrightRoute], Any], Callable[[PlaywrightRoute, PlaywrightRequest], Any]]] = None):
        if handler:
            handler_proxy = self._route_proxies[handler]
            await self._origin_unroute(url=url, handler=handler_proxy)

        await self._origin_unroute(url=url, handler=None)

    def expect_console_message(self, predicate: Optional[Callable[..., bool]] = None, timeout: Optional[float] = None) -> AsyncEventContextManager[PlaywrightConsoleMessage]:
        if self.use_undetected_playwright:
            from botright.extended_typing import NotSupportedError
            raise NotSupportedError("BrowserContext.expect_console_message is currently unsupported, due to CDP Runtime Patches.")

        return self._origin_expect_console_message(predicate=predicate, timeout=timeout)

    async def expose_function(self, name: str, callback: Callable[..., None]) -> None:
        if self.use_undetected_playwright:
            from botright.extended_typing import NotSupportedError
            raise NotSupportedError("BrowserContext.expose_function is currently unsupported, due to CDP Runtime Patches.")

        return await self._origin_expose_function(name=name, callback=callback)

    async def expose_binding(self, name: str, callback: Callable[..., None], handle: Optional[bool] = None):
        if self.use_undetected_playwright:
            from botright.extended_typing import NotSupportedError
            raise NotSupportedError("BrowserContext.expose_binding is currently unsupported, due to CDP Runtime Patches.")

        class SourceDict(TypedDict):
            context: PlaywrightBrowserContext
            page: PlaywrightPage
            frame: PlaywrightFrame

        if handle:
            def callback_proxy_handle(source: SourceDict, element: Any):
                _context: PlaywrightBrowserContext = source["context"]
                _page: PlaywrightPage = source["page"]
                _frame: PlaywrightFrame = source["frame"]

                context = BrowserContext(_context, self.proxy, self.faker, use_undetected_playwright=self.use_undetected_playwright, cache=self.cache,
                                         user_action_layer=self.user_action_layer, scroll_into_view=self.scroll_into_view, mask_fingerprint=self.mask_fingerprint)
                page = Page(_page, self, self.faker)
                frame = Frame(_frame, page)

                source["context"], source["page"], source["frame"] = context, page, frame

                if isinstance(element, PlaywrightElementHandle):
                    element = ElementHandle(element, page)
                else:
                    element = JSHandle(element, page)

                return callback(source, element)

            await self._origin_expose_binding(name, callback_proxy_handle, handle=handle)

        else:
            def callback_proxy(source: SourceDict, *args, **kwargs):
                _context: PlaywrightBrowserContext = source["context"]
                _page: PlaywrightPage = source["page"]
                _frame: PlaywrightFrame = source["frame"]

                context = BrowserContext(_context, self.proxy, self.faker, use_undetected_playwright=self.use_undetected_playwright, cache=self.cache,
                                         user_action_layer=self.user_action_layer, scroll_into_view=self.scroll_into_view, mask_fingerprint=self.mask_fingerprint)
                page = Page(_page, self, self.faker)
                frame = Frame(_frame, page)

                source["context"], source["page"], source["frame"] = context, page, frame

                return callback(source, *args, **kwargs)

            await self._origin_expose_binding(name=name, callback=callback_proxy, handle=handle)
