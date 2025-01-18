from typing import List, Optional
from pydantic import BaseModel

class Player(BaseModel):
    id: int
    name: str
    is_ai: bool = False

class Session:
    def __init__(self, session_id: int):
        self.id = session_id
        self.players: List[Player] = []
        self.chat_log: List[dict] = []