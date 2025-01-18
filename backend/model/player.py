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
