"""Request Wrapper for Nextcloud OCS Talk APIs.

https://nextcloud-talk.readthedocs.io/en/latest/global/
"""

import httpx
import json
import logging

from typing import Dict, Any, Optional, Tuple

from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudOcsApi, NextcloudCapabilities

from nextcloud_async.exceptions import (
    NextcloudRequestTimeoutError,
    NextcloudNotCapableError,
    NextcloudError,
)

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
    ):
        if stub:
            self.stub = stub
        else:
            self.stub = f"/ocs/v{ocs_version}.php"

        self.ocs_version = ocs_version
        self.capabilities_api = NextcloudCapabilities(client)

        super().__init__(client)

    async def has_talk_feature(self, capability: str) -> bool:
        features = await self.capabilities_api.supported(
            ".".join(["spreed.features", capability])
        )
        local_features = await self.capabilities_api.supported(
            ".".join(["spreed.features-local", capability])
        )
        return features or local_features

    has_talk_capability = has_talk_feature

    async def require_talk_feature(self, capability: str) -> None:
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
            method (str): HTTP Method (eg, `GET`, `POST`, etc...)

            url (str, optional): Use a URL outside of the given endpoint. Defaults to None.

            path (str, optional): The portion of the URL after the host. Defaults to ''.

            data (Dict, optional): Data for submission.  Data for GET requests is translated by
            urlencode and tacked on to the end of the URL as arguments. Defaults to {}.

            headers (Dict, optional): Headers for submission. Defaults to {}.

        Returns:
            Tuple[Dict, Dict]: Response Data and headers

        Raises:
            NextcloudException - when invalid response from server
        """
        headers = self._munge_headers(headers)
        data = self._munge_data(data)
        auth = self._get_auth()

        if method.lower() == "get":
            path = self._munge_path_data(data, path)
            data = None

        try:
            log.debug(f"{method} {self.client.endpoint}{self.stub}{path} {data}")
            response = await self.client.http_client.request(
                method,
                auth=auth,
                url=f"{self.client.endpoint}{self.stub}{path}",
                json=data,
                headers=headers,
            )
            log.debug(f"Response: [{response.status_code}] {response.json()}")

        except httpx.ReadTimeout:
            log.warning("Request timed out.")
            raise NextcloudRequestTimeoutError()

        await self.raise_response_exception(response)
        return response.json()["ocs"]["data"], response.headers

    async def raise_response_exception(self, response: httpx.Response) -> None:
        """Raise appropriate exception for given response.

        Args:
            response:
                The response object.

        Raises:
            NextcloudError: If unable to decode response or if exception isn't
                handled by inherited _raise_response_exception.
        """
        try:
            response_content = json.loads(response.content.decode("utf-8"))
        except json.JSONDecodeError:
            raise NextcloudError(status_code=500, reason="Error decoding JSON response.")
        ocs_meta = response_content["ocs"]["meta"]
        if ocs_meta["status"] != "ok":
            await self._raise_response_exception(
                status_code=ocs_meta["statuscode"], reason=ocs_meta["message"]
            )

        if response.status_code >= 300:
            raise NextcloudError(
                status_code=response.status_code, reason=str(response.content)
            )
