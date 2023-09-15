from __future__ import annotations

from typing import Optional

from playwright.async_api import Page, FrameLocator, Locator

from . import locator


def attach_dyn_prop(frame_locator: FrameLocator, prop_name: str, prop: property) -> None:
    """Attach property proper to instance with name prop_name.

    Reference:
      * https://stackoverflow.com/a/1355444/509706
      * https://stackoverflow.com/questions/48448074
    """
    class_name = frame_locator.__class__.__name__ + "Child"
    child_class = type(class_name, (frame_locator.__class__,), {prop_name: prop})

    frame_locator.__class__ = child_class


def mock_frame_locator(frame_locator: FrameLocator, page: Page) -> None:
    # MouseMocking
    def locator_mocker(selector: str, has: Optional[Locator] = None, has_text: Optional[str] = ""):
        _locator = frame_locator.origin_locator(selector, has=has, has_text=has_text)
        locator.mock_locator(_locator, page)
        return _locator

    frame_locator.origin_locator = frame_locator.locator
    frame_locator.locator = locator_mocker

    # FrameLocator
    def nth_mocker(index: int) -> FrameLocator:
        _locator = frame_locator.origin_nth(index)
        mock_frame_locator(_locator, page)
        return _locator

    frame_locator.origin_nth = frame_locator.nth
    frame_locator.nth = nth_mocker

    @property
    def first_mocker(self) -> FrameLocator:
        _locator = frame_locator.origin_first
        mock_frame_locator(_locator, page)
        return _locator

    @property
    def last_mocker(self) -> FrameLocator:
        _locator = frame_locator.origin_last
        mock_frame_locator(_locator, page)
        return _locator

    frame_locator.origin_first = frame_locator.first
    frame_locator.origin_last = frame_locator.last

    attach_dyn_prop(frame_locator, "first", first_mocker)
    attach_dyn_prop(frame_locator, "last", last_mocker)
