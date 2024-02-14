from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Pattern, Union

# from undetected_playwright.async_api import Locator as PlaywrightLocator, FrameLocator as PlaywrightFrameLocator
from playwright.async_api import FrameLocator as PlaywrightFrameLocator
from playwright.async_api import Locator as PlaywrightLocator

if TYPE_CHECKING:
    from . import Locator, Page


class FrameLocator(PlaywrightFrameLocator):
    def __init__(self, frame_locator: PlaywrightFrameLocator, page: Page):
        super().__init__(frame_locator)
        self._impl_obj = frame_locator._impl_obj
        self._page = page
        self._origin_first = frame_locator.first
        self._origin_last = frame_locator.last

        self._origin_locator = frame_locator.locator
        self._origin_nth = frame_locator.nth

    def locator(
        self,
        selector_or_locator: Union[PlaywrightLocator, str],
        has_text: Optional[Union[str, Pattern[str]]] = None,
        has_not_text: Optional[Union[str, Pattern[str]]] = None,
        has: Optional[PlaywrightLocator] = None,
        has_not: Optional[PlaywrightLocator] = None,
    ) -> Locator:
        from . import Locator

        _locator = self._origin_locator(selector_or_locator=selector_or_locator, has=has, has_text=has_text, has_not=has_not, has_not_text=has_not_text)
        locator = Locator(_locator, self._page)
        return locator

    def nth(self, index: int) -> FrameLocator:
        _locator = self._origin_nth(index=index)
        locator = FrameLocator(_locator, self._page)
        return locator

    @property
    def first(self) -> FrameLocator:
        _locator = self._origin_first
        locator = FrameLocator(_locator, self._page)
        return locator

    @property
    def origin_first(self):
        return self._origin_first

    @origin_first.setter
    def origin_first(self, value):
        self._origin_first = value

    @property
    def last(self) -> FrameLocator:
        _locator = self._origin_last
        locator = FrameLocator(_locator, self._page)
        return locator

    @property
    def origin_last(self):
        return self._origin_last

    @origin_last.setter
    def origin_last(self, value):
        self._origin_last = value

    def _attach_dyn_prop(self, frame_locator: FrameLocator, prop_name: str, prop: Any) -> None:
        """Attach property proper to instance with name prop_name.

        Reference:
          * https://stackoverflow.com/a/1355444/509706
          * https://stackoverflow.com/questions/48448074
        """
        class_name = frame_locator.__class__.__name__ + "Child"
        child_class = type(class_name, (frame_locator.__class__,), {prop_name: prop})

        frame_locator.__class__ = child_class
