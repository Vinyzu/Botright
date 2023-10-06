from __future__ import annotations

from typing import Optional, List, Literal, Any

from playwright.async_api import Page, ElementHandle, JSHandle

from . import js_handle


def mock_element_handle(element: ElementHandle, page: Page) -> None:
    element_handle_mocker = ElementHandleMock(element, page)

    async def click_mocker(button="left", click_count: Optional[int] = 1, delay: Optional[int] = 20, force: Optional[bool] = False, modifiers: Optional[list] = None, no_wait_after: Optional[bool] = False, position: Optional[dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        await element_handle_mocker.click(button=button, click_count=click_count, delay=delay, force=force, modifiers=modifiers, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    element.click = click_mocker

    async def dblclick_mocker(button="left", delay: Optional[int] = 20, force: Optional[bool] = False, modifiers: Optional[list] = None, no_wait_after: Optional[bool] = False, position: Optional[dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        await element_handle_mocker.dblclick(button=button, delay=delay, force=force, modifiers=modifiers, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    element.dblclick = dblclick_mocker

    async def check_mocker(force: Optional[bool] = False, no_wait_after: Optional[bool] = False, position: Optional[dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        await element_handle_mocker.check(force=force, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    element.check = check_mocker

    async def uncheck_mocker(force: Optional[bool] = False, no_wait_after: Optional[bool] = False, position: Optional[dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        await element_handle_mocker.uncheck(force=force, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    element.uncheck = uncheck_mocker

    async def set_checked_mocker(checked: Optional[bool] = False, force: Optional[bool] = False, no_wait_after: Optional[bool] = False, position: Optional[dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        await element_handle_mocker.set_checked(checked=checked, force=force, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    element.set_checked = set_checked_mocker

    async def hover_mocker(force: Optional[bool] = False, modifiers: Optional[list] = None, position: Optional[dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        await element_handle_mocker.hover(force=force, modifiers=modifiers, position=position, timeout=timeout, trial=trial)

    element.hover = hover_mocker

    async def type_mocker(text: str, delay: Optional[int] = 200, no_wait_after: Optional[bool] = False, timeout: Optional[float] = None) -> None:
        await element_handle_mocker.type(text, delay=delay, no_wait_after=no_wait_after, timeout=timeout)

    element.type = type_mocker

    # ElementHandle
    async def mock_query_selector(selector: str) -> Optional[ElementHandle]:
        _element = await element.origin_query_selector(selector)
        if _element:
            mock_element_handle(_element, page)
        return _element

    element.origin_query_selector = element.query_selector
    element.query_selector = mock_query_selector

    async def mock_query_selector_all(selector: str) -> List[ElementHandle]:
        elements = await element.origin_query_selector_all(selector)
        for _element in elements:
            mock_element_handle(_element, page)
        return elements

    element.origin_query_selector_all = element.query_selector_all
    element.query_selector_all = mock_query_selector_all

    async def mock_wait_for_selector(selector: str, state: Optional[Literal["attached", "detached", "hidden", "visible"]] = None, timeout: Optional[float] = None, strict: Optional[bool] = False) -> Optional[ElementHandle]:
        _element = await element.origin_wait_for_selector(selector, state=state, strict=strict, timeout=timeout)
        if _element:
            mock_element_handle(_element, page)
        return _element

    element.origin_wait_for_selector = element.wait_for_selector
    element.wait_for_selector = mock_wait_for_selector

    # JsHandle
    async def mock_evaluate_handle(expression: str, arg: Optional[Any] = None) -> JSHandle:
        _js_handle = await element.origin_evaluate_handle(expression, arg=arg)
        js_handle.mock_js_handle(_js_handle, page)
        return _js_handle

    element.origin_evaluate_handle = element.evaluate_handle
    element.evaluate_handle = mock_evaluate_handle


class ElementHandleMock:
    def __init__(self, element: ElementHandle, page: Page):
        self.element = element
        self.page = page

    async def click(self, button: Optional[str] = "left", click_count: Optional[int] = 1, delay: Optional[int] = 20, force: Optional[bool] = False, modifiers: Optional[list] = None, no_wait_after: Optional[bool] = False, position: Optional[dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        modifiers = modifiers or []
        position = position or {}

        if not force:
            await self.element.wait_for_element_state("editable", timeout=timeout)

        if not trial:
            if self.page.scroll_into_view:
                await self.element.scroll_into_view_if_needed(timeout=timeout)

            bounding_box = await self.element.bounding_box()
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

    async def dblclick(self, button: Optional[str] = "left", delay: Optional[int] = 20, force: Optional[bool] = False, modifiers: Optional[list] = None, no_wait_after: Optional[bool] = False, position: Optional[dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        modifiers = modifiers or []
        position = position or {}

        if not force:
            await self.element.wait_for_element_state("editable", timeout=timeout)

        if not trial:
            if self.page.scroll_into_view:
                await self.element.scroll_into_view_if_needed(timeout=timeout)

            bounding_box = await self.element.bounding_box()
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

    async def check(self, force: Optional[bool] = False, no_wait_after: Optional[bool] = False, position: Optional[dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        position = position or {}

        if not force:
            await self.element.wait_for_element_state("editable", timeout=timeout)

        if await self.element.is_checked():
            return

        if not trial:
            if self.page.scroll_into_view:
                await self.element.scroll_into_view_if_needed(timeout=timeout)

            bounding_box = await self.element.bounding_box()
            x, y, width, height = bounding_box.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await self.page.mouse.click(x, y, button="left", click_count=1, delay=20)

            assert await self.element.is_checked()

    async def uncheck(self, force: Optional[bool] = False, no_wait_after: Optional[bool] = False, position: Optional[dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        position = position or {}

        if not force:
            await self.element.wait_for_element_state("editable", timeout=timeout)

        if not await self.element.is_checked():
            return

        if not trial:
            if self.page.scroll_into_view:
                await self.element.scroll_into_view_if_needed(timeout=timeout)

            bounding_box = await self.element.bounding_box()
            x, y, width, height = bounding_box.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await self.page.mouse.click(x, y, button="left", click_count=1, delay=20)

            assert not await self.element.is_checked()

    async def set_checked(self, checked: Optional[bool] = False, force: Optional[bool] = False, no_wait_after: Optional[bool] = False, position: Optional[dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        position = position or {}

        if not force:
            await self.element.wait_for_element_state("editable", timeout=timeout)

        if await self.element.is_checked() == checked:
            return

        if not trial:
            if self.page.scroll_into_view:
                await self.element.scroll_into_view_if_needed(timeout=timeout)

            bounding_box = await self.element.bounding_box()
            x, y, width, height = bounding_box.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await self.page.mouse.click(x, y, button="left", click_count=1, delay=20)

            assert await self.element.is_checked()

    async def hover(self, force: Optional[bool] = False, modifiers: Optional[list] = None, position: Optional[dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        modifiers = modifiers or []
        position = position or {}

        if not force:
            await self.element.wait_for_element_state("editable", timeout=timeout)

        if not trial:
            if self.page.scroll_into_view:
                await self.element.scroll_into_view_if_needed(timeout=timeout)

            bounding_box = await self.element.bounding_box()
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

    async def type(self, text: str, delay: Optional[int] = 200, no_wait_after: Optional[bool] = False, timeout: Optional[float] = None) -> None:
        await self.element.wait_for_element_state("editable", timeout=timeout)

        if self.page.scroll_into_view:
            await self.element.scroll_into_view_if_needed(timeout=timeout)

        bounding_box = await self.element.bounding_box()
        x, y, width, height = bounding_box.values()

        x, y = x + width // 2, y + height // 2

        await self.page.mouse.click(x, y, delay=delay)

        await self.page.keyboard.type(text, delay=delay)
