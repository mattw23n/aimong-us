import logo from './logo.svg';
import './App.css';
import MainPage from './pages/mainPage';
import { Route, Routes } from 'react-router-dom';
import Lobby from './pages/lobby';
import { WebSocketProvider } from './WebSocketContext';
import Game from './pages/game';


function App() {
  return (
    <WebSocketProvider>
    <div className="App">
      <nav>

      </nav>
      <main className="container mx-auto p-4">
          <Routes>
            <Route path="/" element={<MainPage />} />
            <Route path="/lobby" element={<Lobby />} />
            <Route path="/game" element={<Game />} />
          </Routes>
        </main>
    </div>
    </WebSocketProvider>
  );
}

export default App;
