import random
import typing

import playwright_stealth

from .. import geetest, hcaptcha, recaptcha
from . import element_handle, frame, frame_locator, js_handle, locator, mouse


async def new_page(botright, browser, proxy, faker, **launch_arguments) -> "PlaywrightPage":
    # Create new Pag
    page = await browser._new_page(**launch_arguments)
    # Stealthen the page with custom Stealth Config
    config = playwright_stealth.StealthConfig()
    (config.navigator_languages, config.permissions, config.navigator_platform, config.navigator_vendor, config.outerdimensions) = (False, False, False, False, False)
    # Setting Important JS Variables to Botright Variables
    config.vendor, config.renderer, config.nav_user_agent, config.nav_platform = (faker.vendor, faker.renderer, faker.useragent, "Win32")
    # Setting the Language
    config.languages = ("en-US", "en", faker.locale, faker.language_code)
    await playwright_stealth.stealth_async(page, config)

    # Mocking Page
    await mock_page(page, botright)
    botright.stopable.append(page)
    return page


async def mock_keyboard(page) -> None:
    # KeyboardMocking
    async def type_mocker(text, delay=200) -> None:
        for char in text:
            await page.keyboard._type(char, delay=random.randint(delay - 50, delay + 50))
        await page.wait_for_timeout(random.randint(4, 8) * 100)

    page.keyboard._type = page.keyboard.type
    page.keyboard.type = type_mocker


async def mock_page_functions(page):
    # Frame
    def mock_frame_func(name=None, url=None) -> "Frame":
        _frame = page._frame(name=name, url=url)
        frame.mock_frame(_frame)
        return _frame

    page._frame = page.frame
    page.frame = mock_frame_func

    # ElementHandle
    async def mock_query_selector(selector, strict=False) -> typing.Optional["ElementHandle"]:
        element = await page._query_selector(selector, strict=strict)
        if element:
            element_handle.mock_element_handle(element)
        return element

    page._query_selector = page.query_selector
    page.query_selector = mock_query_selector

    async def mock_query_selector_all(selector) -> typing.List["ElementHandle"]:
        elements = await page._query_selector_all(selector)
        for element in elements:
            element_handle.mock_element_handle(element)
        return elements

    page._query_selector_all = page.query_selector_all
    page.query_selector_all = mock_query_selector_all

    async def mock_wait_for_selector(selector, state=[], strict=False, timeout: typing.Optional[float] = None) -> typing.Optional["ElementHandle"]:
        element = await page._wait_for_selector(selector, state=state, strict=strict, timeout=timeout)
        if element:
            element_handle.mock_element_handle(element)
        return element

    page._wait_for_selector = page.wait_for_selector
    page.wait_for_selector = mock_wait_for_selector

    async def mock_add_script_tag(content="", path="", type="", url="") -> "ElementHandle":
        element = await page._add_script_tag(content=content, path=path, type=type, url=url)
        element_handle.mock_element_handle(element)
        return element

    page._add_script_tag = page.add_script_tag
    page.add_script_tag = mock_add_script_tag

    async def mock_add_style_tag(content="", path="", type="", url="") -> "ElementHandle":
        element = await page._add_script_tag(content=content, path=path, type=type, url=url)
        element_handle.mock_element_handle(element)
        return element

    page._add_script_tag = page.add_script_tag
    page.add_script_tag = mock_add_style_tag

    # Locator
    def mock_locator_func(selector, has=None, has_text="") -> "Locator":
        _locator = page._locator(selector, has=has, has_text=has_text)
        locator.mock_locator(_locator)
        return _locator

    page._locator = page.locator
    page.locator = mock_locator_func

    # JsHandle
    async def mock_evaluate_handle(expression, arg=None) -> "JSHandle":
        _js_handle = await page._evaluate_handle(expression, arg=arg)
        js_handle.mock_js_handle(_js_handle)
        return _js_handle

    page._evaluate_handle = page.evaluate_handle
    page.evaluate_handle = mock_evaluate_handle

    async def mock_wait_for_function(expression, arg=None, polling="raf", timeout: typing.Optional[float] = None) -> "JSHandle":
        _js_handle = await page._wait_for_function(expression, arg=arg, polling=polling, timeout=timeout)
        js_handle.mock_js_handle(_js_handle)
        return _js_handle

    page._wait_for_function = page.wait_for_function
    page.wait_for_function = mock_wait_for_function

    # FrameLocator
    def mock_frame_locator_func(selector) -> "JSHandle":
        _frame_locator = page._frame_locator(selector)
        frame_locator.mock_frame_locator(_frame_locator)
        return _frame_locator

    page._frame_locator = page.frame_locator
    page.frame_locator = mock_frame_locator_func


async def mock_page_objects(page) -> None:
    async def click_mocker(selector, button="left", click_count=1, strict=False, delay=20, force=False, modifiers=[], no_wait_after=False, position={}, timeout: typing.Optional[float] = None, trial=False):
        await Page.click(page, selector, button=button, click_count=click_count, strict=strict, delay=delay, force=force, modifiers=modifiers, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    page.click = click_mocker

    async def dblclick_mocker(selector, button="left", strict=False, delay=20, force=False, modifiers=[], no_wait_after=False, position={}, timeout: typing.Optional[float] = None, trial=False):
        await Page.dblclick(page, selector, button=button, strict=strict, delay=delay, force=force, modifiers=modifiers, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    page.dblclick = dblclick_mocker

    async def check_mocker(selector, force=False, no_wait_after=False, position={}, strict=False, timeout: typing.Optional[float] = None, trial=False):
        await Page.check(page, selector, force=force, no_wait_after=no_wait_after, position=position, strict=strict, timeout=timeout, trial=trial)

    page.check = check_mocker

    async def uncheck_mocker(selector, force=False, no_wait_after=False, position={}, strict=False, timeout: typing.Optional[float] = None, trial=False):
        await page.uncheck(page, selector, force=force, no_wait_after=no_wait_after, position=position, strict=strict, timeout=timeout, trial=trial)

    page.uncheck = uncheck_mocker

    async def set_checked_mocker(selector, checked=False, force=False, no_wait_after=False, position={}, timeout: typing.Optional[float] = None, trial=False):
        await Page.set_checked(page, selector, checked=checked, force=force, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    page.set_checked = set_checked_mocker

    async def hover_mocker(selector, force=False, modifiers=[], position={}, strict=False, timeout: typing.Optional[float] = None, trial=False):
        await Page.hover(page, selector, force=force, modifiers=modifiers, position=position, strict=strict, timeout=timeout, trial=trial)

    page.hover = hover_mocker

    async def type_mocker(selector, text, delay=200, no_wait_after=False, strict=False, timeout: typing.Optional[float] = None):
        await Page.type(page, selector, text, delay=delay, no_wait_after=no_wait_after, strict=strict, timeout=timeout)

    page.type = type_mocker


class Page:
    async def click(page, selector, button="left", click_count=1, strict=False, delay=20, force=False, modifiers=[], no_wait_after=False, position={}, timeout: typing.Optional[float] = None, trial=False) -> None:
        element = await page.wait_for_selector(selector, state="visible" if not force else "hidden", strict=strict, timeout=timeout)

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if not trial:
            # await element.scroll_into_view_if_needed(timeout=timeout)

            boundings = await element.bounding_box()
            x, y, width, height = boundings.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            for modifier in modifiers:
                await page.keyboard.down(modifier)

            await page.mouse.click(x, y, button, click_count, delay)

            for modifier in modifiers:
                await page.keyboard.up(modifier)

    async def dblclick(page, selector, button="left", strict=False, delay=20, force=False, modifiers=[], no_wait_after=False, position={}, timeout: typing.Optional[float] = None, trial=False) -> None:
        element = await page.wait_for_selector(selector, state="visible" if not force else "hidden", strict=strict, timeout=timeout)

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if not trial:
            # await element.scroll_into_view_if_needed(timeout=timeout)

            boundings = await element.bounding_box()
            x, y, width, height = boundings.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            for modifier in modifiers:
                await page.keyboard.down(modifier)

            await page.mouse.dblclick(x, y, button, delay)

            for modifier in modifiers:
                await page.keyboard.up(modifier)

    async def check(page, selector, force=False, no_wait_after=False, position={}, strict=False, timeout: typing.Optional[float] = None, trial=False) -> None:
        element = await page.wait_for_selector(selector, state="visible" if not force else "hidden", strict=strict, timeout=timeout)

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if await element.is_checked():
            return

        if not trial:
            # await element.scroll_into_view_if_needed(timeout=timeout)

            boundings = await element.bounding_box()
            x, y, width, height = boundings.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await page.mouse.click(x, y, button="left", click_count=1, delay=20)

            assert await element.is_checked()

    async def uncheck(page, selector, force=False, no_wait_after=False, position={}, strict=False, timeout: typing.Optional[float] = None, trial=False) -> None:
        element = await page.wait_for_selector(selector, state="visible" if not force else "hidden", strict=strict, timeout=timeout)

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if not await element.is_checked():
            return

        if not trial:
            # await element.scroll_into_view_if_needed(timeout=timeout)

            boundings = await element.bounding_box()
            x, y, width, height = boundings.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await page.mouse.click(x, y, button="left", click_count=1, delay=20)

            assert not await element.is_checked()

    async def set_checked(page, selector, checked=False, force=False, no_wait_after=False, position={}, strict=False, timeout: typing.Optional[float] = None, trial=False) -> None:
        element = await page.wait_for_selector(selector, state="visible" if not force else "hidden", strict=strict, timeout=timeout)

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if await element.is_checked() == checked:
            return

        if not trial:
            # await element.scroll_into_view_if_needed(timeout=timeout)

            boundings = await element.bounding_box()
            x, y, width, height = boundings.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await page.mouse.click(x, y, button="left", click_count=1, delay=20)

            assert await element.is_checked()

    async def hover(page, selector, force=False, modifiers=[], position={}, strict=False, timeout: typing.Optional[float] = None, trial=False) -> None:
        element = await page.wait_for_selector(selector, state="visible" if not force else "hidden", strict=strict, timeout=timeout)

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if not trial:
            # await element.scroll_into_view_if_needed(timeout=timeout)

            boundings = await element.bounding_box()
            x, y, width, height = boundings.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            for modifier in modifiers:
                await page.keyboard.down(modifier)

            await page.mouse.move(x, y)

            for modifier in modifiers:
                await page.keyboard.up(modifier)

    async def type(page, selector, text, delay=200, no_wait_after=False, strict=False, timeout: typing.Optional[float] = None) -> None:
        element = await page.wait_for_selector(selector, state="visible", strict=strict, timeout=timeout)

        await element.wait_for_element_state("editable", timeout=timeout)

        # await element.scroll_into_view_if_needed(timeout=timeout)

        boundings = await element.bounding_box()
        x, y, width, height = boundings.values()

        x, y = x + width // 2, y + height // 2

        await page.mouse.click(x, y, "left", 1, delay)

        await page.keyboard.type(text, delay=delay)


async def better_google_score(page):
    await page.goto("https://google.com/")
    await page.click('[id="L2AGLb"]')
    await page.type('[autocomplete="off"]', ".")
    await page.keyboard.press("Enter")
    await page.wait_for_timeout(1000)


async def mock_page(page, botright) -> None:
    # await better_google_score(page)

    page.scroll_into_view = botright.scroll_into_view

    mouse.mock_mouse(page)
    await mock_keyboard(page)

    # Mocking Captcha
    async def hcap_solve_mocker(rqdata=None):
        return await hcaptcha.hCaptcha.solve_hcaptcha(page, rqdata=rqdata)

    page.solve_hcaptcha = hcap_solve_mocker

    async def geetest_mocker(mode="canny"):
        return await geetest.solve_geetest(page, mode=mode)

    page.solve_geetest = geetest_mocker

    async def recap_audio_mocker():
        return await recaptcha.AudioCaptcha.audio_recaptcha(page)

    page.audio_recaptcha = recap_audio_mocker

    async def recap_visual_mocker():
        return await recaptcha.VisualCaptcha.visual_recaptcha(page, first_time=True)

    page.visual_recaptcha = recap_visual_mocker
    page.solve_recaptcha = recap_visual_mocker

    frame.mock_frame(page.main_frame)
    await mock_page_objects(page)

    await mock_page_functions(page)
