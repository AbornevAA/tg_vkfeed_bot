""" Набор функций для работы с VK API """

import datetime

import requests

GET_NEWS_FEED_METHOD_URL = 'https://api.vk.com/method/newsfeed.get'
API_VERSION = '5.131'


def get_news_links(access_token: str, seconds_ago: int = 30, api_version: str = API_VERSION) -> list:
    news_links = []
    now = int(datetime.datetime.now().timestamp())

    get_news_feed_response = requests.get(GET_NEWS_FEED_METHOD_URL,
                                          {'access_token': access_token,
                                           'v': api_version,
                                           'filters': 'post',
                                           'max_photos': 1,
                                           'start_time': now - seconds_ago,
                                           'count': 10})

    get_news_feed_response_json = get_news_feed_response.json()

    error_response = get_news_feed_response_json.get('error', {})
    if error_response:
        error_code = error_response.get('error_code', 'Unknown error')
        error_msg = error_response.get('error_msg', '-1')
        raise ValueError(f'{error_msg} [Error code: {error_code}]')

    get_news_feed_response = get_news_feed_response_json.get('response', {})

    for news in get_news_feed_response.get('items', []):
        source_id = news['source_id']
        post_id = news['post_id']
        if not news.get('marked_as_ads') and post_id != 1636045200:
            news_links.append(f'https://vk.com/wall{source_id}_{post_id}')

    return list(set(news_links))
