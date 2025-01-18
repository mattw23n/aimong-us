from typing import List
from pydantic import BaseModel
from enum import Enum

class Player(BaseModel):
    id: int
    name: str
    is_ai: bool = False
