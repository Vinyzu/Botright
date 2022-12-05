import base64
import json

import httpx
from PIL import Image

from .geetest_helpers import solve_grid_captcha, solve_icon_captcha, solve_icon_crush, solve_nine_captcha, solve_slider_captcha


class geeTestv3:
    puzzle_image_url = ""

    async def get_result(page):
        try:
            geetest_validate = page.locator('[name="geetest_validate"]')
            return await geetest_validate.get_attribute("value", timeout=10000)
        except:
            return None

    async def solve_icon_captcha(page, mode="canny"):
        # Screenshotting the Captcha Area
        captcha_frame = page.locator('[class="geetest_item_wrap"]')
        captcha = await captcha_frame.screenshot(type="jpeg")
        # Screenshotting the Prompt
        template = page.locator('[class="geetest_tip_img"]')
        template = await template.screenshot(type="jpeg")
        # Getting the Boundary Box
        box = await captcha_frame.bounding_box()
        # Solving the Captcha
        res = solve_icon_captcha(captcha, template, mode=mode)
        # Click on the Correct Images
        for coord in res:
            x, y = coord
            x, y = x + box["x"], y + box["y"]
            await page.mouse.click(x, y)
        # Submitting the Captcha
        submit = page.locator('[class="geetest_commit_tip"]')
        await submit.click()

    async def solve_nine_captcha(page):
        # Screenshotting the Captcha Area
        captcha_frame = page.locator('[class="geetest_table_box"]')
        captcha = await captcha_frame.screenshot(type="jpeg")
        # Screenshotting the Prompt
        template = page.locator('[class="geetest_tip_img"]')
        template = await template.screenshot(type="jpeg")
        # Getting the Boundary Box
        box = await captcha_frame.bounding_box()
        # Solving the Captcha
        res = solve_nine_captcha(captcha, template)
        # Click on the Correct Images
        for coord in res:
            x, y = coord
            x, y = x + box["x"], y + box["y"]
            await page.mouse.click(x, y)
        # Submitting the Captcha
        submit = page.locator('[class="geetest_commit_tip"]')
        await submit.click()

    async def log_puzzle_piece(page):
        async def check_json(route, request):
            geeTestv3.puzzle_image_url = request.url
            await route.continue_()

        await page.route("https://static.geetest.com/pictures/**.png", check_json)

    async def solve_slider_captcha(page):
        # Getting The Background (Without the PuzzlePiece) from the Elements Base64
        captcha_base64_url = await page.evaluate('document.getElementsByClassName("geetest_canvas_bg geetest_absolute")[0].toDataURL()')
        captcha_bytes = base64.b64decode(captcha_base64_url.split(",")[1])
        # Getting the PuzzlePiece Image Bytes from Url
        template_bytes = httpx.get(geeTestv3.puzzle_image_url).content

        # Getting the Offset with Template Matching of the Contours
        offset = solve_slider_captcha(captcha_bytes, template_bytes)
        # Getting The Slider Bounding Box
        slider = page.locator('[class="geetest_slider_button"]')
        box = await slider.bounding_box()
        # Getting The Middle of the Slider
        middle_x, middle_y = box["x"] + box["width"] // 2, box["y"] + box["height"] // 2
        # Sliding the Slider by the Offset
        await page.mouse.move(middle_x, middle_y)
        await page.mouse.down()
        await page.mouse.move(middle_x + offset, middle_y)
        await page.mouse.up()

    async def solve_geetest(page, retry=False, mode="canny"):
        # Logging the Puzzle Piece for SliderCaptcha
        await geeTestv3.log_puzzle_piece(page)
        # If Retry has to be clicked
        if retry:
            # Clicking the Retry Button
            reset_button = page.locator('[class="geetest_reset_tip_content"]')
            await reset_button.click()

        # Checking if the Captcha is already solved => NoCaptcha
        await page.wait_for_timeout(4000)
        if result := await geeTestv3.get_result(page):
            return result

        # Checking Captcha Type
        if await page.is_visible('[class="geetest_slider_button"]'):
            # SliderCaptcha
            # Wait for the Captcha to load
            await page.wait_for_timeout(2000)
            # Solve SliderCaptcha
            await geeTestv3.solve_slider_captcha(page)
            await page.wait_for_timeout(2000)
            # Returning Result or doing the Captcha Again
            if result := await geeTestv3.get_result(page):
                return result
            else:
                return await geeTestv3.solve_geetest(page, mode=mode)

        elif await page.is_visible('[class="geetest_tip_img"]'):
            # Wait for the Captcha to load
            await page.wait_for_timeout(2000)
            # Checking Captcha Type Again
            geetest_solving_aria = page.locator('[class="geetest_item_wrap"]')

            if await geetest_solving_aria.count() != 1:
                # 9 Image Captcha
                await geeTestv3.solve_nine_captcha(page)
            else:
                # IconCaptcha
                await geeTestv3.solve_icon_captcha(page, mode=mode)

            # Waiting 2 Seconds to get the result
            await page.wait_for_timeout(2000)
            # Returning Result or doing the Captcha Again
            if result := await geeTestv3.get_result(page):
                return result
            else:
                return await geeTestv3.solve_geetest(page, mode=mode)

        elif await page.is_visible('[class="geetest_tip_space"]'):
            # SpaceCaptcha
            raise NotImplementedError("SpaceCaptcha isnt implemented yet")

        elif await page.is_visible('[class="geetest_reset_tip_content"]'):
            # Retry Button
            return await geeTestv3.solve_geetest(page, retry=True, mode=mode)


class geeTestv4:
    result = None
    bg_image_url = None
    puzzle_image_url = None

    async def log_result(page):
        async def check_json(route, request):
            await route.continue_()
            if "verify" in request.url:
                resp = await request.response()
                resp_text = await resp.text()
                resp_json = json.loads(resp_text.split("(")[1].split(")")[0])
                if data := resp_json.get("data"):
                    if seccode := data.get("seccode"):
                        geeTestv4.result = seccode.get("pass_token")

        await page.route("https://gcaptcha4.geetest.com/**", check_json)

    async def log_images(page):
        async def check_json(route, request):
            if "bg" in request.url:
                geeTestv4.bg_image_url = request.url
            elif "slice" in request.url:
                geeTestv4.puzzle_image_url = request.url
            await route.continue_()

        await page.route("**/*.png", check_json)

    async def solve_slider_captcha(page):
        # Getting The Background Bytes from Url
        captcha_bytes = httpx.get(geeTestv4.bg_image_url).content
        # Getting the PuzzlePiece Image Bytes from Url
        template_bytes = httpx.get(geeTestv4.puzzle_image_url).content

        # Getting the Offset with Template Matching of the Contours
        offset = solve_slider_captcha(captcha_bytes, template_bytes)
        # Getting The Slider Bounding Box
        slider = page.locator('[class *= "geetest_arrow"]')
        box = await slider.bounding_box()
        # Getting The Middle of the Slider
        middle_x, middle_y = box["x"] + box["width"] // 2, box["y"] + box["height"] // 2
        # Sliding the Slider by the Offset
        await page.mouse.move(middle_x, middle_y)
        await page.mouse.down()
        await page.mouse.move(middle_x + offset, middle_y)
        await page.mouse.up()

    async def solve_icon_captcha(page, mode="canny"):
        # Screenshotting the Captcha Area
        captcha_frame = page.locator('[class*= "geetest_bg"]')
        captcha = await captcha_frame.screenshot(type="jpeg")
        # Screenshotting the Prompt
        template = page.locator('[class *= "geetest_ques_tips"]')
        template = await template.screenshot(type="jpeg")
        # Getting the Boundary Box
        box = await captcha_frame.bounding_box()
        # Solving the Captcha
        res = solve_icon_captcha(captcha, template, mode=mode)
        # Click on the Correct Images
        for coord in res:
            x, y = coord
            x, y = x + box["x"], y + box["y"]
            await page.mouse.click(x, y)
        # Submitting the Captcha
        submit = page.locator('[class *= "geetest_submit"]').first
        await submit.click()

    async def solve_gobang(page):
        grid = []
        for y in range(5):
            grid_element = []
            for x in range(5):
                element = page.locator(f'[class *= "geetest_item-{y}-{x} geetest_itemimg"]')
                style = await element.get_attribute("style")
                if len(style.split('url("')) == 1:
                    grid_element.append(None)
                else:
                    url = style.split('url("')[1].split('"')[0]
                    grid_element.append(url)
            grid.append(grid_element)

        start, finish = solve_grid_captcha(grid)
        to_start = page.locator(f'[class *= "geetest_item-{start[0]}-{start[1]} geetest_itemimg"]')
        await to_start.click()
        to_finish = page.locator(f'[class *= "geetest_item-{finish[0]}-{finish[1]} geetest_itemimg"]')
        await to_finish.click()

    async def solve_icon_crush(page):
        grid = []
        for y in range(3):
            grid_element = []
            for x in range(3):
                parent = page.locator(f'[class *= "geetest_item-{y}-{x} geetest_backimg"]')
                child = parent.locator('[class *= "geetest_img"]')
                style = await child.get_attribute("style")
                if len(style.split('url("')) == 1:
                    grid_element.append(None)
                else:
                    url = style.split('url("')[1].split('"')[0]
                    grid_element.append(url)
            grid.append(grid_element)

        start, finish = solve_icon_crush(grid)
        to_start = page.locator(f'[class *= "geetest_item-{start[0]}-{start[1]} geetest_backimg"]')
        await to_start.click()
        to_finish = page.locator(f'[class *= "geetest_item-{finish[0]}-{finish[1]} geetest_backimg"]')
        await to_finish.click()

    async def solve_geetest(page, retry=False, mode="canny"):
        # Logging the Puzzle Piece for SliderCaptcha
        await geeTestv4.log_images(page)
        await page.wait_for_timeout(2000)

        if await page.is_enabled("geetest_lock_success", timeout=3000):
            return True

        # If Retry has to be clicked
        if retry:
            # Clicking the Retry Button
            reset_button = page.locator('[class *= "geetest_refresh"]').first
            await reset_button.click()

        # Checking if the Captcha is already solved => NoCaptcha
        await page.wait_for_timeout(4000)
        if geeTestv4.result:
            return geeTestv4.result

        # Checking Captcha Type
        if await page.is_visible('[class *= "geetest_arrow"]'):
            # SliderCaptcha
            # Wait for the Captcha to load
            await page.wait_for_timeout(2000)
            # Checking if a background is logged
            if not geeTestv4.bg_image_url:
                # Clicking the Retry Button
                reset_button = page.locator('[class *= "geetest_refresh"]').first
                await reset_button.click()
            # Solve SliderCaptcha
            await geeTestv4.solve_slider_captcha(page)
            await page.wait_for_timeout(2000)
            # Returning Result or doing the Captcha Again
            if geeTestv4.result:
                return geeTestv4.result
            else:
                return await geeTestv4.solve_geetest(page, mode=mode)

        elif await page.is_visible('[class *= "geetest_ques_tips"]'):
            # IconCaptcha
            # Wait for the Captcha to load
            await page.wait_for_timeout(2000)
            # Solve IconCaptcha
            await geeTestv4.solve_icon_captcha(page, mode=mode)

            # Waiting 2 Seconds to get the result
            await page.wait_for_timeout(2000)
            # Returning Result or doing the Captcha Again
            if geeTestv4.result:
                return geeTestv4.result
            else:
                return await geeTestv4.solve_geetest(page, mode=mode)

        elif await page.is_visible('[class *= "geetest_winlinze"]'):
            # GoBang Captcha
            # Wait for the Captcha to load
            await page.wait_for_timeout(2000)
            # Solve IconCaptcha
            await geeTestv4.solve_gobang(page)

            # Waiting 2 Seconds to get the result
            await page.wait_for_timeout(2000)
            # Returning Result or doing the Captcha Again
            if geeTestv4.result:
                return geeTestv4.result
            else:
                return await geeTestv4.solve_geetest(page, mode=mode)

        elif await page.is_visible('[class *= "geetest_subitem geetest_match"]'):
            # IconCrush Captcha
            # Wait for the Captcha to load
            await page.wait_for_timeout(2000)
            # Solve IconCaptcha
            await geeTestv4.solve_icon_crush(page)

            # Waiting 2 Seconds to get the result
            await page.wait_for_timeout(2000)
            # Returning Result or doing the Captcha Again
            if geeTestv4.result:
                return geeTestv4.result
            else:
                return await geeTestv4.solve_geetest(page, mode=mode)

        elif await page.is_visible('[class *= "geetest_refresh"]'):
            # Retry Button
            return await geeTestv4.solve_geetest(page, retry=True, mode=mode)


async def solve_geetest(page, mode="canny"):
    if await page.is_visible('[class="geetest_btn"]'):
        # geeTestv3
        # Clicking the Captcha
        geetest_button = page.locator('[class="geetest_btn"]').last
        await geetest_button.scroll_into_view_if_needed()
        await geetest_button.click()

        return await geeTestv3.solve_geetest(page, mode=mode)
    else:
        # geeTestv4
        # Logging the Result
        await geeTestv4.log_result(page)
        # Clicking the Captcha
        geetest_button = page.locator('[class *= "geetest_btn_click"]').last
        await geetest_button.scroll_into_view_if_needed()
        await geetest_button.click()

        return await geeTestv4.solve_geetest(page)
