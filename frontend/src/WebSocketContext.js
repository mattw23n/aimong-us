import React, { createContext, useContext, useState } from 'react';

const WebSocketContext = createContext(null);

export function WebSocketProvider({ children }) {
    const [ws, setWs] = useState(null);

    const createConnection = (sessionId) => {
        if (ws) {
            ws.close();
        }
        const newWs = new WebSocket(`ws://127.0.0.1:8000/ws/${sessionId}`);
        setWs(newWs);
        return newWs;
    };

    return (
        <WebSocketContext.Provider value={{ ws, createConnection }}>
            {children}
        </WebSocketContext.Provider>
    );
}

export const useWebSocket = () => useContext(WebSocketContext);