import httpx

from nextcloud_async.version import USER_AGENT

class NextcloudClient:
    def __init__(
            self,
            endpoint: str,
            user: str,
            password: str,
            http_client: httpx.AsyncClient = httpx.AsyncClient(),
            user_agent: str = USER_AGENT) -> None:
        self.user: str = user
        self.password: str = password
        self.endpoint: str = endpoint
        self.http_client: httpx.AsyncClient = http_client
        self.user_agent: str = user_agent
