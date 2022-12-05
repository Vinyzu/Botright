from . import locator


def attach_dyn_propr(instance, prop_name, propr):
    """Attach property proper to instance with name prop_name.

    Reference:
      * https://stackoverflow.com/a/1355444/509706
      * https://stackoverflow.com/questions/48448074
    """
    class_name = instance.__class__.__name__ + "Child"
    child_class = type(class_name, (instance.__class__,), {prop_name: propr})

    instance.__class__ = child_class


def mock_frame_locator(frame_locator) -> None:
    # MouseMocking
    def locator_mocker(selector, has=None, has_text=""):
        _locator = frame_locator._locator(selector, has=has, has_text=has_text)
        locator.mock_locator(_locator)
        return _locator

    frame_locator._locator = frame_locator.locator
    frame_locator.locator = locator_mocker

    # FrameLocator
    def nth_mocker(index):
        _locator = frame_locator._nth(index)
        mock_frame_locator(_locator)
        return _locator

    frame_locator._nth = frame_locator.nth
    frame_locator.nth = nth_mocker

    @property
    def first_mocker(self):
        _locator = frame_locator._first
        mock_frame_locator(_locator)
        return _locator

    @property
    def last_mocker(self):
        _locator = frame_locator._last
        mock_frame_locator(_locator)
        return _locator

    frame_locator._first = frame_locator.first
    frame_locator._last = frame_locator.last

    attach_dyn_propr(frame_locator, "first", first_mocker)
    attach_dyn_propr(frame_locator, "last", last_mocker)
