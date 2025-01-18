from pydantic import BaseModel
from datetime import datetime

class Message(BaseModel):
    sender_id: int
    sender_name: str
    content: str
    timestamp: datetime
