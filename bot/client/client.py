import logging
import httpx
from bot.client import Subscriber

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
        return response.json()

    def get_subscribers(self, **parameters):
        response = httpx.get(self.subscribers_url, params=parameters)
        response.raise_for_status()
        return response.json()

    def send_subscriber(self, subscriber: Subscriber) -> None:
        try:
            logger.debug(subscriber)
            logger.debug(type(subscriber))
            logger.debug(subscriber.last_update)
            r = httpx.post(
                url=self.subscribers_url,
                content=subscriber.json(),
                headers={'content-type': 'application/json'},
            )
            r.raise_for_status()
            logger.debug('Очередной подписчик был тправлен в бекенд')
        except (httpx.ConnectError, httpx.RemoteProtocolError, httpx.HTTPStatusError) as exc:
            logger.debug('Не могу отправить новости из-за проблем с соединением.')
            logger.exception(exc)