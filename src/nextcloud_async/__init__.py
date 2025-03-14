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
https://nextcloud-talk.readthedocs.io/en/latest/reaction/

# To do:
https://github.com/nextcloud/circles/wiki/Javascript-API-v1
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-share-api.html#federated-cloud-shares
https://docs.nextcloud.com/server/latest/developer_manual/client_apis/OCS/ocs-user-preferences-api.html
https://nextcloud.github.io/cookbook/dev/api/index
https://git.mdns.eu/nextcloud/passwords/-/wikis/Developers/Index
https://github.com/nextcloud/notes/tree/master/docs/api
https://deck.readthedocs.io/en/latest/API/
https://sabre.io/dav/building-a-caldav-client/
https://sabre.io/dav/building-a-carddav-client/
"""

import os
import logging
from logging import config as logging_config

from nextcloud_async.loggers import LOGGING_CONFIG
from nextcloud_async.client import NextcloudClient
from nextcloud_async import api


__all__ = [
    "NextcloudClient",
    "api",
]

logging_config.dictConfig(LOGGING_CONFIG)

log_level = os.getenv("NEXTCLOUD_ASYNC_LOGLEVEL", "WARNING")
my_logger = logging.getLogger("nextcloud_async")
my_logger.setLevel(log_level)
