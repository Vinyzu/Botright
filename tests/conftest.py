from typing import Generator

import pytest_asyncio
from playwright._impl._path_utils import get_file_dirname

import botright

from .server import Server, test_server
from .utils import utils as utils_object

_dirname = get_file_dirname()


@pytest_asyncio.fixture
def assetdir():
    return _dirname / "assets"


@pytest_asyncio.fixture
def utils():
    yield utils_object


@pytest_asyncio.fixture(autouse=True, scope="session")
def run_around_tests():
    test_server.start()
    yield
    test_server.stop()


@pytest_asyncio.fixture
def server() -> Generator[Server, None, None]:
    yield test_server.server


@pytest_asyncio.fixture
async def botright_client():
    botright_client = await botright.Botright(headless=True)
    yield botright_client
    await botright_client.close()


@pytest_asyncio.fixture
async def browser(botright_client, **launch_arguments):
    browser = await botright_client.new_browser(**launch_arguments)
    yield browser
    await browser.close()


@pytest_asyncio.fixture
async def page(browser):
    page = await browser.new_page()
    yield page
    await page.close()
