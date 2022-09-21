Initialization
--------------

Botright
~~~~~~~~

-  ``await botright.Botright()``
-  Initialize a Botright Session

+-----------------------------------+-----------------------------------+
| Kwargs                            | Usage                             |
+===================================+===================================+
| ``headless`` (bool)               | Whether to run browser in         |
|                                   | headless mode. Defaults to        |
|                                   | ``False``                         |
+-----------------------------------+-----------------------------------+

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
| ``locale`` (str)                    | Specify user locale, for       |
|                                     | example en-GB, de-DE, etc.     |
|                                     | Locale will affect             |
|                                     | navigator.language value,      |
|                                     | Accept-Language request header |
|                                     | value as well as number and    |
|                                     | date formatting rules. Affects |
|                                     | Captcha Language. Defaults to  |
|                                     | ``en-US``                      |
+-------------------------------------+--------------------------------+
| ``useragent`` (str)                 | Specific user agent. Defaults  |
|                                     | to ``FakerUseragent``          |
+-------------------------------------+--------------------------------+
| ``geolocation`` (dict)              | Specify the Browsers           |
|                                     | Geolocation. See               |
|                                     | `GeolocationDocs <https:       |
|                                     | //playwright.dev/python/docs/a |
|                                     | pi/class-browser#browser-new-c |
|                                     | ontext-option-geolocation>`__. |
|                                     | Defaults to                    |
|                                     | ``ProxyGeoLocation``           |
+-------------------------------------+--------------------------------+
| ``timezone_id`` (str)               | Specify the Browsers Timezone. |
|                                     | Defaults to                    |
|                                     | ``ProxyTimezoneID``            |
+-------------------------------------+--------------------------------+
| ``screen`` (dict)                   | Specify the Browsers Screen    |
|                                     | Resolution. See                |
|                                     | `ScreenDocs <h                 |
|                                     | ttps://playwright.dev/python/d |
|                                     | ocs/api/class-browser#browser- |
|                                     | new-context-option-screen>`__. |
|                                     | Defaults to                    |
|                                     | ``FakerScreenResolution``      |
+-------------------------------------+--------------------------------+
| ``viewport`` (dict)                 | Specify the Browsers Viewport  |
|                                     | Resolution. See                |
|                                     | `ViewportDocs <htt             |
|                                     | ps://playwright.dev/python/doc |
|                                     | s/api/class-browser#browser-ne |
|                                     | w-context-option-viewport>`__. |
|                                     | Defaults to                    |
|                                     | ``FakerViewportResolution``    |
+-------------------------------------+--------------------------------+
| ``proxy`` (dict)                    | Specify the Browser Proxy. See |
|                                     | `ProxyDocs <                   |
|                                     | https://playwright.dev/python/ |
|                                     | docs/api/class-browser#browser |
|                                     | -new-context-option-proxy>`__. |
|                                     | Defaults to                    |
|                                     | ``ProxyManagerBrowserProxy``   |
+-------------------------------------+--------------------------------+
| ``http_credentials`` (dict)         | Specify the Browser Proxy      |
|                                     | Credentials. See               |
|                                     | `HttpCredentialsDocs <https:// |
|                                     | playwright.dev/python/docs/api |
|                                     | /class-browser#browser-new-pag |
|                                     | e-option-http-credentials>`__. |
|                                     | Defaults to                    |
|                                     | ``ProxyManagerUse              |
|                                     | rname & ProxyManagerPassword`` |
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

Get hCaptcha Key with Sitekey & rqData
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  ``await browser.get_hcaptcha()``
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

Solve hCaptcha
~~~~~~~~~~~~~~

-  ``await page.solve_hcaptcha()``
-  Spawns a new Page

+------------------+--------------------------------------------------+
| Kwargs           | Usage                                            |
+==================+==================================================+
| ``rqdata`` (str) | Specify rqData to mock the Captcha with.         |
|                  | Defaults to ``None``                             |
+------------------+--------------------------------------------------+

-  returns: ``hCaptchaKey``
