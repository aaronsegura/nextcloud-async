from typing import Any, TypedDict

from . import (
    BotsApi,
    BreakoutRoomsApi,
    CallsApi,
    ChatApi,
    ConversationAvatarsApi,
    IntegrationsApi,
    InternalSignalingApi,
    ParticipantsApi,
    PollsApi,
    WebinarsApi,
)

ConversationData = dict[str, Any]
ParticipantData = dict[str, Any]
BreakoutRoomData = dict[str, Any]


class TalkApis(TypedDict):
    chat: "ChatApi"
    calls: "CallsApi"
    bots: "BotsApi"
    avatars: "ConversationAvatarsApi"
    participants: "ParticipantsApi"
    integrations: "IntegrationsApi"
    polls: "PollsApi"
    breakoutrooms: "BreakoutRoomsApi"
    webinars: "WebinarsApi"
    signaling: "InternalSignalingApi"
