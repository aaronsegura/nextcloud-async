import httpx

from typing import Optional

from nextcloud_async.version import USER_AGENT

class NextcloudClient:
    def __init__(
            self,
            endpoint: str,
            user: str,
            password: str,
            http_client: Optional[httpx.AsyncClient] = None,
            user_agent: str = USER_AGENT):
        """Set up authentication for endpoint interaction.

        Args
        ----
            client (httpx.AsyncClient): AsyncClient.  Only httpx supported, but others may
            work.

            endpoint (str): The nextcloud endpoint URL

            user (str, optional): User login. Defaults to ''.

            password (str, optional): User password. Defaults to ''.

        """
        self.user: str = user
        self.password: str = password
        self.endpoint: str = endpoint
        self.http_client: httpx.AsyncClient = http_client or httpx.AsyncClient()
        self.user_agent: str = user_agent
