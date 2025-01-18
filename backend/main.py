from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from datetime import datetime
from typing import Dict
from app.models.player import Player
from app.models.message import Message
from app.models.session import GameSession

app = FastAPI()

# Session management
sessions: Dict[str, GameSession] = {}  # Maps session IDs to GameSession objects
connections: Dict[WebSocket, Player] = {}  # Maps WebSocket connections to Players


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()

    # Ensure session exists or create it
    if session_id not in sessions:
        sessions[session_id] = GameSession(session_id=session_id, topic="Find the AI")

    current_session = sessions[session_id]

    # Add player to the session and connection mapping
    player = Player(id=len(current_session.players) + 1, name=f"Player {len(current_session.players) + 1}")
    current_session.players.append(player)
    connections[websocket] = player

    # Notify others about the new player
    await broadcast_message(current_session, f"{player.name} has joined the session.")

    try:
        while True:
            # Receive and handle incoming messages
            data = await websocket.receive_text()
            message = Message(
                sender_id=player.id,
                sender_name=player.name,
                content=data,
                timestamp=datetime.now(),
            )
            current_session.messages.append(message)
            await broadcast_message(current_session, f"{message.sender_name}: {message.content}")
    except WebSocketDisconnect:
        # Handle player disconnection
        current_session.players.remove(player)
        del connections[websocket]
        await broadcast_message(current_session, f"{player.name} has left the session.")


async def broadcast_message(session: GameSession, message: str):
    """Broadcast a message to all players in a session."""
    for websocket, player in connections.items():
        if player in session.players:
            await websocket.send_text(message)
