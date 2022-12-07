import typing

from . import element_handle, frame_locator, js_handle, locator


def mock_element_handle(element, page) -> None:
    async def click_mocker(button="left", click_count=1, delay=20, force=False, modifiers=[], no_wait_after=False, position={}, timeout: typing.Optional[float] = None, trial=False):
        await ElementHandle.click(element, page, button=button, click_count=click_count, delay=delay, force=force, modifiers=modifiers, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    element.click = click_mocker

    async def dblclick_mocker(button="left", delay=20, force=False, modifiers=[], no_wait_after=False, position={}, timeout: typing.Optional[float] = None, trial=False):
        await ElementHandle.dblclick(element, page, button=button, delay=delay, force=force, modifiers=modifiers, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    element.dblclick = dblclick_mocker

    async def check_mocker(force=False, no_wait_after=False, position={}, timeout: typing.Optional[float] = None, trial=False):
        await ElementHandle.check(element, page, force=force, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    element.check = check_mocker

    async def uncheck_mocker(force=False, no_wait_after=False, position={}, timeout: typing.Optional[float] = None, trial=False):
        await ElementHandle.uncheck(element, page, force=force, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    element.uncheck = uncheck_mocker

    async def set_checked_mocker(checked=False, force=False, no_wait_after=False, position={}, timeout: typing.Optional[float] = None, trial=False):
        await ElementHandle.set_checked(element, page, checked=checked, force=force, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    element.set_checked = set_checked_mocker

    async def hover_mocker(force=False, modifiers=[], position={}, timeout: typing.Optional[float] = None, trial=False):
        await ElementHandle.hover(element, page, force=force, modifiers=modifiers, position=position, timeout=timeout, trial=trial)

    element.hover = hover_mocker

    async def type_mocker(text, delay=200, no_wait_after=False, timeout: typing.Optional[float] = None):
        await ElementHandle.type(element, page, text, delay=delay, no_wait_after=no_wait_after, timeout=timeout)

    element.type = type_mocker

    # ElementHandle
    async def mock_query_selector(selector, strict=False) -> typing.Optional["ElementHandle"]:
        element = await element._query_selector(selector, strict=strict)
        if element:
            await element_handle.mock_element_handle(element, page)
        return element

    element._query_selector = element.query_selector
    element.query_selector = mock_query_selector

    async def mock_query_selector_all(selector) -> typing.List["ElementHandle"]:
        elements = await element._query_selector_all(selector)
        for element in elements:
            await element_handle.mock_element_handle(element, page)
        return elements

    element._query_selector_all = element.query_selector_all
    element.query_selector_all = mock_query_selector_all

    async def mock_wait_for_selector(selector, state=[], strict=False, timeout: typing.Optional[float] = None) -> typing.Optional["ElementHandle"]:
        element = await element.__wait_for_selector(selector, state=state, strict=strict, timeout=timeout)
        if element:
            await element_handle.mock_element_handle(element, page)
        return element

    element.__wait_for_selector = element.wait_for_selector
    element.wait_for_selector = mock_wait_for_selector

    # JsHandle
    async def mock_evaluate_handle(expression, arg=None) -> "JSHandle":
        _js_handle = await element._evaluate_handle(expression, arg=arg)
        await js_handle.mock_js_handle(_js_handle, page)
        return _js_handle

    element._evaluate_handle = element.evaluate_handle
    element.evaluate_handle = mock_evaluate_handle


class ElementHandle:
    async def click(element, page, button="left", click_count=1, delay=20, force=False, modifiers=[], no_wait_after=False, position={}, timeout: typing.Optional[float] = None, trial=False) -> None:
        frame = element.owner_frame()

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if not trial:
            if page.scroll_into_view:
                await element.scroll_into_view_if_needed(timeout=timeout)

            boundings = await element.bounding_box()
            x, y, width, height = boundings.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            for modifier in modifiers:
                await frame.page.keyboard.down(modifier)

            await frame.page.mouse.click(x, y, button, click_count, delay)

            for modifier in modifiers:
                await frame.page.keyboard.up(modifier)

    async def dblclick(element, page, button="left", delay=20, force=False, modifiers=[], no_wait_after=False, position={}, timeout: typing.Optional[float] = None, trial=False) -> None:
        frame = element.owner_frame()

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if not trial:
            if page.scroll_into_view:
                await element.scroll_into_view_if_needed(timeout=timeout)

            boundings = await element.bounding_box()
            x, y, width, height = boundings.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            for modifier in modifiers:
                await frame.page.keyboard.down(modifier)

            await frame.page.mouse.dblclick(x, y, button, delay)

            for modifier in modifiers:
                await frame.page.keyboard.up(modifier)

    async def check(element, page, force=False, no_wait_after=False, position={}, timeout: typing.Optional[float] = None, trial=False) -> None:
        frame = element.owner_frame()

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if await element.is_checked():
            return

        if not trial:
            if page.scroll_into_view:
                await element.scroll_into_view_if_needed(timeout=timeout)

            boundings = await element.bounding_box()
            x, y, width, height = boundings.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await frame.page.mouse.click(x, y, button="left", click_count=1, delay=20)

            assert await element.is_checked()

    async def uncheck(element, page, force=False, no_wait_after=False, position={}, timeout: typing.Optional[float] = None, trial=False) -> None:
        frame = element.owner_frame()

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if not await element.is_checked():
            return

        if not trial:
            if page.scroll_into_view:
                await element.scroll_into_view_if_needed(timeout=timeout)

            boundings = await element.bounding_box()
            x, y, width, height = boundings.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await frame.page.mouse.click(x, y, button="left", click_count=1, delay=20)

            assert not await element.is_checked()

    async def set_checked(element, page, checked=False, force=False, no_wait_after=False, position={}, timeout: typing.Optional[float] = None, trial=False) -> None:
        frame = element.owner_frame()

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if await element.is_checked() == checked:
            return

        if not trial:
            if page.scroll_into_view:
                await element.scroll_into_view_if_needed(timeout=timeout)

            boundings = await element.bounding_box()
            x, y, width, height = boundings.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await frame.page.mouse.click(x, y, button="left", click_count=1, delay=20)

            assert await element.is_checked()

    async def hover(element, page, force=False, modifiers=[], position={}, timeout: typing.Optional[float] = None, trial=False) -> None:
        frame = element.owner_frame()

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if not trial:
            if page.scroll_into_view:
                await element.scroll_into_view_if_needed(timeout=timeout)

            boundings = await element.bounding_box()
            x, y, width, height = boundings.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            for modifier in modifiers:
                await frame.page.keyboard.down(modifier)

            await frame.page.mouse.move(x, y)

            for modifier in modifiers:
                await frame.page.keyboard.up(modifier)

    async def type(element, page, text, delay=200, no_wait_after=False, timeout: typing.Optional[float] = None) -> None:
        frame = element.owner_frame()

        await element.wait_for_element_state("editable", timeout=timeout)

        if page.scroll_into_view:
            await element.scroll_into_view_if_needed(timeout=timeout)

        boundings = await element.bounding_box()
        x, y, width, height = boundings.values()

        x, y = x + width // 2, y + height // 2

        await frame.page.mouse.click(x, y, "left", 1, delay)

        await frame.page.keyboard.type(text, delay=delay)
