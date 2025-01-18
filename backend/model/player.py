from typing import List
from pydantic import BaseModel
from enum import Enum

class PlayerStatus(str, Enum):
    ACTIVE = "active"
    ELIMINATED = "eliminated"
    SPECTATOR = "spectator"

class Player(BaseModel):
    id: int
    name: str
    is_ai: bool = False
    status: PlayerStatus = PlayerStatus.ACTIVE

class Session:
    def __init__(self, session_id: int):
        self.id = session_id
        self.players: List[Player] = []
        self.chat_log: List[dict] = []