from __future__ import annotations

from typing import Optional

from playwright.async_api import BrowserContext, Page, Route, Request

class hCaptcha:
    def __init__(self, browser: BrowserContext, page: Page) -> None:
        self.captcha_token = ""

        self.browser = browser
        self.page = page

    async def log_captcha(self) -> None:
        async def check_json(route: Route, request: Request):
            await route.continue_()
            try:
                response = await request.response()
                await response.finished()
                json = await response.json()
                if json.get("generated_pass_UUID"):
                    hCaptcha.captcha_token = json.get("generated_pass_UUID")
            except Exception:
                pass

        await self.page.route("https://hcaptcha.com/checkcaptcha/**", check_json)

    async def mock_captcha(self, rq_data: str) -> None:
        async def mock_json(route, request):

            payload = {**request.post_data_json, "rqdata": rq_data, "hl": "en"} if rq_data else request.post_data_json
            response = await self.page.request.post(request.url, form=payload, headers=request.headers)
            json = await response.json()

            if json.get("generated_pass_UUID"):
                hCaptcha.captcha_token = json.get("generated_pass_UUID")
            await route.fulfill(response=response)

        await self.page.route("https://hcaptcha.com/getcaptcha/**", mock_json)

    async def solve_hcaptcha(self, rq_data: Optional[str] = None) -> Optional[str]:
        self.captcha_token = None
        # Logging Captcha Token
        await self.log_captcha()
        # Mocking Captcha Request
        await self.mock_captcha(rq_data)
        # Clicking Captcha Checkbox
        await self.page.hcaptcha_agent.handle_checkbox()
        await self.page.hcaptcha_agent()

        return self.captcha_token

    async def get_hcaptcha(self, site_key: Optional[str] = "00000000-0000-0000-0000-000000000000", rq_data: Optional[str] = None) -> Optional[str]:
        page = await self.browser.new_page()
        await page.goto(f"https://accounts.hcaptcha.com/demo?sitekey={site_key}")
        return await page.solve_hcaptcha(rq_data=rq_data)
