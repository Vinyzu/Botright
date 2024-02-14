import asyncio

import pytest

from botright.extended_typing import Page


@pytest.mark.asyncio
async def test_console_event_should_work(page: Page) -> None:
    [message, _] = await asyncio.gather(
        page.context.wait_for_event("console"),
        page.evaluate("() => console.log('hello')"),
    )
    assert message.text == "hello"
    assert Page(message.page, page.browser, page.faker) == page


@pytest.mark.asyncio
async def test_console_event_should_work_in_popup(page: Page) -> None:
    [message, popup, _] = await asyncio.gather(
        page.context.wait_for_event("console"),
        page.wait_for_event("popup"),
        page.evaluate(
            """() => {
            const win = window.open('');
            win.console.log('hello');
        }"""
        ),
    )
    assert message.text == "hello"
    assert message.page == popup


@pytest.mark.asyncio
async def test_console_event_should_work_in_popup_2(page: Page) -> None:
    [message, popup, _] = await asyncio.gather(
        page.context.wait_for_event("console", lambda msg: msg.type == "log"),
        page.context.wait_for_event("page"),
        page.evaluate(
            """async () => {
            const win = window.open('javascript:console.log("hello")');
            await new Promise(f => setTimeout(f, 0));
            win.close();
        }"""
        ),
    )
    assert message.text == "hello"
    assert message.page == popup


@pytest.mark.asyncio
async def test_console_event_should_work_in_immediately_closed_popup(page: Page) -> None:
    [message, popup, _] = await asyncio.gather(
        page.context.wait_for_event("console"),
        page.wait_for_event("popup"),
        page.evaluate(
            """async () => {
            const win = window.open();
            win.console.log('hello');
            win.close();
        }"""
        ),
    )
    assert message.text == "hello"
    assert message.page == popup


@pytest.mark.asyncio
async def test_dialog_event_should_work1(page: Page) -> None:
    prompt_task = None

    async def open_dialog() -> None:
        nonlocal prompt_task
        prompt_task = asyncio.create_task(page.evaluate("() => prompt('hey?')"))

    [dialog1, dialog2, _] = await asyncio.gather(
        page.context.wait_for_event("dialog"),
        page.wait_for_event("dialog"),
        open_dialog(),
    )
    assert dialog1 == dialog2
    assert dialog1.message == "hey?"
    assert Page(dialog1.page, page.browser, page.faker) == page
    await dialog1.accept("hello")
    assert await prompt_task == "hello"


@pytest.mark.asyncio
async def test_dialog_event_should_work_in_popup(page: Page) -> None:
    prompt_task = None

    async def open_dialog() -> None:
        nonlocal prompt_task
        prompt_task = asyncio.create_task(page.evaluate("() => window.open('').prompt('hey?')"))

    [dialog, popup, _] = await asyncio.gather(
        page.context.wait_for_event("dialog"),
        page.wait_for_event("popup"),
        open_dialog(),
    )
    assert dialog.message == "hey?"
    assert dialog.page == popup
    await dialog.accept("hello")
    assert await prompt_task == "hello"


@pytest.mark.asyncio
async def test_dialog_event_should_work_in_popup_2(page: Page) -> None:
    promise = asyncio.create_task(page.evaluate("() => window.open('javascript:prompt(\"hey?\")')"))
    dialog = await page.context.wait_for_event("dialog")
    assert dialog.message == "hey?"
    assert dialog.page is None
    await dialog.accept("hello")
    await promise


@pytest.mark.asyncio
async def test_dialog_event_should_work_in_immdiately_closed_popup(page: Page) -> None:
    [message, popup, _] = await asyncio.gather(
        page.context.wait_for_event("console"),
        page.wait_for_event("popup"),
        page.evaluate(
            """() => {
            const win = window.open();
            win.console.log('hello');
            win.close();
        }"""
        ),
    )
    assert message.text == "hello"
    assert message.page == popup


@pytest.mark.asyncio
async def test_console_event_should_work_with_context_manager(page: Page) -> None:
    async with page.context.expect_console_message() as cm_info:
        await page.evaluate("() => console.log('hello')")
    message = await cm_info.value
    assert message.text == "hello"
    assert Page(message.page, page.browser, page.faker) == page


@pytest.mark.asyncio
async def test_page_error_event_should_work(page: Page) -> None:
    async with page.context.expect_event("weberror") as page_error_info:
        await page.set_content('<script>throw new Error("boom")</script>')
    page_error = await page_error_info.value
    assert Page(page_error.page, page.browser, page.faker) == page
    assert "boom" in page_error.error.stack
