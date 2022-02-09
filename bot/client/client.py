import httpx


class BehemothClient:

    ok_status_code = 201
    timeout = 5

    def __init__(self, backend_url: str):
        self.meetings_url = '{0}{1}'.format(backend_url, '/api/meetings/')
        self.news_url = '{0}{1}'.format(backend_url, '/api/news/')
        self.subscribers_url = '{0}{1}'.format(backend_url, '/api/news/')

    def search_news(self, **parameters) -> str:
        response = httpx.get(self.news_url, params=parameters)
        response.raise_for_status()
        return response.json()

    def search_meetings(self, **parameters) -> str:
        response = httpx.get(self.meetings_url, params=parameters)
        response.raise_for_status()
        return response.json()

    def get_subscribers(self, **parameters):
        response = httpx.get(self.meetings_url, params=parameters)
        response.raise_for_status()
        return response.json()