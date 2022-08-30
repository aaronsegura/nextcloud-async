"""Asynchronous client for Nextcloud.

Reference:
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/WebDAV/index.html
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-api-overview.html
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-share-api.html
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-status-api.html
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
https://github.com/nextcloud/maps/blob/master/openapi.yml

# TODO:
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-share-api.html#federated-cloud-shares
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-sharee-api.html
https://nextcloud-talk.readthedocs.io/en/latest/reaction/
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-user-preferences-api.html
https://github.com/nextcloud/cookbook/blob/0360f7184b0dee58a6dc1ec6068d40685756d1e0/docs/dev/api/0.0.4/openapi-cookbook.yaml
https://git.mdns.eu/nextcloud/passwords/-/wikis/Developers/Index
https://github.com/nextcloud/notes/tree/master/docs/api
https://deck.readthedocs.io/en/latest/API/
https://sabre.io/dav/building-a-caldav-client/
https://sabre.io/dav/building-a-carddav-client/
"""

from nextcloud_async.api.ocs import NextCloudOCSAPI
from nextcloud_async.api.ocs.talk import NextCloudTalkAPI
from nextcloud_async.api.ocs.users import UserManager
from nextcloud_async.api.ocs.status import OCSStatusAPI
from nextcloud_async.api.ocs.shares import OCSShareAPI
from nextcloud_async.api.ocs.ldap import OCSLdapAPI
from nextcloud_async.api.ocs.apps import AppManager
from nextcloud_async.api.ocs.groups import GroupManager
from nextcloud_async.api.ocs.groupfolders import GroupFolderManager
from nextcloud_async.api.ocs.notifications import NotificationManager

from nextcloud_async.api.dav import NextCloudDAVAPI
from nextcloud_async.api.dav.files import FileManager

from nextcloud_async.api.loginflow import LoginFlowV2
from nextcloud_async.api.wipe import Wipe
from nextcloud_async.api.maps import Maps


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
        Wipe,
        Maps):
    """The Asynchronous Nextcloud Client.

    This project aims to provide an async-friendly python wrapper for all
    public APIs provided by the Nextcloud project.

    Currently covered:
        File Management API
        User Management API
        Group Management API
        App Management API
        LDAP Configuration API
        Status API
        Share API (except Federated shares)
        Talk/spreed API
        Notifications API
        Login Flow v2 API
        Remote Wipe API
        Maps API

    To do:
        Sharee API
        Reaction API
        User Preferences API
        Federated Shares API
        Cookbook API
        Passwords API
        Notes API
        Deck API
        Contacts API (CardDAV)
        Calendar API (CalDAV)
        Tasks API (CalDAV)

    Please open an issue if I am missing any APIs so they can be added:
    https://github.com/aaronsegura/nextcloud_async/issues

    ### Simple usage example

        > from nextcloud_async import NextCloudAsync
        > import httpx
        > import asyncio

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
