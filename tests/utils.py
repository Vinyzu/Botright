import re
from typing import List, cast

from undetected_playwright.async_api import Error, Selectors, ViewportSize

from botright.extended_typing import ElementHandle, Frame, Page


class Utils:
    async def attach_frame(self, page: Page, frame_id: str, url: str):
        handle = await page.evaluate_handle(
            """async ({ frame_id, url }) => {
                const frame = document.createElement('iframe');
                frame.src = url;
                frame.id = frame_id;
                document.body.appendChild(frame);
                await new Promise(x => frame.onload = x);
                return frame;
            }""",
            {"frame_id": frame_id, "url": url},
        )
        return await cast(ElementHandle, handle.as_element()).content_frame()

    async def detach_frame(self, page: Page, frame_id: str):
        await page.evaluate("frame_id => document.getElementById(frame_id).remove()", frame_id)

    def dump_frames(self, frame: Frame, indentation: str = "") -> List[str]:
        indentation = indentation or ""
        description = re.sub(r":\d+/", ":<PORT>/", frame.url)
        if frame.name:
            description += " (" + frame.name + ")"
        result = [indentation + description]
        sorted_frames = sorted(frame.child_frames, key=lambda frame: frame.url + frame.name)
        for child in sorted_frames:
            result = result + utils.dump_frames(child, "    " + indentation)
        return result

    async def verify_viewport(self, page: Page, width: int, height: int):
        assert cast(ViewportSize, page.viewport_size)["width"] == width
        assert cast(ViewportSize, page.viewport_size)["height"] == height
        assert await page.evaluate("window.innerWidth") == width
        assert await page.evaluate("window.innerHeight") == height

    async def register_selector_engine(self, selectors: Selectors, *args, **kwargs) -> None:
        try:
            await selectors.register(*args, **kwargs)
        except Error as exc:
            if "has been already registered" not in exc.message:
                raise exc


utils = Utils()
