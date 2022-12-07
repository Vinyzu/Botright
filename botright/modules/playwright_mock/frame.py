import typing

from . import element_handle, frame_locator, js_handle, locator


def mock_frame(frame) -> None:
    if not frame:
        return

    async def click_mocker(selector, button="left", click_count=1, strict=False, delay=20, force=False, modifiers=[], no_wait_after=False, position={}, timeout: typing.Optional[float] = None, trial=False):
        await Frame.click(frame, selector, button=button, click_count=click_count, strict=strict, delay=delay, force=force, modifiers=modifiers, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    frame.click = click_mocker

    async def dblclick_mocker(selector, button="left", strict=False, delay=20, force=False, modifiers=[], no_wait_after=False, position={}, timeout: typing.Optional[float] = None, trial=False):
        await Frame.dblclick(frame, selector, button=button, strict=strict, delay=delay, force=force, modifiers=modifiers, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    frame.dblclick = dblclick_mocker

    async def check_mocker(selector, force=False, no_wait_after=False, position={}, strict=False, timeout: typing.Optional[float] = None, trial=False):
        await Frame.check(frame, selector, force=force, no_wait_after=no_wait_after, position=position, strict=strict, timeout=timeout, trial=trial)

    frame.check = check_mocker

    async def uncheck_mocker(selector, force=False, no_wait_after=False, position={}, strict=False, timeout: typing.Optional[float] = None, trial=False):
        await Frame.uncheck(frame, selector, force=force, no_wait_after=no_wait_after, position=position, strict=strict, timeout=timeout, trial=trial)

    frame.uncheck = uncheck_mocker

    async def set_checked_mocker(selector, checked=False, force=False, no_wait_after=False, position={}, timeout: typing.Optional[float] = None, trial=False):
        await Frame.set_checked(frame, selector, checked=checked, force=force, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    frame.set_checked = set_checked_mocker

    async def hover_mocker(selector, force=False, modifiers=[], position={}, strict=False, timeout: typing.Optional[float] = None, trial=False):
        await Frame.hover(frame, selector, force=force, modifiers=modifiers, position=position, strict=strict, timeout=timeout, trial=trial)

    frame.hover = hover_mocker

    async def type_mocker(selector, text, delay=200, no_wait_after=False, strict=False, timeout: typing.Optional[float] = None):
        await Frame.type(frame, selector, text, delay=delay, no_wait_after=no_wait_after, strict=strict, timeout=timeout)

    frame.type = type_mocker

    for frame in frame.child_frames:
        mock_frame(frame)

    # ElementHandle
    async def mock_query_selector(selector, strict=False) -> typing.Optional["ElementHandle"]:
        element = await frame._query_selector(selector, strict=strict)
        if element:
            await element_handle.mock_element_handle(element, frame.page)
        return element

    frame._query_selector = frame.query_selector
    frame.query_selector = mock_query_selector

    async def mock_query_selector_all(selector) -> typing.List["ElementHandle"]:
        elements = await frame._query_selector_all(selector)
        for element in elements:
            await element_handle.mock_element_handle(element, frame.page)
        return elements

    frame._query_selector_all = frame.query_selector_all
    frame.query_selector_all = mock_query_selector_all

    async def mock_wait_for_selector(selector, state=[], strict=False, timeout: typing.Optional[float] = None) -> typing.Optional["ElementHandle"]:
        element = await frame.__wait_for_selector(selector, state=state, strict=strict, timeout=timeout)
        if element:
            await element_handle.mock_element_handle(element, frame.page)
        return element

    frame.__wait_for_selector = frame.wait_for_selector
    frame.wait_for_selector = mock_wait_for_selector

    async def mock_add_script_tag(content="", path="", type="", url="") -> "ElementHandle":
        element = await frame._add_script_tag(content=content, path=path, type=type, url=url)
        await element_handle.mock_element_handle(element, frame.page)
        return element

    frame._add_script_tag = frame.add_script_tag
    frame.add_script_tag = mock_add_script_tag

    async def mock_add_style_tag(content="", path="", type="", url="") -> "ElementHandle":
        element = await frame._add_script_tag(content=content, path=path, type=type, url=url)
        await element_handle.mock_element_handle(element, frame.page)
        return element

    frame._add_script_tag = frame.add_script_tag
    frame.add_script_tag = mock_add_style_tag

    async def frame_element() -> "ElementHandle":
        element = await frame._frame_element()
        await element_handle.mock_element_handle(element, frame.page)
        return element

    frame._frame_element = frame.frame_element
    frame.frame_element = frame_element

    # JsHandle
    async def mock_evaluate_handle(expression, arg=None) -> "JSHandle":
        _js_handle = await frame._evaluate_handle(expression, arg=arg)
        await js_handle.mock_js_handle(_js_handle, frame.page)
        return _js_handle

    frame._evaluate_handle = frame.evaluate_handle
    frame.evaluate_handle = mock_evaluate_handle

    async def mock_wait_for_function(expression, arg=None, polling="raf", timeout: typing.Optional[float] = None) -> "JSHandle":
        _js_handle = await frame._wait_for_function(expression, arg=arg, polling=polling, timeout=timeout)
        await js_handle.mock_js_handle(_js_handle, frame.page)
        return _js_handle

    frame._wait_for_function = frame.wait_for_function
    frame.wait_for_function = mock_wait_for_function

    # FrameLocator
    async def frame_locator_mocker(selector) -> "JSHandle":
        _frame_locator = await frame._frame_locator(selector)
        await frame_locator.mock_frame_locator(_frame_locator)
        return _frame_locator

    frame._frame_locator = frame.frame_locator
    frame.frame_locator = frame_locator_mocker

    # Locator
    async def locator_mocker(selector, has=None, has_text="") -> "JSHandle":
        _locator = await frame._locator(selector, has=has, has_text=has_text)
        locator.mock_locator(_locator)
        return _locator

    frame._locator = frame.locator
    frame.locator = locator_mocker


class Frame:
    async def click(frame, selector, button="left", click_count=1, strict=False, delay=20, force=False, modifiers=[], no_wait_after=False, position={}, timeout: typing.Optional[float] = None, trial=False) -> None:
        element = await frame.wait_for_selector(selector, state="visible" if not force else "hidden", strict=strict, timeout=timeout)

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if not trial:
            if frame.page.scroll_into_view:
                await locator.scroll_into_view_if_needed(timeout=timeout)

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

    async def dblclick(frame, selector, button="left", strict=False, delay=20, force=False, modifiers=[], no_wait_after=False, position={}, timeout: typing.Optional[float] = None, trial=False) -> None:
        element = await frame.wait_for_selector(selector, state="visible" if not force else "hidden", strict=strict, timeout=timeout)

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if not trial:
            if frame.page.scroll_into_view:
                await locator.scroll_into_view_if_needed(timeout=timeout)

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

    async def check(frame, selector, force=False, no_wait_after=False, position={}, strict=False, timeout: typing.Optional[float] = None, trial=False) -> None:
        element = await frame.wait_for_selector(selector, state="visible" if not force else "hidden", strict=strict, timeout=timeout)

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if await element.is_checked():
            return

        if not trial:
            if frame.page.scroll_into_view:
                await locator.scroll_into_view_if_needed(timeout=timeout)

            boundings = await element.bounding_box()
            x, y, width, height = boundings.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await frame.page.mouse.click(x, y, button="left", click_count=1, delay=20)

            assert await element.is_checked()

    async def uncheck(frame, selector, force=False, no_wait_after=False, position={}, strict=False, timeout: typing.Optional[float] = None, trial=False) -> None:
        element = await frame.wait_for_selector(selector, state="visible" if not force else "hidden", strict=strict, timeout=timeout)

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if not await element.is_checked():
            return

        if not trial:
            if frame.page.scroll_into_view:
                await locator.scroll_into_view_if_needed(timeout=timeout)

            boundings = await element.bounding_box()
            x, y, width, height = boundings.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await frame.page.mouse.click(x, y, button="left", click_count=1, delay=20)

            assert not await element.is_checked()

    async def set_checked(frame, selector, checked=False, force=False, no_wait_after=False, position={}, strict=False, timeout: typing.Optional[float] = None, trial=False) -> None:
        element = await frame.wait_for_selector(selector, state="visible" if not force else "hidden", strict=strict, timeout=timeout)

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if await element.is_checked() == checked:
            return

        if not trial:
            if frame.page.scroll_into_view:
                await locator.scroll_into_view_if_needed(timeout=timeout)

            boundings = await element.bounding_box()
            x, y, width, height = boundings.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await frame.page.mouse.click(x, y, button="left", click_count=1, delay=20)

            assert await element.is_checked()

    async def hover(frame, selector, force=False, modifiers=[], position={}, strict=False, timeout: typing.Optional[float] = None, trial=False) -> None:
        element = await frame.wait_for_selector(selector, state="visible" if not force else "hidden", strict=strict, timeout=timeout)

        if not force:
            await element.wait_for_element_state("editable", timeout=timeout)

        if not trial:
            if frame.page.scroll_into_view:
                await locator.scroll_into_view_if_needed(timeout=timeout)

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

    async def type(frame, selector, text, delay=200, no_wait_after=False, strict=False, timeout: typing.Optional[float] = None) -> None:
        element = await frame.wait_for_selector(selector, state="visible", strict=strict, timeout=timeout)

        await element.wait_for_element_state("editable", timeout=timeout)

        if frame.page.scroll_into_view:
            await locator.scroll_into_view_if_needed(timeout=timeout)

        boundings = await element.bounding_box()
        x, y, width, height = boundings.values()

        x, y = x + width // 2, y + height // 2

        await frame.page.mouse.click(x, y, "left", 1, delay)

        await frame.page.keyboard.type(text, delay=delay)
