from pydantic import BaseModel
from typing import List
from app.models.player import Player
from app.models.message import Message

class GameSession(BaseModel):
    session_id: str
    topic: str
    players: List[Player] = []
    messages: List[Message] = []
    ai_player: Player = None
    start_time: datetime = None
    end_time: datetime = None
