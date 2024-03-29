import asyncio

import pytest
from playwright.async_api import Error


async def give_it_a_chance_to_resolve(page):
    for i in range(5):
        await page.evaluate("() => new Promise(f => requestAnimationFrame(() => requestAnimationFrame(f)))")


async def wait_for_state(div, state, done):
    await div.wait_for_element_state(state)
    done[0] = True


async def wait_for_state_to_throw(div, state):
    with pytest.raises(Error) as exc_info:
        await div.wait_for_element_state(state)
    return exc_info


@pytest.mark.asyncio
async def test_should_wait_for_visible(page):
    await page.set_content('<div style="display:none">content</div>')
    div = await page.query_selector("div")
    done = [False]
    promise = asyncio.create_task(wait_for_state(div, "visible", done))
    await give_it_a_chance_to_resolve(page)
    assert done[0] is False
    await div.evaluate('div => div.style.display = "block"')
    await promise


@pytest.mark.asyncio
async def test_should_wait_for_already_visible(page):
    await page.set_content("<div>content</div>")
    div = await page.query_selector("div")
    await div.wait_for_element_state("visible")


@pytest.mark.asyncio
async def test_should_timeout_waiting_for_visible(page):
    await page.set_content('<div style="display:none">content</div>')
    div = await page.query_selector("div")
    with pytest.raises(Error) as exc_info:
        await div.wait_for_element_state("visible", timeout=1000)
    assert "Timeout 1000ms exceeded" in exc_info.value.message


@pytest.mark.asyncio
async def test_should_throw_waiting_for_visible_when_detached(page):
    await page.set_content('<div style="display:none">content</div>')
    div = await page.query_selector("div")
    promise = asyncio.create_task(wait_for_state_to_throw(div, "visible"))
    await div.evaluate("div => div.remove()")
    exc_info = await promise
    assert "Element is not attached to the DOM" in exc_info.value.message


@pytest.mark.asyncio
async def test_should_wait_for_hidden(page):
    await page.set_content("<div>content</div>")
    div = await page.query_selector("div")
    done = [False]
    promise = asyncio.create_task(wait_for_state(div, "hidden", done))
    await give_it_a_chance_to_resolve(page)
    assert done[0] is False
    await div.evaluate('div => div.style.display = "none"')
    await promise


@pytest.mark.asyncio
async def test_should_wait_for_already_hidden(page):
    await page.set_content("<div></div>")
    div = await page.query_selector("div")
    await div.wait_for_element_state("hidden")


@pytest.mark.asyncio
async def test_should_wait_for_hidden_when_detached(page):
    await page.set_content("<div>content</div>")
    div = await page.query_selector("div")
    done = [False]
    promise = asyncio.create_task(wait_for_state(div, "hidden", done))
    await give_it_a_chance_to_resolve(page)
    assert done[0] is False
    await div.evaluate("div => div.remove()")
    await promise


@pytest.mark.asyncio
async def test_should_wait_for_enabled_button(page):
    await page.set_content("<button disabled><span>Target</span></button>")
    span = await page.query_selector("text=Target")
    done = [False]
    promise = asyncio.create_task(wait_for_state(span, "enabled", done))
    await give_it_a_chance_to_resolve(page)
    assert done[0] is False
    await span.evaluate("span => span.parentElement.disabled = false")
    await promise


@pytest.mark.asyncio
async def test_should_throw_waiting_for_enabled_when_detached(page):
    await page.set_content("<button disabled>Target</button>")
    button = await page.query_selector("button")
    promise = asyncio.create_task(wait_for_state_to_throw(button, "enabled"))
    await button.evaluate("button => button.remove()")
    exc_info = await promise
    assert "Element is not attached to the DOM" in exc_info.value.message


@pytest.mark.asyncio
async def test_should_wait_for_disabled_button(page):
    await page.set_content("<button><span>Target</span></button>")
    span = await page.query_selector("text=Target")
    done = [False]
    promise = asyncio.create_task(wait_for_state(span, "disabled", done))
    await give_it_a_chance_to_resolve(page)
    assert done[0] is False
    await span.evaluate("span => span.parentElement.disabled = true")
    await promise


@pytest.mark.asyncio
async def test_should_wait_for_editable_input(page):
    await page.set_content("<input readonly>")
    input = await page.query_selector("input")
    done = [False]
    promise = asyncio.create_task(wait_for_state(input, "editable", done))
    await give_it_a_chance_to_resolve(page)
    assert done[0] is False
    await input.evaluate("input => input.readOnly = false")
    await promise
