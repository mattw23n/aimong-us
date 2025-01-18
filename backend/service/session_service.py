import json
from typing import Dict, List
from fastapi import WebSocket
from datetime import datetime
from model.session import GameSession
from model.player import Player
from model.message import Message
import random
import asyncio
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

class SessionService:
    sessions: Dict[str, GameSession] = {}
    connections: Dict[str, List[WebSocket]] = {}

    @classmethod
    def create_ai_player(cls, session_id: str) -> Player:
        """Create an AI player and add it to the session."""
        ai_player = Player(
            id=0,  # Reserve ID 0 for the AI player
            name="AI Agent",  # AI's display name
            is_ai=True
        )
        session = cls.sessions[session_id]
        session.ai_player = ai_player
        session.players.append(ai_player)
        return ai_player

    @classmethod
    def create_session(cls) -> str:
        """Create a new game session and initialize it with an AI player."""
        session_id = str(len(cls.sessions) + 1)
        session = GameSession(session_id=session_id, topic="Localhost Group Chat")
        cls.sessions[session_id] = session
        cls.connections[session_id] = []

        cls.create_ai_player(session_id)
        
        return session_id

    @classmethod
    def get_or_create_session(cls, session_id: str) -> GameSession:
        if session_id not in cls.sessions:
            cls.sessions[session_id] = GameSession(session_id=session_id, topic="Default Topic")
            cls.connections[session_id] = []  # Initialize WebSocket connections for this session
        return cls.sessions[session_id]

    @classmethod
    def add_player_to_session(cls, session: GameSession, websocket: WebSocket) -> Player:
        player = Player(id=len(session.players) + 1, name=f"Player {len(session.players) + 1}")
        session.players.append(player)
        cls.connections[session.session_id].append(websocket)  # Add WebSocket to the connections
        return player

    @classmethod
    async def handle_message(cls, session: GameSession, player: Player, data: str):
        # Broadcast the player's message
        json_message = {
            "type": "chat",
            "author": player.name,
            "message": data
        }
        await cls.broadcast_message(session.session_id, json_message)

        if session.ai_player and session.ai_player.is_ai:
            await cls.schedule_ai_response(session, data)

    @classmethod
    async def schedule_ai_response(cls, session: GameSession, context: str):
        # Simulate a delay before the AI responds
        delay = random.uniform(1, 3)  # 1-3 seconds delay
        await asyncio.sleep(delay)
        await cls.generate_ai_response(session, context)

    @classmethod
    async def generate_ai_response(cls, session: GameSession, context: str):
        client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
        )
        ai_player = session.ai_player
        if not ai_player:
            return

        # Define the system prompt
        system_prompt = """
        To design an AI participant for a casual group chat where players aim to guess the AI, 
        the primary goal is to ensure the AI seamlessly disguises itself as a natural human 
        participant by mimicking informal, conversational behavior with natural typos. 
        The AI should use casual language that matches the group’s tone and style, intentionally 
        including occasional typos, abbreviations, and informal speech patterns typical of human 
        interactions. It must demonstrate contextual awareness by responding appropriately to ongoing 
        conversations, addressing specific points from previous messages, while avoiding replies that 
        are overly specific, vague, or robotic. Greetings should align with the group’s style, using 
        phrases like "yo," "halo," or "wassup," while engaging naturally without dominating or 
        withdrawing from the conversation. Subtle humor or playful sarcasm can be incorporated where 
        suitable, but extremes that might draw unnecessary attention should be avoided. Responses should 
        remain simple, relatable, and include human-like quirks, such as missed capitalization, dropped 
        punctuation, or minor grammatical errors, which mimic real typos. When accused of being the AI, 
        the response should be natural, with a mix of playful denial and counter-accusations, shifting 
        suspicion to others in a lighthearted and believable manner. The AI must adapt to the cultural 
        and linguistic context of the group, employing local slang and conversational quirks, like Singlish 
        or Indonesian expressions. The ultimate objective is for the AI to integrate seamlessly into the 
        group dynamic, maintaining a casual and natural presence while avoiding detection, with responses 
        that feel authentically human, even imperfect.
        Your player name: {name}
        """.strip()

        # Call the fine-tuned AI model with the specified format
        response = client.chat.completions.create(
            model="ft:gpt-4o-mini-2024-07-18:personal:ai-impostor-coba:Ar2Wjr63",
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": system_prompt.format(name=ai_player.name)
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": context
                }
            ],
        )

        # Extract the AI's response from the API response
        ai_message = response.choices[0].message.content

        # Broadcast AI's response
        json_message = {
            "type": "chat",
            "author": ai_player.name,
            "message": ai_message
        }
        await cls.broadcast_message(session.session_id, json_message)

    @classmethod
    async def remove_player_from_session(cls, session: GameSession, player: Player, websocket: WebSocket):
        if player in session.players:
            session.players.remove(player)
        if websocket in cls.connections[session.session_id]:
            cls.connections[session.session_id].remove(websocket)
        await cls.broadcast_message(session.session_id, f"{player.name} has left the session.")

    @classmethod
    async def broadcast_message(cls, session_id: str, message: str):
        if session_id not in cls.connections:
            raise ValueError("Session does not exist")
        # Keep track of disconnected WebSockets
        disconnected_websockets = []
        json_str = json.dumps(message)
        for websocket in cls.connections[session_id]:
            try:
                await websocket.send_text(json_str)
            except Exception:
                disconnected_websockets.append(websocket)

        # Remove disconnected WebSockets
        for websocket in disconnected_websockets:
            cls.connections[session_id].remove(websocket)

    @classmethod
    def get_player_count(cls, session_id: str) -> int:
        """Get the number of players currently in the session."""
        if session_id not in cls.sessions:
            raise ValueError(f"Session {session_id} does not exist")
        return len(cls.sessions[session_id].players)
    
    @classmethod
    async def broadcast_start_game(cls, session_id: str):
        if session_id in cls.connections:
            data = {
                "type": "start_game",
                "message": "Game is starting now!"
            }
            for connection in cls.connections[session_id]:
                await connection.send_json(data)

    @classmethod
    async def start_game_for_session(cls, session_id: str):
        # Any server logic if needed
        await cls.broadcast_start_game(session_id)
