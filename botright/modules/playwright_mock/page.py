from __future__ import annotations

import random
import sys
from pathlib import Path
from typing import Optional, Literal, List, Callable, Any
from re import Pattern

from playwright.async_api import BrowserContext, Page, Locator, Frame, FrameLocator, ElementHandle, JSHandle
from botright.modules import Faker

import playwright_stealth
import hcaptcha_challenger as solver
from recaptcha_challenger.agents.playwright import AsyncChallenger

from .. import geetest, hcaptcha
from . import element_handle, frame, frame_locator, js_handle, locator, mouse

tmp_dir = Path(__file__).parent.joinpath("tmp_dir")

async def new_page(botright, browser: BrowserContext, faker: Faker,) -> Page:
    # Create new Page
    page = await browser._new_page()

    # Stealthen the page with custom Stealth Config
    if browser.stealth_page:
        config = playwright_stealth.StealthConfig()
        # Setting shit Options to False
        # config.navigator_languages = False
        config.navigator_platform, config.outerdimensions, config.iframe_content_window, config.chrome_runtime = False, False, False, False
        config.navigator_user_agent, config.navigator_languages = False, False
        config.webdriver = False
        # Setting Important JS Variables to Botright Variables
        config.vendor, config.renderer, config.nav_user_agent, config.nav_platform = faker.vendor, faker.renderer, faker.useragent, sys.platform.capitalize()
        # Setting the Language
        config.languages = ("en-US", "en", faker.locale, faker.language_code)
        await playwright_stealth.stealth_async(page, config)

    # Opening CDP Session
    page.cdp = await browser.new_cdp_session(page)
    await page.cdp.send("Network.setUserAgentOverride",
                        {"userAgent": faker.useragent, "acceptLanguage": "en-US",
                         "userAgentMetadata": {"platform": faker.os_system, "architecture": "x86", "platformVersion": "14.0.0", "model": "", "mobile": False}
                         })

    # Adding Navigator Language
    await page.add_init_script('utils.replaceGetterWithProxy(Object.getPrototypeOf(navigator),"languages",utils.makeHandler().getterValue(Object.freeze(["en-US","en"])));')

    # Source: https://github.com/kkoooqq/fakebrowser/blob/main/src/plugins/user-action-layer/index.js
    if botright.user_action_layer:
        await page.add_init_script('window.addEventListener("DOMContentLoaded",()=>{let e=document.createElement("canvas");e.width=window.innerWidth,e.height=window.innerHeight,e.style.userSelect="none",e.style.pointerEvents="none",e.style.position="fixed",e.style.left="0px",e.style.top="0px",e.style.width=""+window.innerWidth+"px",e.style.height=""+window.innerHeight+"px",e.style.zIndex="999999",document.body.appendChild(e);let t=e.getContext("2d");document.addEventListener("keydown",e=>{}),document.addEventListener("keyup",e=>{}),document.addEventListener("mousemove",e=>{t.beginPath(),t.arc(e.clientX,e.clientY,3,0,360,!1),t.fillStyle="green",t.fill(),t.closePath()}),document.addEventListener("mousedown",e=>{t.beginPath(),t.arc(e.clientX,e.clientY,15,0,360,!1),t.fillStyle="black",t.fill(),t.closePath()}),document.addEventListener("mouseup",e=>{t.beginPath(),t.arc(e.clientX,e.clientY,9,0,360,!1),t.fillStyle="blue",t.fill(),t.closePath()})});')

    page.hcaptcha_agent = solver.AgentT.from_page(page=page, tmp_dir=tmp_dir)
    page.hcaptcha_solver = hcaptcha.hCaptcha(browser, page)
    page.recaptcha_solver = AsyncChallenger(page)

    # Mocking Page
    await mock_page(botright, page)
    botright.stoppable.append(page)
    return page


async def mock_keyboard(page: Page) -> None:
    # KeyboardMocking
    async def type_mocker(text: str, delay: Optional[int] = 100) -> None:
        for char in text:
            await page.keyboard.origin_type(char, delay=random.randint(delay - 50, delay + 50))
        await page.wait_for_timeout(random.randint(4, 8) * 100)

    page.keyboard.origin_type = page.keyboard.type
    page.keyboard.type = type_mocker


async def mock_page_functions(page: Page) -> None:
    # Frame
    def mock_frame_func(name: Optional[str] = None, url: Optional[str | Pattern[str] | Callable[[str], bool] | None] = None) -> Frame:
        _frame = page.origin_frame(name=name, url=url)
        frame.mock_frame(_frame, page)
        return _frame

    page.origin_frame = page.frame
    page.frame = mock_frame_func

    # ElementHandle
    async def mock_query_selector(selector: str, strict: Optional[bool] = False) -> Optional[ElementHandle]:
        element = await page.origin_query_selector(selector, strict=strict)
        if element:
            element_handle.mock_element_handle(element, page)
        return element

    page.origin_query_selector = page.query_selector
    page.query_selector = mock_query_selector

    async def mock_query_selector_all(selector: str) -> List[ElementHandle]:
        elements = await page.origin_query_selector_all(selector)
        for element in elements:
            element_handle.mock_element_handle(element, page)
        return elements

    page.origin_query_selector_all = page.query_selector_all
    page.query_selector_all = mock_query_selector_all

    async def mock_wait_for_selector(selector: str, state: Optional[Literal["attached", "detached", "hidden", "visible"] | None] = None, strict: Optional[bool] = False, timeout: Optional[float] = None) -> Optional[ElementHandle]:
        element = await page.origin_wait_for_selector(selector, state=state, strict=strict, timeout=timeout)
        if element:
            element_handle.mock_element_handle(element, page)
        return element

    page.origin_wait_for_selector = page.wait_for_selector
    page.wait_for_selector = mock_wait_for_selector

    async def mock_add_script_tag(content: Optional[str] = "", path: Optional[str | Path] = "", type: Optional[str] = "", url: Optional[str] = "") -> ElementHandle:
        element = await page.origin_add_script_tag(content=content, path=path, type=type, url=url)
        element_handle.mock_element_handle(element, page)
        return element

    page.origin_add_script_tag = page.add_script_tag
    page.add_script_tag = mock_add_script_tag

    async def mock_add_style_tag(content: Optional[str] = "", path: Optional[str | Path] = "", url: Optional[str] = "") -> ElementHandle:
        element = await page.origin_add_style_tag(content=content, path=path, url=url)
        element_handle.mock_element_handle(element, page)
        return element

    page.origin_add_style_tag = page.add_style_tag
    page.add_style_tag = mock_add_style_tag

    # Locator
    def mock_locator_func(selector: str, has: Optional[Locator] = None, has_not: Optional[Locator] = None, has_text: Optional[str] = "", has_not_text: Optional[str | Pattern] = "") -> Locator:
        _locator = page.origin_locator(selector, has=has, has_not=has_not, has_text=has_text, has_not_text=has_not_text)
        locator.mock_locator(_locator, page)
        return _locator

    page.origin_locator = page.locator
    page.locator = mock_locator_func

    def mock_get_by_alt_text_func(text: str | Pattern, exact: Optional[bool] = False) -> Locator:
        _locator = page.origin_get_by_alt_text(text, exact=exact)
        locator.mock_locator(_locator, page)
        return _locator

    page.origin_get_by_alt_text = page.get_by_alt_text
    page.get_by_alt_text = mock_get_by_alt_text_func

    def mock_get_by_label_func(text: str | Pattern, exact: Optional[bool] = False) -> Locator:
        _locator = page.origin_get_by_label(text, exact=exact)
        locator.mock_locator(_locator, page)
        return _locator

    page.origin_get_by_label = page.get_by_label
    page.get_by_label = mock_get_by_label_func

    def mock_get_by_placeholder_func(text: str | Pattern, exact: Optional[bool] = False) -> Locator:
        _locator = page.origin_get_by_placeholder(text, exact=exact)
        locator.mock_locator(_locator, page)
        return _locator

    page.origin_get_by_placeholder = page.get_by_placeholder
    page.get_by_placeholder = mock_get_by_placeholder_func

    def mock_get_by_role_func(role: Any, checked: Optional[bool] = False, disabled: Optional[bool] = False, expanded: Optional[bool] = False, include_hidden: Optional[bool] = False, level: Optional[int] = 0, name: Optional[str] = "", pressed: Optional[bool] = False, selected: Optional[bool] = False) -> Locator:
        _locator = page.origin_get_by_role(role, checked=checked, disabled=disabled, expanded=expanded, include_hidden=include_hidden, level=level, name=name, pressed=pressed, selected=selected)
        locator.mock_locator(_locator, page)
        return _locator

    page.origin_get_by_role = page.get_by_role
    page.get_by_role = mock_get_by_role_func

    def mock_get_by_test_id_func(test_id: str | Pattern) -> Locator:
        _locator = page.origin_get_by_test_id(test_id)
        locator.mock_locator(_locator, page)
        return _locator

    page.origin_get_by_test_id = page.get_by_test_id
    page.get_by_test_id = mock_get_by_test_id_func

    def mock_get_by_text_func(text: str | Pattern, exact: Optional[bool] = False) -> Locator:
        _locator = page.origin_get_by_text(text, exact=exact)
        locator.mock_locator(_locator, page)
        return _locator

    page.origin_get_by_text = page.get_by_text
    page.get_by_text = mock_get_by_text_func

    def mock_get_by_title_func(text: str | Pattern, exact: Optional[bool] = False) -> Locator:
        _locator = page.origin_get_by_title(text, exact=exact)
        locator.mock_locator(_locator, page)
        return _locator

    page.origin_get_by_title = page.get_by_title
    page.get_by_title = mock_get_by_title_func

    # JsHandle
    async def mock_evaluate_handle(expression: str, arg: Optional[Any] = None) -> JSHandle:
        _js_handle = await page.origin_evaluate_handle(expression, arg=arg)
        js_handle.mock_js_handle(_js_handle, page)
        return _js_handle

    page.origin_evaluate_handle = page.evaluate_handle
    page.evaluate_handle = mock_evaluate_handle

    async def mock_wait_for_function(expression: str, arg: Optional[Any] = None, polling: Optional[float | Literal["raf"] | None] = "raf", timeout: Optional[float] = None) -> JSHandle:
        _js_handle = await page.origin_wait_for_function(expression, arg=arg, polling=polling, timeout=timeout)
        js_handle.mock_js_handle(_js_handle, page)
        return _js_handle

    page.origin_wait_for_function = page.wait_for_function
    page.wait_for_function = mock_wait_for_function

    # FrameLocator
    def mock_frame_locator_func(selector: str) -> FrameLocator:
        _frame_locator = page.origin_frame_locator(selector)
        frame_locator.mock_frame_locator(_frame_locator, page)
        return _frame_locator

    page.origin_frame_locator = page.frame_locator
    page.frame_locator = mock_frame_locator_func


async def mock_page_objects(page) -> None:
    page_mocker = PageMock(page)

    async def click_mocker(selector: str, button: Optional[str] = "left", click_count: Optional[int] = 1, strict: Optional[bool] = False, delay: Optional[int] = 20, force: Optional[bool] = False, modifiers: Optional[list] = None, no_wait_after: Optional[bool] = False, position: Optional[dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False):
        await page_mocker.click(selector, button=button, click_count=click_count, strict=strict, delay=delay, force=force, modifiers=modifiers, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    page.click = click_mocker

    async def dblclick_mocker(selector: str, button: Optional[str] = "left", strict: Optional[bool] = False, delay: Optional[int] = 20, force: Optional[bool] = False, modifiers: Optional[list] = None, no_wait_after: Optional[bool] = False, position: Optional[dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False):
        await page_mocker.dblclick(selector, button=button, strict=strict, delay=delay, force=force, modifiers=modifiers, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    page.dblclick = dblclick_mocker

    async def check_mocker(selector: str, force: Optional[bool] = False, no_wait_after: Optional[bool] = False, position: Optional[dict] = None, strict: Optional[bool] = False, timeout: Optional[float] = None, trial: Optional[bool] = False):
        await page_mocker.check(selector, force=force, no_wait_after=no_wait_after, position=position, strict=strict, timeout=timeout, trial=trial)

    page.check = check_mocker

    async def uncheck_mocker(selector: str, force: Optional[bool] = False, no_wait_after: Optional[bool] = False, position: Optional[dict] = None, strict: Optional[bool] = False, timeout: Optional[float] = None, trial: Optional[bool] = False):
        await page_mocker.uncheck(selector, force=force, no_wait_after=no_wait_after, position=position, strict=strict, timeout=timeout, trial=trial)

    page.uncheck = uncheck_mocker

    async def set_checked_mocker(selector: str, checked: Optional[bool] = False, force: Optional[bool] = False, no_wait_after: Optional[bool] = False, position: Optional[dict] = None, strict: Optional[bool] = False, timeout: Optional[float] = None, trial: Optional[bool] = False):
        await page_mocker.set_checked(selector, checked=checked, force=force, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    page.set_checked = set_checked_mocker

    async def hover_mocker(selector: str, force: Optional[bool] = False, modifiers: Optional[list] = None, position: Optional[dict] = None, strict: Optional[bool] = False, timeout: Optional[float] = None, trial: Optional[bool] = False):
        await page_mocker.hover(selector, force=force, modifiers=modifiers, position=position, strict=strict, timeout=timeout, trial=trial)

    page.hover = hover_mocker

    async def type_mocker(selector: str, text: str, delay: Optional[int] = 200, no_wait_after: Optional[bool] = False, strict: Optional[bool] = False, timeout: Optional[float] = None):
        await page_mocker.type(selector, text, delay=delay, no_wait_after=no_wait_after, strict=strict, timeout=timeout)

    page.type = type_mocker


class PageMock:
    def __init__(self, page):
        self.page = page

    async def click(self, selector: str, button: Optional[str] = "left", click_count: Optional[int] = 1, strict: Optional[bool] = False, delay: Optional[int] = 20, force: Optional[bool] = False, modifiers: Optional[list] = None, no_wait_after: Optional[bool] = False, position: Optional[dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        modifiers = modifiers or []
        position = position or {}

        element = await self.page.wait_for_selector(selector, state="visible" if not force else "hidden", strict=strict, timeout=timeout)

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if not trial:
            # await element.scroll_into_view_if_needed(timeout=timeout)

            bounding_box = await element.bounding_box()
            x, y, width, height = bounding_box.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            for modifier in modifiers:
                await self.page.keyboard.down(modifier)

            await self.page.mouse.click(x, y, button, click_count, delay)

            for modifier in modifiers:
                await self.page.keyboard.up(modifier)

    async def dblclick(self, selector: str, button: Optional[str] = "left", strict: Optional[bool] = False, delay: Optional[int] = 20, force: Optional[bool] = False, modifiers: Optional[list] = None, no_wait_after: Optional[bool] = False, position: Optional[dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        modifiers = modifiers or []
        position = position or {}

        element = await self.page.wait_for_selector(selector, state="visible" if not force else "hidden", strict=strict, timeout=timeout)

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if not trial:
            # await element.scroll_into_view_if_needed(timeout=timeout)

            bounding_box = await element.bounding_box()
            x, y, width, height = bounding_box.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            for modifier in modifiers:
                await self.page.keyboard.down(modifier)

            await self.page.mouse.dblclick(x, y, button, delay)

            for modifier in modifiers:
                await self.page.keyboard.up(modifier)

    async def check(self, selector: str, force: Optional[bool] = False, no_wait_after: Optional[bool] = False, position: Optional[dict] = None, strict: Optional[bool] = False, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        position = position or {}

        element = await self.page.wait_for_selector(selector, state="visible" if not force else "hidden", strict=strict, timeout=timeout)

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if await element.is_checked():
            return

        if not trial:
            # await element.scroll_into_view_if_needed(timeout=timeout)

            bounding_box = await element.bounding_box()
            x, y, width, height = bounding_box.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await self.page.mouse.click(x, y, button="left", click_count=1, delay=20)

            assert await element.is_checked()

    async def uncheck(self, selector: str, force: Optional[bool] = False, no_wait_after: Optional[bool] = False, position: Optional[dict] = None, strict: Optional[bool] = False, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        position = position or {}

        element = await self.page.wait_for_selector(selector, state="visible" if not force else "hidden", strict=strict, timeout=timeout)

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if not await element.is_checked():
            return

        if not trial:
            # await element.scroll_into_view_if_needed(timeout=timeout)

            bounding_box = await element.bounding_box()
            x, y, width, height = bounding_box.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await self.page.mouse.click(x, y, button="left", click_count=1, delay=20)

            assert not await element.is_checked()

    async def set_checked(self, selector: str, checked: Optional[bool] = False, force: Optional[bool] = False, no_wait_after: Optional[bool] = False, position: Optional[dict] = None, strict: Optional[bool] = False, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        position = position or {}

        element = await self.page.wait_for_selector(selector, state="visible" if not force else "hidden", strict=strict, timeout=timeout)

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if await element.is_checked() == checked:
            return

        if not trial:
            # await element.scroll_into_view_if_needed(timeout=timeout)

            bounding_box = await element.bounding_box()
            x, y, width, height = bounding_box.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await self.page.mouse.click(x, y, button="left", click_count=1, delay=20)

            assert await element.is_checked()

    async def hover(self, selector: str, force: Optional[bool] = False, modifiers: Optional[list] = None, position: Optional[dict] = None, strict: Optional[bool] = False, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        modifiers = modifiers or []
        position = position or {}

        element = await self.page.wait_for_selector(selector, state="visible" if not force else "hidden", strict=strict, timeout=timeout)

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if not trial:
            # await element.scroll_into_view_if_needed(timeout=timeout)

            bounding_box = await element.bounding_box()
            x, y, width, height = bounding_box.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            for modifier in modifiers:
                await self.page.keyboard.down(modifier)

            await self.page.mouse.move(x, y)

            for modifier in modifiers:
                await self.page.keyboard.up(modifier)

    async def type(self, selector: str, text: str, delay: Optional[int] = 200, no_wait_after: Optional[bool] = False, strict: Optional[bool] = False, timeout: Optional[float] = None) -> None:
        element = await self.page.wait_for_selector(selector, state="visible", strict=strict, timeout=timeout)

        await element.wait_for_element_state("editable", timeout=timeout)

        # await element.scroll_into_view_if_needed(timeout=timeout)

        bounding_box = await element.bounding_box()
        x, y, width, height = bounding_box.values()

        x, y = x + width // 2, y + height // 2

        await self.page.mouse.click(x, y, "left", 1, delay)

        await self.page.keyboard.type(text, delay=delay)


async def better_google_score(page: Page) -> None:
    await page.goto("https://google.com/")
    await page.click('[id="L2AGLb"]')
    await page.type('[autocomplete="off"]', ".")
    await page.keyboard.press("Enter")
    await page.wait_for_timeout(1000)


async def mock_page(botright, page: Page) -> None:
    # await better_google_score(page)
    page.scroll_into_view = botright.scroll_into_view

    mouse.mock_mouse(page)
    await mock_keyboard(page)

    # Mocking Captcha
    async def hcap_solve_mocker(rq_data: Optional[str] = None) -> Optional[str]:
        return await page.hcaptcha_solver.solve_hcaptcha(rq_data=rq_data)

    page.solve_hcaptcha = hcap_solve_mocker

    async def get_hcaptcha_mocker(site_key: Optional[str] = "00000000-0000-0000-0000-000000000000", rq_data: Optional[str] = None) -> Optional[str]:
        return await page.hcaptcha_solver.get_hcaptcha(site_key=site_key, rq_data=rq_data)

    page.get_hcaptcha = get_hcaptcha_mocker

    async def geetest_mocker(mode: Optional[str] = "canny") -> str:
        return await geetest.solve_geetest(page, mode=mode)

    page.solve_geetest = geetest_mocker

    async def recap_mocker() -> Optional[str]:
        raise NotImplementedError("recaptcha-challenger is not implemented yet. Wait for release shortly.")
        # return await page.recaptcha_solver.solve_recaptcha()

    page.visual_recaptcha = recap_mocker
    page.solve_recaptcha = recap_mocker

    frame.mock_frame(page.main_frame, page)
    await mock_page_objects(page)

    await mock_page_functions(page)
