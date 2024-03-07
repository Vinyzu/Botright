from __future__ import annotations

from typing import Dict, List, Optional

import httpx
from async_class import AsyncObject, link


class SplitError(Exception):
    pass


class ProxyCheckError(Exception):
    pass


class ProxyManager(AsyncObject):
    proxy: str = ""
    http_proxy: Dict[str, str] = {}
    browser_proxy: Optional[Dict[str, str]] = None
    plain_proxy: str = ""
    _httpx: httpx.AsyncClient
    _phttpx: httpx.AsyncClient
    ip: str = ""
    port: str = ""
    username: str = ""
    password: str = ""
    country: str = ""
    country_code: str = ""
    region: str = ""
    city: str = ""
    zip: str = ""
    latitude: str = ""
    longitude: str = ""
    timezone: str = ""

    async def __ainit__(self, botright, proxy: str) -> None:
        """
        Initialize a ProxyManager instance with a proxy string and perform proxy checks.

        Args:
            botright: An instance of Botright for linking purposes.
            proxy (str): The proxy string to be managed and checked.
        """
        link(self, botright)

        self.proxy = proxy.strip() if proxy else ""

        self.timeout = httpx.Timeout(20.0, read=None)
        self._httpx = httpx.AsyncClient(verify=False)

        if self.proxy:
            self.split_proxy()
            self.proxy = f"{self.username}:{self.password}@{self.ip}:{self.port}" if self.username else f"{self.ip}:{self.port}"
            self.plain_proxy = f"http://{self.proxy}"
            self._phttpx = httpx.AsyncClient(proxies={"all://": self.plain_proxy}, verify=False)
            self.http_proxy = {"http": self.plain_proxy, "https": self.plain_proxy}

            if self.username:
                self.browser_proxy = {"server": f"{self.ip}:{self.port}", "username": self.username, "password": self.password}
            else:
                self.browser_proxy = {"server": self.plain_proxy}

            await self.check_proxy(self._phttpx)

        else:
            self._phttpx = self._httpx
            await self.check_proxy(self._phttpx)

    async def __adel__(self) -> None:
        await self._httpx.aclose()
        await self._phttpx.aclose()

    def split_helper(self, split_proxy: List[str]) -> None:
        """
        Helper function to split and parse the proxy string into its components.

        Args:
            split_proxy (List[str]): A list containing the components of the proxy string.
        """
        if not any([_.isdigit() for _ in split_proxy]):
            raise SplitError("No ProxyPort could be detected")
        if split_proxy[1].isdigit():
            self.ip, self.port, self.username, self.password = split_proxy
        elif split_proxy[3].isdigit():
            self.username, self.password, self.ip, self.port = split_proxy
        else:
            raise SplitError(f"Proxy Format ({self.proxy}) isnt supported")

    def split_proxy(self) -> None:
        split_proxy = self.proxy.split(":")
        if len(split_proxy) == 2:
            self.ip, self.port = split_proxy
        elif len(split_proxy) == 3:
            if "@" in self.proxy:
                helper = [_.split(":") for _ in self.proxy.split("@")]
                split_proxy = [x for y in helper for x in y]
                self.split_helper(split_proxy)
            else:
                raise SplitError(f"Proxy Format ({self.proxy}) isnt supported")
        elif len(split_proxy) == 4:
            self.split_helper(split_proxy)
        else:
            raise SplitError(f"Proxy Format ({self.proxy}) isnt supported")

    async def check_proxy(self, httpx_client: httpx.AsyncClient) -> None:
        """
        Check the validity of the proxy by making HTTP requests to determine its properties.

        Args:
            httpx_client (httpx.AsyncClient): The HTTPX client to use for proxy checks.
        """
        get_ip_apis = ["https://api.ipify.org/?format=json", "https://api.myip.com/", "https://get.geojs.io/v1/ip.json", "https://api.ip.sb/jsonip", "https://l2.io/ip.json"]

        for get_ip_api in get_ip_apis:
            try:
                ip_request = await httpx_client.get(get_ip_api, timeout=self.timeout)
                ip = ip_request.json().get("ip")
                break
            except Exception:
                pass
        else:
            raise ProxyCheckError("Could not get IP-Address of Proxy (Proxy is Invalid/Timed Out)")

        get_geo_apis = {
            "http://ip-api.com/json/<IP>": ["country", "countryCode", "lat", "lon", "timezone"],
            "https://ipapi.co/<IP>/json": ["country_name", "country", "latitude", "longitude", "timezone"],
            "https://api.techniknews.net/ipgeo/<IP>": ["country", "countryCode", "lat", "lon", "timezone"],
            "https://get.geojs.io/v1/ip/geo/<IP>.json": ["country", "country_code", "latitude", "longitude", "timezone"],
        }

        for get_geo_api, api_names in get_geo_apis.items():
            try:
                api_url = get_geo_api.replace("<IP>", ip)
                country, country_code, latitude, longitude, timezone = api_names
                r = await self._httpx.get(api_url, timeout=self.timeout)
                data = r.json()

                self.country = data.get(country)
                self.country_code = data.get(country_code)
                self.latitude = data.get(latitude)
                self.longitude = data.get(longitude)
                self.timezone = data.get(timezone)

                assert self.country
                break
            except Exception:
                pass
        else:
            raise ProxyCheckError("Could not get GeoInformation from proxy (Proxy is probably not Indexed)")
