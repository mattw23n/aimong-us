from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from service.session_service import SessionService

router = APIRouter()

# Create a new session on /start
@router.post("/start")
def start_session():
    session_id = SessionService.create_session()
    return {"message": "Session started", "session_id": session_id}

# WebSocket Endpoint for Group Chat and Voting
@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint to handle group chat and voting.
    """
    await websocket.accept()

    # Ensure session exists or create it
    session = SessionService.get_or_create_session(session_id)

    # Add player to the session
    player = SessionService.add_player_to_session(session, websocket)

    # Notify others about the new player
    await SessionService.broadcast_message(session.session_id, {
        "type": "player_join",
        "message": f"{player.name} has joined the session."
    })

    try:
        while True:
            # Receive and handle incoming actions
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "send_message":
                # Handle chat messages
                await SessionService.handle_message(session, player, data.get("content"))
            elif action == "vote":
                # Handle voting
                voted_id = data.get("voted_id")
                success = SessionService.cast_vote(session_id, player.id, voted_id)
                if success:
                    await SessionService.broadcast_message(session_id, {
                        "type": "vote_cast",
                        "message": f"{player.name} voted for Player {voted_id}."
                    })
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid vote. Please try again."
                    })
    except WebSocketDisconnect:
        # Handle player disconnection
        await SessionService.remove_player_from_session(session, player, websocket)

# Get the number of players in a session
@router.get("/get_players/{session_id}")
def get_player_count(session_id: str):
    """
    Retrieve the number of players in a session.
    """
    try:
        player_count = SessionService.get_player_count(session_id)
        return {"session_id": session_id, "player_count": player_count, "max_players": 5}
    except ValueError as e:
        return {"error": str(e)}

@router.post("/start_game")
async def start_game(session_id: str):
    """
    Start the game for the specified session and initiate the game timer.
    """
    try:
        # Start the game
        await SessionService.start_game_for_session(session_id)
        return {"status": "Game started successfully", "session_id": session_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
