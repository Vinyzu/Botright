from __future__ import annotations

import inspect
from pathlib import Path
from re import Pattern
from typing import TYPE_CHECKING, Any, Callable, List, Literal, Optional, Sequence, TypedDict, Union

# fmt: off
from playwright._impl._async_base import AsyncEventContextManager
# from undetected_playwright._impl._impl_to_api_mapping import ImplToApiMapping
# from undetected_playwright._impl._async_base import AsyncEventContextManager
# from undetected_playwright.async_api import Position, \
#     Locator as PlaywrightLocator, \
#     Page as PlaywrightPage, \
#     CDPSession as PlaywrightCDPSession, \
#     ElementHandle as PlaywrightElementHandle, \
#     Error as PlaywrightError, \
#     Route as PlaywrightRoute, \
#     Request as PlaywrightRequest, \
#     ConsoleMessage as PlaywrightConsoleMessage, \
#     Worker as PlaywrightWorker
from playwright._impl._impl_to_api_mapping import ImplToApiMapping
from playwright.async_api import BrowserContext as PlaywrightBrowserContext
from playwright.async_api import CDPSession as PlaywrightCDPSession
from playwright.async_api import ConsoleMessage as PlaywrightConsoleMessage
from playwright.async_api import ElementHandle as PlaywrightElementHandle
from playwright.async_api import Error as PlaywrightError
from playwright.async_api import Frame as PlaywrightFrame
from playwright.async_api import Locator as PlaywrightLocator
from playwright.async_api import Page as PlaywrightPage
from playwright.async_api import Position
from playwright.async_api import Request as PlaywrightRequest
from playwright.async_api import Route as PlaywrightRoute
from playwright.async_api import Worker as PlaywrightWorker
from recognizer.agents.playwright import AsyncChallenger

from botright.modules import Faker, hcaptcha  # , geetest

# fmt: on

if TYPE_CHECKING:
    from .browser import BrowserContext

from . import ElementHandle, Frame, FrameLocator, JSHandle, Keyboard, Locator, Mouse, Request, Route

mapping = ImplToApiMapping()

# fmt: off
role_type = Literal['alert', 'alertdialog', 'application', 'article', 'banner', 'blockquote', 'button', 'caption', 'cell', 'checkbox', 'code', 'columnheader', 'combobox', 'complementary',
                    'contentinfo', 'definition', 'deletion', 'dialog', 'directory', 'document', 'emphasis', 'feed', 'figure', 'form', 'generic', 'grid', 'gridcell', 'group', 'heading', 'img',
                    'insertion', 'link', 'list', 'listbox', 'listitem', 'log', 'main', 'marquee', 'math', 'menu', 'menubar', 'menuitem', 'menuitemcheckbox', 'menuitemradio', 'meter', 'navigation',
                    'none', 'note', 'option', 'paragraph', 'presentation', 'progressbar', 'radio', 'radiogroup', 'region', 'row', 'rowgroup', 'rowheader', 'scrollbar', 'search', 'searchbox',
                    'separator', 'slider', 'spinbutton', 'status', 'strong', 'subscript', 'superscript', 'switch', 'tab', 'table', 'tablist', 'tabpanel', 'term', 'textbox', 'time', 'timer', 'toolbar',
                    'tooltip', 'tree', 'treegrid', 'treeitem']
# fmt: on


async def new_page(browser: BrowserContext, faker: Faker) -> Page:
    """
    Create a new Playwright Page instance with custom configurations and features.

    Args:
        browser (BrowserContext): The parent browser context for the new page.
        faker (Faker): An instance of Faker for generating fake user agent and other details.

    Returns:
        Page: A new Playwright Page instance with customized settings.
    """
    # Create new Page
    _page = await browser._origin_new_page()
    page = Page(_page, browser, faker)
    await page._mock_page()

    return page


class Page(PlaywrightPage):
    def __init__(self, page: PlaywrightPage, browser: BrowserContext, faker: Faker):
        super().__init__(page)
        self._impl_obj = page._impl_obj
        self._page = page

        # Properties
        self.browser = browser
        self.faker = faker
        self.fingerprint = faker.fingerprint
        self.scroll_into_view: Optional[bool] = browser.scroll_into_view
        self._main_frame = page.main_frame

        # Objects
        if isinstance(page.mouse, Mouse):
            self._mouse = page.mouse
        else:
            self._mouse = Mouse(page.mouse, self)
        if isinstance(page.keyboard, Keyboard):
            self._keyboard = page.keyboard
        else:
            self._keyboard = Keyboard(page.keyboard, self)
        self.cdp: Optional[PlaywrightCDPSession] = None
        self.hcaptcha_solver = hcaptcha.hCaptcha(browser, self)
        self.recaptcha_solver = AsyncChallenger(self)

        # Aliases
        self._origin_close = page.close
        self._origin_opener = page.opener
        self._origin_frame = page.frame

        self._origin_query_selector = page.query_selector
        self._origin_query_selector_all = page.query_selector_all
        self._origin_wait_for_selector = page.wait_for_selector
        self._origin_add_script_tag = page.add_script_tag
        self._origin_add_style_tag = page.add_style_tag

        self._origin_locator = page.locator
        self._origin_get_by_alt_text = page.get_by_alt_text
        self._origin_get_by_label = page.get_by_label
        self._origin_get_by_placeholder = page.get_by_placeholder
        self._origin_get_by_role = page.get_by_role
        self._origin_get_by_test_id = page.get_by_test_id
        self._origin_get_by_text = page.get_by_text
        self._origin_get_by_title = page.get_by_title

        self._origin_evaluate_handle = page.evaluate_handle
        self._origin_wait_for_function = page.wait_for_function
        self._origin_frame_locator = page.frame_locator

        self._origin_expect_console_message = page.expect_console_message
        self._origin_expect_worker = page.expect_worker
        self._origin_expose_function = page.expose_function
        self._origin_expose_binding = page.expose_binding
        self._origin_route = page.route

    def __eq__(self, obj):
        if isinstance(obj, Page):
            if (obj._page == self._page) and (obj.browser == self.browser) and (obj.faker == self.faker):
                return True
        return False

    @property
    def context(self):
        return self.browser

    @property
    def mouse(self):
        return self._mouse

    @property
    def keyboard(self):
        return self._keyboard

    @property
    def main_frame(self):
        return Frame(self._main_frame, self)

    @property
    def frames(self):
        _frames = []
        for frame in self._page.frames:
            _frames.append(Frame(frame, self))
        return _frames

    async def _mock_page(self):
        # Opening CDP Session
        self.cdp = await self.browser.new_cdp_session(self)

        nav_hints_platforms = {"Windows": "Win32", "macOS": "MacIntel", "Linux": "Linux x86_64"}

        if self.browser.mask_fingerprint:
            user_agent_metadata = {
                "brands": self.fingerprint.navigator.brands,
                "fullVersionList": self.fingerprint.navigator.full_version_list,
                "fullVersion": self.fingerprint.navigator.full_version,
                "platform": self.fingerprint.navigator.platform.name,
                "architecture": self.fingerprint.navigator.platform.architecture,
                "bitness": self.fingerprint.navigator.platform.bitness,
                "platformVersion": self.fingerprint.navigator.platform.version,
                "model": self.fingerprint.navigator.platform.model,
                "mobile": False,
            }

            await self.cdp.send(
                "Emulation.setUserAgentOverride",
                {
                    "userAgent": self.fingerprint.navigator.user_agent,
                    "acceptLanguage": "en-US",
                    "platform": nav_hints_platforms.get(self.fingerprint.navigator.platform.name, self.fingerprint.navigator.platform.name),
                    "userAgentMetadata": user_agent_metadata,
                },
            )

            await self.cdp.send(
                "Network.setUserAgentOverride",
                {
                    "userAgent": self.fingerprint.navigator.user_agent,
                    "acceptLanguage": "en-US",
                    "platform": nav_hints_platforms.get(self.fingerprint.navigator.platform.name, self.fingerprint.navigator.platform.name),
                    "userAgentMetadata": user_agent_metadata,
                },
            )

        # Source: https://github.com/kkoooqq/fakebrowser/blob/main/src/plugins/user-action-layer/index.js
        if self.browser.user_action_layer:
            await self.add_init_script(
                'window.addEventListener("DOMContentLoaded",()=>{let e=document.createElement("canvas");e.width=window.innerWidth,e.height=window.innerHeight,e.style.userSelect="none",'
                'e.style.pointerEvents="none",e.style.position="fixed",e.style.left="0px",e.style.top="0px",e.style.width=""+window.innerWidth+"px",e.style.height=""+window.innerHeight+"px",'
                'e.style.zIndex="999999",document.body.appendChild(e);let t=e.getContext("2d");document.addEventListener("keydown",e=>{}),document.addEventListener("keyup",e=>{}),'
                'document.addEventListener("mousemove",e=>{t.beginPath(),t.arc(e.clientX,e.clientY,3,0,360,!1),t.fillStyle="green",t.fill(),t.closePath()}),'
                'document.addEventListener("mousedown",e=>{t.beginPath(),t.arc(e.clientX,e.clientY,15,0,360,!1),t.fillStyle="black",t.fill(),t.closePath()}),'
                'document.addEventListener("mouseup",e=>{t.beginPath(),t.arc(e.clientX,e.clientY,9,0,360,!1),t.fillStyle="blue",t.fill(),t.closePath()})});'
            )

    async def solve_hcaptcha(self, rq_data: Optional[str] = None) -> Optional[str]:
        """
        Mocks solving an hCaptcha challenge on a page.

        Args:
            rq_data (Optional[str]): Additional request data for solving the challenge.

        Returns:
            Optional[str]: The hCaptcha token if the challenge is solved successfully, otherwise None.
        """
        return await self.hcaptcha_solver.solve_hcaptcha(rq_data=rq_data)

    async def get_hcaptcha(self, site_key: Optional[str] = "00000000-0000-0000-0000-000000000000", rq_data: Optional[str] = None) -> Optional[str]:
        """
        Get a hCaptcha Key with Sitekey & rqData

        Args:
            site_key (Optional[str]): The hCaptcha site key to use.
            rq_data (Optional[str]): Additional request data for the challenge.

        Returns:
            Optional[str]: The hCaptcha token if the challenge is retrieved successfully, otherwise None.
        """
        return await self.hcaptcha_solver.get_hcaptcha(site_key=site_key, rq_data=rq_data)

    async def solve_geetest(self, mode: Optional[str] = "canny") -> str:
        """
        Mocks solving a Geetest challenge on a page.

        Args:
            mode (Optional[str]): The Geetest challenge mode to use.

        Returns:
            str: The result of solving the Geetest challenge.
        """
        # return await geetest.solve_geetest(self, mode=mode)
        raise NotImplementedError("Geetest challenge currently unavailable!")

    async def solve_recaptcha(self) -> Union[str, bool]:
        """
        Mocks solving a ReCaptcha challenge on a page.

        Returns:
            Union[str, bool]: The ReCaptcha token if the challenge is solved successfully, otherwise None.
        """
        result: Union[str, bool] = await self.recaptcha_solver.solve_recaptcha()
        return result

    visual_recaptcha = solve_recaptcha

    async def close(self, run_before_unload: Optional[bool] = None, reason: Optional[str] = None):
        await self._origin_close(run_before_unload=run_before_unload, reason=reason)

        if self in self.browser.pages:
            self.browser.pages.remove(self)

    async def opener(self):
        _page = await self._origin_opener()
        if not _page:
            return None

        page = Page(_page, self.browser, self.faker)
        return page

    def frame(self, name: Optional[str] = None, *, url: Optional[Union[str, Pattern[str], Callable[[str], bool]]] = None) -> Optional[Frame]:
        _frame = self._origin_frame(name=name, url=url)
        if not _frame:
            return None

        frame = Frame(_frame, self)
        return frame

    # ElementHandle
    async def query_selector(self, selector: str, strict: Optional[bool] = False) -> Optional[ElementHandle]:
        _element_handle = await self._origin_query_selector(selector=selector, strict=strict)
        if not _element_handle:
            return None

        element_handle = ElementHandle(_element_handle, self)
        return element_handle

    async def query_selector_all(self, selector: str) -> List[ElementHandle]:  # type: ignore
        _element_handles = await self._origin_query_selector_all(selector=selector)
        element_handles = []

        for _element_handle in _element_handles:
            element_handle = ElementHandle(_element_handle, self)
            element_handles.append(element_handle)
        return element_handles

    async def wait_for_selector(
        self, selector: str, state: Optional[Literal["attached", "detached", "hidden", "visible"]] = None, strict: Optional[bool] = False, timeout: Optional[float] = None
    ) -> Optional[ElementHandle]:
        _element_handle = await self._origin_wait_for_selector(selector=selector, state=state, strict=strict, timeout=timeout)
        if not _element_handle:
            return None

        element_handle = ElementHandle(_element_handle, self)
        return element_handle

    async def add_script_tag(self, content: Optional[str] = None, path: Optional[Union[str, Path]] = None, type: Optional[str] = None, url: Optional[str] = None) -> ElementHandle:
        _element_handle = await self._origin_add_script_tag(content=content, path=path, type=type, url=url)
        element_handle = ElementHandle(_element_handle, self)
        return element_handle

    async def add_style_tag(self, content: Optional[str] = None, path: Optional[Union[str, Path]] = None, url: Optional[str] = None) -> ElementHandle:
        _element_handle = await self._origin_add_style_tag(content=content, path=path, url=url)
        element_handle = ElementHandle(_element_handle, self)
        return element_handle

    # Locator
    def locator(
        self,
        selector: str,
        has: Optional[PlaywrightLocator] = None,
        has_not: Optional[PlaywrightLocator] = None,
        has_text: Optional[Union[str, Pattern[str]]] = None,
        has_not_text: Optional[Union[str, Pattern[str]]] = None,
    ) -> Locator:
        _locator = self._origin_locator(selector=selector, has=has, has_not=has_not, has_text=has_text, has_not_text=has_not_text)
        locator = Locator(_locator, self)
        return locator

    def get_by_alt_text(self, text: Union[str, Pattern[str]], exact: Optional[bool] = False) -> Locator:
        _locator = self._origin_get_by_alt_text(text=text, exact=exact)
        locator = Locator(_locator, self)
        return locator

    def get_by_label(self, text: Union[str, Pattern[str]], exact: Optional[bool] = False) -> Locator:
        _locator = self._origin_get_by_label(text=text, exact=exact)
        locator = Locator(_locator, self)
        return locator

    def get_by_placeholder(self, text: Union[str, Pattern[str]], exact: Optional[bool] = False) -> Locator:
        _locator = self._origin_get_by_placeholder(text=text, exact=exact)
        locator = Locator(_locator, self)
        return locator

    def get_by_role(
        self,
        role: role_type,
        checked: Optional[bool] = None,
        disabled: Optional[bool] = None,
        expanded: Optional[bool] = None,
        include_hidden: Optional[bool] = None,
        level: Optional[int] = None,
        name: Optional[Union[str, Pattern[str]]] = None,
        pressed: Optional[bool] = None,
        selected: Optional[bool] = None,
        exact: Optional[bool] = None,
    ) -> Locator:
        _locator = self._origin_get_by_role(
            role=role, checked=checked, disabled=disabled, expanded=expanded, include_hidden=include_hidden, level=level, name=name, pressed=pressed, selected=selected, exact=exact
        )

        locator = Locator(_locator, self)
        return locator

    def get_by_test_id(self, test_id: Union[str, Pattern[str]]) -> Locator:
        _locator = self._origin_get_by_test_id(test_id=test_id)
        locator = Locator(_locator, self)
        return locator

    def get_by_text(self, text: Union[str, Pattern[str]], exact: Optional[bool] = False) -> Locator:
        _locator = self._origin_get_by_text(text=text, exact=exact)
        locator = Locator(_locator, self)
        return locator

    def get_by_title(self, text: Union[str, Pattern[str]], exact: Optional[bool] = False) -> Locator:
        _locator = self._origin_get_by_title(text=text, exact=exact)
        locator = Locator(_locator, self)
        return locator

    # JsHandle
    async def evaluate_handle(self, expression: str, arg: Optional[Any] = None) -> Union[JSHandle, ElementHandle]:
        _js_handle = await self._origin_evaluate_handle(expression=expression, arg=arg)

        if isinstance(_js_handle, PlaywrightElementHandle):
            element_handle = ElementHandle(_js_handle, self)
            return element_handle
        else:
            js_handle = JSHandle(_js_handle, self)
            return js_handle

    async def wait_for_function(self, expression: str, arg: Optional[Any] = None, polling: Optional[Union[float, Literal["raf"]]] = "raf", timeout: Optional[float] = None) -> JSHandle:
        from . import JSHandle

        _js_handle = await self._origin_wait_for_function(expression=expression, arg=arg, polling=polling, timeout=timeout)
        js_handle = JSHandle(_js_handle, self)
        return js_handle

    # FrameLocator
    def frame_locator(self, selector: str) -> FrameLocator:
        from . import FrameLocator

        _frame_locator = self._origin_frame_locator(selector=selector)
        frame_locator = FrameLocator(_frame_locator, self)
        return frame_locator

    def expect_console_message(self, predicate: Optional[Callable[..., bool]] = None, timeout: Optional[float] = None) -> AsyncEventContextManager[PlaywrightConsoleMessage]:
        if self.browser.use_undetected_playwright:
            from botright.extended_typing import NotSupportedError

            raise NotSupportedError("Page.expect_console_message is currently unsupported, due to CDP Runtime Patches.")

        return self._origin_expect_console_message(predicate=predicate, timeout=timeout)

    def expect_worker(self, predicate: Optional[Callable[..., bool]] = None, timeout: Optional[float] = None) -> AsyncEventContextManager[PlaywrightWorker]:
        if self.browser.use_undetected_playwright:
            from botright.extended_typing import NotSupportedError

            raise NotSupportedError("Page.expect_worker is currently unsupported, due to CDP Runtime Patches.")

        return self._origin_expect_worker(predicate=predicate, timeout=timeout)

    async def expose_function(self, name: str, callback: Callable[..., None]) -> None:
        if self.browser.use_undetected_playwright:
            from botright.extended_typing import NotSupportedError

            raise NotSupportedError("Page.expose_function is currently unsupported, due to CDP Runtime Patches.")

        return await self._origin_expose_function(name=name, callback=callback)

    async def expose_binding(self, name: str, callback: Callable[..., None], handle: Optional[bool] = None):
        if self.browser.use_undetected_playwright:
            from botright.extended_typing import NotSupportedError

            raise NotSupportedError("Page.expose_binding is currently unsupported, due to CDP Runtime Patches.")

        from .browser import BrowserContext

        class SourceDict(TypedDict):
            context: PlaywrightBrowserContext
            page: PlaywrightPage
            frame: PlaywrightFrame

        if handle:

            def callback_proxy_handle(source: SourceDict, element: Any):
                _context: PlaywrightBrowserContext = source["context"]
                _page: PlaywrightPage = source["page"]
                _frame: PlaywrightFrame = source["frame"]

                source["context"] = BrowserContext(
                    _context,
                    self.browser.proxy,
                    self.browser.faker,
                    use_undetected_playwright=self.browser.use_undetected_playwright,
                    cache=self.browser.cache,
                    user_action_layer=self.browser.user_action_layer,
                    scroll_into_view=self.scroll_into_view,
                    mask_fingerprint=self.browser.mask_fingerprint,
                )
                source["page"] = Page(_page, self.browser, self.faker)
                source["frame"] = Frame(_frame, self)

                if isinstance(element, PlaywrightElementHandle):
                    element = ElementHandle(element, self)
                else:
                    element = JSHandle(element, self)

                return callback(source, element)

            await self._origin_expose_binding(name, callback_proxy_handle, handle=handle)

        else:

            def callback_proxy(source: SourceDict, *args, **kwargs):
                _context: PlaywrightBrowserContext = source["context"]
                _page: PlaywrightPage = source["page"]
                _frame: PlaywrightFrame = source["frame"]

                source["context"] = BrowserContext(
                    _context,
                    self.browser.proxy,
                    self.browser.faker,
                    use_undetected_playwright=self.browser.use_undetected_playwright,
                    cache=self.browser.cache,
                    user_action_layer=self.browser.user_action_layer,
                    scroll_into_view=self.scroll_into_view,
                    mask_fingerprint=self.browser.mask_fingerprint,
                )
                source["page"] = Page(_page, self.browser, self.faker)
                source["frame"] = Frame(_frame, self)

                return callback(source, *args, **kwargs)

            await self._origin_expose_binding(name=name, callback=callback_proxy, handle=handle)

    async def route(
        self, url: Union[str, Pattern[str], Callable[[str], bool]], handler: Union[Callable[[Route], Any], Callable[[PlaywrightRoute, PlaywrightRequest], Any]], times: Optional[int] = None
    ):
        if len(inspect.signature(handler).parameters) == 2:  # Checking how many parameters the callable expects

            def handler_proxy(route: PlaywrightRoute, request: PlaywrightRequest):
                route = Route(route, Page(self, self.browser, self.faker))
                request = Request(request, Page(self, self.browser, self.faker))
                return handler(route, request)  # type: ignore

            await self._origin_route(url=url, handler=handler_proxy, times=times)
        else:

            def handler_proxy_no_request(route: PlaywrightRoute):
                route = Route(route, Page(self, self.browser, self.faker))
                return handler(route)  # type: ignore

            await self._origin_route(url=url, handler=handler_proxy_no_request, times=times)

    # Custom Methods
    async def click(
        self,
        selector: str,
        button: Optional[Literal["left", "middle", "right"]] = "left",
        click_count: Optional[int] = 1,
        strict: Optional[bool] = False,
        delay: Optional[float] = 20.0,
        force: Optional[bool] = False,
        modifiers: Optional[Sequence[Literal["Alt", "Control", "Meta", "Shift"]]] = None,
        no_wait_after: Optional[bool] = False,
        position: Optional[Position] = None,
        timeout: Optional[float] = None,
        trial: Optional[bool] = False,
    ) -> None:
        modifiers = modifiers or []
        position = position or Position(x=0, y=0)

        element = await self.wait_for_selector(selector, state="visible" if not force else "hidden", strict=strict, timeout=timeout)
        if not element:
            raise PlaywrightError("Element is not attached to the DOM")

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if not trial:
            bounding_box = await element.bounding_box()
            if not bounding_box:
                raise PlaywrightError("Element is not visible")

            # await element.scroll_into_view_if_needed(timeout=timeout)

            x, y, width, height = bounding_box["x"], bounding_box["y"], bounding_box["width"], bounding_box["height"]
            if not any(position.values()):
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            for modifier in modifiers:
                await self.keyboard.down(modifier)

            await self.mouse.click(x, y, button=button, click_count=click_count, delay=delay)

            for modifier in modifiers:
                await self.keyboard.up(modifier)

    async def dblclick(
        self,
        selector: str,
        button: Optional[Literal["left", "middle", "right"]] = "left",
        strict: Optional[bool] = False,
        delay: Optional[float] = 20.0,
        force: Optional[bool] = False,
        modifiers: Optional[Sequence[Literal["Alt", "Control", "Meta", "Shift"]]] = None,
        no_wait_after: Optional[bool] = False,
        position: Optional[Position] = None,
        timeout: Optional[float] = None,
        trial: Optional[bool] = False,
    ) -> None:
        modifiers = modifiers or []
        position = position or Position(x=0, y=0)

        element = await self.wait_for_selector(selector, state="visible" if not force else "hidden", strict=strict, timeout=timeout)
        if not element:
            raise PlaywrightError("Element is not attached to the DOM")

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if not trial:
            bounding_box = await element.bounding_box()
            if not bounding_box:
                raise PlaywrightError("Element is not visible")

            # await element.scroll_into_view_if_needed(timeout=timeout)

            x, y, width, height = bounding_box["x"], bounding_box["y"], bounding_box["width"], bounding_box["height"]
            if not any(position.values()):
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            for modifier in modifiers:
                await self.keyboard.down(modifier)

            await self.mouse.dblclick(x, y, button=button, delay=delay)

            for modifier in modifiers:
                await self.keyboard.up(modifier)

    async def check(
        self,
        selector: str,
        force: Optional[bool] = False,
        no_wait_after: Optional[bool] = False,
        position: Optional[Position] = None,
        strict: Optional[bool] = False,
        timeout: Optional[float] = None,
        trial: Optional[bool] = False,
    ) -> None:
        position = position or Position(x=0, y=0)

        element = await self.wait_for_selector(selector, state="visible" if not force else "hidden", strict=strict, timeout=timeout)
        if not element:
            raise PlaywrightError("Element is not attached to the DOM")

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if await element.is_checked():
            return

        if not trial:
            bounding_box = await element.bounding_box()
            if not bounding_box:
                raise PlaywrightError("Element is not visible")

            # await element.scroll_into_view_if_needed(timeout=timeout)

            x, y, width, height = bounding_box["x"], bounding_box["y"], bounding_box["width"], bounding_box["height"]
            if not any(position.values()):
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await self.mouse.click(x, y, button="left", click_count=1, delay=20)

            assert await element.is_checked(), PlaywrightError

    async def uncheck(
        self,
        selector: str,
        force: Optional[bool] = False,
        no_wait_after: Optional[bool] = False,
        position: Optional[Position] = None,
        strict: Optional[bool] = False,
        timeout: Optional[float] = None,
        trial: Optional[bool] = False,
    ) -> None:
        position = position or Position(x=0, y=0)

        element = await self.wait_for_selector(selector, state="visible" if not force else "hidden", strict=strict, timeout=timeout)
        if not element:
            raise PlaywrightError("Element is not attached to the DOM")

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if not await element.is_checked():
            return

        if not trial:
            bounding_box = await element.bounding_box()
            if not bounding_box:
                raise PlaywrightError("Element is not visible")

            # await element.scroll_into_view_if_needed(timeout=timeout)

            x, y, width, height = bounding_box["x"], bounding_box["y"], bounding_box["width"], bounding_box["height"]
            if not any(position.values()):
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await self.mouse.click(x, y, button="left", click_count=1, delay=20)

            assert not await element.is_checked()

    async def set_checked(
        self,
        selector: str,
        checked: Optional[bool] = False,
        force: Optional[bool] = False,
        no_wait_after: Optional[bool] = False,
        position: Optional[Position] = None,
        strict: Optional[bool] = False,
        timeout: Optional[float] = None,
        trial: Optional[bool] = False,
    ) -> None:
        position = position or Position(x=0, y=0)

        element = await self.wait_for_selector(selector, state="visible" if not force else "hidden", strict=strict, timeout=timeout)
        if not element:
            raise PlaywrightError("Element is not attached to the DOM")

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if await element.is_checked() == checked:
            return

        if not trial:
            bounding_box = await element.bounding_box()
            if not bounding_box:
                raise PlaywrightError("Element is not visible")

            # await element.scroll_into_view_if_needed(timeout=timeout)

            x, y, width, height = bounding_box["x"], bounding_box["y"], bounding_box["width"], bounding_box["height"]
            if not any(position.values()):
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await self.mouse.click(x, y, button="left", click_count=1, delay=20)

            assert await element.is_checked() == checked

    async def hover(
        self,
        selector: str,
        force: Optional[bool] = False,
        modifiers: Optional[Sequence[Literal["Alt", "Control", "Meta", "Shift"]]] = None,
        position: Optional[Position] = None,
        strict: Optional[bool] = False,
        timeout: Optional[float] = None,
        trial: Optional[bool] = False,
        no_wait_after: Optional[bool] = False,
    ) -> None:
        modifiers = modifiers or []
        position = position or Position(x=0, y=0)

        element = await self.wait_for_selector(selector, state="visible" if not force else "hidden", strict=strict, timeout=timeout)
        if not element:
            raise PlaywrightError("Element is not attached to the DOM")

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if not trial:
            bounding_box = await element.bounding_box()
            if not bounding_box:
                raise PlaywrightError("Element is not visible")

            # await element.scroll_into_view_if_needed(timeout=timeout)

            x, y, width, height = bounding_box["x"], bounding_box["y"], bounding_box["width"], bounding_box["height"]
            if not any(position.values()):
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            for modifier in modifiers:
                await self.keyboard.down(modifier)

            await self.mouse.move(x, y)

            for modifier in modifiers:
                await self.keyboard.up(modifier)

    async def type(self, selector: str, text: str, delay: Optional[float] = 200.0, no_wait_after: Optional[bool] = False, strict: Optional[bool] = False, timeout: Optional[float] = None) -> None:
        element = await self.wait_for_selector(selector, state="visible", strict=strict, timeout=timeout)
        if not element:
            raise PlaywrightError("Element is not attached to the DOM")

        await element.wait_for_element_state("editable", timeout=timeout)

        bounding_box = await element.bounding_box()
        if not bounding_box:
            raise PlaywrightError("Element is not visible")

        # await element.scroll_into_view_if_needed(timeout=timeout)

        x, y, width, height = bounding_box["x"], bounding_box["y"], bounding_box["width"], bounding_box["height"]
        x, y = x + width // 2, y + height // 2

        await self.mouse.click(x, y, button="left", click_count=1, delay=20)

        await self.keyboard.type(text, delay=delay)
