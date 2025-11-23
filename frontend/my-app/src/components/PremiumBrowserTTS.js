// import React, { useState, useEffect, useRef } from 'react';
// import './PremiumBrowserTTS.css';

// const PremiumBrowserTTS = ({ text, autoPlay = false, onStateChange }) => {
//     const [isPlaying, setIsPlaying] = useState(false);
//     const [isPaused, setIsPaused] = useState(false);
//     const [voices, setVoices] = useState([]);
//     const [selectedVoice, setSelectedVoice] = useState(null);
//     const [rate, setRate] = useState(1.0);
//     const [pitch, setPitch] = useState(1.0);
//     const [volume, setVolume] = useState(1.0);
//     const [isLoading, setIsLoading] = useState(false);
//     const [error, setError] = useState(null);
//     const utteranceRef = useRef(null);

//     // Load available voices
//     useEffect(() => {
//         const loadVoices = () => {
//             try {
//                 const availableVoices = window.speechSynthesis.getVoices();

//                 // Filter for high-quality English voices
//                 const premiumVoices = availableVoices.filter(voice => {
//                     return (
//                         voice.lang.includes('en') &&
//                         !voice.localService && // Cloud voices are usually better
//                         (
//                             voice.name.includes('Google') ||
//                             voice.name.includes('Microsoft') ||
//                             voice.name.includes('Alex') ||
//                             voice.name.includes('Samantha') ||
//                             voice.name.includes('Daniel') ||
//                             voice.name.includes('Karen') ||
//                             voice.name.includes('Moira') ||
//                             voice.name.includes('Tessa') ||
//                             voice.name.includes('Victoria') ||
//                             voice.name.includes('Aaron') ||
//                             voice.name.includes('Fred') ||
//                             voice.name.includes('Google US English') ||
//                             voice.name.includes('Microsoft David') ||
//                             voice.name.includes('Microsoft Zira')
//                         )
//                     );
//                 });

//                 // If no premium voices found, use any English voices
//                 const englishVoices = premiumVoices.length > 0
//                     ? premiumVoices
//                     : availableVoices.filter(voice => voice.lang.includes('en'));

//                 setVoices(englishVoices);

//                 // Auto-select the first premium voice
//                 if (englishVoices.length > 0 && !selectedVoice) {
//                     setSelectedVoice(englishVoices[0]);
//                 }

//                 setError(null);
//             } catch (err) {
//                 setError('Failed to load voices');
//                 console.error('Voice loading error:', err);
//             }
//         };

//         // Initial load
//         loadVoices();

//         // Listen for voice changes
//         if (window.speechSynthesis) {
//             window.speechSynthesis.onvoiceschanged = loadVoices;
//         }

//         return () => {
//             // Cleanup
//             if (utteranceRef.current) {
//                 window.speechSynthesis.cancel();
//             }
//             if (window.speechSynthesis) {
//                 window.speechSynthesis.onvoiceschanged = null;
//             }
//         };
//     }, []);

//     // Auto-play when text changes
//     useEffect(() => {
//         if (autoPlay && text && selectedVoice && !isPlaying) {
//             handleSpeak();
//         }
//     }, [text, autoPlay, selectedVoice]);

//     const handleSpeak = () => {
//         if (!text || !selectedVoice) {
//             setError('No text or voice selected');
//             return;
//         }

//         if (!window.speechSynthesis) {
//             setError('Text-to-speech not supported in this browser');
//             return;
//         }

//         setIsLoading(true);
//         setError(null);

//         // Cancel any current speech
//         window.speechSynthesis.cancel();

//         try {
//             const utterance = new SpeechSynthesisUtterance(text);
//             utterance.voice = selectedVoice;
//             utterance.rate = rate;
//             utterance.pitch = pitch;
//             utterance.volume = volume;

//             // Event handlers
//             utterance.onstart = () => {
//                 setIsPlaying(true);
//                 setIsPaused(false);
//                 setIsLoading(false);
//                 if (onStateChange) onStateChange('playing');
//             };

//             utterance.onend = () => {
//                 setIsPlaying(false);
//                 setIsPaused(false);
//                 if (onStateChange) onStateChange('ended');
//             };

//             utterance.onpause = () => {
//                 setIsPaused(true);
//                 if (onStateChange) onStateChange('paused');
//             };

//             utterance.onresume = () => {
//                 setIsPaused(false);
//                 if (onStateChange) onStateChange('resumed');
//             };

//             utterance.onerror = (event) => {
//                 console.error('Speech synthesis error:', event);
//                 setError(`Speech error: ${event.error}`);
//                 setIsPlaying(false);
//                 setIsLoading(false);
//                 if (onStateChange) onStateChange('error');
//             };

//             utteranceRef.current = utterance;
//             window.speechSynthesis.speak(utterance);

//         } catch (err) {
//             setError('Failed to start speech synthesis');
//             console.error('Speech synthesis error:', err);
//             setIsLoading(false);
//             if (onStateChange) onStateChange('error');
//         }
//     };

//     const handlePause = () => {
//         if (window.speechSynthesis.speaking && !window.speechSynthesis.paused) {
//             window.speechSynthesis.pause();
//         }
//     };

//     const handleResume = () => {
//         if (window.speechSynthesis.paused) {
//             window.speechSynthesis.resume();
//         }
//     };

//     const handleStop = () => {
//         window.speechSynthesis.cancel();
//         setIsPlaying(false);
//         setIsPaused(false);
//         if (onStateChange) onStateChange('stopped');
//     };

//     const getVoiceQuality = (voice) => {
//         if (voice.name.includes('Google') || voice.name.includes('Microsoft')) {
//             return '🎙️ Premium';
//         } else if (voice.localService) {
//             return '🔊 System';
//         } else {
//             return '🌐 Cloud';
//         }
//     };

//     const getVoiceInfo = (voice) => {
//         const isPremium = voice.name.includes('Google') || voice.name.includes('Microsoft');
//         const isCloud = !voice.localService;

//         if (isPremium) return { emoji: '🎙️', label: 'Premium Cloud' };
//         if (isCloud) return { emoji: '🌐', label: 'Cloud' };
//         return { emoji: '🔊', label: 'System' };
//     };

//     const formatVoiceName = (voiceName) => {
//         // Clean up voice names for better display
//         return voiceName
//             .replace('Microsoft', 'MS')
//             .replace('Google', 'Google')
//             .replace('English', 'EN')
//             .replace('United States', 'US')
//             .replace('Desktop', '')
//             .replace(/\s+/g, ' ')
//             .trim();
//     };

//     return (
//         <div className="premium-browser-tts">
//             <div className="tts-header">
//                 <h3>🎤 Premium Text-to-Speech</h3>
//                 <div className="tts-status-indicator">
//                     {isLoading && <span className="status-loading">🔄 Loading...</span>}
//                     {isPlaying && !isPaused && <span className="status-playing">🎙️ Speaking</span>}
//                     {isPaused && <span className="status-paused">⏸️ Paused</span>}
//                     {!isPlaying && !isLoading && selectedVoice && (
//                         <span className="status-ready">✅ Ready</span>
//                     )}
//                 </div>
//             </div>

//             {/* Voice Selection */}
//             <div className="voice-selection-section">
//                 <label className="section-label">Select Voice:</label>
//                 <select
//                     value={selectedVoice ? selectedVoice.name : ''}
//                     onChange={(e) => {
//                         const voice = voices.find(v => v.name === e.target.value);
//                         if (voice) setSelectedVoice(voice);
//                     }}
//                     disabled={isPlaying}
//                     className="voice-select"
//                 >
//                     {voices.length === 0 ? (
//                         <option value="">Loading voices...</option>
//                     ) : (
//                         voices.map(voice => {
//                             const voiceInfo = getVoiceInfo(voice);
//                             return (
//                                 <option key={voice.name} value={voice.name}>
//                                     {voiceInfo.emoji} {formatVoiceName(voice.name)} - {voiceInfo.label}
//                                 </option>
//                             );
//                         })
//                     )}
//                 </select>
//             </div>

//             {/* Advanced Controls */}
//             <div className="advanced-controls-section">
//                 <div className="control-group">
//                     <label className="control-label">
//                         <span className="control-icon">🎚️</span>
//                         Speed: <span className="control-value">{rate}x</span>
//                     </label>
//                     <input
//                         type="range"
//                         min="0.5"
//                         max="2"
//                         step="0.1"
//                         value={rate}
//                         onChange={(e) => setRate(parseFloat(e.target.value))}
//                         disabled={isPlaying}
//                         className="control-slider"
//                     />
//                     <div className="slider-labels">
//                         <span>0.5x</span>
//                         <span>1x</span>
//                         <span>2x</span>
//                     </div>
//                 </div>

//                 <div className="control-group">
//                     <label className="control-label">
//                         <span className="control-icon">🎵</span>
//                         Pitch: <span className="control-value">{pitch}</span>
//                     </label>
//                     <input
//                         type="range"
//                         min="0.5"
//                         max="2"
//                         step="0.1"
//                         value={pitch}
//                         onChange={(e) => setPitch(parseFloat(e.target.value))}
//                         disabled={isPlaying}
//                         className="control-slider"
//                     />
//                     <div className="slider-labels">
//                         <span>Low</span>
//                         <span>Normal</span>
//                         <span>High</span>
//                     </div>
//                 </div>

//                 <div className="control-group">
//                     <label className="control-label">
//                         <span className="control-icon">🔊</span>
//                         Volume: <span className="control-value">{Math.round(volume * 100)}%</span>
//                     </label>
//                     <input
//                         type="range"
//                         min="0"
//                         max="1"
//                         step="0.1"
//                         value={volume}
//                         onChange={(e) => setVolume(parseFloat(e.target.value))}
//                         disabled={isPlaying}
//                         className="control-slider"
//                     />
//                     <div className="slider-labels">
//                         <span>0%</span>
//                         <span>50%</span>
//                         <span>100%</span>
//                     </div>
//                 </div>
//             </div>

//             {/* Main Controls */}
//             <div className="tts-main-controls">
//                 <button
//                     onClick={handleSpeak}
//                     disabled={isLoading || !text || !selectedVoice || isPlaying}
//                     className={`play-btn ${isPlaying ? 'active' : ''}`}
//                 >
//                     {isLoading ? '🔄' : isPlaying ? '⏸️' : '▶️'}
//                     {isLoading ? ' Loading...' : isPlaying ? ' Playing' : ' Speak Now'}
//                 </button>

//                 <div className="secondary-controls">
//                     {isPlaying && (
//                         <>
//                             {isPaused ? (
//                                 <button onClick={handleResume} className="control-btn resume-btn">
//                                     ▶️ Resume
//                                 </button>
//                             ) : (
//                                 <button onClick={handlePause} className="control-btn pause-btn">
//                                     ⏸️ Pause
//                                 </button>
//                             )}
//                             <button onClick={handleStop} className="control-btn stop-btn">
//                                 ⏹️ Stop
//                             </button>
//                         </>
//                     )}
//                 </div>
//             </div>

//             {/* Error Display */}
//             {error && (
//                 <div className="error-message">
//                     ⚠️ {error}
//                 </div>
//             )}

//             {/* Voice Info */}
//             {selectedVoice && (
//                 <div className="voice-info">
//                     <div className="voice-details">
//                         <strong>Selected Voice:</strong> {formatVoiceName(selectedVoice.name)}
//                     </div>
//                     <div className="voice-details">
//                         <strong>Language:</strong> {selectedVoice.lang}
//                     </div>
//                     <div className="voice-details">
//                         <strong>Type:</strong> {getVoiceInfo(selectedVoice).emoji} {getVoiceInfo(selectedVoice).label}
//                     </div>
//                 </div>
//             )}

//             {/* Browser Support Warning */}
//             {!window.speechSynthesis && (
//                 <div className="browser-warning">
//                     ⚠️ Text-to-speech is not supported in your browser.
//                     Try using Chrome, Edge, or Safari for the best experience.
//                 </div>
//             )}

//             {voices.length === 0 && window.speechSynthesis && (
//                 <div className="voice-warning">
//                     ℹ️ No premium voices detected. Using system default voice.
//                 </div>
//             )}
//         </div>
//     );
// };

// export default PremiumBrowserTTS;