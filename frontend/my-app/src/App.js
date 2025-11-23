import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Home from './pages/Home';
import NewsList from './pages/NewsList';
import RandomNews from './pages/RandomNews';
import TextToSpeech from './pages/TextToSpeech';
import './styles/App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/news" element={<NewsList />} />
            <Route path="/random" element={<RandomNews />} />
            <Route path="/tts" element={<TextToSpeech />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;