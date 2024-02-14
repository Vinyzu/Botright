from __future__ import annotations

import asyncio

from async_class import AsyncObject, link
from chrome_fingerprints import ChromeFingerprint

from .proxy_manager import ProxyManager


class Faker(AsyncObject):
    locale: str = ""
    language_code: str = ""
    fingerprint: ChromeFingerprint

    async def __ainit__(self, botright, proxy):
        """
        Initialize a Faker instance with a botright instance and a proxy, and generate fake data.

        Args:
            botright: An instance of Botright for linking purposes.
            proxy: The proxy to be used for generating locale-related fake data.
        """
        self.botright = botright
        link(self, botright)

        threads = [self.get_computer(), self.get_locale(proxy)]
        await asyncio.gather(*threads)

    @staticmethod
    def adjust_browser_version(useragent: str, browser_type: str, browser_version: str) -> str:
        """
        Adjust the browser version in a user agent string.

        Args:
            useragent (str): The user agent string to be adjusted.
            browser_type (str): The type of the browser (e.g., "Firefox").
            browser_version (str): The desired browser version (e.g., "92.0").

        Returns:
            str: The adjusted user agent string.
        """
        ua_browser_version = [word for word in useragent.split() if browser_type.capitalize() + "/" in word]
        browser_version_list = browser_version.split(".")[:2] + ["0", "0"]
        browser_version = ".".join(browser_version_list)
        return useragent.replace(ua_browser_version[0], f"{browser_type}/{browser_version}")

    async def get_computer(self) -> None:
        """
        Generate fake computer-related data such as user agent, vendor, GPU information, screen dimensions, etc.
        """
        self.fingerprint = await self.botright.fingerprint_generator.get_fingerprint()

    async def get_locale(self, proxy: ProxyManager) -> None:
        """
        Generate fake locale-related data such as locale and language code based on the provided proxy.

        Args:
            proxy (ProxyManager): The proxy manager used to determine the locale.
        """
        language_dict = {
            "AF": ["pr-AF", "pr"],
            "AX": ["sw-AX", "sw"],
            "AL": ["sq-AL", "sq"],
            "DZ": ["ar-DZ", "ar"],
            "AS": ["en-AS", "en"],
            "AD": ["ca-AD", "ca"],
            "AO": ["po-AO", "po"],
            "AI": ["en-AI", "en"],
            "AG": ["en-AG", "en"],
            "AR": ["gr-AR", "gr"],
            "AM": ["hy-AM", "hy"],
            "AW": ["nl-AW", "nl"],
            "AU": ["en-AU", "en"],
            "AT": ["ba-AT", "ba"],
            "AZ": ["az-AZ", "az"],
            "BS": ["en-BS", "en"],
            "BH": ["ar-BH", "ar"],
            "BD": ["be-BD", "be"],
            "BB": ["en-BB", "en"],
            "BY": ["be-BY", "be"],
            "BE": ["de-BE", "de"],
            "BQ": ["en-BQ", "en"],
            "BZ": ["bj-BZ", "bj"],
            "BJ": ["fr-BJ", "fr"],
            "BM": ["en-BM", "en"],
            "BT": ["dz-BT", "dz"],
            "BO": ["ay-BO", "ay"],
            "BA": ["bo-BA", "bo"],
            "BW": ["en-BW", "en"],
            "BV": ["no-BV", "no"],
            "BR": ["po-BR", "po"],
            "IO": ["en-IO", "en"],
            "BN": ["ms-BN", "ms"],
            "BG": ["bu-BG", "bu"],
            "BF": ["fr-BF", "fr"],
            "BI": ["fr-BI", "fr"],
            "KH": ["kh-KH", "kh"],
            "CM": ["en-CM", "en"],
            "CA": ["en-CA", "en"],
            "CV": ["po-CV", "po"],
            "KY": ["en-KY", "en"],
            "CF": ["fr-CF", "fr"],
            "TD": ["ar-TD", "ar"],
            "CL": ["sp-CL", "sp"],
            "CN": ["zh-CN", "zh"],
            "CX": ["en-CX", "en"],
            "CC": ["en-CC", "en"],
            "CO": ["sp-CO", "sp"],
            "KM": ["ar-KM", "ar"],
            "CG": ["fr-CG", "fr"],
            "CD": ["fr-CD", "fr"],
            "CK": ["en-CK", "en"],
            "CR": ["sp-CR", "sp"],
            "CI": ["fr-CI", "fr"],
            "HR": ["hr-HR", "hr"],
            "CU": ["sp-CU", "sp"],
            "CW": ["en-CW", "en"],
            "CY": ["el-CY", "el"],
            "CZ": ["ce-CZ", "ce"],
            "DK": ["da-DK", "da"],
            "DJ": ["ar-DJ", "ar"],
            "DM": ["en-DM", "en"],
            "DO": ["sp-DO", "sp"],
            "EC": ["sp-EC", "sp"],
            "EG": ["ar-EG", "ar"],
            "SV": ["sp-SV", "sp"],
            "GQ": ["fr-GQ", "fr"],
            "ER": ["ar-ER", "ar"],
            "EE": ["es-EE", "es"],
            "ET": ["am-ET", "am"],
            "FK": ["en-FK", "en"],
            "FO": ["da-FO", "da"],
            "FJ": ["en-FJ", "en"],
            "FI": ["fi-FI", "fi"],
            "FR": ["fr-FR", "fr"],
            "GF": ["fr-GF", "fr"],
            "PF": ["fr-PF", "fr"],
            "TF": ["fr-TF", "fr"],
            "GA": ["fr-GA", "fr"],
            "GM": ["en-GM", "en"],
            "GE": ["ka-GE", "ka"],
            "DE": ["de-DE", "de"],
            "GH": ["en-GH", "en"],
            "GI": ["en-GI", "en"],
            "GR": ["el-GR", "el"],
            "GL": ["ka-GL", "ka"],
            "GD": ["en-GD", "en"],
            "GP": ["fr-GP", "fr"],
            "GU": ["ch-GU", "ch"],
            "GT": ["sp-GT", "sp"],
            "GG": ["en-GG", "en"],
            "GN": ["fr-GN", "fr"],
            "GW": ["po-GW", "po"],
            "GY": ["en-GY", "en"],
            "HT": ["fr-HT", "fr"],
            "HM": ["en-HM", "en"],
            "VA": ["it-VA", "it"],
            "HN": ["sp-HN", "sp"],
            "HK": ["en-HK", "en"],
            "HU": ["hu-HU", "hu"],
            "IS": ["is-IS", "is"],
            "IN": ["en-IN", "en"],
            "ID": ["in-ID", "in"],
            "IR": ["fa-IR", "fa"],
            "IQ": ["ar-IQ", "ar"],
            "IE": ["en-IE", "en"],
            "IM": ["en-IM", "en"],
            "IL": ["ar-IL", "ar"],
            "IT": ["it-IT", "it"],
            "JM": ["en-JM", "en"],
            "JP": ["jp-JP", "jp"],
            "JE": ["en-JE", "en"],
            "JO": ["ar-JO", "ar"],
            "KZ": ["ka-KZ", "ka"],
            "KE": ["en-KE", "en"],
            "KI": ["en-KI", "en"],
            "KP": ["ko-KP", "ko"],
            "KR": ["ko-KR", "ko"],
            "KW": ["ar-KW", "ar"],
            "KG": ["ki-KG", "ki"],
            "LA": ["la-LA", "la"],
            "LV": ["la-LV", "la"],
            "LB": ["ar-LB", "ar"],
            "LS": ["en-LS", "en"],
            "LR": ["en-LR", "en"],
            "LY": ["ar-LY", "ar"],
            "LI": ["de-LI", "de"],
            "LT": ["li-LT", "li"],
            "LU": ["de-LU", "de"],
            "MO": ["po-MO", "po"],
            "MK": ["mk-MK", "mk"],
            "MG": ["fr-MG", "fr"],
            "MW": ["en-MW", "en"],
            "MY": ["en-MY", "en"],
            "MV": ["di-MV", "di"],
            "ML": ["fr-ML", "fr"],
            "MT": ["en-MT", "en"],
            "MH": ["en-MH", "en"],
            "MQ": ["fr-MQ", "fr"],
            "MR": ["ar-MR", "ar"],
            "MU": ["en-MU", "en"],
            "YT": ["fr-YT", "fr"],
            "MX": ["sp-MX", "sp"],
            "FM": ["en-FM", "en"],
            "MD": ["ro-MD", "ro"],
            "MC": ["fr-MC", "fr"],
            "MN": ["mo-MN", "mo"],
            "MS": ["en-MS", "en"],
            "MA": ["ar-MA", "ar"],
            "MZ": ["po-MZ", "po"],
            "MM": ["my-MM", "my"],
            "NA": ["af-NA", "af"],
            "NR": ["en-NR", "en"],
            "NP": ["ne-NP", "ne"],
            "NL": ["nl-NL", "nl"],
            "NC": ["fr-NC", "fr"],
            "NZ": ["en-NZ", "en"],
            "NI": ["sp-NI", "sp"],
            "NE": ["fr-NE", "fr"],
            "NG": ["en-NG", "en"],
            "NU": ["en-NU", "en"],
            "NF": ["en-NF", "en"],
            "MP": ["ca-MP", "ca"],
            "NO": ["nn-NO", "nn"],
            "OM": ["ar-OM", "ar"],
            "PK": ["en-PK", "en"],
            "PW": ["en-PW", "en"],
            "PS": ["ar-PS", "ar"],
            "PA": ["sp-PA", "sp"],
            "PG": ["en-PG", "en"],
            "PY": ["gr-PY", "gr"],
            "PE": ["ay-PE", "ay"],
            "PH": ["en-PH", "en"],
            "PN": ["en-PN", "en"],
            "PL": ["po-PL", "po"],
            "PT": ["po-PT", "po"],
            "PR": ["en-PR", "en"],
            "QA": ["ar-QA", "ar"],
            "RE": ["fr-RE", "fr"],
            "RO": ["ro-RO", "ro"],
            "RU": ["ru-RU", "ru"],
            "RW": ["en-RW", "en"],
            "SH": ["en-SH", "en"],
            "KN": ["en-KN", "en"],
            "LC": ["en-LC", "en"],
            "PM": ["fr-PM", "fr"],
            "VC": ["en-VC", "en"],
            "WS": ["en-WS", "en"],
            "SM": ["it-SM", "it"],
            "ST": ["po-ST", "po"],
            "SA": ["ar-SA", "ar"],
            "SN": ["fr-SN", "fr"],
            "SC": ["cr-SC", "cr"],
            "SL": ["en-SL", "en"],
            "SG": ["zh-SG", "zh"],
            "SK": ["sl-SK", "sl"],
            "SI": ["sl-SI", "sl"],
            "SB": ["en-SB", "en"],
            "SO": ["ar-SO", "ar"],
            "SS": ["en-SS", "en"],
            "SX": ["en-SX", "en"],
            "ZA": ["af-ZA", "af"],
            "GS": ["en-GS", "en"],
            "ES": ["sp-ES", "sp"],
            "LK": ["si-LK", "si"],
            "SD": ["ar-SD", "ar"],
            "SR": ["nl-SR", "nl"],
            "SJ": ["no-SJ", "no"],
            "SZ": ["en-SZ", "en"],
            "SE": ["sw-SE", "sw"],
            "CH": ["fr-CH", "fr"],
            "SY": ["ar-SY", "ar"],
            "TW": ["zh-TW", "zh"],
            "TJ": ["ru-TJ", "ru"],
            "TZ": ["en-TZ", "en"],
            "TH": ["th-TH", "th"],
            "TL": ["po-TL", "po"],
            "TG": ["fr-TG", "fr"],
            "TK": ["en-TK", "en"],
            "TO": ["en-TO", "en"],
            "TT": ["en-TT", "en"],
            "TN": ["ar-TN", "ar"],
            "TR": ["tu-TR", "tu"],
            "TM": ["ru-TM", "ru"],
            "TC": ["en-TC", "en"],
            "TV": ["en-TV", "en"],
            "UG": ["en-UG", "en"],
            "UA": ["uk-UA", "uk"],
            "AE": ["ar-AE", "ar"],
            "GB": ["en-GB", "en"],
            "US": ["en-US", "en"],
            "UM": ["en-UM", "en"],
            "UY": ["sp-UY", "sp"],
            "UZ": ["ru-UZ", "ru"],
            "VU": ["bi-VU", "bi"],
            "VE": ["sp-VE", "sp"],
            "VN": ["vi-VN", "vi"],
            "VG": ["en-VG", "en"],
            "VI": ["en-VI", "en"],
            "WF": ["fr-WF", "fr"],
            "EH": ["be-EH", "be"],
            "YE": ["ar-YE", "ar"],
            "ZM": ["en-ZM", "en"],
            "ZW": ["bw-ZW", "bw"],
            "RS": ["sr-RS", "sr"],
            "ME": ["cn-ME", "cn"],
            "XK": ["sq-XK", "sq"],
        }
        country_code = proxy.country_code

        if country_code in language_dict:
            self.locale, self.language_code = language_dict[country_code]
        else:
            raise ValueError("Proxy Country not supported")
