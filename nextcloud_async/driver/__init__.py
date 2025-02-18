from .api import NextcloudHttpApi, NextcloudModule, NextcloudCapabilities
from .base import NextcloudBaseApi
from .ocs import NextcloudOcsApi
from .dav import NextcloudDavApi
from .talk import NextcloudTalkApi

__all__ = [
    "NextcloudHttpApi",
    "NextcloudModule",
    "NextcloudCapabilities",
    "NextcloudBaseApi",
    "NextcloudOcsApi",
    "NextcloudDavApi",
    "NextcloudTalkApi"
]
