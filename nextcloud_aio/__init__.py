"""
Asynchronous client for Nextcloud.

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

#TODO
https://nextcloud-talk.readthedocs.io/en/latest/
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

    pass
