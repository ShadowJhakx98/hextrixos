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

// Add this JavaScript to initialize the conversation panel
function initializeConversationPanel() {
    // Add styles to document
    const styleElement = document.createElement('style');
    styleElement.textContent = styles;
    document.head.appendChild(styleElement);
    
    // Add panel HTML to body
    const panelContainer = document.createElement('div');
    panelContainer.innerHTML = panelHTML;
    document.body.appendChild(panelContainer.firstChild);
    
    // Initialize waveform bars
    const waveform = document.getElementById('waveform');
    for (let i = 0; i < 50; i++) {
        const bar = document.createElement('div');
        bar.className = 'waveform-bar';
        bar.style.height = '3px';
        waveform.appendChild(bar);
    }
    
    // Set up panel toggle functionality
    const panel = document.querySelector('.conversation-panel');
    const panelToggle = document.querySelector('.panel-toggle');
    
    panelToggle.addEventListener('click', () => {
        panel.classList.toggle('active');
    });
    
    // Load conversation history
    loadConversationHistory();
    
    // Handle sending messages
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendMessage');
    
    sendButton.addEventListener('click', () => {
        sendMessage(messageInput.value);
        messageInput.value = '';
    });
    
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendButton.click();
        }
    });
    
    // Handle media controls
    const micToggle = document.getElementById('micToggle');
    const cameraToggle = document.getElementById('cameraToggle');
    const screenShareToggle = document.getElementById('screenShareToggle');
    const videoPreview = document.getElementById('videoPreview');
    
    micToggle.addEventListener('click', toggleMicrophone);
    cameraToggle.addEventListener('click', toggleCamera);
    screenShareToggle.addEventListener('click', toggleScreenShare);
    
    // Handle other control buttons
    document.getElementById('clearConversation').addEventListener('click', clearConversation);
    document.getElementById('exportConversation').addEventListener('click', exportConversation);
    
    // Initialize audio analyzer for waveform visualization
    initAudioAnalyzer();
}

// Function to load conversation history from the server
async function loadConversationHistory() {
    try {
        const response = await fetch('/api/conversation/history');
        const data = await response.json();
        
        const historyContainer = document.getElementById('conversationHistory');
        historyContainer.innerHTML = '';
        
        if (data.conversations && data.conversations.length > 0) {
            data.conversations.forEach(item => {
                addMessageToHistory('user', item.user_message, new Date(item.timestamp));
                addMessageToHistory('ai', item.ai_response, new Date(item.timestamp));
            });
            
            // Scroll to bottom
            historyContainer.scrollTop = historyContainer.scrollHeight;
        }
    } catch (error) {
        console.error('Error loading conversation history:', error);
    }
}

// Function to add a message to the conversation history
function addMessageToHistory(role, content, timestamp = new Date()) {
    const historyContainer = document.getElementById('conversationHistory');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `conversation-item ${role === 'user' ? 'user-message' : 'ai-message'}`;
    
    const header = document.createElement('div');
    header.className = 'message-header';
    
    const sender = document.createElement('span');
    sender.textContent = role === 'user' ? 'You' : 'Hextrix AI';
    
    const time = document.createElement('span');
    time.textContent = formatTimestamp(timestamp);
    
    header.appendChild(sender);
    header.appendChild(time);
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.textContent = content;
    
    messageDiv.appendChild(header);
    messageDiv.appendChild(messageContent);
    
    historyContainer.appendChild(messageDiv);
    
    // Scroll to the new message
    historyContainer.scrollTop = historyContainer.scrollHeight;
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

// Toggle microphone functionality
let audioContext;
let audioAnalyser;
let microphone;
let isRecording = false;

async function toggleMicrophone() {
    const micToggle = document.getElementById('micToggle');
    
    if (!isRecording) {
        try {
            // Start recording
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Initialize audio context if not already created
            if (!audioContext) {
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
                audioAnalyser = audioContext.createAnalyser();
                audioAnalyser.fftSize = 256;
            }
            
            microphone = audioContext.createMediaStreamSource(stream);
            microphone.connect(audioAnalyser);
            
            isRecording = true;
            micToggle.classList.add('active');
            
            // Start visualization
            updateWaveform();
        } catch (error) {
            console.error('Error accessing microphone:', error);
            alert('Could not access the microphone. Please check permissions.');
        }
    } else {
        // Stop recording
        if (microphone) {
            microphone.disconnect();
            microphone = null;
        }
        
        isRecording = false;
        micToggle.classList.remove('active');
    }
}

// Initialize audio analyzer for waveform
function initAudioAnalyzer() {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    audioAnalyser = audioContext.createAnalyser();
    audioAnalyser.fftSize = 256;
}

// Update waveform visualization
function updateWaveform() {
    if (!isRecording) return;
    
    const bufferLength = audioAnalyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    
    audioAnalyser.getByteFrequencyData(dataArray);
    
    const bars = document.querySelectorAll('.waveform-bar');
    const step = Math.floor(bufferLength / bars.length);
    
    for (let i = 0; i < bars.length; i++) {
        const value = dataArray[i * step];
        const height = Math.max(3, value / 2); // Scale height (max 128)
        bars[i].style.height = `${height}px`;
    }
    
    requestAnimationFrame(updateWaveform);
}

// Toggle camera functionality
let cameraStream;

async function toggleCamera() {
    const cameraToggle = document.getElementById('cameraToggle');
    const videoPreview = document.getElementById('videoPreview');
    
    if (!cameraStream) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            videoPreview.srcObject = stream;
            cameraStream = stream;
            cameraToggle.classList.add('active');
        } catch (error) {
            console.error('Error accessing camera:', error);
            alert('Could not access the camera. Please check permissions.');
        }
    } else {
        // Stop camera
        cameraStream.getTracks().forEach(track => track.stop());
        videoPreview.srcObject = null;
        cameraStream = null;
        cameraToggle.classList.remove('active');
    }
}

// Toggle screen sharing functionality
let screenStream;

async function toggleScreenShare() {
    const screenShareToggle = document.getElementById('screenShareToggle');
    const videoPreview = document.getElementById('videoPreview');
    
    if (!screenStream) {
        try {
            const stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
            videoPreview.srcObject = stream;
            screenStream = stream;
            screenShareToggle.classList.add('active');
            
            // Handle stream ending (user stops sharing)
            stream.getVideoTracks()[0].onended = () => {
                videoPreview.srcObject = null;
                screenStream = null;
                screenShareToggle.classList.remove('active');
            };
        } catch (error) {
            console.error('Error sharing screen:', error);
            alert('Could not share screen. Please check permissions.');
        }
    } else {
        // Stop screen sharing
        screenStream.getTracks().forEach(track => track.stop());
        videoPreview.srcObject = null;
        screenStream = null;
        screenShareToggle.classList.remove('active');
    }
}

// Clear conversation history
function clearConversation() {
    if (confirm('Are you sure you want to clear the conversation history?')) {
        document.getElementById('conversationHistory').innerHTML = '';
        // You might want to also clear server-side history with an API call
    }
}

// Export conversation history
function exportConversation() {
    const historyContainer = document.getElementById('conversationHistory');
    let exportText = '';
    
    // Extract text from conversation items
    const items = historyContainer.querySelectorAll('.conversation-item');
    items.forEach(item => {
        const isUser = item.classList.contains('user-message');
        const sender = isUser ? 'You' : 'Hextrix AI';
        const content = item.querySelector('.message-content').textContent;
        const time = item.querySelector('.message-header span:last-child').textContent;
        
        exportText += `[${time}] ${sender}: ${content}\n\n`;
    });
    
    // Create download link
    const blob = new Blob([exportText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `hextrix-conversation-${new Date().toISOString().slice(0, 10)}.txt`;
    a.click();
    
    // Clean up
    URL.revokeObjectURL(url);
}

// Initialize the conversation panel when the page loads
document.addEventListener('DOMContentLoaded', initializeConversationPanel);