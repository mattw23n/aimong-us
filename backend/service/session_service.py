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
from datetime import timedelta

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
        """
        Decide whether the AI should respond and schedule the response.
        Prioritize accusations if the AI is mentioned.
        """
        ai_player = session.ai_player
        if not ai_player:
            return

        # Check if the AI is being accused (e.g., its name is mentioned)
        is_accused = ai_player.name.lower() in context.lower()

        if is_accused:
            # Accusation detected; AI should definitely respond
            await asyncio.sleep(random.uniform(2, 4))  # Add a natural delay
            await cls.generate_accusation_response(session, context)
            return

        # Otherwise, decide probabilistically whether the AI should respond (e.g., 70% chance)
        should_respond = random.random() < 0.7
        if not should_respond:
            return  # Skip response to avoid suspicion

        # Add a natural delay before responding
        delay = random.uniform(2, 6)  # 2 to 6 seconds delay
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
        """
        Removes a player from the session and disconnects the WebSocket.
        """
        if player in session.players:
            session.players.remove(player)

        # Handle missing session ID in cls.connections
        if session.session_id not in cls.connections:
            print(f"Session ID {session.session_id} not found in connections. Skipping removal.")
            return

        if websocket in cls.connections[session.session_id]:
            cls.connections[session.session_id].remove(websocket)

        # Broadcast the disconnection
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
        """
        Mark the session as active and start the game timer.
        """
        session = cls.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found.")

        # Broadcast that the game is starting
        start_message = {"type": "start_game", "message": "The game has started!"}
        await cls.broadcast_message(session_id, start_message)

        # Start the game timer
        session.start_time = datetime.now()
        session.end_time = session.start_time + timedelta(minutes=5)
        asyncio.create_task(cls.start_game_timer(session_id))


    @classmethod
    async def start_game_timer(cls, session_id: str):
        """
        Starts the 5-minute timer for a session and triggers voting at the end.
        """
        session = cls.sessions.get(session_id)
        if not session:
            return

        # Wait for 5 minutes (300 seconds)
        await asyncio.sleep(300)

        # Trigger the voting phase
        await cls.initiate_voting(session_id)

    @classmethod
    def cast_vote(cls, session_id: str, voter_id: int, voted_id: int) -> bool:
        """
        Registers a vote from one player to another.

        Args:
            session_id (str): The ID of the game session.
            voter_id (int): The ID of the player casting the vote.
            voted_id (int): The ID of the player being voted for.

        Returns:
            bool: True if the vote is valid and successfully cast, False otherwise.
        """
        # Retrieve the session
        session = cls.sessions.get(session_id)
        if not session:
            return False

        # Validate voter and target
        voter = next((p for p in session.players if p.id == voter_id), None)
        target = next((p for p in session.players if p.id == voted_id), None)

        # Ensure both voter and target are valid and not eliminated
        if not voter or not target or voter in session.eliminated or target in session.eliminated:
            return False

        # Register the vote
        session.votes[voter_id] = voted_id
        return True

    @classmethod
    async def initiate_voting(cls, session_id: str):
        """
        Initiates the voting process for a session.
        """
        # Retrieve the session using session_id
        session = cls.sessions.get(session_id)
        if not session:
            await cls.broadcast_message(session_id, {"type": "error", "message": "Session not found."})
            return

        # Broadcast voting start
        voting_start_message = {
            "type": "voting_start",
            "message": "Time is up! Cast your votes for who you think the AI is."
        }
        await cls.broadcast_message(session_id, voting_start_message)

        # Allow time for voting
        await asyncio.sleep(15)  # Adjust duration as needed

        # Tally votes
        vote_counts = {}
        for target_id in session.votes.values():
            vote_counts[target_id] = vote_counts.get(target_id, 0) + 1

        # Broadcast voting results
        vote_results = {player_id: count for player_id, count in vote_counts.items()}
        await cls.broadcast_message(session_id, {
            "type": "voting_result",
            "message": f"Voting has concluded. Results: {json.dumps(vote_results)}"
        })

        if not vote_counts:
            await cls.broadcast_message(session_id, {"type": "voting_result", "message": "No votes cast. Game will now end."})
            await cls.end_session(session_id)
            return

        # Determine the player with the most votes
        highest_votes = max(vote_counts.values())
        eliminated_id = next((target_id for target_id, count in vote_counts.items() if count == highest_votes), None)

        # Handle elimination
        eliminated_player = next((p for p in session.players if p.id == eliminated_id), None)
        if eliminated_player:
            session.players.remove(eliminated_player)
            session.eliminated.append(eliminated_player)  # Add to eliminated list

            # Broadcast elimination
            elimination_message = {
                "type": "elimination",
                "message": f"Player {eliminated_player.name} has been eliminated."
            }
            await cls.broadcast_message(session_id, elimination_message)

            # Check if the eliminated player is the AI
            if eliminated_player.is_ai:
                await cls.broadcast_message(session_id, {"type": "game_over", "message": "Game Over! The players win!"})
            else:
                await cls.broadcast_message(session_id, {"type": "game_over", "message": "Game Over! The players failed to eliminate the AI."})

            # End the session
            await cls.end_session(session_id)
        else:
            await cls.broadcast_message(session_id, {"type": "error", "message": "Error determining elimination. Game will now end."})
            await cls.end_session(session_id)

    @classmethod
    async def end_session(cls, session_id: str):
        """
        Ends the session, notifying all players and closing the connections.
        """
        session = cls.sessions.get(session_id)
        if not session:
            print(f"Session {session_id} not found during cleanup.")
            return

        # Notify players that the game has ended
        await cls.broadcast_message(session_id, {"type": "game_over", "message": "The game has ended."})

        # Clean up session and connections
        cls.sessions.pop(session_id, None)
        cls.connections.pop(session_id, None)
        print(f"Session {session_id} successfully cleaned up.")

@classmethod
async def initiate_voting(cls, session_id: str):
    """
    Initiates the voting process for a session.
    """
    # Retrieve the session using session_id
    session = cls.sessions.get(session_id)
    if not session:
        await cls.broadcast_message(session_id, {"type": "error", "message": "Session not found."})
        return

    # Broadcast voting start
    voting_start_message = {
        "type": "voting_start",
        "message": "Time is up! Cast your votes for who you think the AI is."
    }
    await cls.broadcast_message(session_id, voting_start_message)

    # Allow time for voting
    await asyncio.sleep(15)  # Adjust duration as needed

    # Tally votes
    vote_counts = {}
    for target_id in session.votes.values():
        vote_counts[target_id] = vote_counts.get(target_id, 0) + 1

    if not vote_counts:
        await cls.broadcast_message(session_id, {"type": "voting_result", "message": "No votes cast. Game will now end."})
        await cls.end_session(session_id)
        return

    # Determine the player with the most votes
    highest_votes = max(vote_counts.values())
    most_voted_id = next((target_id for target_id, count in vote_counts.items() if count == highest_votes), None)

    # Find the player's name
    most_voted_player = next((p.name for p in session.players if p.id == most_voted_id), "Unknown")

    # Broadcast the voting results
    voting_result_message = {
        "type": "voting_result",
        "message": f"The player with the most votes is {most_voted_player} with {highest_votes} vote(s)."
    }
    await cls.broadcast_message(session_id, voting_result_message)

    # Handle elimination
    eliminated_player = next((p for p in session.players if p.id == most_voted_id), None)
    if eliminated_player:
        session.players.remove(eliminated_player)
        session.eliminated.append(eliminated_player)

        # Broadcast elimination
        elimination_message = {
            "type": "elimination",
            "message": f"Player {eliminated_player.name} has been eliminated."
        }
        await cls.broadcast_message(session_id, elimination_message)

        # Check if the eliminated player is the AI
        if eliminated_player.is_ai:
            await cls.broadcast_message(session_id, {"type": "game_over", "message": "Game Over! The players win!"})
        else:
            await cls.broadcast_message(session_id, {"type": "game_over", "message": "Game Over! The players failed to eliminate the AI."})

        # End the session
        await cls.end_session(session_id)
    else:
        await cls.broadcast_message(session_id, {"type": "error", "message": "Error determining elimination. Game will now end."})
        await cls.end_session(session_id)

