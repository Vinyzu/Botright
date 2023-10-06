from __future__ import annotations

from typing import Optional, Union, List, Dict, Literal
from re import Pattern
from pathlib import Path

from playwright.async_api import Page, Frame, ElementHandle, JSHandle, Locator, FrameLocator

from . import element_handle, frame_locator, js_handle, locator


def mock_frame(frame: Frame, page: Page) -> None:
    if not frame:
        return

    frane_mocker = FrameMock(frame, page)

    async def click_mocker(selector: str, button: Optional[str] = "left", click_count: Optional[int] = 1, strict: Optional[bool] = False, delay: Optional[int] = 20, force: Optional[bool] = False, modifiers: Optional[List] = None, no_wait_after: Optional[bool] = False, position: Optional[Dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        await frane_mocker.click(selector, button=button, click_count=click_count, strict=strict, delay=delay, force=force, modifiers=modifiers, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    frame.click = click_mocker

    async def dblclick_mocker(selector: str, button: Optional[str] = "left", click_count: Optional[int] = 1, strict: Optional[bool] = False, delay: Optional[int] = 20, force: Optional[bool] = False, modifiers: Optional[List] = None, no_wait_after: Optional[bool] = False, position: Optional[Dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        await frane_mocker.dblclick(selector, button=button, strict=strict, delay=delay, force=force, modifiers=modifiers, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    frame.dblclick = dblclick_mocker

    async def check_mocker(selector: str, button="left", strict: Optional[bool] = False, delay: Optional[int] = 20, force: Optional[bool] = False, modifiers: Optional[List] = None, no_wait_after: Optional[bool] = False, position: Optional[Dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        await frane_mocker.check(selector, force=force, no_wait_after=no_wait_after, position=position, strict=strict, timeout=timeout, trial=trial)

    frame.check = check_mocker

    async def uncheck_mocker(selector: str, force: Optional[bool] = False, no_wait_after: Optional[bool] = False, position: Optional[Dict] = None, strict: Optional[bool] = False, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        await frane_mocker.uncheck(selector, force=force, no_wait_after=no_wait_after, position=position, strict=strict, timeout=timeout, trial=trial)

    frame.uncheck = uncheck_mocker

    async def set_checked_mocker(selector: str, checked: Optional[bool] = False, force: Optional[bool] = False, no_wait_after: Optional[bool] = False, position: Optional[Dict] = None, strict: Optional[bool] = False, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        await frane_mocker.set_checked(selector, checked=checked, force=force, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    frame.set_checked = set_checked_mocker

    async def hover_mocker(selector: str, force: Optional[bool] = False, modifiers: Optional[list] = None, position: Optional[dict] = None, strict: Optional[bool] = False, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        await frane_mocker.hover(selector, force=force, modifiers=modifiers, position=position, strict=strict, timeout=timeout, trial=trial)

    frame.hover = hover_mocker

    async def type_mocker(selector: str, text: str, delay: Optional[int] = 200, no_wait_after: Optional[bool] = False, strict: Optional[bool] = False, timeout: Optional[float] = None) -> None:
        await frane_mocker.type(selector, text, delay=delay, no_wait_after=no_wait_after, strict=strict, timeout=timeout)

    frame.type = type_mocker

    for frame in frame.child_frames:
        mock_frame(frame, page)

    # ElementHandle
    async def mock_query_selector(selector: str, strict: Optional[bool] = False) -> Optional[ElementHandle]:
        element = await frame.origin_query_selector(selector, strict=strict)
        if element:
            element_handle.mock_element_handle(element, frame.page)
        return element

    frame.origin_query_selector = frame.query_selector
    frame.query_selector = mock_query_selector

    async def mock_query_selector_all(selector: str) -> List[ElementHandle]:
        elements = await frame.origin_query_selector_all(selector)
        for element in elements:
            element_handle.mock_element_handle(element, frame.page)
        return elements

    frame.origin_query_selector_all = frame.query_selector_all
    frame.query_selector_all = mock_query_selector_all

    async def mock_wait_for_selector(selector: str, state: Optional[list] = None, strict: Optional[bool] = False, timeout: Optional[float] = None) -> Optional[ElementHandle]:
        state = state or []

        element = await frame.origin_wait_for_selector(selector, state=state, strict=strict, timeout=timeout)
        if element:
            element_handle.mock_element_handle(element, frame.page)
        return element

    frame.origin_wait_for_selector = frame.wait_for_selector
    frame.wait_for_selector = mock_wait_for_selector

    async def mock_add_script_tag(content: Optional[str] = "", path: Optional[Union[str, Path]] = "", type: Optional[str] = "", url: Optional[str] = "") -> ElementHandle:
        element = await frame.origin_add_script_tag(content=content, path=path, type=type, url=url)
        element_handle.mock_element_handle(element, frame.page)
        return element

    frame.origin_add_script_tag = frame.add_script_tag
    frame.add_script_tag = mock_add_script_tag

    async def mock_add_style_tag(content: Optional[str] = "", path: Optional[Union[str, Path]] = "", url: Optional[str] = "") -> ElementHandle:
        element = await frame.origin_add_script_tag(content=content, path=path, url=url)
        element_handle.mock_element_handle(element, frame.page)
        return element

    frame.origin_add_script_tag = frame.add_script_tag
    frame.add_script_tag = mock_add_style_tag

    async def frame_element() -> ElementHandle:
        element = await frame.origin_frame_element()
        element_handle.mock_element_handle(element, frame.page)
        return element

    frame.origin_frame_element = frame.frame_element
    frame.frame_element = frame_element

    # JsHandle
    async def mock_evaluate_handle(expression: str, arg: Optional["EvaluatingArgument"] = None) -> JSHandle:
        _js_handle = await frame.origin_evaluate_handle(expression, arg=arg)
        js_handle.mock_js_handle(_js_handle, frame.page)
        return _js_handle

    frame.origin_evaluate_handle = frame.evaluate_handle
    frame.evaluate_handle = mock_evaluate_handle

    async def mock_wait_for_function(expression: str, arg: Optional["EvaluatingArgument"] = None, polling: Optional[float | Literal["raf"] | None] = "raf", timeout: Optional[float] = None) -> JSHandle:
        _js_handle = await frame.origin_wait_for_function(expression, arg=arg, polling=polling, timeout=timeout)
        js_handle.mock_js_handle(_js_handle, frame.page)
        return _js_handle

    frame.origin_wait_for_function = frame.wait_for_function
    frame.wait_for_function = mock_wait_for_function

    # FrameLocator
    async def frame_locator_mocker(selector: str) -> FrameLocator:
        _frame_locator = frame.origin_frame_locator(selector)
        frame_locator.mock_frame_locator(_frame_locator)
        return _frame_locator

    frame.origin_frame_locator = frame.frame_locator
    frame.frame_locator = frame_locator_mocker

    # Locator
    def locator_mocker(selector: str, has: Optional[Locator] = None, has_not: Optional[Locator] = None, has_text: Optional[str] = "", has_not_text: Optional[str | Pattern] = "") -> Locator:
        _locator = frame.origin_locator(selector, has=has, has_not=has_not, has_text=has_text, has_not_text=has_not_text)
        locator.mock_locator(_locator, page)
        return _locator

    frame.origin_locator = frame.locator
    frame.locator = locator_mocker


class FrameMock:
    def __init__(self, frame: Frame, page: Page) -> None:
        self.frame = frame
        self.page = page

    async def click(self, selector: str, button: Optional[str] = "left", click_count: Optional[int] = 1, strict: Optional[bool] = False, delay: Optional[int] = 20, force: Optional[bool] = False, modifiers: Optional[List] = None, no_wait_after: Optional[bool] = False, position: Optional[Dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        modifiers = modifiers or []
        position = position or {}

        element = await self.frame.wait_for_selector(selector, state="visible" if not force else "hidden", strict=strict, timeout=timeout)

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if not trial:
            if self.page.scroll_into_view:
                await element.scroll_into_view_if_needed(timeout=timeout)

            bounding_box = await element.bounding_box()
            x, y, width, height = bounding_box.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            for modifier in modifiers:
                await self.page.keyboard.down(modifier)

            await self.page.mouse.click(x, y, button=button, click_count=click_count, delay=delay)

            for modifier in modifiers:
                await self.page.keyboard.up(modifier)

    async def dblclick(self, selector: str, button: Optional[str] = "left", strict: Optional[bool] = False, delay: Optional[int] = 20, force: Optional[bool] = False, modifiers: Optional[List] = None, no_wait_after: Optional[bool] = False, position: Optional[Dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        modifiers = modifiers or []
        position = position or {}

        element = await self.frame.wait_for_selector(selector, state="visible" if not force else "hidden", strict=strict, timeout=timeout)

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if not trial:
            if self.page.scroll_into_view:
                await element.scroll_into_view_if_needed(timeout=timeout)

            bounding_box = await element.bounding_box()
            x, y, width, height = bounding_box.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            for modifier in modifiers:
                await self.page.keyboard.down(modifier)

            await self.page.mouse.dblclick(x, y, button=button, delay=delay)

            for modifier in modifiers:
                await self.page.keyboard.up(modifier)

    async def check(self, selector: str, force: Optional[bool] = False, no_wait_after: Optional[bool] = False, position: Optional[Dict] = None, strict: Optional[bool] = False, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        position = position or {}

        element = await self.frame.wait_for_selector(selector, state="visible" if not force else "hidden", strict=strict, timeout=timeout)

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if await element.is_checked():
            return

        if not trial:
            if self.page.scroll_into_view:
                await element.scroll_into_view_if_needed(timeout=timeout)

            bounding_box = await element.bounding_box()
            x, y, width, height = bounding_box.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await self.page.mouse.click(x, y, button="left", click_count=1, delay=20)

            assert await element.is_checked()

    async def uncheck(self, selector: str, force: Optional[bool] = False, no_wait_after: Optional[bool] = False, position: Optional[Dict] = None, strict: Optional[bool] = False, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        position = position or {}

        element = await self.frame.wait_for_selector(selector, state="visible" if not force else "hidden", strict=strict, timeout=timeout)

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if not await element.is_checked():
            return

        if not trial:
            if self.page.scroll_into_view:
                await element.scroll_into_view_if_needed(timeout=timeout)

            bounding_box = await element.bounding_box()
            x, y, width, height = bounding_box.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await self.page.mouse.click(x, y, button="left", click_count=1, delay=20)

            assert not await element.is_checked()

    async def set_checked(self, selector: str, checked: Optional[bool] = False, force: Optional[bool] = False, no_wait_after: Optional[bool] = False, position: Optional[Dict] = None, strict: Optional[bool] = False, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        position = position or {}

        element = await self.frame.wait_for_selector(selector, state="visible" if not force else "hidden", strict=strict, timeout=timeout)

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if await element.is_checked() == checked:
            return

        if not trial:
            if self.page.scroll_into_view:
                await element.scroll_into_view_if_needed(timeout=timeout)

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

        element = await self.frame.wait_for_selector(selector, state="visible" if not force else "hidden", strict=strict, timeout=timeout)

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if not trial:
            if self.page.scroll_into_view:
                await element.scroll_into_view_if_needed(timeout=timeout)

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
        element = await self.frame.wait_for_selector(selector, state="visible", strict=strict, timeout=timeout)

        await element.wait_for_element_state("editable", timeout=timeout)

        if self.page.scroll_into_view:
            await element.scroll_into_view_if_needed(timeout=timeout)

        bounding_box = await element.bounding_box()
        x, y, width, height = bounding_box.values()
        x, y = x + width // 2, y + height // 2

        await self.page.mouse.click(x, y, button="left", click_count=1, delay=20)

        await self.page.mouse.click(x, y, delay=delay)

        await self.page.keyboard.type(text, delay=delay)
