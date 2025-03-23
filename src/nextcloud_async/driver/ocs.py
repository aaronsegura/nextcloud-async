"""Request Wrapper for Nextcloud OCS APIs.

https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-api-overview.html
"""

import json
import logging
from typing import Any

from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver.http import NextcloudHttpDriver
from nextcloud_async.exceptions import NextcloudAsyncError
from nextcloud_async.provider import HttpClientException, HttpClientResponse

_HTTP_USER_ERROR = 400
_HTTP_SERVER_ERROR = 500

log = logging.getLogger("nextcloud_async.driver")


class NextcloudOcsDriver(NextcloudHttpDriver):
    """Nextcloud OCS Driver.

    All OCS queries must have an {'OCS-APIRequest': 'true'} header. Additionally, we
    request all data to be returned to us in json format.
    """

    def __init__(
        self,
        client: NextcloudClient,
        version: str | None = "1",
        stub: str | None = None,
    ) -> None:
        super().__init__(client)

        if stub:
            self.stub = stub
        else:
            self.stub = f"/ocs/v{version}.php"

        self.version = version

    async def request(
        self,
        method: str = "GET",
        path: str = "",
        data: dict[str, Any] | None = None,
        content: bytes | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        raw_response: bool = False,
    ) -> dict[str, Any] | list[dict[str, Any]] | bytes | HttpClientResponse:
        """Submit OCS-type query to cloud endpoint.

        Only one of json/data/content may be used.

        Args:
            method:
                HTTP Method (eg, `GET`, `POST`, etc...)

            url:
                Use a URL outside of the given endpoint. Defaults to None.

            path:
                The portion of the URL after the host. Defaults to ''.

            data:
                Data for submission.  Data for GET requests is
                translated by urlencode and tacked on to the end of the URL as arguments.
                Defaults to {}.

            content:
                Bytes to pass through as data.

            json:
                JSON-Serializabl data passthrough.

            headers:
                Headers for submission. Defaults to {}.

            raw_response:
                Return entire response object.

        Returns:
            Dict|List: Response Data

            The OCS Endpoint returns metadata about the response in addition to the data
            what was requested.  The metadata is stripped after checking for request
            success, and only the data portion of the response is returned.

        Raises:
            NextcloudRequestTimeoutError - When request times out.

        """
        headers = self._munge_headers(headers, extra={"OCS-APIRequest": "true"})
        json, data = self._munge_json_data(json, data)

        if json and method.lower() == "get":
            path = self._path_args(json, path)
            json = None

        if data and method.lower() == "get":
            path = self._path_args(data, path)
            data = None

        try:
            log.debug(f"{method} {self.client.endpoint}{self.stub}{path} {data}")

            response = await self.client.http_client.request(
                method,
                auth=self.client.auth,
                url=f"{self.client.endpoint}{self.stub}{path}",
                json=json,
                data=data,
                content=content,
                headers=headers,
            )
        except HttpClientException as e:
            log.critical(f"Caught Exception: {e}")
            raise
        else:
            log.debug(f"Response: [{response.status_code}] {response.content}")

        if raw_response:
            return response

        await self.raise_response_exception(response)
        return response.json()["ocs"]["data"]

    async def raise_response_exception(self, response: HttpClientResponse) -> None:
        """Raise an exception, if necessary.

        Args:
            response:
                Response object from server.

        Raises:
            NextcloudAsyncError: When content is unintepretable.

        """
        try:
            response_data = response.json()
        except json.JSONDecodeError as e:
            raise NextcloudAsyncError(reason=str(e))

        log.debug(f"Response Data = {response_data}")
        if response.status_code >= _HTTP_SERVER_ERROR:
            await self._raise_response_exception(response.status_code, response.text)

        ocs_meta = response_data["ocs"]["meta"]
        if ocs_meta["status"] != "ok" or ocs_meta["statuscode"] >= _HTTP_USER_ERROR:
            await self._raise_response_exception(
                ocs_meta["statuscode"], ocs_meta["message"]
            )
