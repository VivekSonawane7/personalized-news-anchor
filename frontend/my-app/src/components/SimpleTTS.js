// import React, { useState, useEffect, useRef, useCallback } from 'react';

// const SimpleTTS = ({ text, autoPlay = false }) => {
//   const [isPlaying, setIsPlaying] = useState(false);
//   const [isPaused, setIsPaused] = useState(false);
//   const [voice, setVoice] = useState(null);
//   const [rate, setRate] = useState(1.0);
//   const [pitch, setPitch] = useState(1.0);
//   const [volume, setVolume] = useState(1.0);
//   const [voices, setVoices] = useState([]);
//   const utteranceRef = useRef(null);

//   // Load available voices
//   const loadVoices = useCallback(() => {
//     const availableVoices = window.speechSynthesis.getVoices();
//     setVoices(availableVoices);

//     // Prefer English voices, fallback to first available
//     const englishVoice = availableVoices.find(v =>
//       v.lang.includes('en') && v.name.includes('Female')
//     ) || availableVoices.find(v => v.lang.includes('en')) || availableVoices[0];

//     if (englishVoice) {
//       setVoice(englishVoice);
//     }
//   }, []);

//   const stopSpeech = useCallback(() => {
//     window.speechSynthesis.cancel();
//     setIsPlaying(false);
//     setIsPaused(false);
//   }, []);

//   useEffect(() => {
//     loadVoices();
//     window.speechSynthesis.onvoiceschanged = loadVoices;

//     return () => {
//       window.speechSynthesis.onvoiceschanged = null;
//       stopSpeech();
//     };
//   }, [loadVoices, stopSpeech]);

//   const speakText = useCallback(() => {
//     if (!text) return;

//     stopSpeech(); // Stop any current speech

//     const utterance = new SpeechSynthesisUtterance(text);

//     if (voice) {
//       utterance.voice = voice;
//     }
//     utterance.rate = rate;
//     utterance.pitch = pitch;
//     utterance.volume = volume;

//     utterance.onstart = () => {
//       setIsPlaying(true);
//       setIsPaused(false);
//     };

//     utterance.onend = () => {
//       setIsPlaying(false);
//       setIsPaused(false);
//     };

//     utterance.onerror = (event) => {
//       console.error('Speech synthesis error:', event);
//       setIsPlaying(false);
//       setIsPaused(false);
//     };

//     window.speechSynthesis.speak(utterance);
//     utteranceRef.current = utterance;
//   }, [text, voice, rate, pitch, volume, stopSpeech]);

//   const pauseSpeech = useCallback(() => {
//     if (window.speechSynthesis.speaking && !window.speechSynthesis.paused) {
//       window.speechSynthesis.pause();
//       setIsPaused(true);
//     }
//   }, []);

//   const resumeSpeech = useCallback(() => {
//     if (window.speechSynthesis.paused) {
//       window.speechSynthesis.resume();
//       setIsPaused(false);
//     }
//   }, []);

//   // Auto-play when text changes and autoPlay is true
//   useEffect(() => {
//     if (text && autoPlay && !isPlaying && !isPaused) {
//       speakText();
//     }
//   }, [text, autoPlay, isPlaying, isPaused, speakText]);

//   const handleVoiceChange = useCallback((event) => {
//     const selectedVoice = voices.find(v => v.name === event.target.value);
//     if (selectedVoice) {
//       setVoice(selectedVoice);
//     }
//   }, [voices]);

//   if (!text) {
//     return null;
//   }

//   return (
//     <div style={{
//       background: 'white',
//       padding: '20px',
//       borderRadius: '10px',
//       boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
//       margin: '20px 0'
//     }}>
//       <h3 style={{ margin: '0 0 15px 0', color: '#333' }}>🔊 Voice Controls</h3>

//       {/* Voice Selection */}
//       <div style={{ marginBottom: '15px' }}>
//         <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
//           Voice:
//         </label>
//         <select
//           value={voice?.name || ''}
//           onChange={handleVoiceChange}
//           style={{
//             width: '100%',
//             padding: '8px',
//             borderRadius: '5px',
//             border: '1px solid #ddd'
//           }}
//         >
//           {voices.map((v) => (
//             <option key={v.name} value={v.name}>
//               {v.name} ({v.lang})
//             </option>
//           ))}
//         </select>
//       </div>

//       {/* Controls */}
//       <div style={{
//         display: 'flex',
//         gap: '10px',
//         marginBottom: '15px',
//         flexWrap: 'wrap'
//       }}>
//         <button
//           onClick={speakText}
//           disabled={isPlaying && !isPaused}
//           style={{
//             padding: '10px 15px',
//             backgroundColor: isPlaying && !isPaused ? '#28a745' : '#007bff',
//             color: 'white',
//             border: 'none',
//             borderRadius: '5px',
//             cursor: 'pointer',
//             flex: 1,
//             minWidth: '80px'
//           }}
//         >
//           {isPlaying && !isPaused ? '🔊 Playing' : '▶️ Play'}
//         </button>

//         <button
//           onClick={pauseSpeech}
//           disabled={!isPlaying || isPaused}
//           style={{
//             padding: '10px 15px',
//             backgroundColor: '#ffc107',
//             color: 'black',
//             border: 'none',
//             borderRadius: '5px',
//             cursor: 'pointer',
//             flex: 1,
//             minWidth: '80px'
//           }}
//         >
//           ⏸️ Pause
//         </button>

//         <button
//           onClick={resumeSpeech}
//           disabled={!isPaused}
//           style={{
//             padding: '10px 15px',
//             backgroundColor: '#17a2b8',
//             color: 'white',
//             border: 'none',
//             borderRadius: '5px',
//             cursor: 'pointer',
//             flex: 1,
//             minWidth: '80px'
//           }}
//         >
//           ⏯️ Resume
//         </button>

//         <button
//           onClick={stopSpeech}
//           disabled={!isPlaying}
//           style={{
//             padding: '10px 15px',
//             backgroundColor: '#dc3545',
//             color: 'white',
//             border: 'none',
//             borderRadius: '5px',
//             cursor: 'pointer',
//             flex: 1,
//             minWidth: '80px'
//           }}
//         >
//           ⏹️ Stop
//         </button>
//       </div>

//       {/* Settings */}
//       <div style={{
//         display: 'grid',
//         gridTemplateColumns: '1fr 1fr 1fr',
//         gap: '15px',
//         marginBottom: '15px'
//       }}>
//         <div>
//           <label style={{ display: 'block', marginBottom: '5px', fontSize: '12px' }}>
//             Speed: {rate.toFixed(1)}
//           </label>
//           <input
//             type="range"
//             min="0.5"
//             max="2"
//             step="0.1"
//             value={rate}
//             onChange={(e) => setRate(parseFloat(e.target.value))}
//             style={{ width: '100%' }}
//           />
//         </div>

//         <div>
//           <label style={{ display: 'block', marginBottom: '5px', fontSize: '12px' }}>
//             Pitch: {pitch.toFixed(1)}
//           </label>
//           <input
//             type="range"
//             min="0.5"
//             max="2"
//             step="0.1"
//             value={pitch}
//             onChange={(e) => setPitch(parseFloat(e.target.value))}
//             style={{ width: '100%' }}
//           />
//         </div>

//         <div>
//           <label style={{ display: 'block', marginBottom: '5px', fontSize: '12px' }}>
//             Volume: {volume.toFixed(1)}
//           </label>
//           <input
//             type="range"
//             min="0"
//             max="1"
//             step="0.1"
//             value={volume}
//             onChange={(e) => setVolume(parseFloat(e.target.value))}
//             style={{ width: '100%' }}
//           />
//         </div>
//       </div>

//       {/* Status */}
//       <div style={{
//         padding: '10px',
//         backgroundColor: '#f8f9fa',
//         borderRadius: '5px',
//         textAlign: 'center',
//         fontSize: '14px',
//         color: '#666'
//       }}>
//         {isPlaying && !isPaused && '🔊 Speaking...'}
//         {isPaused && '⏸️ Paused'}
//         {!isPlaying && !isPaused && '⏹️ Ready to play'}
//       </div>
//     </div>
//   );
// };

// export default SimpleTTS;