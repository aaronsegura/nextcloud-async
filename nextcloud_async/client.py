"""
"""
import httpx

from nextcloud_async.version import USER_AGENT

class NextcloudClient:
    def __init__(
            self,
            endpoint: str,
            user: str,
            password: str,
            http_client: httpx.AsyncClient = httpx.AsyncClient(),
            user_agent: str = USER_AGENT):
        """Set up authentication for endpoint interaction.

        Args
        ----
            client (httpx.AsyncClient): AsyncClient.  Only httpx supported, but others may
            work.

            endpoint (str): The nextcloud endpoint URL

            user (str, optional): User login. Defaults to ''.

            password (str, optional): User password. Defaults to ''.

            user_agent (str, optional): user-agent reported to endpoint in headers.

        """
        self.user: str = user
        self.password: str = password
        self.endpoint: str = endpoint
        self.http_client: httpx.AsyncClient = http_client
        self.user_agent: str = user_agent
