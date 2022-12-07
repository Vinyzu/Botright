from . import element_handle


def mock_js_handle(js_handle, page) -> None:
    # MouseMocking
    def as_element_mocker():
        element = js_handle._as_element()
        element_handle.mock_element_handle(element, page)
        return element

    js_handle._as_element = js_handle.as_element
    js_handle.as_element = as_element_mocker
