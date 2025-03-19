from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from nextcloud_async.api.dataobject import NextcloudDataObject

if TYPE_CHECKING:
    from . import (
        BotsApi,
        BreakoutRoomsApi,
        CallsApi,
        ChatApi,
        ConversationAvatarsApi,
        ConversationsApi,
        IntegrationsApi,
        InternalSignalingApi,
        ParticipantsApi,
        PollsApi,
        WebinarsApi,
    )


@dataclass
class TalkApis:
    conversations: ConversationsApi
    chat: ChatApi
    calls: CallsApi
    bots: BotsApi
    avatars: ConversationAvatarsApi
    participants: ParticipantsApi
    integrations: IntegrationsApi
    polls: PollsApi
    breakoutrooms: BreakoutRoomsApi
    webinars: WebinarsApi
    signaling: InternalSignalingApi


@dataclass
class NextcloudTalkDataObject(NextcloudDataObject):
    apis: TalkApis
