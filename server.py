import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, executor

import vk_api
from middlewares import AccessMiddleware

logging.basicConfig(level=logging.INFO)

TG_API_TOKEN = os.getenv("TG_API_TOKEN")
VK_API_TOKEN = os.getenv("VK_API_TOKEN")
ACCESS_ID = os.getenv("TG_USER_ID")
PYTHONANYWHERE_PROXY_URL = "https://proxy.server:3128"

proxy_url = PYTHONANYWHERE_PROXY_URL if os.getenv('PYTHONANYWHERE_DOMAIN') else None

bot = Bot(token=TG_API_TOKEN, proxy=proxy_url)
loop = asyncio.get_event_loop()
dp = Dispatcher(bot, loop=loop)
dp.middleware.setup(AccessMiddleware(int(ACCESS_ID)))


async def get_last_news(seconds_ago: int = 30):
    while True:
        new_links = vk_api.get_news_links(VK_API_TOKEN, seconds_ago)

        for link in new_links[::-1]:
            await bot.send_message(ACCESS_ID, link,
                                   disable_web_page_preview=False)

        await asyncio.sleep(seconds_ago)


if __name__ == '__main__':
    dp.loop.create_task(get_last_news())
    executor.start_polling(dp, skip_updates=True)
