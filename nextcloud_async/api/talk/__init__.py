"""
    https://nextcloud-talk.readthedocs.io/en/latest/global/
"""
from .conversations import Conversations, Conversation
from .participants import Participants, Participant
from .avatars import ConversationAvatars
from .chat import Chat, Message, MessageReminder, Suggestion

__all__ = [
    "Conversations",
    "Conversation",
    "Participants",
    "Participant",
    "ConversationAvatars",
    "Chat",
    "Message",
    "MessageReminder",
    "Suggestion"
    ]
