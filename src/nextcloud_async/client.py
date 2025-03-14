import httpx
import logging

from typing import Optional

from nextcloud_async.version import USER_AGENT

log = logging.getLogger("nextcloud_async.client")


class NextcloudClient:
    def __init__(
        self,
        endpoint: str,
        user: str,
        password: Optional[str] = None,
        app_token: Optional[str] = None,
        http_client: httpx.AsyncClient = httpx.AsyncClient(),
        user_agent: str = USER_AGENT,
    ) -> None:
        if not (password or app_token):
            raise RuntimeError("Must supply one of password or app_token")

        if app_token:
            log.debug("Using App token authentication.")
        elif user and password:
            log.debug("Using basic http auth")

        self.user = user
        self.password = password
        self.app_token = app_token
        self.endpoint = endpoint
        self.http_client = http_client
        self.user_agent = user_agent
