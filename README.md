# Botright v0.5.1
![Tests & Linting](https://github.com/Vinyzu/botright/actions/workflows/ci.yml/badge.svg)
[![](https://img.shields.io/pypi/v/botright.svg?color=1182C3)](https://pypi.org/project/botright/)
[![Downloads](https://static.pepy.tech/badge/botright)](https://pepy.tech/project/botright)

---

<details open>
    <summary><h3>Sponsors</h1></summary>

 <a href="https://www.scrapeless.com/en/product/scraping-browser?utm_medium=github&utm_campaign=vinyzu-botright"><img src="https://github.com/user-attachments/assets/7ca41a89-95db-4213-9b91-bf4720e778c2" alt="Scrapeless Banner" width="80%"/></a>

If you are looking for a tool focused on **browser automation and anti-detection mechanisms**, I can recommend [**Scrapeless Scraping Browser**](https://www.scrapeless.com/en/product/scraping-browser?utm_medium=github&utm_campaign=vinyzu-botright). It is a cloud-based, Chromium-powered headless browser cluster that enables developers to run **large-scale concurrent browser instances** and handle complex interactions on protected pages. Perfectly suited for **AI infrastructure, web automation, data scraping, page rendering, and automated testing**.

The [**Scrapeless Browser**](https://www.scrapeless.com/en/product/scraping-browser?utm_medium=github&utm_campaign=vinyzu-botright) provides a secure, isolated browser environment that allows you to interact with web applications while minimizing potential risks to your system.  
Key Features

* **Out-of-the-Box Ready**: Natively compatible with [Puppeteer](https://docs.scrapeless.com/en/scraping-browser/libraries/puppeteer/) and [Playwright](https://docs.scrapeless.com/en/scraping-browser/libraries/playwright/), supporting CDP connections. Migrate your projects with just one line of code.  
* **Global IP Resources**: Covers residential IPs, static ISP IPs, and unlimited IPs across 195 countries. Transparent costs **($0.6–$1.8/GB)** with support for custom browser proxies.  
* **Isolated Environment Creation**: Each profile uses an exclusive browser environment, enabling persistent login and identity isolation.  
* **Unlimited Concurrent Scaling**: A single task supports second-level launch of 50 to 1000+ browser instances. Auto-scaling is available with no server resource limits.  
* **Edge Node Service (ENS)** – Multiple nodes worldwide, offering 2–3× faster launch speed and higher stability than other browsers.  
* **Flexible Fingerprint Customization**: Generate random fingerprints or customize fingerprint parameters as needed.  
* **Visual Debugging:** Perform interactive debugging and real-time monitoring of proxy traffic through **Live View**, and quickly pinpoint issues and optimize actions by replaying sessions page by page with **Session Recordings**.  
* **Enterprise Customization**: Undertake customization of enterprise-level automation projects and AI Agent customization.


👉 Learn more: [Scrapeless Scraping Browser Playground](https://app.scrapeless.com/passport/login?utm_medium=github&utm_campaign=vinyzu-botright) | [Scrapeless Scraping Browser Docs](https://docs.scrapeless.com/en/scraping-browser/quickstart/introduction/?utm_medium=github&utm_campaign=vinyzu-botright)


---

[![Evomi Banner](https://my.evomi.com/images/brand/cta.png)](https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=Vinyzu-Botright)

[**Evomi**](https://evomi.com?utm_source=github&utm_medium=banner&utm_campaign=Vinyzu-Botright) is your Swiss Quality, affordable Proxy Provider. I can personally recommend them for their High Quality Residential Proxies.

- 🌍 **Global Presence**: Available in 150+ Countries
- ⚡ **Guaranteed Low Latency**
- 🔒 **Swiss Quality and Privacy**
- 🎁 **Free Trial**: No Credit Card Required
- 🛡️ **99.9% Uptime**
- 🤝 **Special IP Pool selection**: Optimize for fast, quality or quantity of ips
- 🔧 **Easy Integration**: Compatible with most software and programming languages
</details>

---

## Install it from PyPI

```bash
pip install botright
playwright install
```

---

## Usage

### Botright is currently only available in async mode.
### It is fully plugable with your existing playwright code. You only have to change your browser initialization!

```py
import asyncio

import botright


async def main():
    botright_client = await botright.Botright()
    browser = await botright_client.new_browser()
    page = await browser.new_page()

    # Continue by using the Page
    await page.goto("https://google.com")

    await botright_client.close()


if __name__ == "__main__":
    asyncio.run(main())
```

Read the [Documentation](https://github.com/Vinyzu/Botright/blob/main/docs/index.rst)

---

## Browser Stealth

Botright uses a vast amount of techniques to hide its functionality as a bot from websites.
To enhance stealth, since Version 0.3, it uses a real Chromium-based browser from the local machine to start up a botted browser.
For best stealth, you want to install [Ungoogled Chromium](https://ungoogled-software.github.io/ungoogled-chromium-binaries/).

Furthermore, it uses self-scraped [chrome-fingerprints](https://github.com/Vinyzu/chrome-fingerprints) to build up a fake browser fingerprint and to deceive website into thinking it is legit.


| Test                                                                                                | Status | Score                                                      |
|-----------------------------------------------------------------------------------------------------|--------|------------------------------------------------------------|
| **reCaptcha Score**                                                                                 | ✔️     | 0.9                                                        |
| => [nopecha.com](https://nopecha.com/demo/recaptcha#v3)                                             | ✔️     | 0.9                                                        |
| => [recaptcha-demo.appspot.com](https://recaptcha-demo.appspot.com/recaptcha-v3-request-scores.php) | ✔️     | 0.9                                                        |
| => [berstend.github.io](https://berstend.github.io/static/recaptcha/v3-programmatic.html)           | ✔️     | 0.9                                                        |
| => [antcpt.com](https://antcpt.com/score_detector/)                                                 | ❌❓  | 0.1 (Detects Legitimate Browsers as Bad)                   |
| [**CreepJS**](https://abrahamjuliot.github.io/creepjs/)                                             | ✔️     | ~65.5% (With Canvas Manipulation 52%)                      |
| **DataDome**                                                                                        | ✔️     |                                                            |
| => [antoinevastel.com](https://antoinevastel.com/bots/datadome)                                     | ✔️     |                                                            |
| => [datadome.co](https://datadome.co/bot-tester/)                                                   | ✔️     |                                                            |
| **Imperva**                                                                                         | ✔️❓  | (Cant find approved Testing Sites)                         |
| => [ticketmaster.es](https://www.ticketmaster.es/)                                                  | ✔️     |                                                            |
| **Cloudflare**                                                                                      | ✔️     |                                                            |
| => [Turnstile](https://nopecha.com/demo/turnstile)                                                  | ✔️     | (Using Undetected-Playwright-Python)                       |
| => [Interstitial](https://nopecha.com/demo/cloudflare)                                              | ✔️     | (Using Undetected-Playwright-Python)                       |
| [**SannySoft**](https://bot.sannysoft.com/)                                                         | ✔️     |                                                            |
| [**Incolumitas**](https://bot.incolumitas.com/)                                                     | ✔️     | 0.8-1.0                                                    |
| [**Fingerprint.com**](https://fingerprint.com/products/bot-detection/)                              | ✔️     |                                                            |
| [**IpHey**](https://iphey.com/)                                                                     | ✔️     |                                                            |
| [**BrowserScan**](https://browserscan.net/)                                                         | ✔️     |                                                            |
| [**PixelScan**](https://pixelscan.net/)                                                             | ❓     | (Platform Test Outdated & Maybe caused by WebGL-disabling) |
| [**Bet365**](https://www.bet365.com/#/AC/B1/C1/D1002/E79147586/G40/)                                | ✔️     | Currently only using `mask_fingerprint=False`              |


---

## Captcha Solving

Botright is able to solve a wide viarity of Captchas.
For Documentation of these functions visit [BotrightDocumentation](https://github.com/Vinyzu/Botright/blob/main/docs/botright.rst).

It uses Computer Vision/Artificial Intelligence and other Methods to solve these Captchas.

You dont need to pay for any Captcha Solving APIs and you can solve Captchas with just one simple function call.

Here all Captchas supported as of now:

|             Captcha Type             | Supported |            Solved By            | Success Rate |
|:------------------------------------:|:---------:|:-------------------------------:|--------------|
|              `hCaptcha`              |    ✔️ ❓    | hcaptcha-challenger (outdated)  | up to 90%    |
|             `reCaptcha`              |    ✔️     |           reCognizer            | 50%-80%      |
| `geeTestv3` Currently Not Available! |
|         v3 Intelligent Mode          |    ✔️     |     botrights stealthiness      | 100%         |
|          v3 Slider Captcha           |    ✔️     |        cv2.matchTemplate        | 100%         |
|           v3 Nine Captcha            |    ✔️     |         CLIP Detection          | 50%          |
|           v3 Icon Captcha            |    ✔️     | cv2.matchTemplate / SSIM / CLIP | 70%          |
|           v3 Space Captcha           |     ❌     |          Not solvable           | 0%           |
| `geeTestv4` Currently Not Available! |
|         v4 Intelligent Mode          |    ✔️     |     botrights stealthiness      | 100%         |
|          v4 Slider Captcha           |    ✔️     |        cv2.matchTemplate        | 100%         |
|          v4 GoBang Captcha           |    ✔️     |        Math Calculations        | 100%         |
|           v4 Icon Captcha            |    ✔️     | cv2.matchTemplate / SSIM / CLIP | 60%          |
|         v4 IconCrush Captcha         |    ✔️     |        Math Calculations        | 100%         |

## Development

Read the [CONTRIBUTING.md](https://github.com/Vinyzu/Botright/blob/main/docs/CONTRIBUTING.md) file.

---

## Copyright and License
© [Vinyzu](https://github.com/Vinyzu/)

[GNU GPL](https://choosealicense.com/licenses/gpl-3.0/)

(Commercial Usage is allowed, but source, license and copyright has to made available. Botright does not provide and Liability or Warranty)

---

## Thanks to

[Kaliiiiiiiiii](https://github.com/kaliiiiiiiiii/) (For shared knowledge of Anti-Browser-Detection Measures)

[Kaliiiiiiiiii](https://github.com/kaliiiiiiiiii/) (For Main-Authoring [Undetected-Playwright](https://github.com/kaliiiiiiiiii/undetected-playwright-python) (Co-Authored by me) )

[QIN2DIM](https://github.com/QIN2DIM/) (For his great AI work)

[MaxAndolini](https://github.com/MaxAndolini) (For shared knowledge of hCaptcha bypassing)

[CreativeProxies](https://creativeproxies.com) (For sponsoring me with Proxies)

---

![Version](https://img.shields.io/badge/Botright-v0.5.1-blue)
![License](https://img.shields.io/badge/License-GNU%20GPL-green)
![Python](https://img.shields.io/badge/Python-v3.x-lightgrey)

[![my-discord](https://img.shields.io/badge/My_Discord-000?style=for-the-badge&logo=google-chat&logoColor=blue)](https://discordapp.com/users/935224495126487150)
[![buy-me-a-coffee](https://img.shields.io/badge/Buy_Me_A_Coffee-000?style=for-the-badge&logo=ko-fi&logoColor=brown)](https://ko-fi.com/vinyzu)
