Initialization
--------------

Botright_
~~~~~~~~

-  ``await botright.Botright()``
..

 Initialize a Botright Session

+--------------------------------------+--------------------------------------+
| Kwargs                               | Usage                                |
+======================================+======================================+
| ``headless`` (bool)                  | Whether to run browser in            |
|                                      | headless mode. Defaults to           |
|                                      | ``False``                            |
+--------------------------------------+--------------------------------------+
| ``block_images`` (bool)              | Wether to block images to lower      |
|                                      | Network Usage. Defaults to ``False`` |
+--------------------------------------+--------------------------------------+
| ``cache_responses`` (bool)           | Whether to Cache certain responses.  |
|                                      | to lower Network Usage.              |
|                                      | Defaults to ``False``                |
+--------------------------------------+--------------------------------------+
| ``user_action_layer`` (bool)         | Shows what the Bot is doing in the   |
|                                      | Browser GUI. Defaults to ``True``    |
+--------------------------------------+--------------------------------------+
| ``scroll_into_view`` (bool)          | Whether to scroll every Element      |
|                                      | into View. Defaults to ``True``      |
+--------------------------------------+--------------------------------------+
| ``spoof_canvas`` (bool)              | Whether to disable canvas fingerprint|
|                                      | protection. Defaults to ``True``     |
+--------------------------------------+--------------------------------------+
| ``mask_fingerprint`` (bool)          | Wether to mask browser fingerprints  |
|                                      | Disables spoofing a fake fingerprint |
|                                      | boosts stealth. Defaults to ``False``|
+--------------------------------------+--------------------------------------+
| ``spoof_canvas`` (bool)              | Whether to disable canvas fingerprint|
|                                      | protection. Defaults to ``True``     |
+--------------------------------------+--------------------------------------+
| ``use_undetected_playwright`` (bool) | hether to use undetected_playwright. |
|                                      | Only Temporary. Defaults to ``False``|
+--------------------------------------+--------------------------------------+

-  returns: ``Botright``

--------------

NewBrowser_
~~~~~~~~~~

-  ``await botright_client.new_browser()``
..

 Create a new Botright browser instance with specified configurations.

+-------------------------------------+--------------------------------+
| Kwargs                              | Usage                          |
+=====================================+================================+
| ``proxy`` (str)                     | Used to pass a                 |
|                                     | ProxyServer-Address. Example:  |
|                                     | ``username:password@ip:port``. |
|                                     | Defaults to ``None``           |
+-------------------------------------+--------------------------------+
| ``**PlaywrightContextArgs``         | See                            |
|                                     | `ContextDocs <https://playwrig |
|                                     | ht.dev/python/docs/api/class-b |
|                                     | rowser#browser-new-context>`__ |
|                                     | for further possible           |
|                                     | Arguments. Defaults to         |
|                                     | ``None``                       |
+-------------------------------------+--------------------------------+

-  returns: ``botright.extended_typing.Browser``

--------------

Captcha Solving
--------------

Get a hCaptcha Key with Sitekey & rqData_
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  ``await page.get_hcaptcha()``
..

 Spawns a new Page and Solves Captcha

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

-  returns: ``hCaptchaKey (str)``

--------------

Solve hCaptcha_
~~~~~~~~~~~~~~

-  ``await page.solve_hcaptcha()``
..

 Solves a hCaptcha on the given Page

+------------------+--------------------------------------------------+
| Kwargs           | Usage                                            |
+==================+==================================================+
| ``rqdata`` (str) | Specify rqData to mock the Captcha with.         |
|                  | Defaults to ``None``                             |
+------------------+--------------------------------------------------+

-  returns: ``hCaptchaKey (str)``

--------------

Solve reCaptcha_
~~~~~~~~~~~~~~~

-  ``await page.solve_recaptcha()``
..

 Solves a reCaptcha on the given Page

|

-  returns: ``reCaptchaKey``

--------------

Solve geeTest_
~~~~~~~~~~~~~

-  ``await page.solve_geetest()``
..

 Solves a geeTest (v3 or v4) on the given Page

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
