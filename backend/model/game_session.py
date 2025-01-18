from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
from app.models.player import Player
from app.models.message import Message
from app.models.ai_agent import AIAgent

class GameSession(BaseModel):
    session_id: str
    topic: str
    players: List[Player]  # All human players
    spectators: List[Player] = []
    eliminated: List[Player] = []
    ai_agent: AIAgent
    current_round: int = 1
    votes: Dict[int, int] = {}  # voter_id -> target_id
    start_time: datetime
    end_time: datetime
    messages: List[Message] = []