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
https://nextcloud-talk.readthedocs.io/en/latest/poll/
"""

from nextcloud_async.api import *  # noqa: F403
