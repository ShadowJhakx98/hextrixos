// Add these styles to your HTML file
const styles = `
.conversation-panel {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 0;
    background-color: rgba(0, 10, 20, 0.85);
    backdrop-filter: blur(10px);
    transition: height 0.3s ease-in-out;
    z-index: 1000;
    display: flex;
    flex-direction: column;
    border-top: 1px solid rgba(0, 255, 255, 0.3);
    box-shadow: 0 -5px 15px rgba(0, 0, 0, 0.5);
    overflow: hidden;
}

.conversation-panel.active {
    height: 70vh;
}

.panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 20px;
    border-bottom: 1px solid rgba(0, 255, 255, 0.2);
}

.panel-title {
    color: #0ff;
    font-size: 1.2rem;
    font-weight: bold;
}

.panel-toggle {
    width: 40px;
    height: 5px;
    background-color: rgba(0, 255, 255, 0.5);
    border-radius: 5px;
    margin: 0 auto;
    cursor: pointer;
    transition: all 0.3s;
}

.panel-toggle:hover {
    background-color: rgba(0, 255, 255, 0.8);
    width: 50px;
}

.panel-content {
    display: flex;
    flex: 1;
    overflow: hidden;
}

.conversation-history {
    flex: 2;
    overflow-y: auto;
    padding: 15px;
    border-right: 1px solid rgba(0, 255, 255, 0.2);
}

.media-section {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 15px;
}

.video-container {
    flex: 1;
    background-color: rgba(0, 0, 0, 0.3);
    border-radius: 10px;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}

.audio-visualizer {
    height: 100px;
    background-color: rgba(0, 0, 0, 0.3);
    border-radius: 10px;
    position: relative;
    overflow: hidden;
}

.waveform {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 100%;
    padding: 0 10px;
}

.waveform-bar {
    width: 3px;
    background-color: #0ff;
    border-radius: 3px;
    transition: height 0.1s ease;
}

.conversation-item {
    margin-bottom: 15px;
    padding: 10px;
    border-radius: 8px;
    animation: fadeIn 0.3s ease-in-out;
}

.user-message {
    background-color: rgba(45, 50, 80, 0.5);
    border-left: 3px solid #9370DB;
}

.ai-message {
    background-color: rgba(20, 40, 60, 0.5);
    border-left: 3px solid #0ff;
}

.message-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px;
    font-size: 0.8rem;
    color: rgba(255, 255, 255, 0.7);
}

.message-content {
    color: white;
    line-height: 1.4;
}

.input-container {
    display: flex;
    padding: 15px;
    border-top: 1px solid rgba(0, 255, 255, 0.2);
}

.message-input {
    flex: 1;
    background-color: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(0, 255, 255, 0.3);
    border-radius: 5px;
    color: white;
    padding: 10px;
    margin-right: 10px;
}

.send-button {
    background-color: rgba(0, 255, 255, 0.3);
    color: white;
    border: none;
    border-radius: 5px;
    padding: 0 15px;
    cursor: pointer;
    transition: background-color 0.3s;
}

.send-button:hover {
    background-color: rgba(0, 255, 255, 0.5);
}

.control-buttons {
    display: flex;
    justify-content: space-between;
    padding: 0 15px 15px;
}

.control-button {
    background-color: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(0, 255, 255, 0.3);
    color: white;
    border-radius: 5px;
    padding: 8px 15px;
    cursor: pointer;
    transition: all 0.3s;
}

.control-button:hover {
    background-color: rgba(0, 255, 255, 0.2);
}

.control-button.active {
    background-color: rgba(0, 255, 255, 0.3);
    border-color: rgba(0, 255, 255, 0.8);
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Scrollbar styling */
.conversation-history::-webkit-scrollbar {
    width: 5px;
}

.conversation-history::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.2);
}

.conversation-history::-webkit-scrollbar-thumb {
    background-color: rgba(0, 255, 255, 0.3);
    border-radius: 20px;
}
`;

// Add this to your HTML body
const panelHTML = `
<div class="conversation-panel">
    <div class="panel-toggle-container">
        <div class="panel-toggle"></div>
    </div>
    <div class="panel-header">
        <div class="panel-title">Hextrix AI Conversation</div>
        <div>
            <button class="control-button" id="clearConversation">Clear</button>
            <button class="control-button" id="exportConversation">Export</button>
        </div>
    </div>
    <div class="panel-content">
        <div class="conversation-history" id="conversationHistory">
            <!-- Conversation messages will be populated here -->
        </div>
        <div class="media-section">
            <div class="video-container" id="videoContainer">
                <video id="videoPreview" autoplay muted style="max-width: 100%; max-height: 100%;"></video>
            </div>
            <div class="audio-visualizer">
                <div class="waveform" id="waveform">
                    <!-- Audio waveform bars will be generated here -->
                </div>
            </div>
            <div class="control-buttons">
                <button class="control-button" id="micToggle">Microphone</button>
                <button class="control-button" id="cameraToggle">Camera</button>
                <button class="control-button" id="screenShareToggle">Screen</button>
            </div>
        </div>
    </div>
    <div class="input-container">
        <textarea class="message-input" id="messageInput" placeholder="Type your message here..."></textarea>
        <button class="send-button" id="sendMessage">Send</button>
    </div>
</div>
`;

// Conversation Panel Integration
document.addEventListener('DOMContentLoaded', function() {
    // Create a script element for the conversation panel
    const conversationPanelScript = document.createElement('script');
    conversationPanelScript.src = 'conversation-panel.js';
    document.head.appendChild(conversationPanelScript);
    
    // Add event listener for the chat toggle button
    const chatToggleButton = document.getElementById('chatToggleButton');
    if (!chatToggleButton) {
        // If the button doesn't exist, create it
        const button = document.createElement('div');
        button.className = 'chat-toggle-button';
        button.id = 'chatToggleButton';
        button.innerHTML = 'Chat';
        document.body.appendChild(button);
        
        // Add click event listener
        button.addEventListener('click', function() {
            const panel = document.querySelector('.conversation-panel');
            if (panel) {
                panel.classList.toggle('active');
                button.classList.toggle('active');
                
                // If opening, load conversation history
                if (panel.classList.contains('active')) {
                    fetch('/api/conversation/history')
                        .then(response => response.json())
                        .then(data => {
                            const conversationHistory = document.getElementById('conversationHistory');
                            if (conversationHistory && data.conversations) {
                                conversationHistory.innerHTML = ''; // Clear existing messages
                                data.conversations.forEach(item => {
                                    addMessageToHistory('user', item.user_message, new Date(item.timestamp));
                                    addMessageToHistory('ai', item.ai_response, new Date(item.timestamp));
                                });
                                conversationHistory.scrollTop = conversationHistory.scrollHeight;
                            }
                        })
                        .catch(error => console.error('Error loading conversation history:', error));
                }
            }
        });
    }
});

// Variable to track if speech is enabled
let isSpeechEnabled = true;
let useServerTTS = true; // Default to using Cloudflare TTS

// Speech synthesis function using Cloudflare TTS API
async function speakCloudflareResponse(text) {
    try {
        if (!isSpeechEnabled) return false;
        
        const response = await fetch('/api/text-to-speech', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                voice: 'female' // Or get from user preference
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            console.error('TTS error:', data.error);
            // Fall back to browser TTS
            return speakBrowserResponse(text);
        }
        
        // Play the audio
        const audio = new Audio(data.audio);
        
        // Add event listeners for debugging
        audio.onplay = () => console.log('TTS audio playback started');
        audio.onended = () => console.log('TTS audio playback ended');
        audio.onerror = (e) => console.error('TTS audio playback error:', e);
        
        // Play the audio
        audio.play();
        return true;
    } catch (error) {
        console.error('Error with Cloudflare TTS:', error);
        // Fall back to browser TTS
        return speakBrowserResponse(text);
    }
}

// Browser-based TTS as fallback
function speakBrowserResponse(text) {
    // Check if browser supports speech synthesis and if speech is enabled
    if (!isSpeechEnabled) return false;
    
    if ('speechSynthesis' in window) {
        // Create a new speech synthesis utterance
        const utterance = new SpeechSynthesisUtterance(text);
        
        // Optional settings
        utterance.lang = 'en-US';
        utterance.volume = 1.0; // 0 to 1
        utterance.rate = 1.0;   // 0.1 to 10
        utterance.pitch = 1.0;  // 0 to 2
        
        // Get available voices and set a preferred one
        const voices = window.speechSynthesis.getVoices();
        // Try to find a female voice
        const femaleVoice = voices.find(voice => 
            voice.name.includes('Female') || 
            voice.name.includes('woman') || 
            voice.name.includes('girl'));
        
        if (femaleVoice) {
            utterance.voice = femaleVoice;
        }
        
        // Speak the response
        window.speechSynthesis.speak(utterance);
        
        return true;
    } else {
        console.error('Speech synthesis not supported in this browser');
        return false;
    }
}

// Wrapper function to choose the appropriate TTS method
function speakResponse(text) {
    if (useServerTTS) {
        return speakCloudflareResponse(text);
    } else {
        return speakBrowserResponse(text);
    }
}

// Function to add a message to the conversation history
function addMessageToHistory(role, content, timestamp = new Date()) {
    const historyContainer = document.getElementById('conversationHistory');
    if (!historyContainer) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `conversation-item ${role === 'user' ? 'user-message' : 'ai-message'}`;
    
    const header = document.createElement('div');
    header.className = 'message-header';
    
    const sender = document.createElement('span');
    sender.textContent = role === 'user' ? 'You' : 'Hextrix AI'; // ✓ Identity fixed
    
    const time = document.createElement('span');
    time.textContent = formatTimestamp(timestamp);
    
    header.appendChild(sender);
    header.appendChild(time);
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.textContent = content; // Display text message
    
    messageDiv.appendChild(header);
    messageDiv.appendChild(messageContent);
    
    historyContainer.appendChild(messageDiv);
    
    // Scroll to the new message
    historyContainer.scrollTop = historyContainer.scrollHeight;
    
    // Make sure the panel is visible when new messages arrive
    const panel = document.querySelector('.conversation-panel');
    const toggleButton = document.getElementById('chatToggleButton');
    
    // Only auto-open the panel when AI responds (not for user messages)
    if (role === 'ai' && !panel.classList.contains('active')) {
        panel.classList.add('active');
        if (toggleButton) toggleButton.classList.add('active');
    }
    
    // Speak the response if it's from the AI
    if (role === 'ai') {
        speakResponse(content); // Speak the response
    }
}

// Function to send a message to the server
async function sendMessage(message) {
    if (!message.trim()) return;
    
    // Add user message to history immediately
    addMessageToHistory('user', message);
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                model: document.getElementById('model-type')?.value || 'llama'
            })
        });
        
        const data = await response.json();
        
        // Add AI response to history
        if (data.response) {
            addMessageToHistory('ai', data.response);
        }
    } catch (error) {
        console.error('Error sending message:', error);
        addMessageToHistory('ai', 'Sorry, I encountered an error processing your request.');
    }
}

// Helper function to format timestamps
function formatTimestamp(date) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// Initialize the conversation panel when the page loads
function integrateConversationPanel() {
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendMessage');
    const conversationHistory = document.getElementById('conversationHistory');
    
    if (!messageInput || !sendButton || !conversationHistory) {
        console.error('Conversation panel elements not found. Make sure conversation-panel.js is loaded first.');
        return;
    }
    
    // Connect to main chat system
    sendButton.addEventListener('click', function() {
        const message = messageInput.value.trim();
        if (!message) return;
        
        // Send message
        sendMessage(message);
        
        // Clear input
        messageInput.value = '';
    });
    
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendButton.click();
        }
    });
    
    // Add speech toggle button to the UI
    const controlButtons = document.querySelector('.control-buttons');
    if (controlButtons) {
        // Add speech toggle button if it doesn't exist
        if (!document.getElementById('speechToggle')) {
            const speechToggle = document.createElement('button');
            speechToggle.className = 'control-button';
            speechToggle.id = 'speechToggle';
            speechToggle.innerHTML = '🔊 Speech';
            speechToggle.classList.toggle('active', isSpeechEnabled);
            controlButtons.appendChild(speechToggle);
            
            // Add speech toggle functionality
            speechToggle.addEventListener('click', () => {
                isSpeechEnabled = !isSpeechEnabled;
                speechToggle.innerHTML = isSpeechEnabled ? '🔊 Speech' : '🔇 Muted';
                speechToggle.classList.toggle('active', isSpeechEnabled);
                
                // If turning off, cancel any ongoing speech
                if (!isSpeechEnabled) {
                    if (window.speechSynthesis) {
                        window.speechSynthesis.cancel();
                    }
                }
            });
        }
    }
}

// Call this after conversation-panel.js is loaded
setTimeout(integrateConversationPanel, 1000);
