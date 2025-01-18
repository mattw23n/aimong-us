from datetime import datetime, timedelta
from typing import List, Dict, Optional
from app.models.player import Player, PlayerStatus
from app.models.game_session import GameSession
from app.models.message import Message
from app.models.ai_agent import AIAgent
import random


class GameService:
    def __init__(self):
        self.sessions: Dict[str, GameSession] = {}  # Store ongoing sessions

    def create_session(self, session_id: str, player_names: List[str], topic: str) -> GameSession:
    """
    Create a new game session with players and assign an AI.
    """
    players = [Player(id=i, name=name) for i, name in enumerate(player_names)]
    ai_agent = AIAgent()

    session = GameSession(
        session_id=session_id,
        topic=topic,
        players=players,
        spectators=[],
        eliminated=[],
        ai_agent=ai_agent,
        current_round=1,
        votes={},
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(minutes=5),
        messages=[],
    )
    self.sessions[session_id] = session
    return session

    def is_round_active(self, session_id: str) -> bool:
        """
        Check if the current round is still active.
        """
        session = self.sessions.get(session_id)
        if not session:
            return False
        return datetime.now() < session.end_time

    def start_new_round(self, session_id: str):
        """
        Start a new round with the remaining active players.
        """
        session = self.sessions.get(session_id)
        if not session:
            return False

        session.current_round += 1
        session.start_time = datetime.now()
        session.end_time = datetime.now() + timedelta(minutes=5)
        session.votes = {}
        return True

    def submit_vote(self, session_id: str, voter_id: int, target_id: int) -> bool:
        """
        Submit a player's vote for elimination.
        """
        session = self.sessions.get(session_id)
        if not session:
            return False

        voter = next((p for p in session.players if p.id == voter_id and p.status == PlayerStatus.ACTIVE), None)
        target = next((p for p in session.players if p.id == target_id and p.status == PlayerStatus.ACTIVE), None)

        if not voter or not target:
            return False

        session.votes[voter_id] = target_id
        return True

    def conclude_round(self, session_id: str) -> str:
        """
        Conclude the round by processing votes and eliminating a player.
        """
        session = self.sessions.get(session_id)
        if not session:
            return "Session not found."

        # Tally votes
        vote_counts = {}
        for voter, target_id in session.votes.items():
            vote_counts[target_id] = vote_counts.get(target_id, 0) + 1

        if not vote_counts:
            return "No votes were cast this round."

        # Find the player with the highest votes
        highest_votes = max(vote_counts.values())
        eliminated_id = next((target_id for target_id, count in vote_counts.items() if count == highest_votes), None)

        eliminated_player = next((p for p in session.players if p.id == eliminated_id), None)
        if not eliminated_player:
            return "Error processing elimination."

        # Move the player to spectators
        eliminated_player.status = PlayerStatus.ELIMINATED
        session.players.remove(eliminated_player)
        session.spectators.append(eliminated_player)
        session.eliminated.append(eliminated_player)

        # Check if the eliminated player is the AI
        if eliminated_player.is_ai:
            return "Game over! Players win by eliminating the AI."

        # Start a new round if the AI wasn't eliminated
        if len([p for p in session.players if p.status == PlayerStatus.ACTIVE]) > 1:
            self.start_new_round(session_id)
            return f"Player {eliminated_player.name} was eliminated. Moving to round {session.current_round}."
        else:
            return "Game over! Not enough players to continue."

    def get_game_state(self, session_id: str) -> Optional[dict]:
        """
        Retrieve the current state of the game session.
        """
        session = self.sessions.get(session_id)
        if not session:
            return None

        return {
            "session_id": session.session_id,
            "topic": session.topic,
            "current_round": session.current_round,
            "active_players": [p.dict() for p in session.players if p.status == PlayerStatus.ACTIVE],
            "spectators": [p.dict() for p in session.spectators],
            "eliminated": [p.dict() for p in session.eliminated],
            "time_remaining": (session.end_time - datetime.now()).total_seconds(),
        }
