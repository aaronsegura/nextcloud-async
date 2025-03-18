import pytest
import pytest_asyncio

from nextcloud_async.api import Group, GroupsApi, User, UsersApi
from nextcloud_async.exceptions import NextcloudError

_TEST_GROUP = "PytestGroup"

_USER_DATA = {
    "user_id": "PytestUser",
    "display_name": "Pyest User Guy",
    "email": "pytestguy@example.com",
    "language": "en",
    "subadmin": [_TEST_GROUP],
    "groups": [_TEST_GROUP],
    "quota": None,
    "password": "FlibbyMcGiblets",
}


_INSTANTIATED_USER = {
    "enabled": True,
    "storageLocation": "/var/www/html/data/PytestUser",
    "id": "PytestUser",
    "lastLogin": 0,
    "backend": "Database",
    "subadmin": ["PytestGroup"],
    "quota": {"quota": "none", "used": 0},
    "manager": "",
    "email": "pytestguy@example.com",
    "additional_mail": [],
    "displayname": "Pyest User Guy",
    "display-name": "Pyest User Guy",
    "phone": "",
    "address": "",
    "website": "",
    "twitter": "",
    "fediverse": "",
    "organisation": "",
    "role": "",
    "headline": "",
    "biography": "",
    "profile_enabled": "1",
    "groups": ["PytestGroup"],
    "language": "en",
    "locale": "",
    "notify_email": None,
    "backendCapabilities": {"setDisplayName": True, "setPassword": True},
}


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def test_group(groups_api: GroupsApi):
    group = await groups_api.create(_TEST_GROUP)
    yield group
    await group.delete()


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def target_group(groups_api: GroupsApi):
    group = await groups_api.create("TargetGroup")
    yield group
    await group.delete()


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def test_user(users_api: UsersApi, test_group: Group):  # noqa: ARG001
    # test_group is not used here, but must exist to create the user
    user = await users_api.create(**_USER_DATA)
    yield user
    try:
        await user.delete()
    except NextcloudError:
        pass


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope="session")
class TestUserDataObject:
    async def test_create(self, test_user: User, test_group: Group):
        assert test_user.id == _USER_DATA["user_id"]
        assert test_user.display_name == _USER_DATA["display_name"]
        assert test_user.email == _USER_DATA["email"]
        assert test_group.id in test_user.subadmin
        assert test_group.id in test_user["groups"]
        assert test_user.quota["quota"] == "none"

    async def test_update(self, test_user: User, network_blocked: bool):
        _updated_user_data = {
            "displayname": "New Display Name",
            "email": "newemail@example.com",
        }
        await test_user.update(_updated_user_data)
        assert test_user.email == _updated_user_data["email"]
        assert test_user.display_name == _updated_user_data["displayname"]

    async def test_disable_enable(self, test_user: User):
        await test_user.disable()
        assert test_user.enabled is False
        await test_user.enable()
        assert test_user.enabled is True

    async def test_delete(self, users_api: UsersApi, test_user: User):
        _id = test_user.id
        await test_user.delete()
        assert test_user.id == "**deleted**"
        with pytest.raises(NextcloudError) as e:
            await users_api.get(_id)
        assert e.value.reason == "User does not exist"

    async def test_get_groups(self, test_user: User, test_group: Group):
        groups = await test_user.get_groups()
        assert test_group in groups

    async def test_add_to_group(self, test_user: User, target_group: Group):
        await test_user.add_to_group(target_group)
        assert target_group.id in test_user.groups
        await target_group.delete()

    async def test_remove_from_group(self, test_user: User, test_group: Group):
        assert test_group.id in test_user.groups
        await test_user.remove_from_group(test_group)
        assert test_group.id not in test_user.groups

    async def test_promotion_demotion(self, test_user: User, target_group: Group):
        await test_user.promote_to_group_subadmin(target_group)
        assert target_group.id in test_user.subadmin
        await test_user.demote_from_group_subadmin(target_group)
        assert target_group.id not in test_user.subadmin

    async def test_get_subadmin_groups(self, test_user: User, test_group: Group):
        groups = await test_user.get_subadmin_groups()
        assert test_group in groups

    async def test_dunders(self, test_user: User):
        assert "Nextcloud User" in str(test_user)
        assert test_user == test_user  # noqa: PLR0124


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope="session")
class TestUsersApi:
    async def test_get_editable_fields(self, users_api: UsersApi):
        fields = await users_api.get_editable_fields()
        assert isinstance(fields, list)

    async def test_resend_email(self, users_api: UsersApi, test_user: User):
        await users_api.resend_welcome_email(test_user.id)


#     def test_search_users(self):  # noqa: D102
#         json_response = bytes(SIMPLE_100.format(
#             f'{{"users": ["{USER}"]}}\n'), 'utf-8')
#         SEARCH = 'MUTEMATH'
#         with patch(
#                 'httpx.AsyncClient.request',
#                 new_callable=AsyncMock,
#                 return_value=httpx.Response(
#                     status_code=100,
#                     content=json_response)) as mock:
#             response = asyncio.run(self.ncc.search_users(SEARCH))
#             mock.assert_called_with(
#                 method='GET',
#                 auth=(USER, PASSWORD),
#                 url=f'{ENDPOINT}/ocs/v1.php/cloud/users?search={SEARCH}'
#                     '&limit=100&offset=0&format=json',
#                 data=None,
#                 headers={'OCS-APIRequest': 'true'})
#             assert USER in response

#     def test_get_user(self):  # noqa: D102
#         json_response = bytes(
#             '{"ocs":{"meta":{"status":"ok","statuscode":100,"message":"OK","t'
#             'otalitems":"","itemsperpage":""},"data":{"enabled":true,"storage'
#             f'Location":"\\/opt\\/nextcloud\\/\\/{USER}","id":"{USER}","lastLo'
#             'gin":1656858534000,"backend":"Database","subadmin":[],"quota":{"'
#             'free":53003714560,"used":106514002334,"total":159517716894,"rela'
#             'tive":66.77,"quota":-3},"avatarScope":"v2-federated","email":"'
#             f'{EMAIL}","emailScope":"v2-federated","additional_mail":[],"addi'
#             f'tional_mailScope":[],"displayname":"{NAME}","displaynameScope":'
#             '"v2-federated","phone":"","phoneScope":"v2-local","address":"","'
#             'addressScope":"v2-local","website":"","websiteScope":"v2-local",'
#             '"twitter":"","twitterScope":"v2-local","organisation":"","organi'
#             'sationScope":"v2-local","role":"","roleScope":"v2-local","headli'
#             'ne":"","headlineScope":"v2-local","biography":"","biographyScope'
#             '":"v2-local","profile_enabled":"1","profile_enabledScope":"v2-lo'
#             'cal","groups":["admin"],"language":"en","locale":"en","notify_em'
#             'ail":null,"backendCapabilities":{"setDisplayName":true,"setPassw'
#             'ord":true}}}}', 'utf-8')
#         with patch(
#                 'httpx.AsyncClient.request',
#                 new_callable=AsyncMock,
#                 return_value=httpx.Response(
#                     status_code=100,
#                     content=json_response)) as mock:
#             response = asyncio.run(self.ncc.get_user(USER))
#             mock.assert_called_with(
#                 method='GET',
#                 auth=(USER, PASSWORD),
#                 url=f'{ENDPOINT}/ocs/v1.php/cloud/users/{USER}?format=json',
#                 data=None,
#                 headers={'OCS-APIRequest': 'true'})
#             assert response['displayname'] == NAME \
#                 and response['id'] == USER \
#                 and response['email'] == EMAIL

#     def test_get_users(self):  # noqa: D102
#         TESTUSER = 'testuser'
#         json_response = bytes(SIMPLE_100.format(
#             f'{{"users":["{USER}","{TESTUSER}"]}}'), 'utf-8')
#         with patch(
#                 'httpx.AsyncClient.request',
#                 new_callable=AsyncMock,
#                 return_value=httpx.Response(
#                     status_code=100,
#                     content=json_response)) as mock:
#             response = asyncio.run(self.ncc.get_users())
#             mock.assert_called_with(
#                 method='GET',
#                 auth=(USER, PASSWORD),
#                 url=f'{ENDPOINT}/ocs/v1.php/cloud/users?format=json',
#                 data=None,
#                 headers={'OCS-APIRequest': 'true'})
#             assert response == [USER, TESTUSER]

#     def test_user_autocomplete(self):  # noqa: D102
#         json_response = bytes(
#             '{"ocs":{"meta":{"status":"ok","statuscode":200,"message":"OK"},"'
#             f'data":[{{"id":"{USER}","label":"{NAME}","icon":"icon-user","sou'
#             'rce":"users","status":[],"subline":"","shareWithDisplayNameUniqu'
#             f'e":"{USER}"}}]}}}}', 'utf-8')
#         SEARCH = 'dk'
#         with patch(
#                 'httpx.AsyncClient.request',
#                 new_callable=AsyncMock,
#                 return_value=httpx.Response(
#                     status_code=200,
#                     content=json_response)) as mock:
#             asyncio.run(self.ncc.user_autocomplete(
#                 SEARCH,
#                 share_types=[ShareType['user'], ShareType['group']]))
#             mock.assert_called_with(
#                 method='GET',
#                 auth=(USER, PASSWORD),
#                 url='https://cloud.example.com/ocs/v2.php/core/autocomplete/get'
#                     '?search=dk&itemType=None&itemId=None&sorter=None&shareType'
#                     's%5B%5D=0&shareTypes%5B%5D=1&limit=25&format=json',
#                 data=None,
#                 headers={'OCS-APIRequest': 'true'})

#     def test_update_user(self):  # noqa: D102
#         WEBSITE = 'website'
#         DISPLAYNAME = 'displayname'
#         with patch(
#                 'httpx.AsyncClient.request',
#                 new_callable=AsyncMock,
#                 return_value=httpx.Response(
#                     status_code=100,
#                     content=EMPTY_100)) as mock:
#             asyncio.run(self.ncc.update_user(
#                 USER, {DISPLAYNAME: NAME, WEBSITE: ENDPOINT}))
#             mock.assert_any_call(
#                 method='PUT',
#                 auth=(USER, PASSWORD),
#                 url=f'{ENDPOINT}/ocs/v1.php/cloud/users/{USER}',
#                 data={'key': DISPLAYNAME, 'value': NAME, 'format': 'json'},
#                 headers={'OCS-APIRequest': 'true'})
#             mock.assert_any_call(
#                 method='PUT',
#                 auth=(USER, PASSWORD),
#                 url=f'{ENDPOINT}/ocs/v1.php/cloud/users/{USER}',
#                 data={'key': WEBSITE, 'value': ENDPOINT, 'format': 'json'},
#                 headers={'OCS-APIRequest': 'true'})
#             assert mock.call_count == 2

#     def test_get_user_editable_fields(self):  # noqa: D102
#         FIELDS = [
#             'displayname', 'email', 'additional_mail', 'phone', 'address',
#             'website', 'twitter', 'organisation', 'role', 'headline', 'biography',
#             'profile_enabled'
#         ]
#         json_response = bytes(
#             SIMPLE_100
#             .format(
#                 '["displayname","'
#                 'email","additional_mail","phone","address","website","twitter","'
#                 'organisation","role","headline","biography","profile_enabled"]'), 'utf-8')
#         with patch(
#                 'httpx.AsyncClient.request',
#                 new_callable=AsyncMock,
#                 return_value=httpx.Response(
#                     status_code=100,
#                     content=json_response)) as mock:
#             response = asyncio.run(self.ncc.get_user_editable_fields())
#             mock.assert_called_with(
#                 method='GET',
#                 auth=(USER, PASSWORD),
#                 url=f'{ENDPOINT}/ocs/v1.php/cloud/user/fields?format=json',
#                 data=None,
#                 headers={'OCS-APIRequest': 'true'})
#             for field in FIELDS:
#                 assert field in response

#     def test_disable_user(self):  # noqa: D102
#         with patch(
#                 'httpx.AsyncClient.request',
#                 new_callable=AsyncMock,
#                 return_value=httpx.Response(
#                     status_code=100,
#                     content=EMPTY_100)) as mock:
#             asyncio.run(self.ncc.disable_user(USER))
#             mock.assert_called_with(
#                 method='PUT',
#                 auth=(USER, PASSWORD),
#                 url=f'{ENDPOINT}/ocs/v1.php/cloud/users/{USER}/disable',
#                 data={'format': 'json'},
#                 headers={'OCS-APIRequest': 'true'})

#     def test_enable_user(self):  # noqa: D102
#         with patch(
#                 'httpx.AsyncClient.request',
#                 new_callable=AsyncMock,
#                 return_value=httpx.Response(
#                     status_code=100,
#                     content=EMPTY_100)) as mock:
#             asyncio.run(self.ncc.enable_user(USER))
#             mock.assert_called_with(
#                 method='PUT',
#                 auth=(USER, PASSWORD),
#                 url=f'{ENDPOINT}/ocs/v1.php/cloud/users/{USER}/enable',
#                 data={'format': 'json'},
#                 headers={'OCS-APIRequest': 'true'})

#     def test_remove_user(self):  # noqa: D102
#         with patch(
#                 'httpx.AsyncClient.request',
#                 new_callable=AsyncMock,
#                 return_value=httpx.Response(
#                     status_code=100,
#                     content=EMPTY_100)) as mock:
#             asyncio.run(self.ncc.remove_user(user_id=USER))
#             mock.assert_called_with(
#                 method='DELETE',
#                 auth=(USER, PASSWORD),
#                 url=f'{ENDPOINT}/ocs/v1.php/cloud/users/{USER}',
#                 data={'format': 'json'},
#                 headers={'OCS-APIRequest': 'true'})

#     def test_get_self_groups(self):  # noqa: D102
#         json_response = bytes(SIMPLE_100.format('{"groups": []}'), 'utf-8')
#         with patch(
#                 'httpx.AsyncClient.request',
#                 new_callable=AsyncMock,
#                 return_value=httpx.Response(
#                     status_code=100,
#                     content=json_response)) as mock:
#             response = asyncio.run(self.ncc.get_user_groups())
#             mock.assert_called_with(
#                 method='GET',
#                 auth=(USER, PASSWORD),
#                 url=f'{ENDPOINT}/ocs/v1.php/cloud/users/{USER}/groups?format=json',
#                 data=None,
#                 headers={'OCS-APIRequest': 'true'})
#             assert response == []

#     def test_get_user_groups(self):  # noqa: D102
#         TESTUSER = 'testuser'
#         json_response = bytes(SIMPLE_100.format('{"groups": []}'), 'utf-8')
#         with patch(
#                 'httpx.AsyncClient.request',
#                 new_callable=AsyncMock,
#                 return_value=httpx.Response(
#                     status_code=100,
#                     content=json_response)) as mock:
#             response = asyncio.run(self.ncc.get_user_groups(TESTUSER))
#             mock.assert_called_with(
#                 method='GET',
#                 auth=(USER, PASSWORD),
#                 url=f'{ENDPOINT}/ocs/v1.php/cloud/users/{TESTUSER}/groups?format=json',
#                 data=None,
#                 headers={'OCS-APIRequest': 'true'})
#             assert response == []

#     def test_add_user_to_group(self):  # noqa: D102
#         GROUP = 'group'
#         with patch(
#                 'httpx.AsyncClient.request',
#                 new_callable=AsyncMock,
#                 return_value=httpx.Response(
#                     status_code=100,
#                     content=EMPTY_100)) as mock:
#             asyncio.run(self.ncc.add_user_to_group(USER, GROUP))
#             mock.assert_called_with(
#                 method='POST',
#                 auth=(USER, PASSWORD),
#                 url=f'{ENDPOINT}/ocs/v1.php/cloud/users/{USER}/groups',
#                 data={'groupid': GROUP, 'format': 'json'},
#                 headers={'OCS-APIRequest': 'true'})

#     def test_add_user_to_nonexistent_group(self):  # noqa: D102
#         GROUP = 'noexist_group'
#         with patch(
#                 'httpx.AsyncClient.request',
#                 new_callable=AsyncMock) as mock:
#             mock.side_effect = NextcloudError(status_code=102, reason='None')
#             try:
#                 asyncio.run(self.ncc.add_user_to_group(USER, GROUP))
#             except NextcloudError:
#                 pass
#             finally:
#                 mock.assert_called_with(
#                     method='POST',
#                     auth=(USER, PASSWORD),
#                     url=f'{ENDPOINT}/ocs/v1.php/cloud/users/{USER}/groups',
#                     data={'groupid': GROUP, 'format': 'json'},
#                     headers={'OCS-APIRequest': 'true'})
#                 self.assertRaises(NextcloudError)

#     def test_remove_user_from_group(self):  # noqa: D102
#         GROUP = 'group'
#         with patch(
#                 'httpx.AsyncClient.request',
#                 new_callable=AsyncMock,
#                 return_value=httpx.Response(
#                     status_code=100,
#                     content=EMPTY_100)) as mock:
#             asyncio.run(self.ncc.remove_user_from_group(USER, GROUP))
#             mock.assert_called_with(
#                 method='DELETE',
#                 auth=(USER, PASSWORD),
#                 url=f'{ENDPOINT}/ocs/v1.php/cloud/users/{USER}/groups',
#                 data={'groupid': GROUP, 'format': 'json'},
#                 headers={'OCS-APIRequest': 'true'})

#     def test_promote_user_to_subadmin(self):  # noqa: D102
#         GROUP = 'group'
#         with patch(
#                 'httpx.AsyncClient.request',
#                 new_callable=AsyncMock,
#                 return_value=httpx.Response(
#                     status_code=100,
#                     content=EMPTY_100)) as mock:
#             asyncio.run(self.ncc.promote_user_to_subadmin(USER, GROUP))
#             mock.assert_called_with(
#                 method='POST',
#                 auth=(USER, PASSWORD),
#                 url=f'{ENDPOINT}/ocs/v1.php/cloud/users/{USER}/subadmins',
#                 data={'groupid': GROUP, 'format': 'json'},
#                 headers={'OCS-APIRequest': 'true'})

#     def test_demote_user_from_subadmin(self):  # noqa: D102
#         GROUP = 'group'
#         with patch(
#                 'httpx.AsyncClient.request',
#                 new_callable=AsyncMock,
#                 return_value=httpx.Response(
#                     status_code=100,
#                     content=EMPTY_100)) as mock:
#             asyncio.run(self.ncc.demote_user_from_subadmin(USER, GROUP))
#             mock.assert_called_with(
#                 method='DELETE',
#                 auth=(USER, PASSWORD),
#                 url=f'{ENDPOINT}/ocs/v1.php/cloud/users/{USER}/subadmins',
#                 data={'groupid': GROUP, 'format': 'json'},
#                 headers={'OCS-APIRequest': 'true'})

#     def test_get_user_subadmin_groups(self):  # noqa: D102
#         TESTUSER = 'testuser'
#         json_response = EMPTY_100
#         with patch(
#                 'httpx.AsyncClient.request',
#                 new_callable=AsyncMock,
#                 return_value=httpx.Response(
#                     status_code=100,
#                     content=json_response)) as mock:
#             response = asyncio.run(self.ncc.get_user_subadmin_groups(TESTUSER))
#             mock.assert_called_with(
#                 method='GET',
#                 auth=(USER, PASSWORD),
#                 url=f'{ENDPOINT}/ocs/v1.php/cloud/users/{TESTUSER}/subadmins?format=json',
#                 data=None,
#                 headers={'OCS-APIRequest': 'true'})
#             assert response == []

#     def test_resend_welcome_email(self):  # noqa: D102
#         TESTUSER = 'testuser'
#         json_response = EMPTY_100
#         with patch(
#                 'httpx.AsyncClient.request',
#                 new_callable=AsyncMock,
#                 return_value=httpx.Response(
#                     status_code=100,
#                     content=json_response)) as mock:
#             response = asyncio.run(self.ncc.resend_welcome_email(TESTUSER))
#             mock.assert_called_with(
#                 method='POST',
#                 auth=(USER, PASSWORD),
#                 url=f'{ENDPOINT}/ocs/v1.php/cloud/users/{TESTUSER}/welcome',
#                 data={'format': 'json'},
#                 headers={'OCS-APIRequest': 'true'})
#             assert response == []
