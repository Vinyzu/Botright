Initialization
--------------

Botright
~~~~~~~~

-  ``await botright.Botright()``
-  Initialize a Botright Session

+-----------------------------------+--------------------------------------+
| Kwargs                            | Usage                                |
+===================================+======================================+
| ``headless`` (bool)               | Whether to run browser in            |
|                                   | headless mode. Defaults to           |
|                                   | ``False``                            |
+-----------------------------------+--------------------------------------+
| ``block_images`` (bool)           | Wether to block images to lower      |
|                                   | Network Usage. Defaults to ``False`` |
+-----------------------------------+--------------------------------------+
| ``cache_responses`` (bool)        | Whether to Cache certain responses.  |
|                                   | to lower Network Usage.              |
|                                   | Defaults to ``False``                |
+-----------------------------------+--------------------------------------+
| ``disable_canvas`` (bool)         | Whether to disable Canvas reading    |
|                                   | by Websites. Defaults to ``True``    |
+-----------------------------------+--------------------------------------+
| ``scroll_into_view`` (bool)       | Whether to scroll every Element      |
|                                   | into View. Defaults to ``True``      |
+-----------------------------------+--------------------------------------+
| ``user_action_layer`` (bool)      | Shows what the Bot is doing in the   |
|                                   | Browser GUI. Defaults to ``True``    |
| ``dont_mask_fingerprint`` (bool)  | Disables spoofing a fake fingerprint |
|                                   | boosts stealth. Defaults to ``True`` |
+-----------------------------------+--------------------------------------+

-  returns: ``BotrightObject``

--------------

NewBrowser
~~~~~~~~~~

-  ``await botright_client.new_browser()``
-  Spawns a new Browser

+-------------------------------------+--------------------------------+
| Kwargs                              | Usage                          |
+=====================================+================================+
| ``proxy`` (str)                     | Used to pass a                 |
|                                     | ProxyServer-Address. Example:  |
|                                     | ``username:password@ip:port``. |
|                                     | Defaults to ``None``           |
+-------------------------------------+--------------------------------+
| ``stealth_page`` (bool)             | Whether to use certain         |
|                                     | puppeteer-stealth modules to   |
|                                     | enhance the stealthiness of    |
|                                     | botright browsers.             |
|                                     | Defaults to ``True``           |
+-------------------------------------+--------------------------------+
| ``**PlaywrightContextArgs``         | See                            |
|                                     | `ContextDocs <https://playwrig |
|                                     | ht.dev/python/docs/api/class-b |
|                                     | rowser#browser-new-context>`__ |
|                                     | for further possible           |
|                                     | Arguments. Defaults to         |
|                                     | ``None``                       |
+-------------------------------------+--------------------------------+

-  returns: ``PlaywrightContext``

--------------

Get hCaptcha Key with Sitekey & rqData
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  ``await page.get_hcaptcha()``
-  Spawns a new Page and Solves Captcha

+-------------------------------------+--------------------------------+
| Kwargs                              | Usage                          |
+=====================================+================================+
| ``sitekey`` (str)                   | Specify the Sitekey to solve   |
|                                     | the Captcha with. Defaults to  |
|                                     | ``00000000                     |
|                                     | -0000-0000-0000-000000000000`` |
+-------------------------------------+--------------------------------+
| ``rqdata`` (str)                    | Specify rqData to mock the     |
|                                     | Captcha with. Defaults to      |
|                                     | ``None``                       |
+-------------------------------------+--------------------------------+

-  returns: ``hCaptchaKey``

--------------

Solve hCaptcha
~~~~~~~~~~~~~~

-  ``await page.solve_hcaptcha()``
-  Solves a hCaptcha on the given Page

======== =================================================
Args     Usage
======== =================================================
``page`` Specify the Page to solve a hCaptcha Challenge on
======== =================================================

+------------------+--------------------------------------------------+
| Kwargs           | Usage                                            |
+==================+==================================================+
| ``rqdata`` (str) | Specify rqData to mock the Captcha with.         |
|                  | Defaults to ``None``                             |
+------------------+--------------------------------------------------+

-  returns: ``hCaptchaKey``

--------------

Solve reCaptcha
~~~~~~~~~~~~~~~

-  ``await page.solve_recaptcha()``
-  Solves a reCaptcha on the given Page

======== ==================================================
Args     Usage
======== ==================================================
``page`` Specify the Page to solve a reCaptcha Challenge on
======== ==================================================

-  returns: ``reCaptchaKey``

--------------

Solve geeTest
~~~~~~~~~~~~~

-  ``await page.solve_geetest()``
-  Solves a geeTest (v3 or v4) on the given Page

======== =================================================
Args     Usage
======== =================================================
``page`` Specify the Page to solve a hCaptcha Challenge on
======== =================================================

+-------------------------------------+--------------------------------+
| Kwargs                              | Usage                          |
+=====================================+================================+
| ``mode`` (str)                      | Specify Mode to solve          |
|                                     | IconCaptchas with. Defaults to |
|                                     | ``"canny"``. Supported Modes:  |
|                                     | “canny”, “clip”, “ssim”,       |
|                                     | “random”                       |
+-------------------------------------+--------------------------------+

-  returns: ``geeTestKey``
