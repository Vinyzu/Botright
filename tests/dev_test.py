import asyncio
import botright


async def main():
    botright_client = await botright.Botright()
    browser = await botright_client.new_browser()
    page = await browser.new_page()

    tkn = await browser.get_hcaptcha()
    print("tkn: ", tkn)
    page.goto("http://whatsmyuseragent.org/")
    page.screenshot(path="example.png")

    await botright_client.close()

if __name__ == "__main__":
    asyncio.run(main())