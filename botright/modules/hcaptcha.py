from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Optional

from hcaptcha_challenger.agents import AgentT

if TYPE_CHECKING:
    from botright.extended_typing import BrowserContext, Page

tmp_dir = Path(__file__).parent.joinpath("tmp_dir")


class hCaptcha:
    def __init__(self, browser: BrowserContext, page: Page) -> None:
        """
        Initialize an hCaptcha solver.

        Args:
            browser (BrowserContext): The Playwright browser context to use.
            page (Page): The Playwright page where hCaptcha challenges will be solved.
        """
        self.browser = browser
        self.page = page

        self.retry_times = 8
        self.hcaptcha_agent = AgentT.from_page(page=page, tmp_dir=tmp_dir, self_supervised=True)

    async def mock_captcha(self, rq_data: str) -> None:
        """
        Mock hCaptcha requests by intercepting network requests to getcaptcha.

        Args:
            rq_data (str): The data required for mocking the hCaptcha request.

        This method mocks the hCaptcha request and captures the generated hCaptcha token.
        """

        async def mock_json(route, request):

            payload = {**request.post_data_json, "rqdata": rq_data, "hl": "en"} if rq_data else request.post_data_json
            response = await self.page.request.post(request.url, form=payload, headers=request.headers)
            await route.fulfill(response=response)

        await self.page.route("https://hcaptcha.com/getcaptcha/**", mock_json)

    async def solve_hcaptcha(self, rq_data: Optional[str] = None) -> Optional[str]:
        """
        Solve an hCaptcha challenge.

        Args:
            rq_data (Optional[str]): Additional data required for solving the hCaptcha challenge.

        Returns:
            Optional[str]: The hCaptcha token if successfully solved; otherwise, None.

        This method captures the hCaptcha token by logging and mocking hCaptcha requests, then simulates clicking the
        hCaptcha checkbox to solve the challenge.
        """
        # Mocking Captcha Request
        if rq_data:
            await self.mock_captcha(rq_data)
        # Clicking Captcha Checkbox
        await self.hcaptcha_agent.handle_checkbox()

        for pth in range(1, self.retry_times):
            result = await self.hcaptcha_agent.execute()
            if result == self.hcaptcha_agent.status.CHALLENGE_BACKCALL:
                await self.page.wait_for_timeout(500)
                fl = self.page.frame_locator(self.hcaptcha_agent.HOOK_CHALLENGE)
                await fl.locator("//div[@class='refresh button']").click()
            elif result == self.hcaptcha_agent.status.CHALLENGE_SUCCESS:
                if self.hcaptcha_agent.cr:
                    captcha_token: str = self.hcaptcha_agent.cr.generated_pass_UUID
                    return captcha_token

        return f"Exceeded maximum retry times of {self.retry_times}"

    async def get_hcaptcha(self, site_key: Optional[str] = "00000000-0000-0000-0000-000000000000", rq_data: Optional[str] = None) -> Optional[str]:
        """
        Get an hCaptcha token for a specific site.

        Args:
            site_key (Optional[str]): The site key for the hCaptcha challenge (default is a demo site key).
            rq_data (Optional[str]): Additional data required for solving the hCaptcha challenge.

        Returns:
            Optional[str]: The hCaptcha token if successfully obtained; otherwise, None.

        This method opens a new page, navigates to a specified hCaptcha demo page with the given site key, and
        solves the hCaptcha challenge to obtain the token.
        """
        page = await self.browser.new_page()
        await page.goto(f"https://accounts.hcaptcha.com/demo?sitekey={site_key}")
        return await page.solve_hcaptcha(rq_data=rq_data)
