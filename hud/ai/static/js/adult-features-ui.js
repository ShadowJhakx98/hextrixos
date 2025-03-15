// adult-features-ui.js
/**
 * Adult Features UI Component
 * 
 * Implements UI components for adult features in the Hextrix AI system,
 * including safety verification, gender recognition, 3D measurement,
 * activity tracking, erotic roleplay, and JOI.
 */

// Add these styles to your CSS
const adultFeaturesStyles = `
.adult-features-container {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.85);
    backdrop-filter: blur(10px);
    z-index: 2000;
    overflow-y: auto;
    color: #fff;
    font-family: Arial, sans-serif;
}

.adult-features-container.active {
    display: block;
}

.adult-features-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    border-bottom: 1px solid rgba(0, 255, 255, 0.3);
}

.adult-features-title {
    font-size: 1.8rem;
    color: #0ff;
}

.adult-features-close {
    background: rgba(255, 0, 0, 0.3);
    color: white;
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    cursor: pointer;
    transition: background 0.3s;
}

.adult-features-close:hover {
    background: rgba(255, 0, 0, 0.5);
}

.adult-features-nav {
    display: flex;
    padding: 10px 20px;
    border-bottom: 1px solid rgba(0, 255, 255, 0.2);
    overflow-x: auto;
    white-space: nowrap;
}

.adult-features-nav-item {
    padding: 10px 15px;
    margin-right: 10px;
    background: rgba(0, 255, 255, 0.1);
    border-radius: 5px;
    cursor: pointer;
    transition: background 0.3s;
}

.adult-features-nav-item:hover {
    background: rgba(0, 255, 255, 0.2);
}

.adult-features-nav-item.active {
    background: rgba(0, 255, 255, 0.3);
    font-weight: bold;
}

.adult-features-content {
    padding: 20px;
}

.adult-features-section {
    display: none;
    padding: 10px;
    background: rgba(0, 0, 0, 0.4);
    border-radius: 10px;
    margin-bottom: 20px;
}

.adult-features-section.active {
    display: block;
}

.adult-features-warning {
    background: rgba(255, 0, 0, 0.2);
    border-left: 4px solid #ff3333;
    padding: 15px;
    margin-bottom: 20px;
    border-radius: 4px;
}

.adult-features-button {
    background: rgba(0, 255, 255, 0.2);
    color: white;
    border: 1px solid rgba(0, 255, 255, 0.4);
    padding: 10px 15px;
    border-radius: 5px;
    cursor: pointer;
    margin-right: 10px;
    margin-bottom: 10px;
    transition: background 0.3s;
}

.adult-features-button:hover {
    background: rgba(0, 255, 255, 0.3);
}

.adult-features-button.primary {
    background: rgba(0, 150, 255, 0.3);
    border-color: rgba(0, 150, 255, 0.5);
}

.adult-features-button.primary:hover {
    background: rgba(0, 150, 255, 0.4);
}

.adult-features-button.danger {
    background: rgba(255, 0, 0, 0.3);
    border-color: rgba(255, 0, 0, 0.5);
}

.adult-features-button.danger:hover {
    background: rgba(255, 0, 0, 0.4);
}

.adult-features-input {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(0, 255, 255, 0.3);
    color: white;
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 10px;
    width: 100%;
}

.adult-features-textarea {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(0, 255, 255, 0.3);
    color: white;
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 10px;
    width: 100%;
    min-height: 100px;
    resize: vertical;
}

.adult-features-select {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(0, 255, 255, 0.3);
    color: white;
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 10px;
    width: 100%;
}

.adult-features-card {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(0, 255, 255, 0.2);
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 15px;
}

.adult-features-card-title {
    color: #0ff;
    font-size: 1.2rem;
    margin-bottom: 10px;
    border-bottom: 1px solid rgba(0, 255, 255, 0.2);
    padding-bottom: 5px;
}

.adult-features-form-group {
    margin-bottom: 15px;
}

.adult-features-label {
    display: block;
    margin-bottom: 5px;
    color: rgba(255, 255, 255, 0.8);
}

.adult-features-checkbox {
    margin-right: 10px;
}

.adult-features-checkbox-label {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
}

.adult-features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 15px;
    margin-top: 15px;
}

.adult-features-progress {
    width: 100%;
    height: 20px;
    background: rgba(0, 0, 0, 0.3);
    border-radius: 10px;
    overflow: hidden;
    margin-bottom: 10px;
}

.adult-features-progress-bar {
    height: 100%;
    background: linear-gradient(to right, rgba(0, 255, 255, 0.3), rgba(0, 255, 255, 0.6));
    transition: width 0.3s ease;
}

.adult-features-session-messages {
    max-height: 300px;
    overflow-y: auto;
    border: 1px solid rgba(0, 255, 255, 0.2);
    border-radius: 5px;
    padding: 10px;
    background: rgba(0, 0, 0, 0.2);
    margin-bottom: 15px;
}

.adult-features-message {
    margin-bottom: 10px;
    padding: 10px;
    border-radius: 5px;
}

.adult-features-message-user {
    background: rgba(128, 0, 255, 0.2);
    border-left: 3px solid rgba(128, 0, 255, 0.5);
    text-align: right;
}

.adult-features-message-ai {
    background: rgba(0, 255, 255, 0.2);
    border-left: 3px solid rgba(0, 255, 255, 0.5);
}

.adult-features-message-system {
    background: rgba(255, 255, 0, 0.1);
    border-left: 3px solid rgba(255, 255, 0, 0.5);
    font-style: italic;
}

.adult-features-video-container {
    width: 100%;
    max-width: 480px;
    height: 360px;
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(0, 255, 255, 0.3);
    border-radius: 5px;
    margin-bottom: 15px;
    position: relative;
    overflow: hidden;
}

.adult-features-video {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.adult-features-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: white;
}

.adult-features-measurement-result {
    position: absolute;
    bottom: 10px;
    left: 10px;
    right: 10px;
    background: rgba(0, 0, 0, 0.7);
    padding: 10px;
    border-radius: 5px;
    color: #0ff;
    font-weight: bold;
}

.adult-features-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin-bottom: 10px;
}

.adult-features-badge {
    background: rgba(0, 255, 255, 0.2);
    color: white;
    padding: 5px 10px;
    border-radius: 20px;
    font-size: 0.8rem;
}

.adult-features-badge.primary {
    background: rgba(0, 150, 255, 0.3);
}

.adult-features-badge.success {
    background: rgba(0, 255, 0, 0.3);
}

.adult-features-badge.warning {
    background: rgba(255, 255, 0, 0.3);
}

.adult-features-badge.danger {
    background: rgba(255, 0, 0, 0.3);
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}

.adult-features-pulse {
    animation: pulse 1.5s infinite;
}

/* Safety styles */
.adult-features-verification-box {
    border: 2px dashed rgba(0, 255, 255, 0.5);
    padding: 20px;
    text-align: center;
    border-radius: 10px;
    margin-bottom: 20px;
}

.adult-features-consent-toggle {
    display: flex;
    align-items: center;
    margin-bottom: 15px;
}

.adult-features-toggle {
    position: relative;
    display: inline-block;
    width: 60px;
    height: 30px;
    margin-right: 10px;
}

.adult-features-toggle input {
    opacity: 0;
    width: 0;
    height: 0;
}

.adult-features-toggle-slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.3);
    transition: .4s;
    border-radius: 30px;
}

.adult-features-toggle-slider:before {
    position: absolute;
    content: "";
    height: 22px;
    width: 22px;
    left: 4px;
    bottom: 4px;
    background-color: white;
    transition: .4s;
    border-radius: 50%;
}

.adult-features-toggle input:checked + .adult-features-toggle-slider {
    background-color: rgba(0, 255, 255, 0.5);
}

.adult-features-toggle input:checked + .adult-features-toggle-slider:before {
    transform: translateX(30px);
}
`;

// Add the styles to the document
function injectStyles() {
    const styleElement = document.createElement('style');
    styleElement.textContent = adultFeaturesStyles;
    document.head.appendChild(styleElement);
}

// Main UI component
class AdultFeaturesUI {
    constructor() {
        this.container = null;
        this.currentSection = null;
        this.isInitialized = false;
        this.videoStream = null;
        this.isVerified = false;
        this.hasConsent = {};
        this.activeRoleplaySession = null;
        this.activeJOISession = null;
        this.safeWord = null;
        this.measurementCalibrated = false;
        
        // Feature availability flags
        this.featuresAvailable = {
            genderRecognition: true,
            measurement3D: true,
            activityTracking: true,
            eroticRoleplay: true,
            joi: true
        };
    }
    
    // Initialize the UI
    initialize() {
        if (this.isInitialized) return;
        
        // Inject styles
        injectStyles();
        
        // Create container
        this.container = document.createElement('div');
        this.container.className = 'adult-features-container';
        document.body.appendChild(this.container);
        
        // Create UI structure
        this.createUIStructure();
        
        // Attach event listeners
        this.attachEventListeners();
        
        // Check verification status
        this.checkVerificationStatus();
        
        this.isInitialized = true;
        
        console.log('Adult Features UI initialized');
    }
    
    // Create the UI structure
    createUIStructure() {
        this.container.innerHTML = `
            <div class="adult-features-header">
                <div class="adult-features-title">Hextrix AI Adult Features</div>
                <button class="adult-features-close" id="adult-features-close">✕</button>
            </div>
            
            <div class="adult-features-nav">
                <div class="adult-features-nav-item active" data-section="safety">Safety</div>
                <div class="adult-features-nav-item" data-section="gender-recognition">Gender Recognition</div>
                <div class="adult-features-nav-item" data-section="measurement">3D Measurement</div>
                <div class="adult-features-nav-item" data-section="activity-tracking">Activity Tracking</div>
                <div class="adult-features-nav-item" data-section="erotic-roleplay">Erotic Roleplay</div>
                <div class="adult-features-nav-item" data-section="joi">JOI</div>
            </div>
            
            <div class="adult-features-content">
                <!-- Safety Section -->
                <div class="adult-features-section active" id="section-safety">
                    <div class="adult-features-warning">
                        <strong>Important:</strong> Adult features require age verification and explicit consent. Your privacy and safety are our top priorities.
                    </div>
                    
                    <div class="adult-features-card">
                        <div class="adult-features-card-title">Age Verification</div>
                        <div class="adult-features-verification-box" id="verification-box">
                            <p>Age verification required to access adult features</p>
                            <button class="adult-features-button primary" id="verify-age-btn">Verify Age</button>
                        </div>
                        <div id="verification-status"></div>
                    </div>
                    
                    <div class="adult-features-card">
                        <div class="adult-features-card-title">Consent Settings</div>
                        <div class="adult-features-consent-toggle">
                            <label class="adult-features-toggle">
                                <input type="checkbox" id="consent-gender-recognition">
                                <span class="adult-features-toggle-slider"></span>
                            </label>
                            <span>Gender Recognition</span>
                        </div>
                        <div class="adult-features-consent-toggle">
                            <label class="adult-features-toggle">
                                <input type="checkbox" id="consent-measurement">
                                <span class="adult-features-toggle-slider"></span>
                            </label>
                            <span>3D Measurement</span>
                        </div>
                        <div class="adult-features-consent-toggle">
                            <label class="adult-features-toggle">
                                <input type="checkbox" id="consent-activity-tracking">
                                <span class="adult-features-toggle-slider"></span>
                            </label>
                            <span>Activity Tracking</span>
                        </div>
                        <div class="adult-features-consent-toggle">
                            <label class="adult-features-toggle">
                                <input type="checkbox" id="consent-erotic-roleplay">
                                <span class="adult-features-toggle-slider"></span>
                            </label>
                            <span>Erotic Roleplay</span>
                        </div>
                        <div class="adult-features-consent-toggle">
                            <label class="adult-features-toggle">
                                <input type="checkbox" id="consent-joi">
                                <span class="adult-features-toggle-slider"></span>
                            </label>
                            <span>Jerk-Off Instructions (JOI)</span>
                        </div>
                    </div>
                    
                    <div class="adult-features-card">
                        <div class="adult-features-card-title">Safety Features</div>
                        <div class="adult-features-form-group">
                            <label class="adult-features-label" for="safe-word">Safe Word</label>
                            <div style="display: flex; gap: 10px;">
                                <input type="text" id="safe-word" class="adult-features-input" placeholder="Enter a safe word">
                                <button class="adult-features-button" id="save-safe-word">Save</button>
                            </div>
                            <small style="color: rgba(255,255,255,0.6);">Your safe word will instantly stop any active session</small>
                        </div>
                        <button class="adult-features-button danger" id="panic-button">🛑 Panic Button (Emergency Stop)</button>
                    </div>
                </div>
                
                <!-- Gender Recognition Section -->
                <div class="adult-features-section" id="section-gender-recognition">
                    <div class="adult-features-warning" id="gender-consent-warning">
                        <strong>Consent Required:</strong> Please enable consent for gender recognition in the Safety tab.
                    </div>
                    
                    <div class="adult-features-card" id="gender-recognition-card" style="display: none;">
                        <div class="adult-features-card-title">Gender Recognition</div>
                        <p>This feature uses AI to detect gender based on visual appearance. This can assist the AI in providing more personalized responses during intimate conversations.</p>
                        
                        <div class="adult-features-video-container">
                            <video id="gender-video" class="adult-features-video" autoplay muted playsinline></video>
                            <div class="adult-features-overlay" id="gender-video-overlay">
                                <p>Camera access required</p>
                                <button class="adult-features-button" id="gender-camera-btn">Enable Camera</button>
                            </div>
                        </div>
                        
                        <button class="adult-features-button" id="detect-gender-btn">Detect Gender</button>
                        
                        <div id="gender-result" style="margin-top: 15px; display: none;">
                            <div class="adult-features-card">
                                <div class="adult-features-card-title">Detection Result</div>
                                <div id="gender-result-text"></div>
                                <div id="gender-confidence"></div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 3D Measurement Section -->
                <div class="adult-features-section" id="section-measurement">
                    <div class="adult-features-warning" id="measurement-consent-warning">
                        <strong>Consent Required:</strong> Please enable consent for 3D measurement in the Safety tab.
                    </div>
                    
                    <div class="adult-features-card" id="measurement-card" style="display: none;">
                        <div class="adult-features-card-title">3D Measurement</div>
                        <p>This feature uses depth sensing to perform 3D measurements of objects or body parts. A depth-sensing camera like Intel RealSense is required for accuracy.</p>
                        
                        <div class="adult-features-video-container">
                            <video id="measurement-video" class="adult-features-video" autoplay muted playsinline></video>
                            <div class="adult-features-overlay" id="measurement-video-overlay">
                                <p>Camera access required</p>
                                <button class="adult-features-button" id="measurement-camera-btn">Enable Camera</button>
                            </div>
                            <div class="adult-features-measurement-result" id="measurement-result" style="display: none;"></div>
                        </div>
                        
                        <div class="adult-features-form-group">
                            <label class="adult-features-label">Calibration</label>
                            <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                                <input type="number" id="reference-size" class="adult-features-input" placeholder="Reference size in mm">
                                <button class="adult-features-button" id="calibrate-btn">Calibrate</button>
                            </div>
                            <small style="color: rgba(255,255,255,0.6);">Hold a reference object of known size for calibration</small>
                        </div>
                        
                        <button class="adult-features-button" id="measure-btn" disabled>Measure Object</button>
                        <button class="adult-features-button" id="clear-measurement-btn">Clear</button>
                    </div>
                </div>
                
                <!-- Activity Tracking Section -->
                <div class="adult-features-section" id="section-activity-tracking">
                    <div class="adult-features-warning" id="activity-consent-warning">
                        <strong>Consent Required:</strong> Please enable consent for activity tracking in the Safety tab.
                    </div>
                    
                    <div class="adult-features-card" id="activity-tracking-card" style="display: none;">
                        <div class="adult-features-card-title">Sexual Activity Tracking</div>
                        <p>Track your sexual activities and sync with Google Fit. This feature helps you monitor calories burned, duration, and frequency of sexual activities.</p>
                        
                        <div class="adult-features-form-group">
                            <label class="adult-features-label">Log New Activity</label>
                            <select id="activity-type" class="adult-features-select">
                                <option value="masturbation">Masturbation</option>
                                <option value="sex">Sex</option>
                            </select>
                        </div>
                        
                        <div class="adult-features-form-group">
                            <label class="adult-features-label">Duration (minutes)</label>
                            <input type="number" id="activity-duration" class="adult-features-input" value="15" min="1" max="180">
                        </div>
                        
                        <div class="adult-features-form-group">
                            <label class="adult-features-label">Heart Rate (optional)</label>
                            <input type="number" id="activity-heart-rate" class="adult-features-input" placeholder="Average heart rate (BPM)">
                        </div>
                        
                        <button class="adult-features-button primary" id="log-activity-btn">Log Activity</button>
                        
                        <div class="adult-features-card-title" style="margin-top: 20px;">Activity History</div>
                        <div id="activity-history"></div>
                        
                        <div class="adult-features-card-title" style="margin-top: 20px;">Statistics</div>
                        <div id="activity-stats"></div>
                    </div>
                </div>
                
                <!-- Erotic Roleplay Section -->
                <div class="adult-features-section" id="section-erotic-roleplay">
                    <div class="adult-features-warning" id="roleplay-consent-warning">
                        <strong>Consent Required:</strong> Please enable consent for erotic roleplay in the Safety tab.
                    </div>
                    
                    <div class="adult-features-card" id="roleplay-card" style="display: none;">
                        <div class="adult-features-card-title">Erotic Roleplay</div>
                        <p>Engage in immersive erotic roleplays with AI personas. Choose from various scenarios or create your own.</p>
                        
                        <div id="roleplay-start-panel">
                            <div class="adult-features-form-group">
                                <label class="adult-features-label">Select Scenario</label>
                                <select id="roleplay-scenario" class="adult-features-select"></select>
                            </div>
                            
                            <div class="adult-features-form-group">
                                <label class="adult-features-label">Select Persona</label>
                                <select id="roleplay-persona" class="adult-features-select"></select>
                            </div>
                            
                            <button class="adult-features-button primary" id="start-roleplay-btn">Start Roleplay</button>
                        </div>
                        
                        <div id="roleplay-session-panel" style="display: none;">
                            <div class="adult-features-badges">
                                <div class="adult-features-badge" id="roleplay-scenario-badge"></div>
                                <div class="adult-features-badge primary" id="roleplay-persona-badge"></div>
                                <div class="adult-features-badge success" id="roleplay-stage-badge"></div>
                            </div>
                            
                            <div class="adult-features-session-messages" id="roleplay-messages"></div>
                            
                            <div class="adult-features-form-group">
                                <textarea id="roleplay-input" class="adult-features-textarea" placeholder="Type your message..."></textarea>
                                <button class="adult-features-button primary" id="send-roleplay-message">Send</button>
                                <button class="adult-features-button danger" id="end-roleplay-session">End Session</button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- JOI Section -->
                <div class="adult-features-section" id="section-joi">
                    <div class="adult-features-warning" id="joi-consent-warning">
                        <strong>Consent Required:</strong> Please enable consent for JOI in the Safety tab.
                    </div>
                    
                    <div class="adult-features-card" id="joi-card" style="display: none;">
                        <div class="adult-features-card-title">Jerk-Off Instructions (JOI)</div>
                        <p>Follow guided masturbation instructions with timing control and intensity adjustment.</p>
                        
                        <div id="joi-start-panel">
                            <div class="adult-features-form-group">
                                <label class="adult-features-label">Session Type</label>
                                <select id="joi-session-type" class="adult-features-select"></select>
                            </div>
                            
                            <div class="adult-features-form-group">
                                <label class="adult-features-label">Intensity</label>
                                <select id="joi-intensity" class="adult-features-select">
                                    <option value="low">Low</option>
                                    <option value="medium" selected>Medium</option>
                                    <option value="high">High</option>
                                </select>
                            </div>
                            
                            <div class="adult-features-form-group">
                                <label class="adult-features-label">Duration (minutes)</label>
                                <input type="number" id="joi-duration" class="adult-features-input" value="10" min="5" max="30">
                            </div>
                            
                            <button class="adult-features-button primary" id="start-joi-btn">Start JOI Session</button>
                        </div>
                        
                        <div id="joi-session-panel" style="display: none;">
                            <div class="adult-features-badges">
                                <div class="adult-features-badge" id="joi-session-badge"></div>
                                <div class="adult-features-badge primary" id="joi-intensity-badge"></div>
                                <div class="adult-features-badge success" id="joi-phase-badge"></div>
                            </div>
                            
                            <div class="adult-features-card" id="joi-instruction-card">
                                <div class="adult-features-card-title">Current Instruction</div>
                                <p id="joi-instruction" class="adult-features-pulse"></p>
                            </div>
                            
                            <div class="adult-features-form-group">
                                <label class="adult-features-label">Session Progress</label>
                                <div class="adult-features-progress">
                                    <div class="adult-features-progress-bar" id="joi-progress-bar" style="width: 0%"></div>
                                </div>
                                <div style="display: flex; justify-content: space-between;">
                                    <span id="joi-elapsed-time">00:00</span>
                                    <span id="joi-remaining-time">00:00</span>
                                </div>
                            </div>
                            
                            <div class="adult-features-form-group">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                                    <button class="adult-features-button" id="joi-pause-btn">Pause</button>
                                    <button class="adult-features-button" id="joi-skip-btn">Skip Instruction</button>
                                    <button class="adult-features-button danger" id="joi-end-btn">End Session</button>
                                </div>
                            </div>
                            
                            <div class="adult-features-card">
                                <div class="adult-features-card-title">Session Stats</div>
                                <div id="joi-stats">Session will begin soon...</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Attach event listeners to UI elements
    attachEventListeners() {
        // Close button
        document.getElementById('adult-features-close').addEventListener('click', () => {
            this.hide();
        });
        
        // Navigation
        document.querySelectorAll('.adult-features-nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const section = e.target.getAttribute('data-section');
                this.showSection(section);
            });
        });
        
        // Safety features
        document.getElementById('verify-age-btn').addEventListener('click', () => {
            this.verifyAge();
        });
        
        document.getElementById('save-safe-word').addEventListener('click', () => {
            const safeWordInput = document.getElementById('safe-word');
            this.setSafeWord(safeWordInput.value);
        });
        
        document.getElementById('panic-button').addEventListener('click', () => {
            this.triggerPanicMode();
        });
        
        // Consent toggles
        const consentTypes = ['gender-recognition', 'measurement', 'activity-tracking', 'erotic-roleplay', 'joi'];
        consentTypes.forEach(type => {
            document.getElementById(`consent-${type}`).addEventListener('change', (e) => {
                this.updateConsent(type, e.target.checked);
            });
        });
        
        // Gender recognition
        document.getElementById('gender-camera-btn').addEventListener('click', () => {
            this.enableCamera('gender-video', 'gender-video-overlay');
        });
        
        document.getElementById('detect-gender-btn').addEventListener('click', () => {
            this.detectGender();
        });
        
        // 3D Measurement
        document.getElementById('measurement-camera-btn').addEventListener('click', () => {
            this.enableCamera('measurement-video', 'measurement-video-overlay');
        });
        
        document.getElementById('calibrate-btn').addEventListener('click', () => {
            const referenceSize = document.getElementById('reference-size').value;
            this.calibrateMeasurement(referenceSize);
        });
        
        document.getElementById('measure-btn').addEventListener('click', () => {
            this.performMeasurement();
        });
        
        document.getElementById('clear-measurement-btn').addEventListener('click', () => {
            this.clearMeasurement();
        });
        
        // Activity tracking
        document.getElementById('log-activity-btn').addEventListener('click', () => {
            const type = document.getElementById('activity-type').value;
            const duration = document.getElementById('activity-duration').value;
            const heartRate = document.getElementById('activity-heart-rate').value;
            this.logActivity(type, duration, heartRate);
        });
        
        // Erotic roleplay
        this.populateRoleplayOptions();
        
        document.getElementById('start-roleplay-btn').addEventListener('click', () => {
            const scenario = document.getElementById('roleplay-scenario').value;
            const persona = document.getElementById('roleplay-persona').value;
            this.startRoleplay(scenario, persona);
        });
        
        document.getElementById('send-roleplay-message').addEventListener('click', () => {
            const message = document.getElementById('roleplay-input').value;
            this.sendRoleplayMessage(message);
            document.getElementById('roleplay-input').value = '';
        });
        
        document.getElementById('roleplay-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                document.getElementById('send-roleplay-message').click();
            }
        });
        
        document.getElementById('end-roleplay-session').addEventListener('click', () => {
            this.endRoleplaySession();
        });
        
        // JOI
        this.populateJOIOptions();
        
        document.getElementById('start-joi-btn').addEventListener('click', () => {
            const sessionType = document.getElementById('joi-session-type').value;
            const intensity = document.getElementById('joi-intensity').value;
            const duration = document.getElementById('joi-duration').value;
            this.startJOISession(sessionType, intensity, duration);
        });
        
        document.getElementById('joi-pause-btn').addEventListener('click', () => {
            this.toggleJOIPause();
        });
        
        document.getElementById('joi-skip-btn').addEventListener('click', () => {
            this.skipJOIInstruction();
        });
        
        document.getElementById('joi-end-btn').addEventListener('click', () => {
            this.endJOISession();
        });
    }
    
    // Show the UI
    show() {
        this.container.classList.add('active');
        return this;
    }
    
    // Hide the UI
    hide() {
        this.container.classList.remove('active');
        return this;
    }
    
    // Show a specific section
    showSection(sectionName) {
        // Update navigation
        document.querySelectorAll('.adult-features-nav-item').forEach(item => {
            if (item.getAttribute('data-section') === sectionName) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
        
        // Update section visibility
        document.querySelectorAll('.adult-features-section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(`section-${sectionName}`).classList.add('active');
        
        // Additional actions when switching to a section
        if (sectionName === 'activity-tracking') {
            this.loadActivityHistory();
        }
        
        this.currentSection = sectionName;
        
        return this;
    }
    
    // Check if user is verified
    checkVerificationStatus() {
        const status = localStorage.getItem('hextrix_age_verified');
        this.isVerified = status === 'true';
        
        if (this.isVerified) {
            // Update UI for verified state
            document.getElementById('verification-box').style.display = 'none';
            document.getElementById('verification-status').innerHTML = `
                <div style="background: rgba(0, 255, 0, 0.1); color: #0f0; padding: 10px; border-radius: 5px;">
                    <strong>Verified:</strong> Age verification completed successfully.
                </div>
            `;
        }
        
        // Load consent settings
        const consentData = localStorage.getItem('hextrix_consent');
        if (consentData) {
            try {
                this.hasConsent = JSON.parse(consentData);
                
                // Update UI toggles
                for (const [key, value] of Object.entries(this.hasConsent)) {
                    const toggle = document.getElementById(`consent-${key}`);
                    if (toggle) {
                        toggle.checked = value;
                        this.updateFeatureVisibility(key, value);
                    }
                }
            } catch (error) {
                console.error('Error parsing consent data:', error);
            }
        }
        
        // Load safe word
        const safeWord = localStorage.getItem('hextrix_safe_word');
        if (safeWord) {
            this.safeWord = safeWord;
            document.getElementById('safe-word').value = safeWord;
        }
    }
    
    // Age verification
    verifyAge() {
        // In a production system, this would connect to a third-party age verification service
        // For this implementation, we'll use a simple confirmation dialog
        const confirmed = confirm("By proceeding, you confirm that you are at least 18 years old or the age of majority in your jurisdiction, whichever is higher. This is a legally binding confirmation.");
        
        if (confirmed) {
            this.isVerified = true;
            localStorage.setItem('hextrix_age_verified', 'true');
            
            // Update UI
            document.getElementById('verification-box').style.display = 'none';
            document.getElementById('verification-status').innerHTML = `
                <div style="background: rgba(0, 255, 0, 0.1); color: #0f0; padding: 10px; border-radius: 5px;">
                    <strong>Verified:</strong> Age verification completed successfully.
                </div>
            `;
        }
    }
    
    // Update consent settings
    updateConsent(featureType, hasConsent) {
        this.hasConsent[featureType] = hasConsent;
        localStorage.setItem('hextrix_consent', JSON.stringify(this.hasConsent));
        
        // Update UI based on consent
        this.updateFeatureVisibility(featureType, hasConsent);
    }
    
    // Update feature visibility based on consent
    updateFeatureVisibility(featureType, hasConsent) {
        switch (featureType) {
            case 'gender-recognition':
                document.getElementById('gender-consent-warning').style.display = hasConsent ? 'none' : 'block';
                document.getElementById('gender-recognition-card').style.display = hasConsent ? 'block' : 'none';
                break;
            case 'measurement':
                document.getElementById('measurement-consent-warning').style.display = hasConsent ? 'none' : 'block';
                document.getElementById('measurement-card').style.display = hasConsent ? 'block' : 'none';
                break;
            case 'activity-tracking':
                document.getElementById('activity-consent-warning').style.display = hasConsent ? 'none' : 'block';
                document.getElementById('activity-tracking-card').style.display = hasConsent ? 'block' : 'none';
                break;
            case 'erotic-roleplay':
                document.getElementById('roleplay-consent-warning').style.display = hasConsent ? 'none' : 'block';
                document.getElementById('roleplay-card').style.display = hasConsent ? 'block' : 'none';
                break;
            case 'joi':
                document.getElementById('joi-consent-warning').style.display = hasConsent ? 'none' : 'block';
                document.getElementById('joi-card').style.display = hasConsent ? 'block' : 'none';
                break;
        }
    }
    
    // Set safe word
    setSafeWord(word) {
        if (!word || word.trim() === '') {
            alert('Please enter a valid safe word.');
            return;
        }
        
        this.safeWord = word.trim();
        localStorage.setItem('hextrix_safe_word', this.safeWord);
        
        alert(`Safe word set to: "${this.safeWord}". Use this word to immediately stop any session.`);
    }
    
    // Trigger panic mode
    triggerPanicMode() {
        // Stop all active sessions
        if (this.activeRoleplaySession) {
            this.endRoleplaySession();
        }
        
        if (this.activeJOISession) {
            this.endJOISession();
        }
        
        // Stop camera streams
        if (this.videoStream) {
            this.videoStream.getTracks().forEach(track => track.stop());
            this.videoStream = null;
        }
        
        // Hide adult features UI
        this.hide();
        
        // Clear sensitive UI elements
        document.querySelectorAll('.adult-features-video').forEach(video => {
            video.srcObject = null;
        });
        
        // Show emergency notification
        alert('Emergency stop triggered. All adult features have been disabled and streams closed.');
    }
    
    // Enable camera for a video element
    async enableCamera(videoElementId, overlayElementId) {
        try {
            // Check if verified and has consent
            if (!this.isVerified) {
                alert('Age verification required before enabling camera.');
                return;
            }
            
            // Request camera access
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            
            // Set the video source
            const videoElement = document.getElementById(videoElementId);
            videoElement.srcObject = stream;
            
            // Hide overlay
            document.getElementById(overlayElementId).style.display = 'none';
            
            // Store stream reference
            this.videoStream = stream;
        } catch (error) {
            console.error('Error accessing camera:', error);
            alert('Error accessing camera. Please ensure you have a camera connected and have granted permission.');
        }
    }
    
    // Detect gender from video
    detectGender() {
        // Verify prerequisites
        if (!this.isVerified || !this.hasConsent['gender-recognition']) {
            alert('Age verification and consent required for gender recognition.');
            return;
        }
        
        if (!this.videoStream) {
            alert('Please enable camera access first.');
            return;
        }
        
        // In a real implementation, this would capture a frame and send it to a backend API
        // For this demo, we'll use a simulated response
        const genderOptions = ['male', 'female'];
        const detectedGender = genderOptions[Math.floor(Math.random() * genderOptions.length)];
        const confidence = (0.7 + Math.random() * 0.3).toFixed(2); // Random confidence between 0.7-1.0
        
        // Display result
        document.getElementById('gender-result').style.display = 'block';
        document.getElementById('gender-result-text').textContent = `Detected Gender: ${detectedGender}`;
        document.getElementById('gender-confidence').textContent = `Confidence: ${confidence * 100}%`;
        
        // Send result to main system
        if (window.socket) {
            window.socket.emit('gender_detected', {
                gender: detectedGender,
                confidence: parseFloat(confidence)
            });
        }
    }
    
    // Calibrate 3D measurement
    calibrateMeasurement(referenceSizeMm) {
        // Verify prerequisites
        if (!this.isVerified || !this.hasConsent['measurement']) {
            alert('Age verification and consent required for measurement.');
            return;
        }
        
        if (!this.videoStream) {
            alert('Please enable camera access first.');
            return;
        }
        
        if (!referenceSizeMm || isNaN(referenceSizeMm) || referenceSizeMm <= 0) {
            alert('Please enter a valid reference size in millimeters.');
            return;
        }
        
        // In a real implementation, this would capture a frame and perform calibration
        // For this demo, we'll simulate calibration
        this.measurementCalibrated = true;
        document.getElementById('measure-btn').disabled = false;
        
        alert(`Calibration successful with reference size: ${referenceSizeMm}mm`);
    }
    
    // Perform 3D measurement
    performMeasurement() {
        // Verify prerequisites
        if (!this.isVerified || !this.hasConsent['measurement']) {
            alert('Age verification and consent required for measurement.');
            return;
        }
        
        if (!this.videoStream) {
            alert('Please enable camera access first.');
            return;
        }
        
        if (!this.measurementCalibrated) {
            alert('Please calibrate the measurement system first.');
            return;
        }
        
        // In a real implementation, this would capture a frame and analyze it
        // For this demo, we'll generate random measurements
        const width = (100 + Math.random() * 100).toFixed(1);
        const height = (100 + Math.random() * 100).toFixed(1);
        const depth = (50 + Math.random() * 50).toFixed(1);
        
        // Convert to inches (1mm = 0.03937 inches)
        const widthInch = (width * 0.03937).toFixed(1);
        const heightInch = (height * 0.03937).toFixed(1);
        const depthInch = (depth * 0.03937).toFixed(1);
        
        // Display result
        const resultElement = document.getElementById('measurement-result');
        resultElement.innerHTML = `
            Width: ${width}mm (${widthInch}")<br>
            Height: ${height}mm (${heightInch}")<br>
            Depth: ${depth}mm (${depthInch}")
        `;
        resultElement.style.display = 'block';
        
        // Send result to main system
        if (window.socket) {
            window.socket.emit('measurement_result', {
                width: parseFloat(width),
                height: parseFloat(height),
                depth: parseFloat(depth),
                width_inch: parseFloat(widthInch),
                height_inch: parseFloat(heightInch),
                depth_inch: parseFloat(depthInch)
            });
        }
    }
    
    // Clear measurement result
    clearMeasurement() {
        document.getElementById('measurement-result').style.display = 'none';
    }
    
    // Log new activity
    logActivity(type, duration, heartRate = null) {
        // Verify prerequisites
        if (!this.isVerified || !this.hasConsent['activity-tracking']) {
            alert('Age verification and consent required for activity tracking.');
            return;
        }
        
        if (!type || !duration || isNaN(duration) || duration <= 0) {
            alert('Please enter valid activity details.');
            return;
        }
        
        // Convert heart rate to number if provided
        if (heartRate) {
            heartRate = parseFloat(heartRate);
        }
        
        // In a real implementation, this would call a backend API to log the activity
        // For this demo, we'll store in localStorage
        const activityData = {
            type,
            duration: parseFloat(duration),
            heart_rate: heartRate,
            timestamp: new Date().toISOString()
        };
        
        // Get existing activity history
        let history = [];
        try {
            const storedHistory = localStorage.getItem('hextrix_activity_history');
            if (storedHistory) {
                history = JSON.parse(storedHistory);
            }
        } catch (error) {
            console.error('Error parsing activity history:', error);
        }
        
        // Add new activity
        history.push(activityData);
        
        // Store updated history
        localStorage.setItem('hextrix_activity_history', JSON.stringify(history));
        
        // Update UI
        this.loadActivityHistory();
        
        // Send to main system
        if (window.socket) {
            window.socket.emit('activity_logged', activityData);
        }
        
        alert(`Activity logged: ${type} for ${duration} minutes`);
    }
    
    // Load activity history
    loadActivityHistory() {
        // Get history from localStorage
        let history = [];
        try {
            const storedHistory = localStorage.getItem('hextrix_activity_history');
            if (storedHistory) {
                history = JSON.parse(storedHistory);
            }
        } catch (error) {
            console.error('Error parsing activity history:', error);
        }
        
        // Sort by most recent first
        history.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        
        // Display history
        const historyElement = document.getElementById('activity-history');
        if (history.length === 0) {
            historyElement.innerHTML = '<p>No activity logged yet.</p>';
        } else {
            let html = '<div class="adult-features-grid">';
            
            history.slice(0, 10).forEach(activity => {
                const date = new Date(activity.timestamp).toLocaleString();
                html += `
                    <div class="adult-features-card">
                        <div class="adult-features-card-title">${activity.type}</div>
                        <p>Duration: ${activity.duration} minutes</p>
                        ${activity.heart_rate ? `<p>Heart Rate: ${activity.heart_rate} BPM</p>` : ''}
                        <p>Date: ${date}</p>
                    </div>
                `;
            });
            
            html += '</div>';
            historyElement.innerHTML = html;
        }
        
        // Calculate and display statistics
        this.calculateActivityStats(history);
    }
    
    // Calculate activity statistics
    calculateActivityStats(activities) {
        if (!activities || activities.length === 0) {
            document.getElementById('activity-stats').innerHTML = '<p>No data available for statistics.</p>';
            return;
        }
        
        // Calculate total activities
        const totalCount = activities.length;
        
        // Calculate total by type
        const sexCount = activities.filter(a => a.type === 'sex').length;
        const masturbationCount = activities.filter(a => a.type === 'masturbation').length;
        
        // Calculate total duration
        const totalDuration = activities.reduce((sum, activity) => sum + activity.duration, 0);
        
        // Calculate average duration
        const avgDuration = totalDuration / totalCount;
        
        // Calculate average heart rate (if available)
        const activitiesWithHeartRate = activities.filter(a => a.heart_rate);
        let avgHeartRate = 0;
        if (activitiesWithHeartRate.length > 0) {
            avgHeartRate = activitiesWithHeartRate.reduce((sum, a) => sum + a.heart_rate, 0) / activitiesWithHeartRate.length;
        }
        
        // Estimate calories (rough estimate)
        // MET values: ~3.0 for masturbation, ~5.8 for sex
        const weightKg = 70; // Default weight, in a real app this would be user-specific
        const sexDuration = activities.filter(a => a.type === 'sex').reduce((sum, a) => sum + a.duration, 0);
        const masturbationDuration = activities.filter(a => a.type === 'masturbation').reduce((sum, a) => sum + a.duration, 0);
        
        const sexCalories = (5.8 * weightKg * (sexDuration / 60));
        const masturbationCalories = (3.0 * weightKg * (masturbationDuration / 60));
        const totalCalories = sexCalories + masturbationCalories;
        
        // Display statistics
        document.getElementById('activity-stats').innerHTML = `
            <div class="adult-features-grid">
                <div class="adult-features-card">
                    <div class="adult-features-card-title">Activity Count</div>
                    <p>Total: ${totalCount}</p>
                    <p>Sex: ${sexCount}</p>
                    <p>Masturbation: ${masturbationCount}</p>
                </div>
                
                <div class="adult-features-card">
                    <div class="adult-features-card-title">Duration</div>
                    <p>Total: ${totalDuration.toFixed(1)} minutes</p>
                    <p>Average: ${avgDuration.toFixed(1)} minutes/session</p>
                </div>
                
                <div class="adult-features-card">
                    <div class="adult-features-card-title">Calories</div>
                    <p>Total: ${totalCalories.toFixed(1)} kcal</p>
                    <p>Sex: ${sexCalories.toFixed(1)} kcal</p>
                    <p>Masturbation: ${masturbationCalories.toFixed(1)} kcal</p>
                </div>
                
                ${avgHeartRate > 0 ? `
                <div class="adult-features-card">
                    <div class="adult-features-card-title">Heart Rate</div>
                    <p>Average: ${avgHeartRate.toFixed(1)} BPM</p>
                </div>` : ''}
            </div>
        `;
    }
    
    // Populate roleplay options
    populateRoleplayOptions() {
        // Scenarios
        const scenarios = [
            { id: 'fantasy', name: 'Fantasy Adventure' },
            { id: 'office', name: 'Office Romance' },
            { id: 'strangers', name: 'Strangers Meeting' },
            { id: 'date', name: 'First Date' },
            { id: 'vacation', name: 'Vacation Fling' },
            { id: 'reunion', name: 'High School Reunion' },
            { id: 'neighbors', name: 'Neighbors' },
            { id: 'custom', name: 'Custom Scenario' }
        ];
        
        // Personas
        const personas = [
            { id: 'flirty', name: 'Flirty & Playful' },
            { id: 'dominant', name: 'Dominant & Assertive' },
            { id: 'submissive', name: 'Shy & Submissive' },
            { id: 'teasing', name: 'Teasing & Seductive' },
            { id: 'romantic', name: 'Sweet & Romantic' },
            { id: 'experienced', name: 'Experienced & Confident' },
            { id: 'innocent', name: 'Innocent & Curious' },
            { id: 'custom', name: 'Custom Persona' }
        ];
        
        // Populate dropdowns
        const scenarioSelect = document.getElementById('roleplay-scenario');
        scenarioSelect.innerHTML = '';
        scenarios.forEach(scenario => {
            const option = document.createElement('option');
            option.value = scenario.id;
            option.textContent = scenario.name;
            scenarioSelect.appendChild(option);
        });
        
        const personaSelect = document.getElementById('roleplay-persona');
        personaSelect.innerHTML = '';
        personas.forEach(persona => {
            const option = document.createElement('option');
            option.value = persona.id;
            option.textContent = persona.name;
            personaSelect.appendChild(option);
        });
    }
    
    // Start roleplay session
    startRoleplay(scenario, persona) {
        // Verify prerequisites
        if (!this.isVerified || !this.hasConsent['erotic-roleplay']) {
            alert('Age verification and consent required for roleplay.');
            return;
        }
        
        // Get scenario and persona names
        const scenarioName = document.getElementById('roleplay-scenario').options[document.getElementById('roleplay-scenario').selectedIndex].text;
        const personaName = document.getElementById('roleplay-persona').options[document.getElementById('roleplay-persona').selectedIndex].text;
        
        // Create session
        this.activeRoleplaySession = {
            scenario,
            scenarioName,
            persona,
            personaName,
            messages: [],
            startTime: new Date()
        };
        
        // Update UI
        document.getElementById('roleplay-start-panel').style.display = 'none';
        document.getElementById('roleplay-session-panel').style.display = 'block';
        
        document.getElementById('roleplay-scenario-badge').textContent = scenarioName;
        document.getElementById('roleplay-persona-badge').textContent = personaName;
        document.getElementById('roleplay-stage-badge').textContent = 'Starting';
        
        document.getElementById('roleplay-messages').innerHTML = '';
        
        // Add system message
        this.addRoleplayMessage('system', `Starting new roleplay: "${scenarioName}" with AI persona: "${personaName}"`);
        
        // Add AI intro message based on scenario and persona
        let introMessage = '';
        
        // Generate intro message based on scenario and persona
        switch (scenario) {
            case 'fantasy':
                if (persona === 'dominant') {
                    introMessage = "I've been watching you, adventurer. Your skills with that sword are... impressive. Perhaps you'd like to show me what else you can do with your hands?";
                } else if (persona === 'submissive') {
                    introMessage = "Oh! I didn't see you there, brave warrior. I've been lost in these woods for days. Could you... help me find shelter for the night?";
                } else {
                    introMessage = "Well met, traveler. The stars are beautiful tonight, aren't they? Almost as captivating as the way you look at me...";
                }
                break;
            case 'office':
                if (persona === 'dominant') {
                    introMessage = "Close the door and lock it. I've been watching you all day, and I think it's time we discussed your... performance review in private.";
                } else if (persona === 'submissive') {
                    introMessage = "I hope I'm not bothering you... but I've been having trouble concentrating at my desk. Every time I look up, I catch you staring at me...";
                } else {
                    introMessage = "These late nights at the office are so boring... unless we find a way to make them more interesting. Any ideas?";
                }
                break;
            default:
                introMessage = "Hi there. I've been looking forward to this moment. Shall we get to know each other better?";
        }
        
        // Add AI message
        setTimeout(() => {
            this.addRoleplayMessage('ai', introMessage);
            document.getElementById('roleplay-stage-badge').textContent = 'In Progress';
        }, 1500);
    }
    
    // Add message to roleplay session
    addRoleplayMessage(type, content) {
        if (!this.activeRoleplaySession) return;
        
        // Add to session
        this.activeRoleplaySession.messages.push({
            type,
            content,
            timestamp: new Date()
        });
        
        // Add to UI
        const messagesElement = document.getElementById('roleplay-messages');
        const messageDiv = document.createElement('div');
        
        messageDiv.className = `adult-features-message adult-features-message-${type}`;
        messageDiv.textContent = content;
        
        messagesElement.appendChild(messageDiv);
        
        // Scroll to bottom
        messagesElement.scrollTop = messagesElement.scrollHeight;
    }
    
    // Send roleplay message
    sendRoleplayMessage(message) {
        if (!this.activeRoleplaySession) return;
        if (!message || message.trim() === '') return;
        
        // Check for safe word
        if (this.safeWord && message.toLowerCase().includes(this.safeWord.toLowerCase())) {
            this.addRoleplayMessage('system', 'Safe word detected. Ending session immediately.');
            this.endRoleplaySession();
            return;
        }
        
        // Add user message
        this.addRoleplayMessage('user', message);
        
        // Generate AI response
        document.getElementById('roleplay-stage-badge').textContent = 'AI Responding...';
        
        // In a real implementation, this would send the message to a backend API
        // For this demo, we'll simulate an AI response
        setTimeout(() => {
            // Generate simple responses based on persona
            let response = '';
            const persona = this.activeRoleplaySession.persona;
            
            if (persona === 'dominant') {
                const dominantResponses = [
                    "I like how eager you are. But remember who's in control here.",
                    "That's interesting. Now let me tell you what I want you to do next...",
                    "You're being very good. I think you deserve a reward, don't you?",
                    "Is that what you think? How cute. Now let me show you what I had in mind..."
                ];
                response = dominantResponses[Math.floor(Math.random() * dominantResponses.length)];
            } else if (persona === 'submissive') {
                const submissiveResponses = [
                    "Oh my... I didn't expect you to say that. *blushes*",
                    "Whatever you want... I'm yours to command.",
                    "That makes me feel so... I don't know if I should tell you what I'm thinking.",
                    "You're making me feel things I've never felt before..."
                ];
                response = submissiveResponses[Math.floor(Math.random() * submissiveResponses.length)];
            } else if (persona === 'flirty') {
                const flirtyResponses = [
                    "Oh, is that so? What else do you have in mind? *winks*",
                    "I love the way you think. Let's see where this goes...",
                    "You're making me blush! But please, don't stop.",
                    "Mmm, I was hoping you'd say something like that."
                ];
                response = flirtyResponses[Math.floor(Math.random() * flirtyResponses.length)];
            } else {
                const genericResponses = [
                    "That sounds wonderful. Tell me more...",
                    "I'm definitely interested in exploring that with you.",
                    "You have my full attention now. What else would you like to share?",
                    "I can't help but smile when you talk like that."
                ];
                response = genericResponses[Math.floor(Math.random() * genericResponses.length)];
            }
            
            // Add AI response
            this.addRoleplayMessage('ai', response);
            document.getElementById('roleplay-stage-badge').textContent = 'In Progress';
        }, 1500);
    }
    
    // End roleplay session
    endRoleplaySession() {
        if (!this.activeRoleplaySession) return;
        
        // Add system message
        this.addRoleplayMessage('system', 'Roleplay session ended.');
        
        // Reset UI
        document.getElementById('roleplay-start-panel').style.display = 'block';
        document.getElementById('roleplay-session-panel').style.display = 'none';
        
        // Clear session
        this.activeRoleplaySession = null;
    }
    
    // Populate JOI options
    populateJOIOptions() {
        // Session types
        const sessionTypes = [
            { id: 'standard', name: 'Standard JOI' },
            { id: 'edging', name: 'Edging' },
            { id: 'guided', name: 'Guided Experience' },
            { id: 'tease', name: 'Teasing & Denial' },
            { id: 'countdown', name: 'Countdown' },
            { id: 'roleplay', name: 'Roleplay JOI' },
            { id: 'custom', name: 'Custom Session' }
        ];
        
        // Populate dropdown
        const sessionTypeSelect = document.getElementById('joi-session-type');
        sessionTypeSelect.innerHTML = '';
        sessionTypes.forEach(type => {
            const option = document.createElement('option');
            option.value = type.id;
            option.textContent = type.name;
            sessionTypeSelect.appendChild(option);
        });
    }
    
    // Start JOI session
    startJOISession(sessionType, intensity, duration) {
        // Verify prerequisites
        if (!this.isVerified || !this.hasConsent['joi']) {
            alert('Age verification and consent required for JOI.');
            return;
        }
        
        // Validate parameters
        if (!sessionType || !intensity || !duration || isNaN(duration) || duration <= 0) {
            alert('Please enter valid session parameters.');
            return;
        }
        
        // Get session name
        const sessionName = document.getElementById('joi-session-type').options[document.getElementById('joi-session-type').selectedIndex].text;
        
        // Create session
        this.activeJOISession = {
            type: sessionType,
            typeName: sessionName,
            intensity,
            duration: parseInt(duration),
            startTime: new Date(),
            elapsedSeconds: 0,
            isPaused: false,
            currentPhase: 'warmup',
            currentInstruction: '',
            instructionIndex: 0,
            instructions: this.generateJOIInstructions(sessionType, intensity, duration)
        };
        
        // Update UI
        document.getElementById('joi-start-panel').style.display = 'none';
        document.getElementById('joi-session-panel').style.display = 'block';
        
        document.getElementById('joi-session-badge').textContent = sessionName;
        document.getElementById('joi-intensity-badge').textContent = `${intensity.charAt(0).toUpperCase() + intensity.slice(1)} Intensity`;
        document.getElementById('joi-phase-badge').textContent = 'Warm-up';
        
        // Start session timer
        this.joiTimer = setInterval(() => this.updateJOISession(), 1000);
        
        // Set first instruction
        this.updateJOIInstruction(0);
        
        // Update stats
        document.getElementById('joi-stats').textContent = `Session started. ${this.activeJOISession.instructions.length} instructions planned.`;
    }
    
    // Generate JOI instructions based on parameters
    generateJOIInstructions(sessionType, intensity, duration) {
        // Calculate number of instructions based on duration
        const instructionCount = Math.floor(duration * 60 / 30); // Approx. one instruction per 30 seconds
        
        // Basic instructions common to all types
        const instructions = [
            "Start by gently touching yourself, getting comfortable.",
            "Slowly start stroking, finding your rhythm."
        ];
        
        // Add session-specific instructions
        switch (sessionType) {
            case 'standard':
                instructions.push(...[
                    "Maintain a steady rhythm, not too fast.",
                    "Now gradually increase your speed.",
                    "Slow down a bit, focus on sensation.",
                    "Speed up, but don't go too fast yet.",
                    "Keep going at this pace."
                ]);
                break;
                
            case 'edging':
                instructions.push(...[
                    "Increase your speed until you're close.",
                    "Now STOP completely. Take a deep breath.",
                    "Start again, but very slowly.",
                    "Build up again, getting close.",
                    "STOP. Wait 10 seconds.",
                    "Start again, medium pace."
                ]);
                break;
                
            case 'countdown':
                instructions.push(...[
                    "10 fast strokes, then pause.",
                    "9 slow, deep strokes.",
                    "8 faster strokes now.",
                    "7 strokes while building intensity.",
                    "6 deep, slow strokes.",
                    "5 quick strokes.",
                    "4 strokes edging yourself.",
                    "3 passionate strokes.",
                    "2 final strokes.",
                    "1 last stroke."
                ]);
                break;
                
            default:
                instructions.push(...[
                    "Find your preferred rhythm.",
                    "Focus on your pleasure.",
                    "Adjust your speed as needed.",
                    "Keep going at your own pace."
                ]);
        }
        
        // Add intensity-specific instructions
        if (intensity === 'high') {
            instructions.push(...[
                "Go as fast as you can for 30 seconds.",
                "Maintain maximum intensity.",
                "Push yourself to the limit."
            ]);
        } else if (intensity === 'low') {
            instructions.push(...[
                "Keep a slow, gentle pace.",
                "Focus on the subtle sensations.",
                "Gentle strokes only."
            ]);
        }
        
        // Add final instructions
        instructions.push(...[
            "You're approaching the end of the session.",
            "Find the pace that works best for you now.",
            "Focus on your pleasure as we conclude."
        ]);
        
        // Final instruction for all sessions
        instructions.push("Feel free to finish when you're ready.");
        
        // If we need more instructions, repeat some
        while (instructions.length < instructionCount) {
            const randomInstruction = instructions[Math.floor(Math.random() * (instructions.length - 1)) + 1];
            instructions.splice(instructions.length - 1, 0, randomInstruction);
        }
        
        // If we have too many, trim some
        if (instructions.length > instructionCount) {
            // Keep first and last instructions, trim from middle
            const first = instructions.slice(0, 2);
            const last = instructions.slice(-2);
            const middle = instructions.slice(2, -2);
            
            // Randomly select from middle to reach desired count
            const middleNeeded = instructionCount - 4;
            const selectedMiddle = this.getRandomElements(middle, middleNeeded);
            
            return [...first, ...selectedMiddle, ...last];
        }
        
        return instructions;
    }
    
    // Get random elements from array
    getRandomElements(arr, count) {
        const shuffled = [...arr].sort(() => 0.5 - Math.random());
        return shuffled.slice(0, count);
    }
    
    // Update JOI session timer and progress
    updateJOISession() {
        if (!this.activeJOISession || this.activeJOISession.isPaused) return;
        
        // Update elapsed time
        this.activeJOISession.elapsedSeconds++;
        
        // Calculate progress
        const totalDurationSeconds = this.activeJOISession.duration * 60;
        const elapsedSeconds = this.activeJOISession.elapsedSeconds;
        const progress = (elapsedSeconds / totalDurationSeconds) * 100;
        
        // Update UI
        document.getElementById('joi-progress-bar').style.width = `${Math.min(100, progress)}%`;
        
        // Update time displays
        const elapsedMinutes = Math.floor(elapsedSeconds / 60);
        const elapsedSecondsRemainder = elapsedSeconds % 60;
        document.getElementById('joi-elapsed-time').textContent = 
            `${elapsedMinutes.toString().padStart(2, '0')}:${elapsedSecondsRemainder.toString().padStart(2, '0')}`;
        
        const remainingSeconds = Math.max(0, totalDurationSeconds - elapsedSeconds);
        const remainingMinutes = Math.floor(remainingSeconds / 60);
        const remainingSecondsRemainder = remainingSeconds % 60;
        document.getElementById('joi-remaining-time').textContent = 
            `${remainingMinutes.toString().padStart(2, '0')}:${remainingSecondsRemainder.toString().padStart(2, '0')}`;
        
        // Check if we need to update phase
        if (progress < 20) {
            if (this.activeJOISession.currentPhase !== 'warmup') {
                this.activeJOISession.currentPhase = 'warmup';
                document.getElementById('joi-phase-badge').textContent = 'Warm-up';
            }
        } else if (progress < 80) {
            if (this.activeJOISession.currentPhase !== 'main') {
                this.activeJOISession.currentPhase = 'main';
                document.getElementById('joi-phase-badge').textContent = 'Main Phase';
            }
        } else {
            if (this.activeJOISession.currentPhase !== 'climax') {
                this.activeJOISession.currentPhase = 'climax';
                document.getElementById('joi-phase-badge').textContent = 'Climax Phase';
            }
        }
        
        // Check if we need a new instruction
        // On average, update every 30 seconds, but add some randomness
        if (elapsedSeconds % 30 === 0 || (Math.random() < 0.03 && elapsedSeconds % 10 === 0)) {
            const nextIndex = this.activeJOISession.instructionIndex + 1;
            if (nextIndex < this.activeJOISession.instructions.length) {
                this.updateJOIInstruction(nextIndex);
            }
        }
        
        // Check if session is complete
        if (elapsedSeconds >= totalDurationSeconds) {
            this.endJOISession();
        }
    }
    
    // Update JOI instruction
    updateJOIInstruction(index) {
        if (!this.activeJOISession) return;
        if (index >= this.activeJOISession.instructions.length) return;
        
        this.activeJOISession.instructionIndex = index;
        this.activeJOISession.currentInstruction = this.activeJOISession.instructions[index];
        
        // Update UI
        document.getElementById('joi-instruction').textContent = this.activeJOISession.currentInstruction;
        
        // Update stats
        const progress = Math.floor((index / this.activeJOISession.instructions.length) * 100);
        document.getElementById('joi-stats').textContent = `Instruction ${index + 1} of ${this.activeJOISession.instructions.length} (${progress}% complete)`;
    }
    
    // Toggle JOI pause state
    toggleJOIPause() {
        if (!this.activeJOISession) return;
        
        this.activeJOISession.isPaused = !this.activeJOISession.isPaused;
        
        // Update button text
        document.getElementById('joi-pause-btn').textContent = this.activeJOISession.isPaused ? 'Resume' : 'Pause';
        
        // Update phase badge
        if (this.activeJOISession.isPaused) {
            document.getElementById('joi-phase-badge').textContent = 'Paused';
        } else {
            // Restore previous phase name
            let phaseName = 'Main Phase';
            if (this.activeJOISession.currentPhase === 'warmup') phaseName = 'Warm-up';
            if (this.activeJOISession.currentPhase === 'climax') phaseName = 'Climax Phase';
            document.getElementById('joi-phase-badge').textContent = phaseName;
        }
    }
    
    // Skip to next JOI instruction
    skipJOIInstruction() {
        if (!this.activeJOISession) return;
        
        const nextIndex = this.activeJOISession.instructionIndex + 1;
        if (nextIndex < this.activeJOISession.instructions.length) {
            this.updateJOIInstruction(nextIndex);
        }
    }
    
    // End JOI session
    endJOISession() {
        if (!this.activeJOISession) return;
        
        // Clear timer
        if (this.joiTimer) {
            clearInterval(this.joiTimer);
            this.joiTimer = null;
        }
        
        // Calculate session statistics
        const sessionDuration = this.activeJOISession.elapsedSeconds;
        const durationMinutes = Math.floor(sessionDuration / 60);
        const durationSeconds = sessionDuration % 60;
        const formattedDuration = `${durationMinutes}:${durationSeconds.toString().padStart(2, '0')}`;
        
        // Update UI
        document.getElementById('joi-start-panel').style.display = 'block';
        document.getElementById('joi-session-panel').style.display = 'none';
        
        // Show completion message
        alert(`JOI session completed!\nDuration: ${formattedDuration}\nType: ${this.activeJOISession.typeName}\nIntensity: ${this.activeJOISession.intensity}`);
        
        // Clear session
        this.activeJOISession = null;
    }
}

// Create global instance
window.adultFeaturesUI = new AdultFeaturesUI();

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', () => {
    // Add button to main UI
    const button = document.createElement('button');
    button.className = 'adult-features-toggle-button';
    button.innerHTML = '🔞';
    button.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: rgba(0, 0, 0, 0.7);
        color: #0ff;
        border: 2px solid #0ff;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        z-index: 1000;
        font-size: 20px;
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
    `;
    document.body.appendChild(button);
    
    // Add click event to toggle
    button.addEventListener('click', () => {
        // Make sure UI is initialized
        if (!window.adultFeaturesUI.isInitialized) {
            window.adultFeaturesUI.initialize();
        }
        
        // Toggle visibility
        window.adultFeaturesUI.show();
    });
});

// Expose global methods
window.showAdultFeatures = () => {
    if (!window.adultFeaturesUI.isInitialized) {
        window.adultFeaturesUI.initialize();
    }
    window.adultFeaturesUI.show();
};

window.hideAdultFeatures = () => {
    if (window.adultFeaturesUI.isInitialized) {
        window.adultFeaturesUI.hide();
    }
};

window.setAdultFeatureConsent = (feature, hasConsent) => {
    if (!window.adultFeaturesUI.isInitialized) {
        window.adultFeaturesUI.initialize();
    }
    window.adultFeaturesUI.updateConsent(feature, hasConsent);
};
