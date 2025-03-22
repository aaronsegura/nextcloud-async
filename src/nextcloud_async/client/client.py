import logging

from nextcloud_async.client.legacy import NextCloudAsync
from nextcloud_async.provider import HttpClientBasicAuth, HttpClientProvider
from nextcloud_async.version import USER_AGENT

log = logging.getLogger("nextcloud_async.client")


class NextcloudClient:
    _user: str

    def __init__(
        self,
        endpoint: str,
        http_client: HttpClientProvider,
        auth: HttpClientBasicAuth | None = None,
        user: str | None = None,
        app_token: str | None = None,
        user_agent: str = USER_AGENT,
    ) -> None:
        if not (auth or app_token):
            raise RuntimeError("Must supply one of `auth` or `app_token`.")
        if auth and app_token:
            raise RuntimeError("`auth` and `app_token` are mutually exclusive.")
        if app_token and not user:
            raise RuntimeError("When using `app_token` you must supply a user name.")

        if app_token and user:
            self.auth = None
            self.request_headers = {"Authorization": f"Bearer {app_token}"}
            self._user = user
            log.debug("Using App token authentication.")
        elif auth:
            self.auth = auth
            self.request_headers = {}
            self._user = self.auth.user
            log.debug("Using basic http auth")

        self.app_token = app_token
        self.endpoint = endpoint
        self.http_client = http_client
        self.user_agent = user_agent

    @property
    def user(self) -> str:
        """Return the username."""
        return self._user

    def legacy_client(self) -> NextCloudAsync:
        """Return the legacy client for backwards compatibility.

        Returns:
            NextCloudAsync client

        """
        return NextCloudAsync(
            self.endpoint,
            self.http_client,
            self.auth,
            self.app_token,
            self.user_agent,
        )
