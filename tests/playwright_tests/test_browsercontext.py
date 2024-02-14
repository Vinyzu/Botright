import asyncio
import re
import sys

import pytest
from playwright.async_api import Error

from botright.extended_typing import Page


@pytest.mark.asyncio
async def test_pages_should_return_all_of_the_pages(browser):
    page = await browser.new_page()
    second = await browser.new_page()
    all_pages = browser.pages
    assert len(all_pages) == 2
    assert page in all_pages
    assert second in all_pages


@pytest.mark.asyncio
async def test_pages_should_close_all_belonging_pages_once_closing_context(browser):
    await browser.new_page()
    assert len(browser.pages) == 1
    await browser.close()
    assert browser.pages == []


@pytest.mark.asyncio
async def test_expose_binding_should_work(browser):
    binding_source = []

    def binding(source, a, b):
        binding_source.append(source)
        return a + b

    await browser.expose_binding("add", lambda source, a, b: binding(source, a, b))

    page = await browser.new_page()
    result = await page.evaluate("add(5, 6)")
    assert binding_source[0]["context"] == browser
    assert binding_source[0]["page"] == page
    assert binding_source[0]["frame"] == page.main_frame
    assert result == 11


@pytest.mark.asyncio
async def test_expose_function_should_work(browser):
    await browser.expose_function("add", lambda a, b: a + b)
    page = await browser.new_page()
    await page.expose_function("mul", lambda a, b: a * b)
    await browser.expose_function("sub", lambda a, b: a - b)
    result = await page.evaluate(
        """async function() {
      return { mul: await mul(9, 4), add: await add(9, 4), sub: await sub(9, 4) }
    }"""
    )

    assert result == {"mul": 36, "add": 13, "sub": 5}


@pytest.mark.asyncio
async def test_expose_function_should_throw_for_duplicate_registrations(browser):
    await browser.expose_function("foo", lambda: None)
    await browser.expose_function("bar", lambda: None)
    with pytest.raises(Error) as exc_info:
        await browser.expose_function("foo", lambda: None)
    assert exc_info.value.message == 'Function "foo" has been already registered'
    page = await browser.new_page()
    with pytest.raises(Error) as exc_info:
        await page.expose_function("foo", lambda: None)
    assert exc_info.value.message == 'Function "foo" has been already registered in the browser context'
    await page.expose_function("baz", lambda: None)
    with pytest.raises(Error) as exc_info:
        await browser.expose_function("baz", lambda: None)
    assert exc_info.value.message == 'Function "baz" has been already registered in one of the pages'


@pytest.mark.asyncio
async def test_expose_function_should_be_callable_from_inside_add_init_script(browser):
    args = []
    await browser.expose_function("woof", lambda arg: args.append(arg))
    await browser.add_init_script("woof('context')")
    page = await browser.new_page()
    await page.evaluate("undefined")
    assert args == ["context"]
    args = []
    await page.add_init_script("woof('page')")
    await page.reload()
    assert args == ["context", "page"]


@pytest.mark.asyncio
async def test_expose_bindinghandle_should_work(browser):
    targets = []

    def logme(t):
        targets.append(t)
        return 17

    page = await browser.new_page()
    await page.expose_binding("logme", lambda source, t: logme(t), handle=True)
    result = await page.evaluate("logme({ foo: 42 })")
    assert (await targets[0].evaluate("x => x.foo")) == 42
    assert result == 17


@pytest.mark.asyncio
async def test_route_should_intercept(browser, server):
    intercepted = []

    def handle(route, request):
        intercepted.append(True)
        assert "empty.html" in request.url
        assert request.headers["user-agent"]
        assert request.method == "GET"
        assert request.post_data is None
        assert request.is_navigation_request
        assert request.resource_type == "document"
        assert request.frame == page.main_frame
        assert request.frame.url == "about:blank"
        asyncio.create_task(route.continue_())

    await browser.route("**/empty.html", lambda route, request: handle(route, request))
    page = await browser.new_page()
    response = await page.goto(server.EMPTY_PAGE)
    assert response.ok
    assert intercepted == [True]
    await browser.close()


@pytest.mark.asyncio
async def test_route_should_unroute(browser, server):
    page = await browser.new_page()

    intercepted = []

    def handler(route, request, ordinal):
        intercepted.append(ordinal)
        asyncio.create_task(route.continue_())

    await browser.route("**/*", lambda route, request: handler(route, request, 1))
    await browser.route("**/empty.html", lambda route, request: handler(route, request, 2))
    await browser.route("**/empty.html", lambda route, request: handler(route, request, 3))

    def handler4(route, request):
        handler(route, request, 4)

    await browser.route(re.compile("empty.html"), handler4)

    await page.goto(server.EMPTY_PAGE)
    assert intercepted == [4]

    intercepted = []
    await browser.unroute(re.compile("empty.html"), handler4)
    await page.goto(server.EMPTY_PAGE)
    assert intercepted == [3]

    intercepted = []
    await browser.unroute("**/empty.html")
    await page.goto(server.EMPTY_PAGE)
    assert intercepted == [1]


@pytest.mark.asyncio
async def test_route_should_yield_to_page_route(browser, server):
    await browser.route(
        "**/empty.html",
        lambda route, request: asyncio.create_task(route.fulfill(status=200, body="context")),
    )

    page = await browser.new_page()
    await page.route(
        "**/empty.html",
        lambda route, request: asyncio.create_task(route.fulfill(status=200, body="page")),
    )

    response = await page.goto(server.EMPTY_PAGE)
    assert response.ok
    assert await response.text() == "page"


@pytest.mark.asyncio
async def test_route_should_fall_back_to_context_route(browser, server):
    await browser.route(
        "**/empty.html",
        lambda route, request: asyncio.create_task(route.fulfill(status=200, body="context")),
    )

    page = await browser.new_page()
    await page.route(
        "**/non-empty.html",
        lambda route, request: asyncio.create_task(route.fulfill(status=200, body="page")),
    )

    response = await page.goto(server.EMPTY_PAGE)
    assert response.ok
    assert await response.text() == "context"


@pytest.mark.asyncio
async def test_offline_should_emulate_navigator_online(browser):
    page = await browser.new_page()
    assert await page.evaluate("window.navigator.onLine")
    await browser.set_offline(True)
    assert await page.evaluate("window.navigator.onLine") is False
    await browser.set_offline(False)
    assert await page.evaluate("window.navigator.onLine")


@pytest.mark.asyncio
async def test_page_event_should_have_url(browser, server):
    page = await browser.new_page()
    async with browser.expect_page() as other_page_info:
        await page.evaluate("url => window.open(url)", server.EMPTY_PAGE)
    other_page = await other_page_info.value
    assert other_page.url == server.EMPTY_PAGE


@pytest.mark.asyncio
async def test_page_event_should_have_url_after_domcontentloaded(browser, server):
    page = await browser.new_page()
    async with browser.expect_page() as other_page_info:
        await page.evaluate("url => window.open(url)", server.EMPTY_PAGE)
    other_page = await other_page_info.value
    await other_page.wait_for_load_state("domcontentloaded")
    assert other_page.url == server.EMPTY_PAGE


@pytest.mark.asyncio
async def test_page_event_should_have_about_blank_url_with_domcontentloaded(browser):
    page = await browser.new_page()
    async with browser.expect_page() as other_page_info:
        await page.evaluate("url => window.open(url)", "about:blank")
    other_page = await other_page_info.value
    await other_page.wait_for_load_state("domcontentloaded")
    assert other_page.url == "about:blank"


@pytest.mark.asyncio
async def test_page_event_should_have_about_blank_for_empty_url_with_domcontentloaded(browser):
    page = await browser.new_page()
    async with browser.expect_page() as other_page_info:
        await page.evaluate("window.open()")
    other_page = await other_page_info.value
    await other_page.wait_for_load_state("domcontentloaded")
    assert other_page.url == "about:blank"


@pytest.mark.asyncio
async def test_page_event_should_report_when_a_new_page_is_created_and_closed(browser, server):
    page = await browser.new_page()
    async with browser.expect_page() as page_info:
        await page.evaluate("url => window.open(url)", server.CROSS_PROCESS_PREFIX + "/empty.html")
    other_page = Page(await page_info.value, browser, browser.faker)

    # The url is about:blank in FF when 'page' event is fired.
    assert server.CROSS_PROCESS_PREFIX + "/empty.html" in other_page.url
    assert await other_page.evaluate("['Hello', 'world'].join(' ')") == "Hello world"
    assert await other_page.query_selector("body")

    all_pages = browser.pages
    assert page in all_pages
    assert other_page in browser.pages

    close_event_received = []
    other_page.once("close", lambda: close_event_received.append(True))
    await other_page.close()
    assert close_event_received == [True]

    all_pages = browser.pages
    assert page in all_pages
    assert other_page not in all_pages


@pytest.mark.asyncio
async def test_page_event_should_report_initialized_pages(browser):
    async with browser.expect_page() as page_info:
        await browser.new_page()
    new_page = await page_info.value
    assert new_page.url == "about:blank"

    async with browser.expect_page() as popup_info:
        await new_page.evaluate("window.open('about:blank')")
    popup = await popup_info.value
    assert popup.url == "about:blank"


@pytest.mark.asyncio
async def test_page_event_should_have_an_opener(browser, server):
    page = await browser.new_page()
    await page.goto(server.EMPTY_PAGE)
    async with browser.expect_page() as page_info:
        await page.goto(server.PREFIX + "/popup/window-open.html")
    popup = Page(await page_info.value, browser, browser.faker)
    assert popup.url == server.PREFIX + "/popup/popup.html"
    assert await popup.opener() == page
    assert await page.opener() is None


@pytest.mark.asyncio
async def test_page_event_should_fire_page_lifecycle_events(browser, server):
    events = []

    def handle_page(page):
        events.append("CREATED: " + page.url)
        page.on("close", lambda: events.append("DESTROYED: " + page.url))

    browser.on("page", handle_page)

    page = await browser.new_page()
    await page.goto(server.EMPTY_PAGE)
    await page.close()
    assert events == ["CREATED: about:blank", f"DESTROYED: {server.EMPTY_PAGE}"]


@pytest.mark.asyncio
async def test_page_event_should_work_with_shift_clicking(browser, server):
    # WebKit: Shift+Click does not open a new window.
    page = await browser.new_page()
    await page.goto(server.EMPTY_PAGE)
    await page.set_content('<a href="/one-style.html">yo</a>')
    async with browser.expect_page() as page_info:
        await page.click("a", modifiers=["Shift"])
    popup = await page_info.value
    assert await popup.opener() is None


@pytest.mark.asyncio
async def test_page_event_should_work_with_ctrl_clicking(browser, server):
    # Firefox: reports an opener in this case.
    # WebKit: Ctrl+Click does not open a new tab.
    page = await browser.new_page()
    await page.goto(server.EMPTY_PAGE)
    await page.set_content('<a href="/one-style.html">yo</a>')
    async with browser.expect_page() as popup_info:
        await page.click("a", modifiers=["Meta" if (sys.platform == "darwin") else "Control"])
    popup = await popup_info.value
    assert await popup.opener() is None
