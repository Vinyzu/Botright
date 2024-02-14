from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, Optional, Pattern, Sequence, Union

# from undetected_playwright.async_api import Position, Locator as PlaywrightLocator, ElementHandle as PlaywrightElementHandle, Error as PlaywrightError
from playwright.async_api import ElementHandle as PlaywrightElementHandle
from playwright.async_api import Error as PlaywrightError
from playwright.async_api import Locator as PlaywrightLocator
from playwright.async_api import Position

if TYPE_CHECKING:
    from . import ElementHandle, FrameLocator, JSHandle, Page


class Locator(PlaywrightLocator):
    def __init__(self, locator: PlaywrightLocator, page: Page):
        super().__init__(locator)
        self._impl_obj = locator._impl_obj
        self._page = page
        self._origin_first = None
        self._origin_last = None

        self.origin_locator = locator.locator
        self.origin_evaluate_handle = locator.evaluate_handle
        self.origin_frame_locator = locator.frame_locator
        self.origin_element_handle = locator.element_handle
        self.origin_nth = locator.nth

        self.origin_first = locator.first  # type: ignore
        self.origin_last = locator.last  # type: ignore

        # self._attach_dyn_prop(locator, "first", self.first)
        # self._attach_dyn_prop(locator, "last", self.last)

    @property
    def page(self) -> Page:
        return self._page

    def locator(
        self,
        selector_or_locator: Union[str, PlaywrightLocator],
        has_text: Optional[Union[str, Pattern[str]]] = None,
        has_not_text: Optional[Union[str, Pattern[str]]] = None,
        has: Optional[PlaywrightLocator] = None,
        has_not: Optional[PlaywrightLocator] = None,
    ) -> Locator:
        _locator = self.origin_locator(selector_or_locator, has=has, has_not=has_not, has_text=has_text, has_not_text=has_not_text)
        locator = Locator(_locator, self._page)
        return locator

    # JsHandle
    async def evaluate_handle(self, expression: str, arg: Optional[Any] = None, timeout: Optional[float] = None) -> Union[JSHandle, ElementHandle]:
        from . import ElementHandle, JSHandle

        _js_handle = await self.origin_evaluate_handle(expression=expression, arg=arg, timeout=timeout)
        if isinstance(_js_handle, PlaywrightElementHandle):
            element_handle = ElementHandle(_js_handle, self._page)
            return element_handle
        else:
            js_handle = JSHandle(_js_handle, self._page)
            return js_handle

    # FrameLocator
    def frame_locator(self, selector) -> FrameLocator:
        from . import FrameLocator

        _frame_locator = self.origin_frame_locator(selector=selector)
        frame_locator = FrameLocator(_frame_locator, self._page)
        return frame_locator

    # ElementHandle
    async def element_handle(self, timeout: Optional[float] = None) -> ElementHandle:
        from . import ElementHandle

        _element = await self.origin_element_handle(timeout=timeout)
        element = ElementHandle(_element, self._page)
        return element

    # Locator
    def nth(self, index) -> Locator:
        _locator = self.origin_nth(index=index)
        locator = Locator(_locator, self._page)
        return locator

    @property
    def first(self) -> Locator:
        _locator = self.origin_first

        locator = Locator(_locator, self._page)
        return locator

    @property
    def origin_first(self):
        return self._origin_first

    @origin_first.setter
    def origin_first(self, value):
        self._origin_first = value

    @property
    def last(self) -> Locator:
        _locator = self.origin_last
        locator = Locator(_locator, self._page)
        return locator

    @property
    def origin_last(self):
        return self._origin_last

    @origin_last.setter
    def origin_last(self, value):
        self._origin_last = value

    async def click(
        self,
        button: Optional[Literal["left", "middle", "right"]] = "left",
        click_count: Optional[int] = 1,
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

        if not force:
            await self.wait_for(state="attached", timeout=timeout)

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

            await self._page.mouse.click(x=int(x), y=y, button=button, click_count=click_count, delay=delay)

            for modifier in modifiers:
                await self._page.keyboard.up(modifier)

    async def dblclick(
        self,
        modifiers: Optional[Sequence[Literal["Alt", "Control", "Meta", "Shift"]]] = None,
        position: Optional[Position] = None,
        delay: Optional[float] = 20.0,
        button: Optional[Literal["left", "middle", "right"]] = None,
        timeout: Optional[float] = None,
        force: Optional[bool] = None,
        no_wait_after: Optional[bool] = None,
        trial: Optional[bool] = None,
    ) -> None:
        modifiers = modifiers or []
        position = position or Position(x=0, y=0)

        if not force:
            await self.wait_for(state="attached", timeout=timeout)

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
            await self.wait_for(state="attached", timeout=timeout)

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

            assert await self.is_checked()

    async def uncheck(
        self, force: Optional[bool] = False, no_wait_after: Optional[bool] = False, position: Optional[Position] = None, timeout: Optional[float] = None, trial: Optional[bool] = False
    ) -> None:
        position = position or Position(x=0, y=0)

        if not force:
            await self.wait_for(state="attached", timeout=timeout)

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
        self, checked: bool, force: Optional[bool] = False, no_wait_after: Optional[bool] = False, position: Optional[Position] = None, timeout: Optional[float] = None, trial: Optional[bool] = False
    ) -> None:
        position = position or Position(x=0, y=0)

        if not force:
            await self.wait_for(state="attached", timeout=timeout)

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
        force: Optional[bool] = False,
        modifiers: Optional[Sequence[Literal["Alt", "Control", "Meta", "Shift"]]] = None,
        position: Optional[Position] = None,
        timeout: Optional[float] = None,
        trial: Optional[bool] = False,
        no_wait_after: Optional[bool] = False,
    ) -> None:
        modifiers = modifiers or []
        position = position or Position(x=0, y=0)

        if not force:
            await self.wait_for(state="attached", timeout=timeout)

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

    async def type(self, text: str, delay: Optional[float] = 200.0, no_wait_after: Optional[bool] = False, timeout: Optional[float] = None) -> None:
        await self.wait_for(state="attached", timeout=timeout)

        bounding_box = await self.bounding_box()
        if not bounding_box:
            raise PlaywrightError("Element is not visible")

        if self._page.scroll_into_view:
            await self.scroll_into_view_if_needed(timeout=timeout)

        x, y, width, height = bounding_box["x"], bounding_box["y"], bounding_box["width"], bounding_box["height"]

        x, y = x + width // 2, y + height // 2

        await self.click(delay=delay)

        await self._page.keyboard.type(text, delay=delay)

    def _attach_dyn_prop(self, locator: Locator, prop_name: str, prop: Any) -> None:
        """Attach property proper to instance with name prop_name.y

        Reference:
          * https://stackoverflow.com/a/1355444/509706
          * https://stackoverflow.com/questions/48448074
        """
        class_name = locator.__class__.__name__ + "Child"
        child_class = type(class_name, (locator.__class__,), {prop_name: prop})

        locator.__class__ = child_class
