""" Набор функций для работы с VK API """

import datetime
from typing import Union

import requests

VK_API = 'https://api.vk.com/method/'
GET_NEWS_FEED_METHOD_URL = VK_API + 'newsfeed.get'
GET_USER_METHOD_URL = VK_API + 'users.get'
GET_GROUP_METHOD_URL = VK_API + 'groups.getById'
API_VERSION = '5.131'


def get_last_posts(access_token: str, seconds_ago: int = 30, api_version: str = API_VERSION) -> list:
    posts_list = []
    now = int(datetime.datetime.now().timestamp())

    posts = vk_response(GET_NEWS_FEED_METHOD_URL,
                        {'access_token': access_token,
                         'v': api_version,
                         'filters': 'post',
                         'max_photos': 1,
                         'start_time': now - seconds_ago,
                         'count': 10})

    for post in posts:
        if not post.get('marked_as_ads') and post['post_id'] != 1636045200:
            posts_list.append(post)

    return posts_list


def get_user(access_token: str, user_id: int, api_version: str = API_VERSION) -> dict:
    user = vk_response(GET_USER_METHOD_URL,
                       {'access_token': access_token,
                        'v': api_version,
                        'user_ids': user_id})
    return user


def get_group(access_token: str, group_id: int, api_version: str = API_VERSION) -> dict:
    group = vk_response(GET_GROUP_METHOD_URL,
                        {'access_token': access_token,
                         'v': api_version,
                         'group_id': abs(group_id)})
    return group


def vk_response(method_url: str, params: dict) -> Union[list, dict]:
    response = requests.get(method_url, params)
    response_json = response.json()
    error_response = response_json.get('error', {})

    if error_response:
        error_code = error_response.get('error_code', 'Unknown error')
        error_msg = error_response.get('error_msg', '-1')
        raise ValueError(f'{error_msg} [Error code: {error_code}]')

    response = response_json.get('response', {})

    if isinstance(response, dict):
        items = response.get('items')
        if isinstance(items, list):
            return items

    return response[0]
