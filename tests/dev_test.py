import asyncio

import botright


async def main():
    botright_client = await botright.Botright(headless=False)
    browser = await botright_client.new_browser()
    page = await browser.new_page()

    # Continue by using the Page
    await page.goto("https://google.com")

    await botright_client.close()

if __name__ == "__main__":
    asyncio.run(main())