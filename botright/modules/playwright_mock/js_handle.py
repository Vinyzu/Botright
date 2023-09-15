from __future__ import annotations

from playwright.async_api import Page, JSHandle, ElementHandle

from . import element_handle


def mock_js_handle(js_handle: JSHandle, page: Page) -> None:
    # MouseMocking
    def as_element_mocker() -> ElementHandle:
        element = js_handle.origin_as_element()
        element_handle.mock_element_handle(element, page)
        return element

    js_handle.origin_as_element = js_handle.as_element
    js_handle.as_element = as_element_mocker
