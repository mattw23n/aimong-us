from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
from model.player import Player
from model.message import Message
from model.ai_agent import AIAgent

class GameSession(BaseModel):
    session_id: str
    topic: str
    players: List[Player] = []
    messages: List[Message] = []
    ai_agent:Optional[AIAgent] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    votes: Dict[int, int] = {}  # voter_id -> target_id