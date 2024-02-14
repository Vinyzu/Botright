from __future__ import annotations

from pathlib import Path
from re import Pattern
from typing import TYPE_CHECKING, Any, List, Literal, Optional, Sequence, Union

# from undetected_playwright.async_api import Position, Locator as PlaywrightLocator, Frame as PlaywrightFrame, ElementHandle as PlaywrightElementHandle, Error as PlaywrightError
from playwright.async_api import ElementHandle as PlaywrightElementHandle
from playwright.async_api import Error as PlaywrightError
from playwright.async_api import Frame as PlaywrightFrame
from playwright.async_api import Locator as PlaywrightLocator
from playwright.async_api import Position

if TYPE_CHECKING:
    from . import ElementHandle, FrameLocator, JSHandle, Locator, Page


class Frame(PlaywrightFrame):
    def __init__(self, frame: PlaywrightFrame, page: Page) -> None:
        super().__init__(frame)
        self._impl_obj = frame._impl_obj
        self._page = page
        self._frame = frame
        self._parent_frame = frame.parent_frame

        self._origin_query_selector = frame.query_selector
        self._origin_query_selector_all = frame.query_selector_all
        self._origin_wait_for_selector = frame.wait_for_selector
        self._origin_add_script_tag = frame.add_script_tag
        self._origin_add_style_tag = frame.add_style_tag
        self._origin_frame_element = frame.frame_element

        self._origin_evaluate_handle = frame.evaluate_handle
        self._origin_wait_for_function = frame.wait_for_function
        self._origin_frame_locator = frame.frame_locator
        self._origin_locator = frame.locator

        self._child_frames = []
        for frame in frame.child_frames:
            self._child_frames.append(Frame(frame, page))

    def __eq__(self, obj):
        if isinstance(obj, Frame):
            if obj._frame == self._frame:  # and (obj._page == self._page)
                return True
        return False

    @property
    def page(self):
        return self._page

    @property
    def child_frames(self):
        return self._child_frames

    @property
    def parent_frame(self):
        if not self._parent_frame:
            return None

        return Frame(self._parent_frame, self._page)

    # ElementHandle
    async def query_selector(self, selector: str, strict: Optional[bool] = False) -> Optional[ElementHandle]:
        from . import ElementHandle

        _element_handle = await self._origin_query_selector(selector, strict=strict)
        if not _element_handle:
            return None

        element_handle = ElementHandle(_element_handle, self._page)
        return element_handle

    async def query_selector_all(self, selector: str) -> List[ElementHandle]:  # type: ignore
        from . import ElementHandle

        _element_handles = await self._origin_query_selector_all(selector)
        element_handles = []

        for _element_handle in _element_handles:
            element_handle = ElementHandle(_element_handle, self._page)
            element_handles.append(element_handle)

        return element_handles

    async def wait_for_selector(
        self, selector: str, state: Optional[Literal["attached", "detached", "hidden", "visible"]] = None, strict: Optional[bool] = False, timeout: Optional[float] = None
    ) -> Optional[ElementHandle]:
        from . import ElementHandle

        _element_handle = await self._origin_wait_for_selector(selector, state=state, strict=strict, timeout=timeout)
        if not _element_handle:
            return None

        element_handle = ElementHandle(_element_handle, self._page)
        return element_handle

    async def add_script_tag(self, content: Optional[str] = "", path: Optional[Union[str, Path]] = "", type: Optional[str] = "", url: Optional[str] = "") -> ElementHandle:
        from . import ElementHandle

        _element_handle = await self._origin_add_script_tag(content=content, path=path, type=type, url=url)

        element_handle = ElementHandle(_element_handle, self._page)
        return element_handle

    async def add_style_tag(self, content: Optional[str] = "", path: Optional[Union[str, Path]] = "", url: Optional[str] = "") -> ElementHandle:
        from . import ElementHandle

        _element_handle = await self._origin_add_script_tag(content=content, path=path, url=url)

        element_handle = ElementHandle(_element_handle, self._page)
        return element_handle

    async def frame_element(self) -> ElementHandle:
        from . import ElementHandle

        _element_handle = await self._origin_frame_element()

        element_handle = ElementHandle(_element_handle, self._page)
        return element_handle

    # JsHandle
    async def evaluate_handle(self, expression: str, arg: Optional[Any] = None) -> Union[JSHandle, ElementHandle]:
        from . import ElementHandle, JSHandle

        _js_handle = await self._origin_evaluate_handle(expression, arg=arg)

        if isinstance(_js_handle, PlaywrightElementHandle):
            element_handle = ElementHandle(_js_handle, self._page)
            return element_handle
        else:
            js_handle = JSHandle(_js_handle, self._page)
            return js_handle

    async def wait_for_function(self, expression: str, arg: Optional[Any] = None, polling: Optional[Union[float, Literal["raf"]]] = "raf", timeout: Optional[float] = None) -> JSHandle:
        from . import JSHandle

        _js_handle = await self._origin_wait_for_function(expression, arg=arg, polling=polling, timeout=timeout)
        js_handle = JSHandle(_js_handle, self._page)
        return js_handle

    # FrameLocator
    def frame_locator(self, selector: str) -> FrameLocator:
        from . import FrameLocator

        _frame_locator = self._origin_frame_locator(selector)
        frame_locator = FrameLocator(_frame_locator, self._page)
        return frame_locator

    # Locator
    def locator(
        self,
        selector: str,
        has: Optional[PlaywrightLocator] = None,
        has_not: Optional[PlaywrightLocator] = None,
        has_text: Optional[Union[str, Pattern[str]]] = "",
        has_not_text: Optional[Union[str, Pattern[str]]] = "",
    ) -> Locator:
        from . import Locator

        _locator = self._origin_locator(selector, has=has, has_not=has_not, has_text=has_text, has_not_text=has_not_text)
        locator = Locator(_locator, self._page)
        return locator

    async def click(
        self,
        selector: str,
        button: Optional[Literal["left", "middle", "right"]] = "left",
        click_count: Optional[int] = 1,
        delay: Optional[float] = 20.0,
        force: Optional[bool] = False,
        modifiers: Optional[Sequence[Literal["Alt", "Control", "Meta", "Shift"]]] = None,
        no_wait_after: Optional[bool] = False,
        position: Optional[Position] = None,
        timeout: Optional[float] = None,
        trial: Optional[bool] = False,
        strict: Optional[bool] = None,
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

            if self._page.scroll_into_view:
                await element.scroll_into_view_if_needed(timeout=timeout)

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
        selector: str,
        button: Optional[Literal["left", "middle", "right"]] = "left",
        delay: Optional[float] = 20.0,
        force: Optional[bool] = False,
        modifiers: Optional[Sequence[Literal["Alt", "Control", "Meta", "Shift"]]] = None,
        no_wait_after: Optional[bool] = False,
        position: Optional[Position] = None,
        timeout: Optional[float] = None,
        trial: Optional[bool] = False,
        strict: Optional[bool] = None,
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

            if self._page.scroll_into_view:
                await element.scroll_into_view_if_needed(timeout=timeout)

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
        self,
        selector: str,
        position: Optional[Position] = None,
        timeout: Optional[float] = None,
        force: Optional[bool] = None,
        no_wait_after: Optional[bool] = None,
        trial: Optional[bool] = None,
        strict: Optional[bool] = False,
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

            if self._page.scroll_into_view:
                await element.scroll_into_view_if_needed(timeout=timeout)

            x, y, width, height = bounding_box["x"], bounding_box["y"], bounding_box["width"], bounding_box["height"]
            if not any(position.values()):
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await self._page.mouse.click(x, y, button="left", click_count=1, delay=20)

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

            if self._page.scroll_into_view:
                await element.scroll_into_view_if_needed(timeout=timeout)

            x, y, width, height = bounding_box["x"], bounding_box["y"], bounding_box["width"], bounding_box["height"]
            if not any(position.values()):
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await self._page.mouse.click(x, y, button="left", click_count=1, delay=20)

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

            if self._page.scroll_into_view:
                await element.scroll_into_view_if_needed(timeout=timeout)

            x, y, width, height = bounding_box["x"], bounding_box["y"], bounding_box["width"], bounding_box["height"]
            if not any(position.values()):
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await self._page.mouse.click(x, y, button="left", click_count=1, delay=20)

            assert await element.is_checked(), PlaywrightError

    async def hover(
        self,
        selector: str,
        force: Optional[bool] = False,
        modifiers: Optional[Sequence[Literal["Alt", "Control", "Meta", "Shift"]]] = None,
        position: Optional[Position] = None,
        strict: Optional[bool] = False,
        timeout: Optional[float] = None,
        trial: Optional[bool] = False,
        no_wait_after: Optional[bool] = None,
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

            if self._page.scroll_into_view:
                await element.scroll_into_view_if_needed(timeout=timeout)

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

    async def type(self, selector: str, text: str, delay: Optional[float] = 200.0, no_wait_after: Optional[bool] = False, timeout: Optional[float] = None, strict: Optional[bool] = False) -> None:
        element = await self.wait_for_selector(selector, state="visible", strict=strict, timeout=timeout)
        if not element:
            raise PlaywrightError("Element is not attached to the DOM")

        await element.wait_for_element_state("editable", timeout=timeout)

        bounding_box = await element.bounding_box()
        if not bounding_box:
            raise PlaywrightError("Element is not visible")

        if self._page.scroll_into_view:
            await element.scroll_into_view_if_needed(timeout=timeout)

        x, y, width, height = bounding_box["x"], bounding_box["y"], bounding_box["width"], bounding_box["height"]
        x, y = x + width // 2, y + height // 2

        await self._page.mouse.click(x, y, button="left", click_count=1, delay=20)

        await self._page.mouse.click(x, y, delay=delay)

        await self._page.keyboard.type(text, delay=delay)
