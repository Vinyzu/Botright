import asyncio

import botright


async def main():
    botright_client = await botright.Botright(headless=False)
    browser = await botright_client.new_browser()
    page = await browser.new_page()

    await page.goto("https://accounts.hcaptcha.com/demo?sitekey=00000000-0000-0000-0000-000000000000")

    result = await page.solve_hcaptcha()
    print(result)

    await botright_client.close()



if __name__ == "__main__":
    asyncio.run(main())