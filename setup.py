"""Python setup.py for botright package"""
import io
import os

from setuptools import find_packages, setup

def read(*paths, **kwargs):
    """Read the contents of a text file safely.
    >>> read("botright", "VERSION")
    "0.1.0"
    >>> read("README.md")
    ...
    """

    with io.open(os.path.join(os.path.dirname(__file__), *paths), encoding=kwargs.get("encoding", "utf8")) as open_file:
        content = open_file.read().strip()
    return content

requires = ["async_class",
            "httpx>=0.24.1",
            "playwright==1.37.0",
            "playwright_stealth==1.0.6",
            "pybrowsers==0.5.2",
            "fake-useragent==1.3.0",
            "numpy==1.26.0",
            "scipy==1.11.2",
            "Pillow==10.0.1",
            "hcaptcha_challenger>=0.7.10.post2",
            "yolov5==7.0.12",
            "sentence_transformers",
            "easyocr==1.7.1",
            "Faker==19.6.1",
            "scikit-image==0.21.0",
            "opencv-python~=4.8.0.76",
            "pytest==7.4.2",
            "imageio==2.31.3",
            "setuptools==68.2.2"]

setup(
    name="botright",
    version=read("botright", "VERSION"),
    keywords=["botright", "playwright", "recaptcha_challenger", "recaptcha-solver", "hcaptcha_challenger", "hcaptcha-solver", "geetest_challenger", "geetest-solver"],
    author="Vinyzu",
    url="https://github.com/Vinyzu/Botright",
    description="Botright, the next level automation studio for Python. Based on Playwright.",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    license="GNU General Public License v3.0",
    packages=find_packages(include=["botright", "botright.*", "LICENSE", "WebRTC-Leak-Shield"], exclude=["tests", ".github"]),
    package_data={"": ["requirements.txt", "geetest.torchscript", "WebRTC-Leak-Shield", "fingerprints.json"]},
    install_requires=requires,
    python_requires=">=3.8",
    classifiers=[
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
    ],
    project_urls={
        "Documentation": "https://github.com/Vinyzu/Botright/blob/main/docs/index.rst",
        "Source": "https://github.com/Vinyzu/Botright",
    },
)
