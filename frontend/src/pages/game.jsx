import React, { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { useWebSocket } from '../WebSocketContext';

export default function Game() {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const location = useLocation();
    const { ws } = useWebSocket();
    const sessionId = location.state?.sessionId;
    const messageContainerRef = useRef(null);

    useEffect(() => {
        if (!ws) return;

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log(data)
                if (data.type === 'chat') {
                    setMessages(prev => [...prev, data]);
                }
            } catch (e) {
                console.log('Received plain text:', event.data);
            }
        };

        return () => {
            ws.onmessage = null;
        };
    }, [ws]);

    useEffect(() => {
        // Scroll to bottom when new messages arrive
        if (messageContainerRef.current) {
            messageContainerRef.current.scrollTop = messageContainerRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!inputMessage.trim()) return;

        ws.send(JSON.stringify({
            type: 'chat',
            message: inputMessage
        }));
        setInputMessage('');
    };

    return (
        <div className="h-screen flex flex-col">
            <div className="bg-gray-800 text-white p-4">
                <h1 className="text-2xl">Game Room {sessionId}</h1>
            </div>

            {/* Message Display Area */}
            <div 
                ref={messageContainerRef}
                className="flex-1 overflow-y-auto p-4 space-y-2"
            >
            {messages.map((msg, index) => {
                let parsedMessage;
                try {
                    parsedMessage = JSON.parse(msg.message);
                } catch (error) {
                    console.error('Error parsing message:', error);
                    parsedMessage = { message: msg.message };
                }

                return (
                    <div key={index} className="flex flex-col items-start bg-gray-100 rounded-xl px-3 py-1.5 w-fit">
                        <span className="font-bold text-blue-600">{msg.author}</span>
                        <span>{parsedMessage.message}</span>
                    </div>
                );
            })}
            </div>

            {/* Message Input Form */}
            <form onSubmit={handleSubmit} className="bg-gray-200 p-4">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        placeholder="Type your message..."
                        className="flex-1 p-2 rounded-lg border"
                    />
                    <button 
                        type="submit"
                        className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
                    >
                        Send
                    </button>
                </div>
            </form>
        </div>
    );
}