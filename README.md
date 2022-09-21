# Botright v1.0

## Install it from PyPI

```bash
pip install botright
playwright install
```

---

## Usage

### Botright is only available in async mode.
### It is fully plugable with your existing playwright code. You only have to change your browser initialization!

```py
import asyncio

import botright


async def main():
    botright_client = await botright.Botright(headless=False)
    browser = await botright_client.new_browser()
    page = await browser.new_page()

    # Continue by using the Page

    await botright_client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Documentation
Read the [Documentation](docs/index.md)

---

## Artificial Intelligence

The AI of this bot is not mine and i dont take any credits for it.

It was created by QIN2DIM and can be found [here](https://github.com/QIN2DIM/hcaptcha-challenger).

However, i edited out some code/files, to make Botright lightweighter and to use less imports.

Also, i coded a MouseMovement Generator, to get more realistic MotionData. It uses Interpolation between CaptchaImage-Coordinates to do so.

## Development

Read the [CONTRIBUTING.md](https://github.com/Vinyzu/Botright/blob/main/CONTRIBUTING.md) file.

---

## Copyright and License
© [Vinyzu](https://github.com/Vinyzu/)

[GNU GPL](https://choosealicense.com/licenses/gpl-3.0/)

(Commercial Usage is allowed, but source, license and copyright has to made available. Botright does not provide and Liability or Warranty)

---

## Thanks to

[QIN2DIM](https://github.com/QIN2DIM/) (For his great AI work.)

[MaxAndolini](https://github.com/MaxAndolini) (For shared knowledge of hCaptcha bypassing.)

---

![Version](https://img.shields.io/badge/Botright-v1.0.0-blue)
![License](https://img.shields.io/badge/License-GNU%20GPL-green)
![Python](https://img.shields.io/badge/Python-v3.x-lightgrey)

[![my-discord](https://img.shields.io/badge/My_Discord-000?style=for-the-badge&logo=google-chat&logoColor=blue)](https://discordapp.com/users/935224495126487150)
[![buy-me-a-coffee](https://img.shields.io/badge/Buy_Me_A_Coffee-000?style=for-the-badge&logo=ko-fi&logoColor=brown)](https://ko-fi.com/vinyzu)