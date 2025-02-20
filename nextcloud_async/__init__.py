"""Asynchronous client for Nextcloud.

Reference:
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/WebDAV/index.html
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-api-overview.html
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-share-api.html
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-status-api.html
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/LoginFlow/index.html
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/RemoteWipe/index.html
https://github.com/nextcloud/groupfolders/blob/master/openapi.json
https://docs.nextcloud.com/server/latest/admin_manual/configuration_user/user_auth_ldap_api.html
https://docs.nextcloud.com/server/latest/admin_manual/configuration_user/instruction_set_for_apps.html
https://docs.nextcloud.com/server/latest/admin_manual/configuration_user/instruction_set_for_users.html
qhttps://github.com/nextcloud/notifications/blob/master/docs/ocs-endpoint-v2.md
https://github.com/nextcloud/activity/blob/master/docs/endpoint-v2.md
https://nextcloud-talk.readthedocs.io/en/latest/
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/RemoteWipe/index.html
https://github.com/nextcloud/maps/blob/master/openapi.yml
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-sharee-api.html
https://nextcloud-talk.readthedocs.io/en/latest/poll/

# TODO:
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-share-api.html#federated-cloud-shares
https://nextcloud-talk.readthedocs.io/en/latest/reaction/
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-user-preferences-api.html
https://nextcloud.github.io/cookbook/dev/api/index
https://git.mdns.eu/nextcloud/passwords/-/wikis/Developers/Index
https://github.com/nextcloud/notes/tree/master/docs/api
https://deck.readthedocs.io/en/latest/API/
https://sabre.io/dav/building-a-caldav-client/
https://sabre.io/dav/building-a-carddav-client/
"""

from nextcloud_async.client import NextcloudClient
from nextcloud_async import api, driver

__all__ = [
    "NextcloudClient",
    "api",
    "driver"
]
