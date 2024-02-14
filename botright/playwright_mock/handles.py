from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Literal, Optional, Sequence, Union

# from undetected_playwright.async_api import Position, ElementHandle as PlaywrightElementHandle, JSHandle as PlaywrightJSHandle, Error as PlaywrightError
from playwright.async_api import ElementHandle as PlaywrightElementHandle
from playwright.async_api import Error as PlaywrightError
from playwright.async_api import JSHandle as PlaywrightJSHandle
from playwright.async_api import Position

if TYPE_CHECKING:
    from . import Frame, Page


class JSHandle(PlaywrightJSHandle):
    def __init__(self, js_handle: PlaywrightJSHandle, page: Page):
        super().__init__(js_handle)
        self._impl_obj = js_handle._impl_obj

        self._page = page
        self._origin_as_element = js_handle.as_element

    def as_element(self) -> Optional[ElementHandle]:  # Optional[ElementHandle]:
        from . import ElementHandle

        _element_handle = self._origin_as_element()
        if not _element_handle:
            return None

        element_handle = ElementHandle(_element_handle, self._page)
        return element_handle


class ElementHandle(JSHandle, PlaywrightElementHandle):
    def __init__(self, element: PlaywrightElementHandle, page: Page):
        super().__init__(element, page)
        self._impl_obj = element._impl_obj
        self._page = page

        self._origin_owner_frame = element.owner_frame
        self._origin_content_frame = element.content_frame
        self._origin_query_selector = element.query_selector
        self._origin_query_selector_all = element.query_selector_all
        self._origin_wait_for_selector = element.wait_for_selector
        self._origin_evaluate_handle = element.evaluate_handle

        self._origin_click = element.click

    async def owner_frame(self) -> Optional[Frame]:
        from . import Frame

        _frame = await self._origin_owner_frame()
        if not _frame:
            return None

        if isinstance(_frame, Frame):
            return _frame

        frame = Frame(_frame, self._page)
        return frame

    async def content_frame(self) -> Optional[Frame]:
        from . import Frame

        _frame = await self._origin_content_frame()
        if not _frame:
            return None

        if isinstance(_frame, Frame):
            return _frame

        frame = Frame(_frame, self._page)
        return frame

    # ElementHandle
    async def query_selector(self, selector: str) -> Optional[ElementHandle]:
        from . import ElementHandle

        _element_handle = await self._origin_query_selector(selector=selector)
        if not _element_handle:
            return None

        element_handle = ElementHandle(_element_handle, self._page)
        return element_handle

    async def query_selector_all(self, selector: str) -> List[ElementHandle]:  # type: ignore
        from . import ElementHandle

        _element_handles = await self._origin_query_selector_all(selector=selector)
        element_handles = []

        for _element_handle in _element_handles:
            element_handle = ElementHandle(_element_handle, self._page)
            element_handles.append(element_handle)

        return element_handles

    async def wait_for_selector(
        self, selector: str, state: Optional[Literal["attached", "detached", "hidden", "visible"]] = None, timeout: Optional[float] = None, strict: Optional[bool] = False
    ) -> Optional[ElementHandle]:
        from . import ElementHandle

        _element_handle = await self._origin_wait_for_selector(selector=selector, state=state, strict=strict, timeout=timeout)
        if not _element_handle:
            return None

        element_handle = ElementHandle(_element_handle, self._page)
        return element_handle

    # JsHandle
    async def evaluate_handle(self, expression: str, arg: Optional[Any] = None) -> Union[JSHandle, ElementHandle]:
        _js_handle = await self._origin_evaluate_handle(expression=expression, arg=arg)

        if isinstance(_js_handle, PlaywrightElementHandle):
            element_handle = ElementHandle(_js_handle, self._page)
            return element_handle
        else:
            js_handle = JSHandle(_js_handle, self._page)
            return js_handle

    async def click(
        self,
        modifiers: Optional[Sequence[Literal["Alt", "Control", "Meta", "Shift"]]] = None,
        position: Optional[Position] = None,
        delay: Optional[float] = None,
        button: Optional[Literal["left", "middle", "right"]] = None,
        click_count: Optional[int] = None,
        timeout: Optional[float] = None,
        force: Optional[bool] = None,
        no_wait_after: Optional[bool] = None,
        trial: Optional[bool] = None,
    ) -> None:
        modifiers = modifiers or []
        position = position or Position(x=0, y=0)

        if not force:
            await self.wait_for_element_state("editable", timeout=timeout)

        if not trial:
            bounding_box = await self.bounding_box()
            if not bounding_box:
                raise PlaywrightError("Element is not visible")

            if self._page.scroll_into_view:
                await self.scroll_into_view_if_needed(timeout=timeout)

            try:
                is_visible = await self.is_visible()
            except PlaywrightError:
                is_visible = True

            if not is_visible:
                raise PlaywrightError("Element is outside of the viewport")

            x, y, width, height = bounding_box["x"], bounding_box["y"], bounding_box["width"], bounding_box["height"]
            if not any(position.values()):
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            for modifier in modifiers:
                await self._page.keyboard.down(modifier)

            await self._page.mouse.click(x, y, button=button, click_count=click_count, delay=delay)

            for modifier in modifiers:
                await self._page.keyboard.up(modifier)

    async def dblclick(
        self,
        modifiers: Optional[Sequence[Literal["Alt", "Control", "Meta", "Shift"]]] = None,
        position: Optional[Position] = None,
        delay: Optional[float] = None,
        button: Optional[Literal["left", "middle", "right"]] = None,
        timeout: Optional[float] = None,
        force: Optional[bool] = None,
        no_wait_after: Optional[bool] = None,
        trial: Optional[bool] = None,
    ) -> None:
        modifiers = modifiers or []
        position = position or Position(x=0, y=0)

        if not force:
            await self.wait_for_element_state("editable", timeout=timeout)

        if not trial:
            bounding_box = await self.bounding_box()
            if not bounding_box:
                raise PlaywrightError("Element is not visible")

            if self._page.scroll_into_view:
                await self.scroll_into_view_if_needed(timeout=timeout)

            if not await self.is_visible():
                raise PlaywrightError("Element is outside of the viewport")

            x, y, width, height = bounding_box["x"], bounding_box["y"], bounding_box["width"], bounding_box["height"]
            if not any(position.values()):
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            for modifier in modifiers:
                await self._page.keyboard.down(modifier)

            await self._page.mouse.dblclick(x, y, button=button, delay=delay)

            for modifier in modifiers:
                await self._page.keyboard.up(modifier)

    async def check(
        self, position: Optional[Position] = None, timeout: Optional[float] = None, force: Optional[bool] = None, no_wait_after: Optional[bool] = None, trial: Optional[bool] = None
    ) -> None:
        position = position or Position(x=0, y=0)

        if not force:
            await self.wait_for_element_state("editable", timeout=timeout)

        if await self.is_checked():
            return

        if not trial:
            bounding_box = await self.bounding_box()
            if not bounding_box:
                raise PlaywrightError("Element is not visible")

            if self._page.scroll_into_view:
                await self.scroll_into_view_if_needed(timeout=timeout)

            if not await self.is_visible():
                raise PlaywrightError("Element is outside of the viewport")

            x, y, width, height = bounding_box["x"], bounding_box["y"], bounding_box["width"], bounding_box["height"]
            if not any(position.values()):
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await self._page.mouse.click(x, y, button="left", click_count=1, delay=20)

            assert await self.is_checked(), PlaywrightError

    async def uncheck(
        self, position: Optional[Position] = None, timeout: Optional[float] = None, force: Optional[bool] = None, no_wait_after: Optional[bool] = None, trial: Optional[bool] = None
    ) -> None:
        position = position or Position(x=0, y=0)

        if not force:
            await self.wait_for_element_state("editable", timeout=timeout)

        if not await self.is_checked():
            return

        if not trial:
            bounding_box = await self.bounding_box()
            if not bounding_box:
                raise PlaywrightError("Element is not visible")

            if self._page.scroll_into_view:
                await self.scroll_into_view_if_needed(timeout=timeout)

            if not await self.is_visible():
                raise PlaywrightError("Element is outside of the viewport")

            x, y, width, height = bounding_box["x"], bounding_box["y"], bounding_box["width"], bounding_box["height"]
            if not any(position.values()):
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await self._page.mouse.click(x, y, button="left", click_count=1, delay=20)

            assert not await self.is_checked()

    async def set_checked(
        self, checked: bool, position: Optional[Position] = None, timeout: Optional[float] = None, force: Optional[bool] = None, no_wait_after: Optional[bool] = None, trial: Optional[bool] = None
    ) -> None:
        position = position or Position(x=0, y=0)

        if not force:
            await self.wait_for_element_state("editable", timeout=timeout)

        if await self.is_checked() == checked:
            return

        if not trial:
            bounding_box = await self.bounding_box()
            if not bounding_box:
                raise PlaywrightError("Element is not visible")

            if self._page.scroll_into_view:
                await self.scroll_into_view_if_needed(timeout=timeout)

            if not await self.is_visible():
                raise PlaywrightError("Element is outside of the viewport")

            x, y, width, height = bounding_box["x"], bounding_box["y"], bounding_box["width"], bounding_box["height"]
            if not any(position.values()):
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await self._page.mouse.click(x, y, button="left", click_count=1, delay=20)

            assert await self.is_checked() == checked

    async def hover(
        self,
        modifiers: Optional[Sequence[Literal["Alt", "Control", "Meta", "Shift"]]] = None,
        position: Optional[Position] = None,
        timeout: Optional[float] = None,
        no_wait_after: Optional[bool] = None,
        force: Optional[bool] = None,
        trial: Optional[bool] = None,
    ) -> None:
        modifiers = modifiers or []
        position = position or Position(x=0, y=0)

        if not force:
            await self.wait_for_element_state("editable", timeout=timeout)

        if not trial:
            bounding_box = await self.bounding_box()
            if not bounding_box:
                raise PlaywrightError("Element is not visible")

            if self._page.scroll_into_view:
                await self.scroll_into_view_if_needed(timeout=timeout)

            if not await self.is_visible():
                raise PlaywrightError("Element is outside of the viewport")

            x, y, width, height = bounding_box["x"], bounding_box["y"], bounding_box["width"], bounding_box["height"]
            if not any(position.values()):
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            for modifier in modifiers:
                await self._page.keyboard.down(modifier)

            await self._page.mouse.move(x, y)

            for modifier in modifiers:
                await self._page.keyboard.up(modifier)

    async def type(self, text: str, delay: Optional[float] = None, timeout: Optional[float] = None, no_wait_after: Optional[bool] = None) -> None:
        await self.wait_for_element_state("editable", timeout=timeout)

        bounding_box = await self.bounding_box()
        if not bounding_box:
            raise PlaywrightError("Element is not visible")

        if self._page.scroll_into_view:
            await self.scroll_into_view_if_needed(timeout=timeout)

        x, y, width, height = bounding_box["x"], bounding_box["y"], bounding_box["width"], bounding_box["height"]

        x, y = x + width // 2, y + height // 2

        await self._page.mouse.click(x, y, delay=delay)

        await self._page.keyboard.type(text, delay=delay)
