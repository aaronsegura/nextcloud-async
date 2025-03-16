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
