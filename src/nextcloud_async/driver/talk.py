"""Request Wrapper for Nextcloud OCS Talk APIs.

https://nextcloud-talk.readthedocs.io/en/latest/global/
"""

import logging
from typing import TYPE_CHECKING, Any, cast

from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudOcsDriver
from nextcloud_async.exceptions import NextcloudNotCapableError

if TYPE_CHECKING:
    from nextcloud_async.provider import HttpClientResponse

log = logging.getLogger("nextcloud_async.driver")


class NextcloudTalkDriver(NextcloudOcsDriver):
    """Nextcloud Talk OCS API.

    All OCS queries must have an {'OCS-APIRequest': 'true'} header. Additionally, we
    request all data to be returned to us in json format.
    """

    def __init__(
        self,
        client: NextcloudClient,
        ocs_version: str | None = "2",
        stub: str | None = None,
    ) -> None:
        super().__init__(client, ocs_version, stub)

    async def has_feature(self, feature: str) -> bool:
        """Check to see if Talk supports a given feature.

        Args:
            feature:
                String from Capabilities.spreed.features list.

        Returns:
            True or False

        """
        features = await self._capabilities_api.supported(f"spreed.features.{feature}")
        local_features = await self._capabilities_api.supported(
            f"spreed.features-local.{feature}"
        )
        return features or local_features

    async def require_feature(self, feature: str) -> None:
        """Raise an exception if talk doesn't support the given feature."""
        if not await self.has_feature(feature):
            raise NextcloudNotCapableError()

    async def request(
        self,
        method: str = "GET",
        path: str = "",
        headers: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        content: bytes | None = None,
        json: Any | None = None,
        file: bytes | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Submit OCS-type query to cloud endpoint.

        Only one of json/content/data may be used.

        Args:
            method:
                HTTP Method (eg, `GET`, `POST`, etc...)

            url:
                Use a URL outside of the given endpoint. Defaults to None.

            headers:
                Headers for submission. Defaults to {}.

            path:
                The portion of the URL after the host. Defaults to ''.

            data:
                Data for submission.  Data for GET requests is translated by
                urlencode and tacked on to the end of the URL as arguments.

            content:
                Bytes data to pass as body.

            json:
                JSON-serializable data for submission.

            file:
                File bytes for multipart form-data upload.

        Returns:
            tuple[Dict, Dict]: Response Data and headers

        Raises:
            NextcloudException - when invalid response from server

        """
        response = cast(
            "HttpClientResponse",
            await super().request(
                method=method,
                path=path,
                headers=headers,
                data=data,
                content=content,
                json=json,
                file=file,
                raw_response=True,
            ),
        )
        await self.raise_response_exception(response)
        return response.json()["ocs"]["data"], response.headers
