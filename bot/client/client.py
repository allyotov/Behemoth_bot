import logging
from re import sub
import httpx
from bot.client import Subscriber, NewsItem

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class BehemothClient:

    ok_status_code = 201
    timeout = 5

    def __init__(self, backend_url: str):
        self.news_url = '{0}{1}'.format(backend_url, '/api/news/')
        self.subscribers_url = '{0}{1}'.format(backend_url, '/api/subscribers/')

    def search_news(self, **parameters) -> str:
        response = httpx.get(self.news_url, params=parameters)
        response.raise_for_status()
        return [NewsItem(**json_dict) for json_dict in response.json()]

    def get_subscribers(self, **parameters):
        response = httpx.get(self.subscribers_url, params=parameters)
        response.raise_for_status()
        logger.debug(response.json)
        return [Subscriber(**json_dict) for json_dict in response.json()]

    def send_subscriber(self, subscriber: Subscriber) -> None:
        try:
            logger.debug(subscriber)
            logger.debug(type(subscriber))
            logger.debug(subscriber.last_update)
            logger.info(subscriber.active)
            r = httpx.post(
                url=self.subscribers_url,
                content=subscriber.json(),
                headers={'content-type': 'application/json'},
            )
            r.raise_for_status()
            logger.debug('Очередной подписчик был отправлен в бекенд')
        except (httpx.ConnectError, httpx.RemoteProtocolError, httpx.HTTPStatusError) as exc:
            logger.debug('Не могу отправить подписчика из-за проблем с соединением.')
            logger.exception(exc)

    def edit_subscriber(self, subscriber: Subscriber):
        try:
            resp = httpx.put(
                url=f'{self.subscribers_url}{subscriber.id}/',
                data=subscriber.json(),
                headers={'content-type': 'application/json'},
            )
            resp.raise_for_status()
            logger.debug('Очередной подписчик был изменен в бекенде')
        except (httpx.ConnectError, httpx.RemoteProtocolError, httpx.HTTPStatusError) as exc:
            logger.debug('Не могу отредактировать подписчика из-за проблем с соединением.')
            logger.exception(exc)