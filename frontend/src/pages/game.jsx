import React, { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { useWebSocket } from '../WebSocketContext';

export default function Game() {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [remainingTime, setRemainingTime] = useState(300);
    const [isVoting, setIsVoting] = useState(false); // State for voting popup
    const [vote, setVote] = useState(null); // State to track the selected vote
    const [votingResult, setVotingResult] = useState(null); // State for voting result message
    const [playerAssignments, setPlayerAssignments] = useState({}); // Mapping of sessionId to pseudonym/color
    const location = useLocation();
    const { ws } = useWebSocket();
    const sessionId = location.state?.sessionId;
    const messageContainerRef = useRef(null);

    // Predefined pseudonyms and colors
    const nameColorPairs = [
        { name: "SmartDuck", color: "red" },
        { name: "SleepyPuppy", color: "green" },
        { name: "HappyCat", color: "blue" },
        { name: "ChillPenguin", color: "yellow" },
        { name: "CarefreeSeagull", color: "purple" },
        { name: "EnergeticEagle", color: "pink" },
        { name: "WiseQuokka", color: "indigo" },
    ];

    useEffect(() => {
        if (!ws) return;

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                // Handle chat messages
                if (data.type === 'chat') {
                    setMessages((prev) => [...prev, data]);

                    // Assign pseudonym/color to new users
                    if (!playerAssignments[data.author]) {
                        assignPseudonymAndColor(data.author);
                    }
                }

                if (data.type === 'voting_result') {
                    setVotingResult(data.message); // Update voting result
                    setIsVoting(false); // Ensure voting popup is closed
                }
                

                // Handle voting result
                if (data.type === 'voting_result') {
                    setVotingResult(data.message); // Update voting result
                    setIsVoting(false); // Ensure voting popup is closed
                }
            } catch (e) {
                console.log('Received plain text:', event.data);
            }
        };

        return () => {
            ws.onmessage = null;
        };
    }, [ws, playerAssignments]);

    useEffect(() => {
        if (messageContainerRef.current) {
            messageContainerRef.current.scrollTop = messageContainerRef.current.scrollHeight;
        }
    }, [messages]);

    useEffect(() => {
        const timer = setInterval(() => {
            setRemainingTime((prev) => {
                if (prev <= 0) {
                    clearInterval(timer);
                    setIsVoting(true); // Trigger the voting popup when time is up
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);

        return () => clearInterval(timer);
    }, []);

    const assignPseudonymAndColor = (sessionId) => {
        const keys = Object.keys(playerAssignments);
        const index = keys.length % nameColorPairs.length; // Assign based on current player count
        const assignment = nameColorPairs[index];

        setPlayerAssignments((prev) => ({
            ...prev,
            [sessionId]: assignment,
        }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!inputMessage.trim()) return;
    
        ws.send(
            JSON.stringify({
                action: 'chat', // Correct key
                message: inputMessage, // Matches what the back-end expects
            })
        );
        setInputMessage('');
    };

    const handleVoteSubmit = () => {
        if (!vote) return;

        // Send the vote to the backend
        ws.send(
            JSON.stringify({
                action: 'vote',
                voted_id: vote, // The ID of the player being voted for
            })
        );

        setIsVoting(false); // Close the voting popup
    };

    const formatTime = (seconds) => {
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${minutes}:${secs < 10 ? '0' : ''}${secs}`;
    };

    return (
        <div className="h-screen flex flex-col items-center font-sans">
            <p className="text-4xl mt-10">Room {sessionId}</p>
            <p className="text-xl">Time Remaining: {formatTime(remainingTime)}</p>
            {remainingTime === 0 && (
                <p className="text-lg text-red-500">Time's up! Cast your vote!</p>
            )}

            {/* Message Display Area */}
            <div
                ref={messageContainerRef}
                className="flex-1 w-[600px] overflow-x-none max-h-[500px] overflow-y-auto p-4 space-y-2 border-2 border-gray-300 rounded-xl my-4"
            >
                {messages.map((msg, index) => {
                    let parsedMessage;
                    try {
                        parsedMessage = JSON.parse(msg.message);
                    } catch (error) {
                        console.error('Error parsing message:', error);
                        parsedMessage = { message: msg.message };
                    }

                    const player = playerAssignments[msg.author] || {
                        name: 'Unknown',
                        color: 'black',
                    };

                    return (
                        <div
                            key={index}
                            className="flex flex-col items-start bg-gray-100 rounded-xl px-3 py-1.5 w-fit max-w-full text-left"
                        >
                            <span
                                className="font-bold"
                                style={{ color: player.color }}
                            >
                                {player.name}
                            </span>
                            <span>{parsedMessage.message}</span>
                        </div>
                    );
                })}
            </div>

            {/* Message Input Form */}
            <form
                onSubmit={handleSubmit}
                className="bg-gray-200 p-4 border-2 border-gray-300 w-[600px] rounded-xl"
            >
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        placeholder="Type your message..."
                        className="flex-1 p-2 rounded-lg border"
                        disabled={remainingTime <= 0 || isVoting}
                    />
                    <button
                        type="submit"
                        className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
                        disabled={remainingTime <= 0 || isVoting}
                    >
                        Send
                    </button>
                </div>
            </form>

            {/* Voting Result Popup */}
            {votingResult && (
                <div className="absolute top-0 left-0 w-full h-full flex items-center justify-center bg-black bg-opacity-50">
                    <div className="bg-white p-6 rounded-lg shadow-lg">
                        <h2 className="text-xl font-bold mb-4">Voting Result</h2>
                        <p>{votingResult}</p>
                        <button
                            className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 mt-4"
                            onClick={() => setVotingResult(null)}
                        >
                            Close
                        </button>
                    </div>
                </div>
            )}

            {/* Voting Popup */}
            {isVoting && (
                <div className="absolute top-0 left-0 w-full h-full flex items-center justify-center bg-black bg-opacity-50">
                    <div className="bg-white p-6 rounded-lg shadow-lg">
                        <h2 className="text-xl font-bold mb-4">Cast Your Vote</h2>
                        {Object.entries(playerAssignments).map(([playerId, player], index) => (
                            <button
                                key={index}
                                className={`block w-full p-2 mb-2 rounded-lg border ${
                                    vote === playerId ? 'bg-blue-500 text-white' : 'bg-gray-100'
                                }`}
                                onClick={() => setVote(playerId)}
                            >
                                {player.name}
                            </button>
                        ))}
                        <button
                            className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600"
                            onClick={handleVoteSubmit}
                        >
                            Submit Vote
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
