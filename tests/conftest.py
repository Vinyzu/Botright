import pytest_asyncio

import botright
from playwright._impl._path_utils import get_file_dirname
from .utils import utils as utils_object

_dirname = get_file_dirname()


@pytest_asyncio.fixture
def utils():
    yield utils_object


@pytest_asyncio.fixture  # (scope="session")
async def botright_client():
    botright_client = await botright.Botright(headless=False)
    yield botright_client
    await botright_client.close()


@pytest_asyncio.fixture  # (scope="session")
async def browser(botright_client, **launch_arguments):
    browser = await botright_client.new_browser(**launch_arguments)
    yield browser
    await browser.close()


@pytest_asyncio.fixture
async def page(browser):
    page = await browser.new_page()
    yield page
    await page.close()


@pytest_asyncio.fixture
def assetdir():
    return _dirname / "assets"
