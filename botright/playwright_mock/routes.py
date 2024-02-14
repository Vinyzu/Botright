from __future__ import annotations

from typing import TYPE_CHECKING

# from undetected_playwright.async_api import Route as PlaywrightRoute, Request as PlaywrightRequest, Response as PlaywrightResponse
from playwright.async_api import Request as PlaywrightRequest
from playwright.async_api import Response as PlaywrightResponse
from playwright.async_api import Route as PlaywrightRoute

if TYPE_CHECKING:
    from . import Page

from . import Frame


class Request(PlaywrightRequest):
    def __init__(self, request: PlaywrightRequest, page: Page):
        super().__init__(request)
        self._impl_obj = request._impl_obj
        self._page = page

        self._frame = request.frame
        self._redirected_from = request.redirected_from
        self._redirected_to = request.redirected_to

        self.origin_response = request.response

    @property
    def frame(self):
        return Frame(self._frame, self._page)

    @property
    def redirected_from(self):
        if not self._redirected_from:
            return False
        return Request(self._redirected_from, self._page)

    @property
    def redirected_to(self):
        if not self._redirected_to:
            return False
        return Request(self._redirected_to, self._page)

    async def response(self):
        _response = await self.origin_response()
        if not _response:
            return None

        return Response(_response, self._page)


class Response(PlaywrightResponse):
    def __init__(self, response: PlaywrightResponse, page: Page):
        super().__init__(response)
        self._impl_obj = response._impl_obj
        self._page = page

        self._frame = response.frame
        self._request = response.request

    @property
    def frame(self):
        return Frame(self._frame, self._page)

    @property
    def request(self):
        return Request(self._request, self._page)


class Route(PlaywrightRoute):
    def __init__(self, route: PlaywrightRoute, page: Page):
        super().__init__(route)
        self._impl_obj = route._impl_obj
        self._page = page

        self._request = route.request

    @property
    def request(self):
        return Request(self._request, self._page)
