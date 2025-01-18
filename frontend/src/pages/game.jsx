import React, { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { useWebSocket } from '../WebSocketContext';

export default function Game() {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [remainingTime, setRemainingTime] = useState(300); // 5 minutes in seconds
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

    useEffect(() => {
        const timer = setInterval(() => {
            setRemainingTime(prev => {
                if (prev <= 0) {
                    clearInterval(timer);
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);

        return () => clearInterval(timer);
    }, []);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!inputMessage.trim()) return;

        ws.send(JSON.stringify({
            type: 'chat',
            message: inputMessage
        }));
        setInputMessage('');
    };

    const formatTime = (seconds) => {
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${minutes}:${secs < 10 ? '0' : ''}${secs}`;
    };


    return (
        <div className="h-screen flex flex-col items-center font-sans">
            <p className='text-4xl mt-10'>Room {sessionId}</p>
            <p className='text-xl'>Time Remaining: {formatTime(remainingTime)}</p>
            {remainingTime === 0 && (
                <p className='text-lg text-red-500'>Time's up!</p>
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

                return (
                    <div
                        key={index}
                        className="flex flex-col items-start bg-gray-100 rounded-xl px-3 py-1.5 w-fit max-w-full text-wrap text-left text-pretty break-all "
                    >
                        <span className="font-bold text-blue-600">{msg.author}</span>
                        <span className=''>{parsedMessage.message}</span>
                    </div>
                );                
                                
            })}
            </div>

            {/* Message Input Form */}
            <form onSubmit={handleSubmit} className="bg-gray-200 p-4 border-2 border-gray-300 w-[600px] rounded-xl">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        placeholder="Type your message..."
                        className="flex-1 p-2 rounded-lg border"
                        disabled={remainingTime <= 0}
                    />
                    <button 
                        type="submit"
                        className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
                        disabled={remainingTime <= 0}
                    >
                        Send
                    </button>
                </div>
            </form>
        </div>
    );
}