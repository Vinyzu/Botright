from __future__ import annotations

from typing import Optional

from playwright.async_api import Locator, Page, JSHandle, ElementHandle, FrameLocator

from . import element_handle, frame_locator, js_handle


def attach_dyn_prop(locator: Locator, prop_name: str, prop: property) -> None:
    """Attach property proper to instance with name prop_name.

    Reference:
      * https://stackoverflow.com/a/1355444/509706
      * https://stackoverflow.com/questions/48448074
    """
    class_name = locator.__class__.__name__ + "Child"
    child_class = type(class_name, (locator.__class__,), {prop_name: prop})

    locator.__class__ = child_class


def mock_locator(locator: Locator, page: Page) -> None:
    locator_mocker = LocatorMock(locator, page)

    async def click_mocker(button="left", click_count: Optional[int] = 1, delay: Optional[int] = 20, force: Optional[bool] = False, modifiers: Optional[list] = None, no_wait_after: Optional[bool] = False, position: Optional[dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        await locator_mocker.click(button=button, click_count=click_count, delay=delay, force=force, modifiers=modifiers, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    locator.click = click_mocker

    async def dblclick_mocker(button="left", delay: Optional[int] = 20, force: Optional[bool] = False, modifiers: Optional[list] = None, no_wait_after: Optional[bool] = False, position: Optional[dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        await locator_mocker.dblclick(button=button, delay=delay, force=force, modifiers=modifiers, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    locator.dblclick = dblclick_mocker

    async def check_mocker(force: Optional[bool] = False, no_wait_after: Optional[bool] = False, position: Optional[dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        await locator_mocker.check(force=force, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    locator.check = check_mocker

    async def uncheck_mocker(force: Optional[bool] = False, no_wait_after: Optional[bool] = False, position: Optional[dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        await locator_mocker.uncheck(force=force, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    locator.uncheck = uncheck_mocker

    async def set_checked_mocker(checked: Optional[bool] = False, force: Optional[bool] = False, no_wait_after: Optional[bool] = False, position: Optional[dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        await locator_mocker.set_checked(checked=checked, force=force, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    locator.set_checked = set_checked_mocker

    async def hover_mocker(force: Optional[bool] = False, modifiers: Optional[list] = None, position: Optional[dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        await locator_mocker.hover(force=force, modifiers=modifiers, position=position, timeout=timeout, trial=trial)

    locator.hover = hover_mocker

    async def type_mocker(text: str, delay: Optional[int] = 200, no_wait_after: Optional[bool] = False, timeout: Optional[float] = None) -> None:
        await Locator.type(locator, text, delay=delay, no_wait_after=no_wait_after, timeout=timeout)

    locator.type = type_mocker

    # JsHandle
    async def mock_evaluate_handle(expression, arg=None) -> JSHandle:
        _js_handle = await locator.origin_evaluate_handle(expression, arg=arg)
        js_handle.mock_js_handle(_js_handle, locator.page)
        return _js_handle

    locator.origin_evaluate_handle = locator.evaluate_handle
    locator.evaluate_handle = mock_evaluate_handle

    # FrameLocator
    def mock_frame_locator_func(selector) -> FrameLocator:
        _frame_locator = locator.origin_frame_locator(selector)
        frame_locator.mock_frame_locator(_frame_locator, page)
        return _frame_locator

    locator.origin_frame_locator = locator.frame_locator
    locator.frame_locator = mock_frame_locator_func

    # ElementHandle
    async def element_handle_mocker(timeout: Optional[float] = None) -> ElementHandle:
        element = await locator.origin_element_handle(timeout=timeout)
        element_handle.mock_element_handle(element, page)
        return element

    locator.origin_element_handle = locator.element_handle
    locator.element_handle = element_handle_mocker

    # Locator
    def nth_mocker(index) -> Locator:
        _locator = locator.origin_nth(index)
        mock_locator(_locator, page)
        return _locator

    locator.origin_nth = locator.nth
    locator.nth = nth_mocker

    @property
    def first_mocker(self) -> Locator:
        _locator = locator.origin_first
        mock_locator(_locator, page)
        return _locator

    @property
    def last_mocker(self) -> Locator:
        _locator = locator.origin_last
        mock_locator(_locator, page)
        return _locator

    locator.origin_first = locator.first
    locator.origin_last = locator.last

    attach_dyn_prop(locator, "first", first_mocker)
    attach_dyn_prop(locator, "last", last_mocker)


class LocatorMock:
    def __init__(self, locator: Locator, page: Page):
        self.locator = locator
        self.page = page

    async def click(self, button="left", click_count: Optional[int] = 1, delay: Optional[int] = 20, force: Optional[bool] = False, modifiers: Optional[list] = None, no_wait_after: Optional[bool] = False, position: Optional[dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        modifiers = modifiers or []
        position = position or {}

        if not force:
            await self.locator.wait_for(state="attached", timeout=timeout)

        if not trial:
            if self.page.scroll_into_view:
                await self.locator.scroll_into_view_if_needed(timeout=timeout)

            bounding_box = await self.locator.bounding_box()
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

    async def dblclick(self, button="left", delay: Optional[int] = 20, force: Optional[bool] = False, modifiers: Optional[list] = None, no_wait_after: Optional[bool] = False, position: Optional[dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        modifiers = modifiers or []
        position = position or {}

        if not force:
            await self.locator.wait_for(state="attached", timeout=timeout)

        if not trial:
            if self.page.scroll_into_view:
                await self.locator.scroll_into_view_if_needed(timeout=timeout)

            bounding_box = await self.locator.bounding_box()
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

    async def check(self, force: Optional[bool] = False, no_wait_after: Optional[bool] = False, position: Optional[dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        position = position or {}

        if not force:
            await self.locator.wait_for(state="attached", timeout=timeout)

        if await self.locator.is_checked():
            return

        if not trial:
            if self.page.scroll_into_view:
                await self.locator.scroll_into_view_if_needed(timeout=timeout)

            bounding_box = await self.locator.bounding_box()
            x, y, width, height = bounding_box.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await self.page.mouse.click(x, y, button="left", click_count=1, delay=20)

            assert await self.locator.is_checked()

    async def uncheck(self, force: Optional[bool] = False, no_wait_after: Optional[bool] = False, position: Optional[dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        position = position or {}

        if not force:
            await self.locator.wait_for(state="attached", timeout=timeout)

        if not await self.locator.is_checked():
            return

        if not trial:
            if self.page.scroll_into_view:
                await self.locator.scroll_into_view_if_needed(timeout=timeout)

            bounding_box = await self.locator.bounding_box()
            x, y, width, height = bounding_box.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await self.page.mouse.click(x, y, button="left", click_count=1, delay=20)

            assert not await self.locator.is_checked()

    async def set_checked(self, checked: Optional[bool] = False, force: Optional[bool] = False, no_wait_after: Optional[bool] = False, position: Optional[dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        position = position or {}

        if not force:
            await self.locator.wait_for(state="attached", timeout=timeout)

        if await self.locator.is_checked() == checked:
            return

        if not trial:
            if self.page.scroll_into_view:
                await self.locator.scroll_into_view_if_needed(timeout=timeout)

            bounding_box = await self.locator.bounding_box()
            x, y, width, height = bounding_box.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await self.page.mouse.click(x, y, button="left", click_count=1, delay=20)

            assert await self.locator.is_checked()

    async def hover(self, force: Optional[bool] = False, modifiers: Optional[list] = None, position: Optional[dict] = None, timeout: Optional[float] = None, trial: Optional[bool] = False) -> None:
        modifiers = modifiers or []
        position = position or {}

        if not force:
            await self.locator.wait_for(state="attached", timeout=timeout)

        if not trial:
            if self.page.scroll_into_view:
                await self.locator.scroll_into_view_if_needed(timeout=timeout)

            bounding_box = await self.locator.bounding_box()
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
        await self.locator.wait_for(state="attached", timeout=timeout)

        if self.page.scroll_into_view:
            await self.locator.scroll_into_view_if_needed(timeout=timeout)

        bounding_box = await self.locator.bounding_box()
        x, y, width, height = bounding_box.values()

        x, y = x + width // 2, y + height // 2

        await self.click(delay=delay)

        await self.page.keyboard.type(text, delay=delay)
