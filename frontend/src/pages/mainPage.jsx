import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useWebSocket } from "../WebSocketContext";

export default function MainPage() {
    const navigate = useNavigate();
    const { createConnection } = useWebSocket();
    const [portNumber, setPortNumber] = useState("");

    const handleCreateLobby = async () => {
        try {
            const response = await fetch('http://127.0.0.1:8000/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (response.ok) {
                const data = await response.json();
                const ws = createConnection(data.session_id);
                
                ws.onopen = () => {
                    navigate("/lobby", { 
                        state: { 
                            isCreator: true, 
                            sessionId: data.session_id
                        } 
                    });
                };
            }
        } catch (error) {
            console.error('Error creating lobby:', error);
        }
    };

    const handleJoinLobby = () => {
        if (!portNumber) {
            alert("Please enter a port number");
            return;
        }

        const ws = createConnection(portNumber);

        ws.onopen = () => {
            navigate("/lobby", { 
                state: { 
                    isCreator: false, 
                    sessionId: portNumber
                } 
            });
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            alert("Failed to connect to the WebSocket server. Please check the port number and try again.");
        };
    };

    return (
        <div className="font-sans max-w-4xl mx-auto mt-20">
            <p className="text-4xl">AImong Us</p>
            <p className="text-xl">A modern unofficial Turing Test</p>

            <button onClick={handleCreateLobby} className="p-4 rounded-xl bg-blue-500 text-white mt-4 hover:bg-blue-700">
                Create Lobby
            </button>

            <div className="mt-4">
                <input 
                    type="text" 
                    value={portNumber} 
                    onChange={(e) => setPortNumber(e.target.value)} 
                    placeholder="Enter port number" 
                    className="p-2 border rounded"
                />
                <button onClick={handleJoinLobby} className="p-4 rounded-xl bg-blue-500 text-white mt-4 hover:bg-blue-700 ml-2">
                    Join Lobby
                </button>
            </div>
        </div>
    );
}