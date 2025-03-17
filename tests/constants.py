import json
import os

from nextcloud_async.version import VERSION

NEXTCLOUD_VERSION = os.environ.get("PYTEST_NEXTCLOUD_VERSION", "30")
USER = os.environ.get("PYTEST_NEXTCLOUD_USER", "admin")
PASSWORD = os.environ.get("PYTEST_NEXTCLOUD_PASSWORD", "admin")
ENDPOINT = os.environ.get("PYTEST_NEXTCLOUD_ENDPOINT", "http://localhost:8181")
APP_TOKEN = os.environ.get("PYTEST_NEXTCLOUD_APP_TOKEN", "[app token]")

REMOTE_TEST_DIR = "/.nextcloud-async-pytest"
USER_AGENT = f"nextcloud-async-pytest/{VERSION}"
REQUEST_HEADERS = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate",
    "connection": "keep-alive",
    "ocs-apirequest": True,
    "user-agent": USER_AGENT,
}

EMPTY_RESPONSE = b"[]"

OCS_EMPTY_200 = (
    b'{"ocs": {"meta": {"status": "ok", "statuscode": 200, "message": "OK"}, "data": []}}'
)

OCS_EXCEPTION_RESPONSE = (
    b'{"ocs": {'
    b'"meta": {"status": "failure", "statuscode": {status_code}, "message": "Excepted"}, '
    b'"data": []}}'
)

CAPABILITIES_RESPONSE = bytes(
    json.dumps(
        {
            "ocs": {
                "meta": {"status": "ok", "statuscode": 200, "message": "OK"},
                "data": {
                    "version": {
                        "major": 30,
                        "minor": 0,
                        "micro": 6,
                        "string": "30.0.6",
                        "edition": "",
                        "extendedSupport": False,
                    },
                    "capabilities": {
                        "core": {
                            "pollinterval": 60,
                            "webdav-root": "remote.php/webdav",
                            "reference-api": True,
                            "reference-regex": "(\\s|\\n|^)(https?:\\/\\/)([-A-Z0-9+_.]+(?::[0-9]+)?(?:\\/[-A-Z0-9+&@#%?=~|!:,.;()]*)*)(\\s|\\n|$)",
                            "mod-rewrite-working": True,
                        },
                        "bruteforce": {"delay": 0, "allow-listed": False},
                        "files": {
                            "$comment": '"blacklisted_files" is deprecated as of Nextcloud 30, use "forbidden_filenames" instead',
                            "blacklisted_files": [".htaccess"],
                            "forbidden_filenames": [".htaccess"],
                            "forbidden_filename_basenames": [],
                            "forbidden_filename_characters": ["\\", "/"],
                            "forbidden_filename_extensions": [".filepart", ".part"],
                            "bigfilechunking": True,
                            "directEditing": {
                                "url": "http://localhost:8181/ocs/v2.php/apps/files/api/v1/directEditing",
                                "etag": "c748e8fc588b54fc5af38c4481a19d20",
                                "supportsFileId": True,
                            },
                            "comments": True,
                            "undelete": True,
                            "versioning": True,
                            "version_labeling": True,
                            "version_deletion": True,
                        },
                        "spreed": {
                            "features": [
                                "audio",
                                "video",
                                "chat-v2",
                                "conversation-v4",
                                "guest-signaling",
                                "empty-group-room",
                                "guest-display-names",
                                "multi-room-users",
                                "favorites",
                                "last-room-activity",
                                "no-ping",
                                "system-messages",
                                "delete-messages",
                                "mention-flag",
                                "in-call-flags",
                                "conversation-call-flags",
                                "notification-levels",
                                "invite-groups-and-mails",
                                "locked-one-to-one-rooms",
                                "read-only-rooms",
                                "listable-rooms",
                                "chat-read-marker",
                                "chat-unread",
                                "webinary-lobby",
                                "start-call-flag",
                                "chat-replies",
                                "circles-support",
                                "force-mute",
                                "sip-support",
                                "sip-support-nopin",
                                "chat-read-status",
                                "phonebook-search",
                                "raise-hand",
                                "room-description",
                                "rich-object-sharing",
                                "temp-user-avatar-api",
                                "geo-location-sharing",
                                "voice-message-sharing",
                                "signaling-v3",
                                "publishing-permissions",
                                "clear-history",
                                "direct-mention-flag",
                                "notification-calls",
                                "conversation-permissions",
                                "rich-object-list-media",
                                "rich-object-delete",
                                "unified-search",
                                "chat-permission",
                                "silent-send",
                                "silent-call",
                                "send-call-notification",
                                "talk-polls",
                                "breakout-rooms-v1",
                                "recording-v1",
                                "avatar",
                                "chat-get-context",
                                "single-conversation-status",
                                "chat-keep-notifications",
                                "typing-privacy",
                                "remind-me-later",
                                "bots-v1",
                                "markdown-messages",
                                "media-caption",
                                "session-state",
                                "note-to-self",
                                "recording-consent",
                                "sip-support-dialout",
                                "delete-messages-unlimited",
                                "edit-messages",
                                "silent-send-state",
                                "chat-read-last",
                                "federation-v1",
                                "federation-v2",
                                "ban-v1",
                                "chat-reference-id",
                                "mention-permissions",
                                "edit-messages-note-to-self",
                                "archived-conversations-v2",
                                "talk-polls-drafts",
                                "download-call-participants",
                                "email-csv-import",
                                "call-notification-state-api",
                                "reactions",
                            ],
                            "features-local": [
                                "favorites",
                                "chat-read-status",
                                "listable-rooms",
                                "phonebook-search",
                                "temp-user-avatar-api",
                                "unified-search",
                                "avatar",
                                "remind-me-later",
                                "note-to-self",
                                "archived-conversations-v2",
                                "chat-summary-api",
                                "call-notification-state-api",
                            ],
                            "config": {
                                "attachments": {"allowed": True, "folder": "/Talk"},
                                "call": {
                                    "enabled": True,
                                    "breakout-rooms": True,
                                    "recording": False,
                                    "recording-consent": 0,
                                    "supported-reactions": [
                                        "\u2764\ufe0f",
                                        "\ud83c\udf89",
                                        "\ud83d\udc4f",
                                        "\ud83d\udc4b",
                                        "\ud83d\udc4d",
                                        "\ud83d\udc4e",
                                        "\ud83d\udd25",
                                        "\ud83d\ude02",
                                        "\ud83e\udd29",
                                        "\ud83e\udd14",
                                        "\ud83d\ude32",
                                        "\ud83d\ude25",
                                    ],
                                    "can-upload-background": True,
                                    "sip-enabled": False,
                                    "sip-dialout-enabled": False,
                                    "can-enable-sip": True,
                                    "start-without-media": False,
                                    "max-duration": 0,
                                    "blur-virtual-background": False,
                                    "predefined-backgrounds": [
                                        "1_office.jpg",
                                        "2_home.jpg",
                                        "3_abstract.jpg",
                                        "4_beach.jpg",
                                        "5_park.jpg",
                                        "6_theater.jpg",
                                        "7_library.jpg",
                                        "8_space_station.jpg",
                                    ],
                                },
                                "chat": {
                                    "max-length": 32000,
                                    "read-privacy": 0,
                                    "has-translation-providers": False,
                                    "typing-privacy": 0,
                                    "summary-threshold": 100,
                                },
                                "conversations": {"can-create": True},
                                "federation": {
                                    "enabled": False,
                                    "incoming-enabled": False,
                                    "outgoing-enabled": False,
                                    "only-trusted-servers": True,
                                },
                                "previews": {"max-gif-size": 3145728},
                                "signaling": {
                                    "session-ping-limit": 200,
                                    "hello-v2-token-key": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEIV5osi53Bc0WoIxR3xk7zKdn9JtY\nG/Z/rDdqElfgVsjJt+UMQSuR2UbeKy4sEbB7phQE+CVXactaoT+YrNVCcw==\n-----END PUBLIC KEY-----\n",
                                },
                            },
                            "config-local": {
                                "attachments": ["allowed", "folder"],
                                "call": [
                                    "predefined-backgrounds",
                                    "can-upload-background",
                                    "start-without-media",
                                    "blur-virtual-background",
                                ],
                                "chat": [
                                    "read-privacy",
                                    "has-translation-providers",
                                    "typing-privacy",
                                    "summary-threshold",
                                ],
                                "conversations": ["can-create"],
                                "federation": [
                                    "enabled",
                                    "incoming-enabled",
                                    "outgoing-enabled",
                                    "only-trusted-servers",
                                ],
                                "previews": ["max-gif-size"],
                                "signaling": ["session-ping-limit", "hello-v2-token-key"],
                            },
                            "version": "20.1.5",
                        },
                        "activity": {
                            "apiv2": [
                                "filters",
                                "filters-api",
                                "previews",
                                "rich-strings",
                            ]
                        },
                        "app_api": {
                            "loglevel": 2,
                            "version": "4.0.6",
                            "text_processing": {
                                "task_types": [
                                    "free_prompt",
                                    "headline",
                                    "summary",
                                    "topics",
                                ]
                            },
                        },
                        "circles": {
                            "version": "30.0.0",
                            "status": {"globalScale": False},
                            "settings": {
                                "frontendEnabled": True,
                                "allowedCircles": 262143,
                                "allowedUserTypes": 31,
                                "membersLimit": -1,
                            },
                            "circle": {
                                "constants": {
                                    "flags": {
                                        "1": "Single",
                                        "2": "Personal",
                                        "4": "System",
                                        "8": "Visible",
                                        "16": "Open",
                                        "32": "Invite",
                                        "64": "Join request",
                                        "128": "Friends",
                                        "256": "Password protected",
                                        "512": "No Owner",
                                        "1024": "Hidden",
                                        "2048": "Backend",
                                        "4096": "Local",
                                        "8192": "Root",
                                        "16384": "Team invite",
                                        "32768": "Federated",
                                        "65536": "Mount point",
                                    },
                                    "source": {
                                        "core": {
                                            "1": "Nextcloud Account",
                                            "2": "Nextcloud Group",
                                            "4": "Email address",
                                            "8": "Contact",
                                            "16": "Circle",
                                            "10000": "Nextcloud App",
                                        },
                                        "extra": {
                                            "10001": "CircleApp",
                                            "10002": "Admin Command Line",
                                        },
                                    },
                                },
                                "config": {
                                    "coreFlags": [1, 2, 4],
                                    "systemFlags": [512, 1024, 2048],
                                },
                            },
                            "member": {
                                "constants": {
                                    "level": {
                                        "1": "Member",
                                        "4": "Moderator",
                                        "8": "Admin",
                                        "9": "Owner",
                                    }
                                },
                                "type": {
                                    "0": "single",
                                    "1": "user",
                                    "2": "group",
                                    "4": "mail",
                                    "8": "contact",
                                    "16": "circle",
                                    "10000": "app",
                                },
                            },
                            "teamResourceProviders": ["files"],
                        },
                        "ocm": {
                            "enabled": True,
                            "apiVersion": "1.0-proposal1",
                            "endPoint": "http://localhost:8181/ocm",
                            "resourceTypes": [
                                {
                                    "name": "file",
                                    "shareTypes": ["user", "group"],
                                    "protocols": {"webdav": "/public.php/webdav/"},
                                }
                            ],
                        },
                        "dav": {
                            "chunking": "1.0",
                            "bulkupload": "1.0",
                            "absence-supported": True,
                            "absence-replacement": True,
                        },
                        "downloadlimit": {"enabled": True},
                        "files_sharing": {
                            "api_enabled": True,
                            "public": {
                                "enabled": True,
                                "password": {
                                    "enforced": False,
                                    "askForOptionalPassword": False,
                                },
                                "expire_date": {"enabled": False},
                                "multiple_links": True,
                                "expire_date_internal": {"enabled": False},
                                "expire_date_remote": {"enabled": False},
                                "send_mail": False,
                                "upload": True,
                                "upload_files_drop": True,
                            },
                            "resharing": True,
                            "user": {
                                "send_mail": False,
                                "expire_date": {"enabled": True},
                            },
                            "group_sharing": True,
                            "group": {"enabled": True, "expire_date": {"enabled": True}},
                            "default_permissions": 31,
                            "federation": {
                                "outgoing": True,
                                "incoming": True,
                                "expire_date": {"enabled": True},
                                "expire_date_supported": {"enabled": True},
                            },
                            "sharee": {
                                "query_lookup_default": False,
                                "always_show_unique": True,
                            },
                            "sharebymail": {
                                "enabled": True,
                                "send_password_by_mail": True,
                                "upload_files_drop": {"enabled": True},
                                "password": {"enabled": True, "enforced": False},
                                "expire_date": {"enabled": True, "enforced": False},
                            },
                        },
                        "groupfolders": {
                            "appVersion": "18.1.1",
                            "hasGroupFolders": False,
                        },
                        "notifications": {
                            "ocs-endpoints": [
                                "list",
                                "get",
                                "delete",
                                "delete-all",
                                "icons",
                                "rich-strings",
                                "action-web",
                                "user-status",
                                "exists",
                            ],
                            "push": ["devices", "object-data", "delete"],
                            "admin-notifications": ["ocs", "cli"],
                        },
                        "password_policy": {
                            "minLength": 10,
                            "enforceNonCommonPassword": True,
                            "enforceNumericCharacters": False,
                            "enforceSpecialCharacters": False,
                            "enforceUpperLowerCase": False,
                            "api": {
                                "generate": "http://localhost:8181/ocs/v2.php/apps/password_policy/api/v1/generate",
                                "validate": "http://localhost:8181/ocs/v2.php/apps/password_policy/api/v1/validate",
                            },
                        },
                        "provisioning_api": {
                            "version": "1.20.0",
                            "AccountPropertyScopesVersion": 2,
                            "AccountPropertyScopesFederatedEnabled": True,
                            "AccountPropertyScopesPublishedEnabled": True,
                        },
                        "systemtags": {"enabled": True},
                        "theming": {
                            "name": "Nextcloud",
                            "url": "https://nextcloud.com",
                            "slogan": "a safe home for all your data",
                            "color": "#00679e",
                            "color-text": "#ffffff",
                            "color-element": "#00679e",
                            "color-element-bright": "#00679e",
                            "color-element-dark": "#00679e",
                            "logo": "http://localhost:8181/core/img/logo/logo.svg?v=0",
                            "background": "http://localhost:8181/apps/theming/img/background/jenna-kim-the-globe.webp",
                            "background-text": "#ffffff",
                            "background-plain": False,
                            "background-default": True,
                            "logoheader": "http://localhost:8181/core/img/logo/logo.svg?v=0",
                            "favicon": "http://localhost:8181/core/img/logo/logo.svg?v=0",
                        },
                        "user_status": {
                            "enabled": True,
                            "restore": True,
                            "supports_emoji": True,
                        },
                        "weather_status": {"enabled": True},
                    },
                },
            }
        }
    ),
    "utf-8",
)
