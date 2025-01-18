from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from datetime import datetime
from model.player import Player
from model.message import Message
from model.session import GameSession
from service.session_service import SessionService

router = APIRouter()

# Create a new session on /start
@router.post("/start")
def start_session():
    session_id = SessionService.create_session()
    return {"message": "Session started", "session_id": session_id}

# WebSocket Endpoint for Group Chat
@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()

    # Ensure session exists or create it
    session = SessionService.get_or_create_session(session_id)

    # Add player to the session
    player = SessionService.add_player_to_session(session, websocket)

    # Notify others about the new player
    await SessionService.broadcast_message(session.session_id, f"{player.name} has joined the session.")

    try:
        while True:
            # Receive and handle incoming messages
            data = await websocket.receive_text()
            await SessionService.handle_message(session, player, data)
    except WebSocketDisconnect:
        # Handle player disconnection
        await SessionService.remove_player_from_session(session, player, websocket)
