import asyncio

import botright


async def main():
    botright_client = await botright.Botright(headless=False)
    browser = await botright_client.new_browser()

    single_url = ["https://abrahamjuliot.github.io/creepjs/", "https://nowsecure.nl/#relax"]
    # webrtc_urls = ["https://browserleaks.com/webrtc", "https://www.expressvpn.com/en/webrtc-leak-test", "https://www.vpnmentor.com/tools/ip-leak-test-vpns-tor/",
    #                "https://surfshark.com/en/webrtc-leak-test", "https://hide.me/en/webrtc-leak-test", "https://www.hidemyass.com/en-en/webrtc-leak-test", "https://abrahamjuliot.github.io/creepjs/"]
    # all_urls = ["https://abrahamjuliot.github.io/creepjs/", "https://hmaker.github.io/selenium-detector/", "https://arh.antoinevastel.com/bots/", "https://antoinevastel.com/bots/datadome",
    #             "https://datadome.co/bot-tester/", "https://mihneamanolache.github.io/simple-sw-test/", "https://bot.sannysoft.com/", "https://bot.incolumitas.com/",
    #             "https://www.whatismybrowser.com/detect/client-hints/", "https://nopecha.com/demo/recaptcha#v3", "https://iphey.com/", "https://www.browserscan.net/", "https://pixelscan.net",
    #             "https://fingerprint.com/products/bot-detection/", "https://nowsecure.nl/#relax"]
    #
    for url in single_url:
        page = await browser.new_page()
        await page.goto(url)

    # await page.goto("https://www.aircanada.com/aeroplan/redeem/availability/outbound?org0=JFK&dest0=LHR&departureDate0=2024-01-01&lang=en-CA")

    await page.wait_for_timeout(900000)

    await botright_client.close()


if __name__ == "__main__":
    asyncio.run(main())
