"""Request Wrapper for Nextcloud OCS Talk APIs.

https://nextcloud-talk.readthedocs.io/en/latest/global/
"""

import logging
from typing import Any, Dict, Optional, Tuple

import httpx

from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudOcsApi
from nextcloud_async.exceptions import (
    NextcloudNotCapableError,
    NextcloudRequestTimeoutError,
)

_HTTP_USER_ERROR = 400
_HTTP_SERVER_ERROR = 500

log = logging.getLogger("nextcloud_async.driver")


class NextcloudTalkApi(NextcloudOcsApi):
    """Nextcloud Talk OCS API.

    All OCS queries must have an {'OCS-APIRequest': 'true'} header. Additionally, we
    request all data to be returned to us in json format.
    """

    def __init__(
        self,
        client: NextcloudClient,
        ocs_version: Optional[str] = "2",
        stub: Optional[str] = None,
    ) -> None:
        super().__init__(client, ocs_version, stub)

    async def has_talk_feature(self, capability: str) -> bool:
        """Checks to see if Talk supports a given feature.

        Args:
            capability:
                Dot-separated strings

        Returns:
            True or False
        """
        features = await self._capabilities_api.supported(
            ".".join(["spreed.features", capability])
        )
        local_features = await self._capabilities_api.supported(
            ".".join(["spreed.features-local", capability])
        )
        return features or local_features

    has_talk_capability = has_talk_feature

    async def require_talk_feature(self, capability: str) -> None:
        """Raise an exception if talk doesn't support the given feature."""
        if not await self.has_talk_feature(capability):
            raise NextcloudNotCapableError()

    require_talk_capability = require_talk_feature

    async def request(
        self,
        method: str = "GET",
        path: str = "",
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Dict[str, Any], httpx.Headers]:
        """Submit OCS-type query to cloud endpoint.

        Args:
            method:
                HTTP Method (eg, `GET`, `POST`, etc...)

            url:
                Use a URL outside of the given endpoint. Defaults to None.

            path:
                The portion of the URL after the host. Defaults to ''.

            data:
                Data for submission.  Data for GET requests is translated by
                urlencode and tacked on to the end of the URL as arguments.

            headers:
                Headers for submission. Defaults to {}.

        Returns:
            Tuple[Dict, Dict]: Response Data and headers

        Raises:
            NextcloudException - when invalid response from server
        """
        headers = self._munge_headers(headers)
        data = self._format_json(data)

        if method.lower() == "get":
            path = self._path_args(data, path)
            data = None

        try:
            log.debug(f"{method} {self.client.endpoint}{self.stub}{path} {data}")
            response = await self.client.http_client.request(
                method,
                auth=self.client.auth,
                url=f"{self.client.endpoint}{self.stub}{path}",
                json=data,
                headers=headers,
            )
            log.debug(f"Response: [{response.status_code}] {response.text}")
        except httpx.ReadTimeout:
            log.warning("Request timed out.")
            raise NextcloudRequestTimeoutError()

        await self.raise_response_exception(response)
        return response.json()["ocs"]["data"], response.headers
