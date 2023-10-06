from __future__ import annotations

from typing import List

import httpx
from async_class import AsyncObject, link

class SplitError(Exception):
    pass


class ProxyCheckError(Exception):
    pass


class ProxyManager(AsyncObject):
    async def __ainit__(self, botright, proxy: str) -> None:
        """
        Initialize a ProxyManager instance with a proxy string and perform proxy checks.

        Args:
            botright: An instance of Botright for linking purposes.
            proxy (str): The proxy string to be managed and checked.
        """
        link(self, botright)

        self.proxy, self.http_proxy = proxy.strip() if proxy else None, None
        self.ip, self.port, self.username, self.password = None,  None, None, None
        self.browser_proxy, self.plain_proxy = None, None

        self.country, self.country_code = None, None
        self.region, self.city, self.zip = None, None, None
        self.latitude, self.longitude, self.timezone = None, None, None

        self.timeout = httpx.Timeout(20.0, read=None)
        self.httpx = httpx.AsyncClient()

        if self.proxy:
            self.split_proxy()
            self.proxy = f"{self.username}:{self.password}@{self.ip}:{self.port}" if self.username else f"{self.ip}:{self.port}"
            self.plain_proxy = f"http://{self.proxy}"
            self.phttpx = httpx.AsyncClient(proxies={"all://": self.plain_proxy})
            self.http_proxy = {"http": self.plain_proxy, "https": self.plain_proxy}

            if self.username:
                self.browser_proxy = {"server": f"{self.ip}:{self.port}", "username": self.username, "password": self.password}
            else:
                self.browser_proxy = {"server": self.plain_proxy}

            await self.check_proxy(self.phttpx)

        else:
            self.phttpx = self.httpx
            await self.check_proxy(self.httpx)

    async def __adel__(self) -> None:
        await self.httpx.aclose()
        await self.phttpx.aclose()

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
        try:
            ip_request = await httpx_client.get("http://jsonip.com", timeout=self.timeout)
            ip = ip_request.json().get("ip")
        except Exception as e:

            # Trying again on different site (jsonip.com is known to have downtimes)
            try:
                ip_request = await httpx_client.get("http://httpbin.org/ip", timeout=self.timeout)
                ip = ip_request.json().get("origin")
            except Exception as e:
                raise ProxyCheckError("Could not get IP-Address of Proxy (Proxy is Invalid/Timed Out)")
        try:
            r = await self.httpx.get(f"http://ip-api.com/json/{ip}", timeout=self.timeout)
            data = r.json()
            self.country = data.get("country")
            self.country_code = data.get("countryCode")
            self.region = data.get("regionName")
            self.city = data.get("city")
            self.zip = data.get("zip")
            self.latitude = data.get("lat")
            self.longitude = data.get("lon")
            self.timezone = data.get("timezone")

            if not self.country:
                raise ProxyCheckError("Could not get GeoInformation from proxy (Proxy is probably not Indexed)")
        except Exception as e:
            raise ProxyCheckError("Could not get GeoInformation from proxy (Proxy is probably not Indexed)")
