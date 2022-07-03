"""Asynchronous client for Nextcloud.

Reference:
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/WebDAV/index.html
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-api-overview.html
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-share-api.html
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/LoginFlow/index.html
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/RemoteWipe/index.html
https://docs.nextcloud.com/server/latest/admin_manual/configuration_user/user_auth_ldap_api.html
https://docs.nextcloud.com/server/latest/admin_manual/configuration_user/instruction_set_for_apps.html
https://docs.nextcloud.com/server/latest/admin_manual/configuration_user/instruction_set_for_users.html
https://github.com/nextcloud/groupfolders#api
https://github.com/nextcloud/notifications/blob/master/docs/ocs-endpoint-v2.md
https://github.com/nextcloud/activity/blob/master/docs/endpoint-v2.md
https://nextcloud-talk.readthedocs.io/en/latest/
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/RemoteWipe/index.html

# TODO:
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-sharee-api.html
https://nextcloud-talk.readthedocs.io/en/latest/reaction/
https://github.com/nextcloud/maps/blob/master/openapi.yml
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-user-preferences-api.html
"""

from nextcloud_aio.api.ocs import NextCloudOCSAPI
from nextcloud_aio.api.ocs.talk import NextCloudTalkAPI
from nextcloud_aio.api.ocs.users import UserManager
from nextcloud_aio.api.ocs.status import OCSStatusAPI
from nextcloud_aio.api.ocs.shares import OCSShareAPI
from nextcloud_aio.api.ocs.ldap import OCSLdapAPI
from nextcloud_aio.api.ocs.apps import AppManager
from nextcloud_aio.api.ocs.groups import GroupManager
from nextcloud_aio.api.ocs.groupfolders import GroupFolderManager
from nextcloud_aio.api.ocs.notifications import NotificationManager

from nextcloud_aio.api.dav import NextCloudDAVAPI
from nextcloud_aio.api.dav.files import FileManager

from nextcloud_aio.api.loginflow import LoginFlowV2
from nextcloud_aio.api.wipe import Wipe


class NextCloudAsync(
        NextCloudDAVAPI,
        NextCloudOCSAPI,
        OCSStatusAPI,
        OCSShareAPI,
        OCSLdapAPI,
        NextCloudTalkAPI,
        UserManager,
        GroupManager,
        AppManager,
        FileManager,
        GroupFolderManager,
        NotificationManager,
        LoginFlowV2,
        Wipe):
    """The Asynchronous Nextcloud Client.

    This project aims to provide an async-friendly python wrapper for all
    public APIs provided by the Nextcloud project.

    Currently covered:
        File Management API (except chunked uploads)
        User Management API
        Group Management API
        App Management API
        LDAP Configuration API
        Status API
        Share API
        Talk/spreed API
        Notifications API
        Login Flow v2 API
        Remote Wipe API

    To do:
        File API Chunked Uploads
        Sharee API
        Reaction API
        Maps API
        User Preferences API

    If I am missing any, please open an issue so they can be added:
    https://github.com/aaronsegura/nextcloud_aio/issues

    ### Simple usage example

        > from nextcloud_aio import NextCloudAsync
        > import httpx

        > u = 'user'
        > p = 'password'
        > e = 'https://cloud.example.com'
        > c = httpx.AsyncClient()
        > nca = NextCloudAsync(client=c, user=u, password=p, endpoint=e)
        > users = asyncio.run(nca.get_users())
        > print(users)
        ['admin', 'slippinjimmy', 'chunks', 'flipper', 'squishface']
    """

    pass
