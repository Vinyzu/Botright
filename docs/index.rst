Welcome to Botright!
====================

For full documentation of changes (compared to Playwright) visit
`Botright Documentation <botright.rst>`__. Except of these changes, you
can use Botright after the
`Playwright Docs <https://playwright.dev/python/docs/api/class-playwright>`__

Installation
------------

Pip
~~~

|PyPI version|

.. code:: bash

   pip install --upgrade pip
   pip install botright
   playwright install
   python -c 'import hcaptcha_challenger; solver.install(clip=True)'

Usage
-----

Once installed, you can ``import`` Botright in a Python script, and
launch a firefox browser.

.. code:: py

   import asyncio
   import botright


   async def main():
       botright_client = await botright.Botright()
       browser = await botright_client.new_browser()
       page = await browser.new_page()

       await page.goto("http://playwright.dev")
       print(await page.title())

       await botright_client.close()

   if __name__ == "__main__":
       asyncio.run(main())

Captchas
--------

Botright is able to solve a wide variety of Captchas. For Documentation
of these functions visit `BotrightDocumentation <botright.md>`__.

Here all Captchas supported as of now

+----------------------+-----------+---------------------------------+---------------------------+
| Captcha Type         | Supported | Solved By                       | Success Rate              |
+======================+===========+=================================+===========================+
| **hCaptcha**         | Yes       | hcaptcha-challenger             | Up to 90%                 |
+----------------------+-----------+---------------------------------+---------------------------+
|                      |           |                                 |                           |
+----------------------+-----------+---------------------------------+---------------------------+
| **reCaptcha**        | Yes       | reCognizer                      | 50%-80%                   |
+----------------------+-----------+---------------------------------+---------------------------+
|                      |           |                                 |                           |
+----------------------+-----------+---------------------------------+---------------------------+
| **geeTestv3**        | Temp. Not |                                 |                           |
+----------------------+-----------+---------------------------------+---------------------------+
| v3 Intelligent Mode  | Yes       | botright´s stealthiness          | 100%                      |
+----------------------+-----------+---------------------------------+---------------------------+
| v3 Slider Captcha    | Yes       | cv2.matchTemplate               | 100%                      |
+----------------------+-----------+---------------------------------+---------------------------+
| v3 Nine Captcha      | Yes       | CLIP Detection                  | 50%                       |
+----------------------+-----------+---------------------------------+---------------------------+
| v3 Icon Captcha      | Yes       | cv2.matchTemplate / SSIM / CLIP | 70%                       |
+----------------------+-----------+---------------------------------+---------------------------+
| v3 Space Captcha     | No        | Not solvable                    | 0%                        |
+----------------------+-----------+---------------------------------+---------------------------+
|                      |           |                                 |                           |
+----------------------+-----------+---------------------------------+---------------------------+
| **geeTestv4**        | Temp. Not |                                 |                           |
+----------------------+-----------+---------------------------------+---------------------------+
| v4 Intelligent Mode  | Yes       | botright´s stealthiness          | 100%                      |
+----------------------+-----------+---------------------------------+---------------------------+
| v4 Slider Captcha    | Yes       | cv2.matchTemplate               | 100%                      |
+----------------------+-----------+---------------------------------+---------------------------+
| v4 GoBang Captcha    | Yes       | Math Calculations               | 100%                      |
+----------------------+-----------+---------------------------------+---------------------------+
| v4 Icon Captcha      | Yes       | cv2.matchTemplate / SSIM / CLIP | 60%                       |
+----------------------+-----------+---------------------------------+---------------------------+
| v4 IconCrush Captcha | Yes       | Math Calculations               | 100%                      |
+----------------------+-----------+---------------------------------+---------------------------+

Proxies
--------

Botright currently only supports HTTP(S) proxies.
You can use almost every common format, but if you want to go safe, use ``ip:port`` or ``username:password@ip:port`` for auth proxies.

First script
------------

In our first script, we will navigate to `Creep.js <https://abrahamjuliot.github.io/creepjs/>`__ and
take a screenshot in Chromium.

.. code:: py

   import asyncio
   import botright


   async def main():
       botright_client = await botright.Botright()
       browser = await botright_client.new_browser()
       page = await browser.new_page()

       await page.goto("https://abrahamjuliot.github.io/creepjs/")
       await page.wait_for_timeout(5000) # Wait for stats to load
       await page.screenshot(path="example.png", full_page=True)

       await botright_client.close()

   if __name__ == "__main__":
       asyncio.run(main())

Interactive mode (REPL)
-----------------------

You can launch the interactive python REPL:

.. code:: bash

   python -m asyncio

and then launch Botright within it for quick experimentation:

.. code:: py

   >>> import botright
      >>> botright_client = await botright.Botright()
      # Pass headless=False to botright.Botright() to see the browser UI
      >>> browser = await botright_client.new_browser()
      >>> page = await browser.new_page()
      >>> await page.goto("https://abrahamjuliot.github.io/creepjs/")
      >>> await page.wait_for_timeout(5000) # Wait for stats to load
      >>> await page.screenshot(path="example.png", full_page=True)
      >>> await botright_client.close()
   >>> botright_client = await botright.Botright()
   # Pass headless=False to botright.Botright() to see the browser UI
   >>> browser = await botright_client.new_browser()
   >>> page = await browser.new_page()
   >>> await page.goto("https://abrahamjuliot.github.io/creepjs/")
   >>> await page.wait_for_timeout(5000) # Wait for stats to load
   >>> await page.screenshot(path="example.png", full_page=True)
   >>> await botright_client.close()

Pyinstaller
-----------

You can use Botright with `Pyinstaller <https://www.pyinstaller.org/>`__
to create standalone executables.

.. code:: py

   # main.py
   import asyncio
   import botright


   async def main():
       botright_client = await botright.Botright()
       browser = await botright_client.new_browser()
       page = await browser.new_page()

       page.goto("http://whatsmyuseragent.org/")
       page.screenshot(path="example.png")

       await botright_client.close()

   if __name__ == "__main__":
       asyncio.run(main())

If you want to bundle browsers with the executables:

.. code:: bash

   PLAYWRIGHT_BROWSERS_PATH=0 playwright install firefox
   pyinstaller -F main.py

.. code:: batch

   set PLAYWRIGHT_BROWSERS_PATH=0
   playwright install firefox
   pyinstaller -F main.py

.. code:: powershell

   $env:PLAYWRIGHT_BROWSERS_PATH="0"
   playwright install firefox
   pyinstaller -F main.py

Known issues
------------

Threading
~~~~~~~~~

Botright´s API is not thread-safe. If you are using Botright in a
multi-threaded environment, you should create a botright instance per
thread. See `threading
issue <https://github.com/microsoft/playwright-python/issues/623>`__ for
more details.
For asynchronous usage, you should probably use asyncio.gather(*threads) instead.

.. |PyPI version| image:: https://badge.fury.io/py/botright.svg
   :target: https://pypi.python.org/pypi/botright/
