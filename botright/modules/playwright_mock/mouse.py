import random

import numpy


def mock_mouse(page) -> None:
    # MouseMocking
    async def click_mocker(x, y, button="left", click_count=1, delay=20, humanly=True):
        await Mouse.click(page, x, y, button, click_count, delay, humanly)

    page.mouse.click = click_mocker

    async def dblclick_mocker(x, y, button="left", delay=20, humanly=True):
        await Mouse.dblclick(page, x, y, button, delay, humanly)

    page.mouse.dblclick = dblclick_mocker

    async def move_mocker(x, y, steps=1, humanly=True):
        await Mouse.move(page, x, y, steps, humanly)

    page.mouse._move = page.mouse.move
    page.mouse.move = move_mocker


class Mouse:
    last_x = 0
    last_y = 0

    async def click(page, x, y, button="left", click_count=1, delay=20, humanly=True) -> None:
        # Move mouse humanly to the Coordinates and wait some random time
        await Mouse.move(page, x, y, humanly)
        await page.wait_for_timeout(random.randint(4, 8) * 100)

        # Clicking the Coordinates
        await page.mouse.down(button=button, click_count=click_count)
        # Waiting as delay
        await page.wait_for_timeout(delay)
        await page.mouse.up(button=button, click_count=click_count)

        # Waiting random time
        await page.wait_for_timeout(random.randint(4, 8) * 100)

    async def dblclick(page, x, y, button="left", delay=20, humanly=True) -> None:
        # Move mouse humanly to the Coordinates and wait some random time
        await Mouse.move(page, x, y, humanly)
        await page.wait_for_timeout(random.randint(4, 8) * 100)

        # Clicking the Coordinates
        await page.mouse.down(button=button)
        # Waiting as delay
        await page.wait_for_timeout(delay)
        await page.mouse.up(button=button)

        # Waiting short random time
        await page.wait_for_timeout(random.randint(8, 14) * 10)
        # Clicking the Coordinates
        await page.mouse.down(button=button)
        # Waiting as delay
        await page.wait_for_timeout(delay)
        await page.mouse.up(button=button)

        # Waiting random time
        await page.wait_for_timeout(random.randint(4, 8) * 100)

    async def move(page, x, y, steps=1, humanly=True) -> None:
        # If you wanna move in a straight line
        if not humanly:
            await page.mouse._move(x, y, steps=steps)
            return

        def getEquidistantPoints(p1, p2, parts):
            return numpy.linspace(p1[0], p2[0], parts + 1), numpy.linspace(p1[1], p2[1], parts + 1)

        x_points, y_points = getEquidistantPoints((Mouse.last_x, Mouse.last_y), (x, y), 20)

        random_x_points, random_y_points = [], []
        # Randomize Points
        for x, y in zip(x_points[0:], y_points[0:]):
            random_x_points.append(random.uniform(x - 0.4, x + 0.4))
            random_y_points.append(random.uniform(y - 0.4, y + 0.4))

        final_x_points = [*random_x_points, x_points[-1]]
        final_y_points = [*random_y_points, y_points[-1]]

        # Move Mouse to new random locations
        for x, y in zip(final_x_points, final_y_points):
            await page.mouse._move(x, y)
            await page.wait_for_timeout(random.randint(20, 60))
        # Set LastX and LastY cause Playwright doesnt have mouse.current_location
        Mouse.last_x, Mouse.last_y = final_x_points[-1], final_y_points[-1]
