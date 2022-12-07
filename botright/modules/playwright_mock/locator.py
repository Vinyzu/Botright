import typing

from . import element_handle, frame, frame_locator, js_handle


def attach_dyn_propr(instance, prop_name, propr):
    """Attach property proper to instance with name prop_name.

    Reference:
      * https://stackoverflow.com/a/1355444/509706
      * https://stackoverflow.com/questions/48448074
    """
    class_name = instance.__class__.__name__ + "Child"
    child_class = type(class_name, (instance.__class__,), {prop_name: propr})

    instance.__class__ = child_class


def mock_locator(locator) -> None:
    async def click_mocker(button="left", click_count=1, delay=20, force=False, modifiers=[], no_wait_after=False, position={}, timeout: typing.Optional[float] = None, trial=False):
        await Locator.click(locator, button=button, click_count=click_count, delay=delay, force=force, modifiers=modifiers, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    locator.click = click_mocker

    async def dblclick_mocker(button="left", delay=20, force=False, modifiers=[], no_wait_after=False, position={}, timeout: typing.Optional[float] = None, trial=False):
        await Locator.dblclick(locator, button=button, delay=delay, force=force, modifiers=modifiers, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    locator.dblclick = dblclick_mocker

    async def check_mocker(force=False, no_wait_after=False, position={}, timeout: typing.Optional[float] = None, trial=False):
        await Locator.check(locator, force=force, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    locator.check = check_mocker

    async def uncheck_mocker(force=False, no_wait_after=False, position={}, timeout: typing.Optional[float] = None, trial=False):
        await Locator.uncheck(locator, force=force, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    locator.uncheck = uncheck_mocker

    async def set_checked_mocker(checked=False, force=False, no_wait_after=False, position={}, timeout: typing.Optional[float] = None, trial=False):
        await Locator.set_checked(locator, checked=checked, force=force, no_wait_after=no_wait_after, position=position, timeout=timeout, trial=trial)

    locator.set_checked = set_checked_mocker

    async def hover_mocker(force=False, modifiers=[], position={}, timeout: typing.Optional[float] = None, trial=False):
        await Locator.hover(locator, force=force, modifiers=modifiers, position=position, timeout=timeout, trial=trial)

    locator.hover = hover_mocker

    async def type_mocker(text, delay=200, no_wait_after=False, timeout: typing.Optional[float] = None):
        await Locator.type(locator, text, delay=delay, no_wait_after=no_wait_after, timeout=timeout)

    locator.type = type_mocker

    # JsHandle
    async def mock_evaluate_handle(expression, arg=None) -> "JSHandle":
        _js_handle = await locator._evaluate_handle(expression, arg=arg)
        await js_handle.mock_js_handle(_js_handle, locator.page)
        return _js_handle

    locator._evaluate_handle = locator.evaluate_handle
    locator.evaluate_handle = mock_evaluate_handle

    # FrameLocator
    async def mock_frame_locator_func(selector) -> "JSHandle":
        _frame_locator = await locator._frame_locator(selector)
        await frame_locator.mock_frame_locator(_frame_locator)
        return _frame_locator

    locator._frame_locator = locator.frame_locator
    locator.frame_locator = mock_frame_locator_func

    # ElementHandle
    def element_handle_mocker(timeout: typing.Optional[float] = None):
        element = locator._element_handle(timeout=timeout)
        element_handle.mock_element_handle(element, locator.page)
        return element

    locator._element_handle = locator.element_handle
    locator.element_handle = element_handle_mocker

    # Locator
    def nth_mocker(index):
        _locator = locator._nth(index)
        mock_locator(_locator)
        return _locator

    locator._nth = locator.nth
    locator.nth = nth_mocker

    @property
    def first_mocker(self):
        _locator = locator._first
        mock_locator(_locator)
        return _locator

    @property
    def last_mocker(self):
        _locator = locator._last
        mock_locator(_locator)
        return _locator

    locator._first = locator.first
    locator._last = locator.last

    attach_dyn_propr(locator, "first", first_mocker)
    attach_dyn_propr(locator, "last", last_mocker)


class Locator:
    async def click(locator, button="left", click_count=1, delay=20, force=False, modifiers=[], no_wait_after=False, position={}, timeout: typing.Optional[float] = None, trial=False) -> None:
        if not force:
            await locator.wait_for(state="visible", timeout=timeout)

        if not trial:
            if locator.page.scroll_into_view:
                await locator.scroll_into_view_if_needed(timeout=timeout)

            boundings = await locator.bounding_box()
            x, y, width, height = boundings.values()

            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            for modifier in modifiers:
                await locator.page.keyboard.down(modifier)

            await locator.page.mouse.click(x, y, button, click_count, delay)

            for modifier in modifiers:
                await locator.page.keyboard.up(modifier)

    async def dblclick(locator, button="left", delay=20, force=False, modifiers=[], no_wait_after=False, position={}, timeout: typing.Optional[float] = None, trial=False) -> None:
        if not force:
            await locator.wait_for(state="visible", timeout=timeout)

        if not trial:
            if locator.page.scroll_into_view:
                await locator.scroll_into_view_if_needed(timeout=timeout)

            boundings = await locator.bounding_box()
            x, y, width, height = boundings.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            for modifier in modifiers:
                await locator.page.keyboard.down(modifier)

            await locator.page.mouse.dblclick(x, y, button, delay)

            for modifier in modifiers:
                await locator.page.keyboard.up(modifier)

    async def check(locator, force=False, no_wait_after=False, position={}, timeout: typing.Optional[float] = None, trial=False) -> None:
        if not force:
            await locator.wait_for(state="visible", timeout=timeout)

        if await locator.is_checked():
            return

        if not trial:
            if locator.page.scroll_into_view:
                await locator.scroll_into_view_if_needed(timeout=timeout)

            boundings = await locator.bounding_box()
            x, y, width, height = boundings.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await locator.page.mouse.click(x, y, button="left", click_count=1, delay=20)

            assert await locator.is_checked()

    async def uncheck(locator, force=False, no_wait_after=False, position={}, timeout: typing.Optional[float] = None, trial=False) -> None:
        if not force:
            await locator.wait_for(state="visible", timeout=timeout)

        if not await locator.is_checked():
            return

        if not trial:
            if locator.page.scroll_into_view:
                await locator.scroll_into_view_if_needed(timeout=timeout)

            boundings = await locator.bounding_box()
            x, y, width, height = boundings.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await locator.page.mouse.click(x, y, button="left", click_count=1, delay=20)

            assert not await locator.is_checked()

    async def set_checked(locator, checked=False, force=False, no_wait_after=False, position={}, timeout: typing.Optional[float] = None, trial=False) -> None:
        if not force:
            await locator.wait_for(state="visible", timeout=timeout)

        if await locator.is_checked() == checked:
            return

        if not trial:
            if locator.page.scroll_into_view:
                await locator.scroll_into_view_if_needed(timeout=timeout)

            boundings = await locator.bounding_box()
            x, y, width, height = boundings.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            await locator.page.mouse.click(x, y, button="left", click_count=1, delay=20)

            assert await locator.is_checked()

    async def hover(locator, force=False, modifiers=[], position={}, timeout: typing.Optional[float] = None, trial=False) -> None:
        if not force:
            await locator.wait_for(state="visible", timeout=timeout)

        if not trial:
            if locator.page.scroll_into_view:
                await locator.scroll_into_view_if_needed(timeout=timeout)

            boundings = await locator.bounding_box()
            x, y, width, height = boundings.values()
            if not position:
                x, y = x + width // 2, y + height // 2
            else:
                x, y = x + position["x"], y + position["y"]

            for modifier in modifiers:
                await locator.page.keyboard.down(modifier)

            await locator.page.mouse.move(x, y)

            for modifier in modifiers:
                await locator.page.keyboard.up(modifier)

    async def type(locator, text, delay=200, no_wait_after=False, timeout: typing.Optional[float] = None) -> None:
        await locator.wait_for(state="visible", timeout=timeout)

        if locator.page.scroll_into_view:
            await locator.scroll_into_view_if_needed(timeout=timeout)

        boundings = await locator.bounding_box()
        x, y, width, height = boundings.values()

        x, y = x + width // 2, y + height // 2

        await locator.page.mouse.click(x, y, "left", 1, delay)

        await locator.page.keyboard.type(text, delay=delay)
