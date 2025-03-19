from dataclasses import dataclass

from nextcloud_async.api.modules import NextcloudModule
from nextcloud_async.client import NextcloudClient
from nextcloud_async.driver import NextcloudTalkDriver

from .avatars import ConversationAvatarsApi
from .bots import BotsApi
from .breakout_rooms import BreakoutRoomsApi
from .calls import CallsApi
from .chat import ChatApi
from .conversations import ConversationsApi
from .integrations import IntegrationsApi
from .participants import ParticipantsApi
from .polls import PollsApi
from .signaling import InternalSignalingApi
from .webinars import WebinarsApi


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


class TalkApi(NextcloudModule):
    """Api for accessing Talk functions."""

    def __init__(
        self, talk_api: NextcloudTalkDriver, apis: TalkApis, version: str = "2"
    ) -> None:
        self.api = talk_api
        self.stub = f"/apps/spreed/api/v{version}"

        self.bots = apis.bots
        self.breakoutrooms = apis.breakoutrooms
        self.calls = apis.calls
        self.chat = apis.chat
        self.conversations = apis.conversations
        self.integrations = apis.integrations
        self.signaling = apis.signaling
        self.participants = apis.participants
        self.polls = apis.polls
        self.webinars = apis.webinars


def talk_api(client: NextcloudClient) -> TalkApi:
    """TalkApi Factory."""
    talk_api = NextcloudTalkDriver(client)
    bots = BotsApi(talk_api)
    breakoutrooms = BreakoutRoomsApi(talk_api)
    calls = CallsApi(talk_api)
    chat = ChatApi(talk_api)
    avatars = ConversationAvatarsApi(talk_api)
    signaling = InternalSignalingApi(talk_api)
    participants = ParticipantsApi(talk_api)
    polls = PollsApi(talk_api)
    webinars = WebinarsApi(talk_api)
    integrations = IntegrationsApi(talk_api)
    conversations = ConversationsApi(
        talk_api,
        avatars,
        bots,
        breakoutrooms,
        calls,
        chat,
        integrations,
        participants,
        polls,
        signaling,
        webinars,
    )

    apis = TalkApis(
        avatars=avatars,
        bots=bots,
        breakoutrooms=breakoutrooms,
        calls=calls,
        chat=chat,
        conversations=conversations,
        integrations=integrations,
        participants=participants,
        polls=polls,
        signaling=signaling,
        webinars=webinars,
    )

    return TalkApi(talk_api, apis)
