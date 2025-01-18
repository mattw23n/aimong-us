from pydantic import BaseModel

class AIAgent(BaseModel):
    id: int = -1  # Unique identifier for the AI
    name: str = "AI Agent"
    # TODO: Change the prompt
    prompt: str = "You are participating in a game chat on a specific topic. Respond naturally."
    is_active: bool = True