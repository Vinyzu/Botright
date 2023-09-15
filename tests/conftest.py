import pytest
import pytest_asyncio

import botright


@pytest_asyncio.fixture  # (scope="session")
async def botright_client(headless=False):
    botright_client = await botright.Botright(headless=headless)
    yield botright_client
    await botright_client.close()


@pytest_asyncio.fixture  # (scope="session")
async def browser(botright_client, **launch_arguments):
    #
    browser = await botright_client.new_browser(block_images=True, no_proxy=True, **launch_arguments)
    yield browser
    await browser.close()


@pytest_asyncio.fixture
async def page(browser):
    page = await browser.new_page()
    yield page
    await page.close()
