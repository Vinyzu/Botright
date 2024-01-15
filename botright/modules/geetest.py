# from __future__ import annotations
#
# import base64
# import json
# from typing import Optional
#
# import httpx
# from playwright.async_api import Page, Route, Request
#
# from .geetest_helpers import solve_grid_captcha, solve_icon_captcha, solve_icon_crush, solve_nine_captcha, solve_slider_captcha
#
#
# class geeTestv3:
#     def __init__(self, page: Page) -> None:
#         self.page = page
#         self.puzzle_image_url = ""
#
#     async def get_result(self) -> Optional[str]:
#         try:
#             geetest_validate = self.page.locator('[name="geetest_validate"]')
#             return await geetest_validate.get_attribute("value", timeout=10000)
#         except Exception:
#             return None
#
#     async def solve_icon_captcha(self, mode: Optional[str] = "canny") -> None:
#         # Screenshotting the Captcha Area
#         captcha_frame = self.page.locator('[class="geetest_item_wrap"]')
#         captcha = await captcha_frame.screenshot(type="jpeg")
#         # Screenshotting the Prompt
#         template = self.page.locator('[class="geetest_tip_img"]')
#         template = await template.screenshot(type="jpeg")
#         # Getting the Boundary Box
#         box = await captcha_frame.bounding_box()
#         # Solving the Captcha
#         res = solve_icon_captcha(captcha, template, mode=mode)
#         # Click on the Correct Images
#         for coord in res:
#             x, y = coord
#             x, y = x + box["x"], y + box["y"]
#             await self.page.mouse.click(x, y)
#         # Submitting the Captcha
#         submit = self.page.locator('[class="geetest_commit_tip"]')
#         await submit.click()
#
#     async def solve_nine_captcha(self) -> None:
#         # Screenshotting the Captcha Area
#         captcha_frame = self.page.locator('[class="geetest_table_box"]')
#         captcha = await captcha_frame.screenshot(type="jpeg")
#         # Screenshotting the Prompt
#         template = self.page.locator('[class="geetest_tip_img"]')
#         template = await template.screenshot(type="jpeg")
#         # Getting the Boundary Box
#         box = await captcha_frame.bounding_box()
#         # Solving the Captcha
#         res = solve_nine_captcha(captcha, template)
#         # Click on the Correct Images
#         for coord in res:
#             x, y = coord
#             x, y = x + box["x"], y + box["y"]
#             await self.page.mouse.click(x, y)
#         # Submitting the Captcha
#         submit = self.page.locator('[class="geetest_commit_tip"]')
#         await submit.click()
#
#     async def log_puzzle_piece(self) -> None:
#         async def check_json(route, request):
#             self.puzzle_image_url = request.url
#             await route.continue_()
#
#         await self.page.route("https://static.geetest.com/pictures/**.png", check_json)
#
#     async def solve_slider_captcha(self) -> None:
#         # Getting The Background (Without the PuzzlePiece) from the Elements Base64
#         captcha_base64_url = await self.page.evaluate('document.getElementsByClassName("geetest_canvas_bg geetest_absolute")[0].toDataURL()')
#         captcha_bytes = base64.b64decode(captcha_base64_url.split(",")[1])
#         # Getting the PuzzlePiece Image Bytes from Url
#         template_bytes = httpx.get(self.puzzle_image_url).content
#
#         # Getting the Offset with Template Matching of the Contours
#         offset = solve_slider_captcha(captcha_bytes, template_bytes)
#         # Getting The Slider Bounding Box
#         slider = self.page.locator('[class="geetest_slider_button"]')
#         box = await slider.bounding_box()
#         # Getting The Middle of the Slider
#         middle_x, middle_y = box["x"] + box["width"] // 2, box["y"] + box["height"] // 2
#         # Sliding the Slider by the Offset
#         await self.page.mouse.move(middle_x, middle_y)
#         await self.page.mouse.down()
#         await self.page.mouse.move(middle_x + offset, middle_y)
#         await self.page.mouse.up()
#
#     async def solve_geetest(self, retry: Optional[bool] = False, mode: Optional[str] = "canny") -> str:
#         # Logging the Puzzle Piece for SliderCaptcha
#         await self.log_puzzle_piece()
#         # If Retry has to be clicked
#         if retry:
#             # Clicking the Retry Button
#             reset_button = self.page.locator('[class="geetest_reset_tip_content"]')
#             await reset_button.click()
#
#         # Checking if the Captcha is already solved => NoCaptcha
#         await self.page.wait_for_timeout(4000)
#         if result := await self.get_result():
#             return result
#
#         # Checking Captcha Type
#         if await self.page.is_visible('[class="geetest_slider_button"]'):
#             # SliderCaptcha
#             # Wait for the Captcha to load
#             await self.page.wait_for_timeout(2000)
#             # Solve SliderCaptcha
#             await self.solve_slider_captcha()
#             await self.page.wait_for_timeout(2000)
#             # Returning Result or doing the Captcha Again
#             if result := await self.get_result():
#                 return result
#             else:
#                 return await self.solve_geetest(mode=mode)
#
#         elif await self.page.is_visible('[class="geetest_tip_img"]'):
#             # Wait for the Captcha to load
#             await self.page.wait_for_timeout(2000)
#             # Checking Captcha Type Again
#             geetest_solving_aria = self.page.locator('[class="geetest_item_wrap"]')
#
#             if await geetest_solving_aria.count() != 1:
#                 # 9 Image Captcha
#                 await self.solve_nine_captcha()
#             else:
#                 # IconCaptcha
#                 await self.solve_icon_captcha(mode=mode)
#
#             # Waiting 2 Seconds to get the result
#             await self.page.wait_for_timeout(2000)
#             # Returning Result or doing the Captcha Again
#             if result := await self.get_result():
#                 return result
#             else:
#                 return await self.solve_geetest(mode=mode)
#
#         elif await self.page.is_visible('[class="geetest_tip_space"]'):
#             # SpaceCaptcha
#             raise NotImplementedError("SpaceCaptcha isnt implemented yet")
#
#         elif await self.page.is_visible('[class="geetest_reset_tip_content"]'):
#             # Retry Button
#             return await self.solve_geetest(retry=True, mode=mode)
#
#
# class geeTestv4:
#     def __init__(self, page: Page) -> None:
#         self.page = page
#         self.result = None
#         self.bg_image_url = None
#         self.puzzle_image_url = None
#
#     async def log_result(self) -> None:
#         async def check_json(route: Route, request: Request):
#             await route.continue_()
#             if "verify" in request.url:
#                 resp = await request.response()
#                 resp_text = await resp.text()
#                 resp_json = json.loads(resp_text.split("(")[1].split(")")[0])
#                 if data := resp_json.get("data"):
#                     if seccode := data.get("seccode"):
#                         geeTestv4.result = seccode.get("pass_token")
#
#         await self.page.route("https://gcaptcha4.geetest.com/**", check_json)
#
#     async def log_images(self) -> None:
#         async def check_json(route: Route, request: Request):
#             if "bg" in request.url:
#                 self.bg_image_url = request.url
#             elif "slice" in request.url:
#                 self.puzzle_image_url = request.url
#             await route.continue_()
#
#         await self.page.route("**/*.png", check_json)
#
#     async def solve_slider_captcha(self) -> None:
#         # Getting The Background Bytes from Url
#         captcha_bytes = httpx.get(self.bg_image_url).content
#         # Getting the PuzzlePiece Image Bytes from Url
#         template_bytes = httpx.get(self.puzzle_image_url).content
#
#         # Getting the Offset with Template Matching of the Contours
#         offset = solve_slider_captcha(captcha_bytes, template_bytes)
#         # Getting The Slider Bounding Box
#         slider = self.page.locator('[class *= "geetest_arrow"]')
#         box = await slider.bounding_box()
#         # Getting The Middle of the Slider
#         middle_x, middle_y = box["x"] + box["width"] // 2, box["y"] + box["height"] // 2
#         # Sliding the Slider by the Offset
#         await self.page.mouse.move(middle_x, middle_y)
#         await self.page.mouse.down()
#         await self.page.mouse.move(middle_x + offset, middle_y)
#         await self.page.mouse.up()
#
#     async def solve_icon_captcha(self, mode: Optional[str] = "canny") -> None:
#         # Screenshotting the Captcha Area
#         captcha_frame = self.page.locator('[class*= "geetest_bg"]')
#         captcha = await captcha_frame.screenshot(type="jpeg")
#         # Screenshotting the Prompt
#         template = self.page.locator('[class *= "geetest_ques_tips"]')
#         template = await template.screenshot(type="jpeg")
#         # Getting the Boundary Box
#         box = await captcha_frame.bounding_box()
#         # Solving the Captcha
#         res = solve_icon_captcha(captcha, template, mode=mode)
#         # Click on the Correct Images
#         for coord in res:
#             x, y = coord
#             x, y = x + box["x"], y + box["y"]
#             await self.page.mouse.click(x, y)
#         # Submitting the Captcha
#         submit = self.page.locator('[class *= "geetest_submit"]').first
#         await submit.click()
#
#     async def solve_gobang(self) -> None:
#         grid = []
#         for y in range(5):
#             grid_element = []
#             for x in range(5):
#                 element = self.page.locator(f'[class *= "geetest_item-{y}-{x} geetest_itemimg"]')
#                 style = await element.get_attribute("style")
#                 if len(style.split('url("')) == 1:
#                     grid_element.append(None)
#                 else:
#                     url = style.split('url("')[1].split('"')[0]
#                     grid_element.append(url)
#             grid.append(grid_element)
#
#         start, finish = solve_grid_captcha(grid)
#         to_start = self.page.locator(f'[class *= "geetest_item-{start[0]}-{start[1]} geetest_itemimg"]')
#         await to_start.click()
#         to_finish = self.page.locator(f'[class *= "geetest_item-{finish[0]}-{finish[1]} geetest_itemimg"]')
#         await to_finish.click()
#
#     async def solve_icon_crush(self) -> None:
#         grid = []
#         for y in range(3):
#             grid_element = []
#             for x in range(3):
#                 parent = self.page.locator(f'[class *= "geetest_item-{y}-{x} geetest_backimg"]')
#                 child = parent.locator('[class *= "geetest_img"]')
#                 style = await child.get_attribute("style")
#                 if len(style.split('url("')) == 1:
#                     grid_element.append(None)
#                 else:
#                     url = style.split('url("')[1].split('"')[0]
#                     grid_element.append(url)
#             grid.append(grid_element)
#
#         start, finish = solve_icon_crush(grid)
#         to_start = self.page.locator(f'[class *= "geetest_item-{start[0]}-{start[1]} geetest_backimg"]')
#         await to_start.click()
#         to_finish = self.page.locator(f'[class *= "geetest_item-{finish[0]}-{finish[1]} geetest_backimg"]')
#         await to_finish.click()
#
#     async def solve_geetest(self, retry: Optional[bool] = False, mode: Optional[str] = "canny") -> bool | str:
#         # Logging the Puzzle Piece for SliderCaptcha
#         await self.log_images()
#         await self.page.wait_for_timeout(2000)
#
#         if await self.page.is_enabled("geetest_lock_success", timeout=3000):
#             return True
#
#         # If Retry has to be clicked
#         if retry:
#             # Clicking the Retry Button
#             reset_button = self.page.locator('[class *= "geetest_refresh"]').first
#             await reset_button.click()
#
#         # Checking if the Captcha is already solved => NoCaptcha
#         await self.page.wait_for_timeout(4000)
#         if self.result:
#             return self.result
#
#         # Checking Captcha Type
#         if await self.page.is_visible('[class *= "geetest_arrow"]'):
#             # SliderCaptcha
#             # Wait for the Captcha to load
#             await self.page.wait_for_timeout(2000)
#             # Checking if a background is logged
#             if not self.bg_image_url:
#                 # Clicking the Retry Button
#                 reset_button = self.page.locator('[class *= "geetest_refresh"]').first
#                 await reset_button.click()
#             # Solve SliderCaptcha
#             await self.solve_slider_captcha()
#             await self.page.wait_for_timeout(2000)
#             # Returning Result or doing the Captcha Again
#             if self.result:
#                 return self.result
#             else:
#                 return await self.solve_geetest(mode=mode)
#
#         elif await self.page.is_visible('[class *= "geetest_ques_tips"]'):
#             # IconCaptcha
#             # Wait for the Captcha to load
#             await self.page.wait_for_timeout(2000)
#             # Solve IconCaptcha
#             await self.solve_icon_captcha(mode=mode)
#
#             # Waiting 2 Seconds to get the result
#             await self.page.wait_for_timeout(2000)
#             # Returning Result or doing the Captcha Again
#             if self.result:
#                 return self.result
#             else:
#                 return await self.solve_geetest(mode=mode)
#
#         elif await self.page.is_visible('[class *= "geetest_winlinze"]'):
#             # GoBang Captcha
#             # Wait for the Captcha to load
#             await self.page.wait_for_timeout(2000)
#             # Solve IconCaptcha
#             await self.solve_gobang()
#
#             # Waiting 2 Seconds to get the result
#             await self.page.wait_for_timeout(2000)
#             # Returning Result or doing the Captcha Again
#             if self.result:
#                 return self.result
#             else:
#                 return await self.solve_geetest(mode=mode)
#
#         elif await self.page.is_visible('[class *= "geetest_subitem geetest_match"]'):
#             # IconCrush Captcha
#             # Wait for the Captcha to load
#             await self.page.wait_for_timeout(2000)
#             # Solve IconCaptcha
#             await self.solve_icon_crush()
#
#             # Waiting 2 Seconds to get the result
#             await self.page.wait_for_timeout(2000)
#             # Returning Result or doing the Captcha Again
#             if self.result:
#                 return self.result
#             else:
#                 return await self.solve_geetest(mode=mode)
#
#         elif await self.page.is_visible('[class *= "geetest_refresh"]'):
#             # Retry Button
#             return await self.solve_geetest(retry=True, mode=mode)
#
#
# async def solve_geetest(page: Page, mode: Optional[str] = "canny") -> str:
#     if await page.is_visible('[class="geetest_btn"]'):
#         # geeTestv3
#         geetest = geeTestv3(page)
#         # Clicking the Captcha
#         geetest_button = page.locator('[class="geetest_btn"]').last
#         await geetest_button.scroll_into_view_if_needed()
#         await geetest_button.click()
#
#         return await geetest.solve_geetest(mode=mode)
#     else:
#         # geeTestv4
#         geetest = geeTestv4(page)
#         # Logging the Result
#         await geetest.log_result()
#         # Clicking the Captcha
#         geetest_button = page.locator('[class *= "geetest_btn_click"]').last
#         await geetest_button.scroll_into_view_if_needed()
#         await geetest_button.click()
#
#         return await geetest.solve_geetest()
