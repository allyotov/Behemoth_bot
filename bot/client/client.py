import httpx


class BehemothClient:

    ok_status_code = 201
    timeout = 5

    def __init__(self, backend_url: str):
        self.url = '{0}{1}'.format(backend_url, '/api/v1/books/')

    def search_news(self, phrase) -> str:
        parameter = {'search': phrase}
        response = httpx.get(self.url, params=parameter)
        response.raise_for_status()
        return response.json()

    def search_meetings(self, phrase) -> str:
        parameter = {'search': phrase}
        response = httpx.get(self.url, params=parameter)
        response.raise_for_status()
        return response.json()