import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import UserPill from '../component/userPill';
import { useWebSocket } from '../WebSocketContext';

export default function Lobby() {
    const [users, setUsers] = useState([]);
    const [activePlayerCount, setActivePlayerCount] = useState(0);
    const [notification, setNotification] = useState('');
    const location = useLocation();
    const { ws } = useWebSocket();
    const sessionId = location.state?.sessionId;


    const navigate = useNavigate()

    useEffect(() => {
        const fetchActivePlayers = async () => {
            try {
                const response = await fetch(`http://127.0.0.1:8000/get_players/${sessionId}`);
                const data = await response.json();
                setActivePlayerCount(data.player_count);
            } catch (error) {
                console.error('Error fetching active players:', error);
            }
        };

        // Initial fetch
        fetchActivePlayers();

        // Set up interval
        const interval = setInterval(fetchActivePlayers, 5000);

        // Cleanup
        return () => clearInterval(interval);
    }, [sessionId]);

    useEffect(() => {
        if (!ws) return;

         // Send initial join message
         ws.send(JSON.stringify({
            type: 'join',
            sessionId: sessionId
        }));
    
        // WebSocket message handler
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log('Parsed JSON:', data);
    
                // Check the message type
                if (data.type === 'start_game') {
                    console.log('Received start_game message:', data.message);
                    navigate("/game", { state: { sessionId } });
                } else if (data.type === 'chat') {
                    console.log(`Chat from ${data.author}: ${data.message}`);
                    const message = JSON.parse(data.message)
                    let messageText = ''
                    if (message.type ==='join'){
                        messageText = `${data.author} has joined`
                    }
                    setNotification(messageText); // Display plain text messages as notifications
                    setTimeout(() => setNotification(''), 3000); // Clear notification after 3 seconds
                    return; // Skip further processing for plain text messages
                }
                // ... handle other types of messages ...
            } catch (error) {
                console.error('Error parsing JSON message:', error);
            }
        };
    
        return () => {
            ws.onmessage = null;
        };
    }, [ws, navigate, sessionId]);


    const anonymizeUsers = (count) => {
        return Array.from({ length: count }, (_, index) => ({
            id: index + 1,
            name: `Player ${index + 1}`
        }));
    };

    const anonymizedUsers = anonymizeUsers(activePlayerCount);

    const handleClick = async () => {
          try {
            const response = await fetch(`http://127.0.0.1:8000/start_game?session_id=${sessionId}`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
            });
            if (!response.ok) {
              console.error('Failed to start game');
            }
          } catch (error) {
            console.error('Error starting game:', error);
          }
      };


    return (
        <div className="font-sans text-center mx-auto mt-20">
            {notification && (
                <div className="fixed top-0 left-0 right-0 bg-blue-500 text-white p-4 animate-fade-out">
                    {notification}
                </div>
            )}
            <p className="text-4xl">Lobby</p>
            <div className='text-lg my-4'>
                <p>Currently hosted on  <b> Port {sessionId}</b> </p>
                <p>Active Players: <b>{activePlayerCount}</b></p>
            </div>
            

            <div className="flex flex-col items-center my-10 gap-4">
                {anonymizedUsers.length > 0 ? (
                    anonymizedUsers.map((user) => (
                        <UserPill key={user.id} user={user} />
                    ))
                ) : (
                    <p>No users in the lobby</p>
                )}
            </div>

            <div className='flex flex-col gap-y-2 items-center'>
                <button onClick={handleClick} className="p-4 w-48 rounded-xl bg-blue-500 text-white mt-4 hover:bg-blue-700">
                    Start Game
                </button>

                <button onClick={() => navigate('/')} className="p-4 w-48 rounded-xl bg-red-500 text-white mt-4 hover:bg-red-700">
                    Leave Lobby
                </button>

            </div>
            
        </div>
    );
}