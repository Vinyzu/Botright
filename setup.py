"""Python setup.py for botright package"""
import io
import os

from setuptools import find_packages, setup

def read(*paths, **kwargs):
    """Read the contents of a text file safely.
    >>> read("botright", "VERSION")
    '0.1.0'
    >>> read("README.md")
    ...
    """

    with io.open(os.path.join(os.path.dirname(__file__), *paths), encoding=kwargs.get("encoding", "utf8")) as open_file:
        content = open_file.read().strip()
    return content


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
    packages=find_packages(include=["botright", "botright.*", "LICENSE"], exclude=["tests", ".github"]),
    # package_data={"": ["names.txt", "passwords.txt", "requirements.txt", "geetest.torchscript", "labels.txt", "keras_model.h5"]},
    install_requires=read("requirements.txt").splitlines(),
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
)
