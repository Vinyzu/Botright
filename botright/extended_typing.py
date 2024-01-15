from botright.playwright_mock import ElementHandle, \
    Frame, \
    FrameLocator, \
    JSHandle, \
    Locator, \
    Mouse, \
    Keyboard, \
    Page, \
    new_page, \
    BrowserContext, \
    Route, \
    Request


class NotSupportedError(NotImplementedError):
    def __init__(self, message):
        super().__init__(f"{message} \n Some Bindings and Exposures are (currently) not supported. Learn more at https://github.com/kaliiiiiiiiii/undetected-playwright-python/issues/5 and "
                         "https://github.com/kaliiiiiiiiii/undetected-playwright-python/discussions/6")


__all__ = [
    "ElementHandle",
    "Frame",
    "FrameLocator",
    "JSHandle",
    "Locator",
    "Mouse",
    "Keyboard",
    "Page",
    "new_page",
    "BrowserContext",
    "Route",
    "Request",
    "NotSupportedError"
]
