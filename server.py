import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import vk_api
from middlewares import AccessMiddleware

logging.basicConfig(level=logging.INFO)

TG_API_TOKEN = os.getenv("TG_API_TOKEN")
VK_API_TOKEN = os.getenv("VK_API_TOKEN")
ACCESS_ID = os.getenv("TG_USER_ID")
PROXY_URL = os.getenv("http_proxy")

bot = Bot(token=TG_API_TOKEN, proxy=PROXY_URL)
loop = asyncio.get_event_loop()
dp = Dispatcher(bot, loop=loop)
dp.middleware.setup(AccessMiddleware(int(ACCESS_ID)))


async def refresh_news_feed(seconds_ago: int = 30):
    while True:
        last_posts = vk_api.get_last_posts(VK_API_TOKEN, seconds_ago)

        for post in last_posts[::-1]:
            attachment_types = {}
            for attachment in post.get('attachments', []):
                if attachment_types.get(attachment['type']):
                    attachment_types[attachment['type']] += 1
                else:
                    attachment_types[attachment['type']] = 1

            link = f"https://vk.com/wall{post['source_id']}_{post['post_id']}"
            message_text = link

            attachments_count = len(attachment_types)
            if attachments_count > 1:
                attachment_descriptions = []
                for attachment_type in attachment_types:
                    attachment_count = attachment_types[attachment_type]
                    attachment_descriptions.append(
                        f'{attachment_count} {attachment_type}{"s" if attachment_count > 1 else ""}')
                message_text = ', '.join(attachment_descriptions) + "\n" + message_text
            elif attachments_count == 1:
                attachment_type, attachment_count = attachment_types.popitem()
                if attachment_count > 1:
                    message_text = f"{attachment_count} {attachment_type}s" + "\n" + message_text
            elif post.get('text'):
                if post['source_id'] > 0:
                    user = vk_api.get_user(VK_API_TOKEN, post['source_id'])
                    source_name = f'{user["first_name"]} {user["last_name"]}'
                else:
                    group = vk_api.get_group(VK_API_TOKEN, post['source_id'])
                    source_name = group['name']
                message_text = f'{post["text"][:120]}...' if len(post['text']) > 120 else post['text']
                message_text = f'{source_name}\n\n' + message_text

            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(text='Go to post', url=link))

            logging.info(msg=f"{post['date']} {message_text}")
            await bot.send_message(ACCESS_ID, message_text, disable_web_page_preview=False, reply_markup=markup)

        await asyncio.sleep(seconds_ago)


if __name__ == '__main__':
    dp.loop.create_task(refresh_news_feed(seconds_ago=30))
    executor.start_polling(dp, skip_updates=True)
