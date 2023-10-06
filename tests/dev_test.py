import asyncio

import botright


async def main():
    botright_client = await botright.Botright()
    browser = await botright_client.new_browser()

    single_url = ["https://abrahamjuliot.github.io/creepjs/"]
    all_urls = ["https://abrahamjuliot.github.io/creepjs/", "https://arh.antoinevastel.com/bots/", "https://antoinevastel.com/bots/datadome", "https://datadome.co/bot-tester/", "https://bot.sannysoft.com/", "https://bot.incolumitas.com/", "https://www.whatismybrowser.com/detect/client-hints/", "https://nopecha.com/demo/recaptcha#v3", "https://iphey.com/", "https://www.browserscan.net/", "https://pixelscan.net", "https://fingerprint.com/products/bot-detection/", "https://nowsecure.nl"]
    for url in all_urls:
        page = await browser.new_page()
        await page.goto(url)

    await page.wait_for_timeout(1000000)

    await botright_client.close()

if __name__ == "__main__":
    asyncio.run(main())
