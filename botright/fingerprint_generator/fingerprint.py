from __future__ import annotations

from typing import Optional, Literal
import os.path

from fake_useragent import UserAgent
from .bayesian_network import BayesianNetwork


class FingerprintGenerator:
    def __init__(self, os_system: Literal["windows", "macos", "linux"], browser: Optional[Literal["chrome", "edge", "firefox", "safari"]] = "chrome") -> None:
        """
        Initialize a FingerprintGenerator instance.

        Args:
            os_system (Literal["windows", "macos", "linux"]): The operating system for which the fingerprint will be generated.
            browser (Optional[Literal["chrome", "edge", "firefox", "safari"]]): The web browser to include in the user agent (default is "chrome").
        """
        self.ua = UserAgent(os=[os_system], browsers=[browser], min_percentage=1.5)
        self.bayesian_network = BayesianNetwork(path=rf"{os.path.dirname(os.path.abspath(__file__))}\fingerprints.json")

    def get_fingerprint(self) -> dict:
        """
        Generate a fingerprint using a Bayesian network.

        Returns:
            dict: A dictionary containing the generated fingerprint information.
        """
        sample = self.bayesian_network.generate_sample(input_values={"userAgent": self.ua.chrome})
        return sample

if __name__ == "__main__":
    import json

    gen = FingerprintGenerator("windows")
    fingerprint = gen.get_fingerprint()
    print(json.dumps(fingerprint, indent=4))
    print(fingerprint["platform"])
