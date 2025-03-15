"""Request Wrapper for Nextcloud OCS APIs.

https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-api-overview.html
"""

import json
import logging
from typing import Any, Optional

import httpx

from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudCapabilities, NextcloudHttpApi
from nextcloud_async.exceptions import NextcloudAsyncError, NextcloudRequestTimeoutError

_HTTP_USER_ERROR = 400
_HTTP_SERVER_ERROR = 500

log = logging.getLogger("nextcloud_async.driver")


class NextcloudOcsApi(NextcloudHttpApi):
    """Nextcloud OCS API.

    All OCS queries must have an {'OCS-APIRequest': 'true'} header. Additionally, we
    request all data to be returned to us in json format.
    """

    def __init__(
        self,
        client: NextcloudClient,
        ocs_version: Optional[str] = "1",
        ocs_stub: Optional[str] = None,
    ) -> None:
        if ocs_stub:
            self.stub = ocs_stub
        else:
            self.stub = f"/ocs/v{ocs_version}.php"

        self.ocs_version = ocs_version
        self.capabilities_api = NextcloudCapabilities(client)

        super().__init__(client)

    async def request(
        self,
        method: str = "GET",
        path: str = "",
        data: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Submit OCS-type query to cloud endpoint.

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

            headers:
                Headers for submission. Defaults to {}.

        Returns:
            Dict|List: Response Data

            The OCS Endpoint returns metadata about the response in addition to the data
            what was requested.  The metadata is stripped after checking for request
            success, and only the data portion of the response is returned.

        Raises:
            NextcloudException - when invalid response from server
        """
        headers = self._munge_headers(headers)
        data = self._munge_data(data)

        if method.lower() == "get":
            path = self._munge_path_data(data, path)
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
            log.debug(f"Response: [{response.status_code}] {response.json()}")
        except httpx.ReadTimeout:
            log.warning("Request timed out.")
            raise NextcloudRequestTimeoutError()

        await self.raise_response_exception(response)
        return response.json()["ocs"]["data"]

    def _munge_headers(self, headers: dict[str, Any] | None) -> dict[str, Any]:
        if headers:
            headers["OCS-APIRequest"] = "true"
            headers["User-Agent"] = self.client.user_agent
        else:
            headers = {"OCS-APIRequest": "true", "User-Agent": self.client.user_agent}

        if self.client.request_headers:
            headers.update(self.client.request_headers)

        return headers

    def _munge_data(self, data: dict[str, Any] | None) -> dict[str, Any]:
        if data:
            data.update({"format": "json"})
        else:
            data = {"format": "json"}
        return data

    async def raise_response_exception(self, response: httpx.Response):
        try:
            response_content = json.loads(response.content.decode("utf-8"))
        except json.JSONDecodeError:
            raise NextcloudError(status_code=500, reason="Error decoding JSON response.")

        if response.status_code >= 500:
            raise NextcloudError(
                status_code=response.status_code, reason=response_content
            )
        else:
            ocs_meta = response_content["ocs"]["meta"]
        if response.status_code >= 300:
            await self._raise_response_exception(
                status_code=response.status_code, reason=ocs_meta["message"]
            )
        elif ocs_meta["status"] != "ok":
            await self._raise_response_exception(
                status_code=ocs_meta["statuscode"], reason=ocs_meta["message"]
            )
            raise NextcloudError(ocs_meta["statuscode"], reason=ocs_meta["message"])

    # TODO: Move this to another module

    # async def get_file_guest_link(self, file_id: int) -> str:
    #     """Generate a generic sharable link for a file.

    #     Link expires in 8 hours.

    #     https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-api-overview.html#direct-download

    #     Args
    #         file_id (int): File ID to generate link for

    #     Returns
    #         str: Link to file

    #     Raises
    #         NextcloudNotFound - file not found

    #     """

    #     result = await self.request(
    #         method='POST',
    #         path=r'/ocs/v2.php/apps/dav/api/v1/direct',
    #         data={'fileId': file_id})

    #     return result['url']

    # # TODO: Move this to another module
    # async def get_activity(
    #         self,
    #         since: Optional[int] = 0,
    #         object_id: Optional[str] = None,
    #         object_type: Optional[str] = None,
    #         sort: Optional[str] = 'desc',
    #         limit: Optional[int] = 50) -> dict[str, Any]:
    #     """Get Recent activity for the current user.

    #     Args
    #         since (int optional): Only return ativity since activity with given ID. Defaults
    #         to 0.

    #         object_id (str optional): object_id filter. Defaults to None.

    #         object_type (str optional): object_type filter. Defaults to None.

    #         sort (str optional): Sort order; either `asc` or `desc`. Defaults to 'desc'.

    #         limit (int optional): How many results per request. Defaults to 50.

    #     Raises
    #         NextcloudException: When given invalid argument combination

    #     Returns
    #         Tuple(dict, dict): activity results and headers

    #     Raises
    #         NextcloudException - when Activities isn't installed.

    #     """
    #     await self.get_capabilities('activity.apiv2')

    #     data: dict[str, Any] = {}
    #     filter = ''
    #     if object_id and object_type:
    #         filter = '/filter'
    #         data.update({
    #             'object_type': object_type,
    #             'object_id': object_id})
    #     elif object_id or object_type:
    #         raise NextcloudException(
    #             403,
    #             'filter_object_type and filter_object are both required.')

    #     data.update({
    #         'limit': limit,
    #         'sort': sort,
    #         'since': since})

    #     response = await self.request(
    #         method='GET',
    #         path=f'/ocs/v2.php/apps/activity/api/v2/activity{filter}',
    #         data=data,
    #         return_full_response=True)

    #     return response
