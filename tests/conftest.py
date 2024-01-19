import asyncio
from typing import Generator, AsyncGenerator

import pytest_asyncio
from playwright._impl._path_utils import get_file_dirname

import botright
from .utils import utils as utils_object
from .server import test_server, Server

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


@pytest_asyncio.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def botright_client():
    botright_client = await botright.Botright(headless=True)
    yield botright_client
    await botright_client.close()


@pytest_asyncio.fixture(scope="session")
async def scoped_browser(botright_client, **launch_arguments):
    browser = await botright_client.new_browser(**launch_arguments)
    yield browser
    await browser.close()

@pytest_asyncio.fixture
async def browser(botright_client, **launch_arguments):
    browser = await botright_client.new_browser(**launch_arguments)
    yield browser
    await browser.close()


@pytest_asyncio.fixture
async def page(scoped_browser):
    page = await scoped_browser.new_page()
    yield page
    await page.close()
