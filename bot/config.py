import os

backend_url = os.environ['BACKEND_URL']
api_key = os.environ['API_KEY']
proxy_url = os.environ['PROXY_URL']
proxy_username = os.environ['PROXY_USERNAME']
proxy_password = os.environ['PROXY_PASSWORD']

proxy = {
    'proxy_url': proxy_url,
    'urllib3_proxy_kwargs':
    {
        'username': proxy_username,
        'password': proxy_password,
    },
}

prev_days = int(os.environ['PREV_DAYS'])
hello_message = os.environ['HELLO_MESSAGE']