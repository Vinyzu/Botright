import asyncio

import botright


async def main():
    botright_client = await botright.Botright(headless=False, scroll_into_view=False)
    browser = await botright_client.new_browser()
    page = await browser.new_page()

    await page.goto("https://www.geetest.com/en/adaptive-captcha-demo")

    checkbox = page.locator('[class="tab-item tab-item-4"]')
    await checkbox.click()

    await page.wait_for_timeout(2000)

    result = await page.solve_geetest()
    print(result)

    await page.wait_for_timeout(2000)
    await botright_client.close()


if __name__ == "__main__":
    asyncio.run(main())
