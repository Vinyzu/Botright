import asyncio

import pytest

from playwright.async_api import Error, Page


@pytest.mark.asyncio
async def test_evaluate_handle(page):
    await page.goto("https://raw.githack.com/microsoft/playwright-python/main/tests/assets/empty.html")
    main_frame = page.main_frame
    assert main_frame.page == page
    window_handle = await main_frame.evaluate_handle("window")
    assert window_handle


@pytest.mark.asyncio
async def test_frame_element(page, utils):
    await page.goto("https://raw.githack.com/microsoft/playwright-python/main/tests/assets/empty.html")
    frame1 = await utils.attach_frame(page, "frame1", "https://raw.githack.com/microsoft/playwright-python/main/tests/assets/empty.html")
    await utils.attach_frame(page, "frame2", "https://raw.githack.com/microsoft/playwright-python/main/tests/assets/empty.html")
    frame3 = await utils.attach_frame(page, "frame3", "https://raw.githack.com/microsoft/playwright-python/main/tests/assets/empty.html")
    frame1handle1 = await page.query_selector("#frame1")
    frame1handle2 = await frame1.frame_element()
    frame3handle1 = await page.query_selector("#frame3")
    frame3handle2 = await frame3.frame_element()
    assert await frame1handle1.evaluate("(a, b) => a === b", frame1handle2)
    assert await frame3handle1.evaluate("(a, b) => a === b", frame3handle2)
    assert await frame1handle1.evaluate("(a, b) => a === b", frame3handle1) is False


@pytest.mark.asyncio
async def test_frame_element_with_content_frame(page, utils):
    await page.goto("https://raw.githack.com/microsoft/playwright-python/main/tests/assets/empty.html")
    frame = await utils.attach_frame(page, "frame1", "https://raw.githack.com/microsoft/playwright-python/main/tests/assets/empty.html")
    handle = await frame.frame_element()
    content_frame = await handle.content_frame()
    assert content_frame == frame


@pytest.mark.asyncio
async def test_frame_element_throw_when_detached(page, utils):
    await page.goto("https://raw.githack.com/microsoft/playwright-python/main/tests/assets/empty.html")
    frame1 = await utils.attach_frame(page, "frame1", "https://raw.githack.com/microsoft/playwright-python/main/tests/assets/empty.html")
    await page.eval_on_selector("#frame1", "e => e.remove()")
    error = None
    try:
        await frame1.frame_element()
    except Error as e:
        error = e
    assert error.message == "Frame has been detached."


@pytest.mark.asyncio
async def test_evaluate_throw_for_detached_frames(page, utils):
    frame1 = await utils.attach_frame(page, "frame1", "https://raw.githack.com/microsoft/playwright-python/main/tests/assets/empty.html")
    await utils.detach_frame(page, "frame1")
    error = None
    try:
        await frame1.evaluate("7 * 8")
    except Error as e:
        error = e
    assert "Frame was detached" in error.message


@pytest.mark.asyncio
async def test_evaluate_isolated_between_frames(page, utils):
    await page.goto("https://raw.githack.com/microsoft/playwright-python/main/tests/assets/empty.html")
    await utils.attach_frame(page, "frame1", "https://raw.githack.com/microsoft/playwright-python/main/tests/assets/empty.html")
    assert len(page.frames) == 2
    [frame1, frame2] = page.frames
    assert frame1 != frame2

    await asyncio.gather(
        frame1.evaluate("window.a = 1"), frame2.evaluate("window.a = 2")
    )
    [a1, a2] = await asyncio.gather(
        frame1.evaluate("window.a"), frame2.evaluate("window.a")
    )
    assert a1 == 1
    assert a2 == 2


@pytest.mark.asyncio
async def test_should_handle_nested_frames(page, utils):
    await page.goto("https://raw.githack.com/microsoft/playwright-python/main/tests/assets/frames/nested-frames.html")
    assert utils.dump_frames(page.main_frame) == [
        "https://raw.githack.com/microsoft/playwright-python/main/tests/assets/frames/nested-frames.html",
        "    https://raw.githack.com/microsoft/playwright-python/main/tests/assets/frames/frame.html (aframe)",
        "    https://raw.githack.com/microsoft/playwright-python/main/tests/assets/frames/two-frames.html (2frames)",
        "        https://raw.githack.com/microsoft/playwright-python/main/tests/assets/frames/frame.html (dos)",
        "        https://raw.githack.com/microsoft/playwright-python/main/tests/assets/frames/frame.html (uno)",
    ]


@pytest.mark.asyncio
async def test_should_send_events_when_frames_are_manipulated_dynamically(
    page, utils
):
    await page.goto("https://raw.githack.com/microsoft/playwright-python/main/tests/assets/empty.html")
    # validate frameattached events
    attached_frames = []
    page.on("frameattached", lambda frame: attached_frames.append(frame))
    await utils.attach_frame(page, "frame1", "./assets/frame.html")
    assert len(attached_frames) == 1
    assert "/assets/frame.html" in attached_frames[0].url

    # validate framenavigated events
    navigated_frames = []
    page.on("framenavigated", lambda frame: navigated_frames.append(frame))
    await page.evaluate(
        """() => {
            frame = document.getElementById('frame1')
            frame.src = './empty.html'
            return new Promise(x => frame.onload = x)
        }"""
    )

    assert len(navigated_frames) == 1
    assert navigated_frames[0].url == "https://raw.githack.com/microsoft/playwright-python/main/tests/assets/empty.html"

    # validate framedetached events
    detached_frames = []
    page.on("framedetached", lambda frame: detached_frames.append(frame))
    await utils.detach_frame(page, "frame1")
    assert len(detached_frames) == 1
    assert detached_frames[0].is_detached()


@pytest.mark.asyncio
async def test_framenavigated_when_navigating_on_anchor_urls(page):
    await page.goto("https://raw.githack.com/microsoft/playwright-python/main/tests/assets/empty.html")
    async with page.expect_event("framenavigated"):
        await page.goto("https://raw.githack.com/microsoft/playwright-python/main/tests/assets/empty.html" + "#foo")
    assert page.url == "https://raw.githack.com/microsoft/playwright-python/main/tests/assets/empty.html" + "#foo"


@pytest.mark.asyncio
async def test_should_not_send_attach_detach_events_for_main_frame(page):
    has_events = []
    page.on("frameattached", lambda frame: has_events.append(True))
    page.on("framedetached", lambda frame: has_events.append(True))
    await page.goto("https://raw.githack.com/microsoft/playwright-python/main/tests/assets/empty.html")
    assert has_events == []


@pytest.mark.asyncio
async def test_detach_child_frames_on_navigation(page):
    attached_frames = []
    detached_frames = []
    navigated_frames = []
    page.on("frameattached", lambda frame: attached_frames.append(frame))
    page.on("framedetached", lambda frame: detached_frames.append(frame))
    page.on("framenavigated", lambda frame: navigated_frames.append(frame))
    await page.goto("https://raw.githack.com/microsoft/playwright-python/main/tests/assets/frames/nested-frames.html")
    assert len(attached_frames) == 4
    assert len(detached_frames) == 0
    assert len(navigated_frames) == 5

    attached_frames = []
    detached_frames = []
    navigated_frames = []
    await page.goto("https://raw.githack.com/microsoft/playwright-python/main/tests/assets/empty.html")
    assert len(attached_frames) == 0
    assert len(detached_frames) == 4
    assert len(navigated_frames) == 1


@pytest.mark.asyncio
async def test_framesets(page):
    attached_frames = []
    detached_frames = []
    navigated_frames = []
    page.on("frameattached", lambda frame: attached_frames.append(frame))
    page.on("framedetached", lambda frame: detached_frames.append(frame))
    page.on("framenavigated", lambda frame: navigated_frames.append(frame))
    await page.goto("https://raw.githack.com/microsoft/playwright-python/main/tests/assets/frames/frameset.html")
    await page.wait_for_timeout(100)  # Small wait for loading
    assert len(attached_frames) == 4
    assert len(detached_frames) == 0
    assert len(navigated_frames) == 4

    attached_frames = []
    detached_frames = []
    navigated_frames = []
    await page.goto("https://raw.githack.com/microsoft/playwright-python/main/tests/assets/empty.html")
    await page.wait_for_timeout(100)  # Small wait for loading
    assert len(attached_frames) == 0
    assert len(detached_frames) == 4
    assert len(navigated_frames) == 1


@pytest.mark.asyncio
async def test_frame_from_inside_shadow_dom(page):
    await page.goto("https://raw.githack.com/microsoft/playwright-python/main/tests/assets/shadow.html")
    await page.evaluate(
        """async url => {
            frame = document.createElement('iframe');
            frame.src = url;
            document.body.shadowRoot.appendChild(frame);
            await new Promise(x => frame.onload = x);
        }""",
        "https://raw.githack.com/microsoft/playwright-python/main/tests/assets/empty.html",
    )
    assert len(page.frames) == 2
    assert page.frames[1].url == "https://raw.githack.com/microsoft/playwright-python/main/tests/assets/empty.html"


@pytest.mark.asyncio
async def test_frame_name(page, utils):
    await utils.attach_frame(page, "theFrameId", "https://raw.githack.com/microsoft/playwright-python/main/tests/assets/empty.html")
    await page.evaluate(
        """url => {
            frame = document.createElement('iframe');
            frame.name = 'theFrameName';
            frame.src = url;
            document.body.appendChild(frame);
            return new Promise(x => frame.onload = x);
        }""",
        "https://raw.githack.com/microsoft/playwright-python/main/tests/assets/empty.html",
    )
    assert page.frames[0].name == ""
    assert page.frames[1].name == "theFrameId"
    assert page.frames[2].name == "theFrameName"


@pytest.mark.asyncio
async def test_frame_parent(page, utils):
    await utils.attach_frame(page, "frame1", "https://raw.githack.com/microsoft/playwright-python/main/tests/assets/empty.html")
    await utils.attach_frame(page, "frame2", "https://raw.githack.com/microsoft/playwright-python/main/tests/assets/empty.html")
    assert page.frames[0].parent_frame is None
    assert page.frames[1].parent_frame == page.main_frame
    assert page.frames[2].parent_frame == page.main_frame


@pytest.mark.asyncio
async def test_should_report_different_frame_instance_when_frame_re_attaches(
    page, utils
):
    frame1 = await utils.attach_frame(page, "frame1", "https://raw.githack.com/microsoft/playwright-python/main/tests/assets/empty.html")
    await page.evaluate(
        """() => {
            window.frame = document.querySelector('#frame1')
            window.frame.remove()
        }"""
    )

    assert frame1.is_detached()
    async with page.expect_event("frameattached") as frame2_info:
        await page.evaluate("() => document.body.appendChild(window.frame)")

    frame2 = await frame2_info.value
    assert frame2.is_detached() is False
    assert frame1 != frame2


@pytest.mark.asyncio
async def test_strict_mode(page: Page):
    await page.goto("https://raw.githack.com/microsoft/playwright-python/main/tests/assets/empty.html")
    await page.set_content(
        """
        <button>Hello</button>
        <button>Hello</button>
    """
    )
    with pytest.raises(Error):
        await page.text_content("button", strict=True)
    with pytest.raises(Error):
        await page.query_selector("button", strict=True)
