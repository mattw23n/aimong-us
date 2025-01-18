from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
from model.player import Player
from model.message import Message

class GameSession(BaseModel):
    session_id: str
    topic: str
    players: List[Player] = []
    messages: List[Message] = []
    ai_player: Optional[Player] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
