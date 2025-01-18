from typing import Dict, List
from fastapi import WebSocket
from datetime import datetime
from model.session import GameSession
from model.player import Player
from model.message import Message


class SessionService:
    sessions: Dict[str, GameSession] = {}
    connections: Dict[str, List[WebSocket]] = {}

    @classmethod
    def create_session(cls) -> str:
        session_id = str(len(cls.sessions) + 1)
        cls.sessions[session_id] = GameSession(session_id=session_id, topic="Localhost Group Chat")
        cls.connections[session_id] = []  # Initialize WebSocket connections for this session
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
        message = Message(
            sender_id=player.id,
            sender_name=player.name,
            content=data,
            timestamp=datetime.now(),
        )
        session.messages.append(message)
        await cls.broadcast_message(session.session_id, f"{message.sender_name}: {message.content}")

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
        for websocket in cls.connections[session_id]:
            try:
                await websocket.send_text(message)
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

