import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GLib, Pango
import threading
import os
import sys
from datetime import datetime
import json

# Try to import AI modules if available
try:
    import google.generativeai as genai
    from openai import OpenAI
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

class ChatPanel:
    def __init__(self, parent):
        self.parent = parent
        self.panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # Set default model
        self.current_model = "Gemini"
        
        # Create panel widgets
        self.create_header()
        self.create_message_area()
        self.create_input_area()
        self.create_media_controls()
        
        # Apply custom styling
        self.apply_styling()
        
        # Add welcome message
        self._add_welcome_message()
        
        # Initialize AI modules
        GLib.idle_add(self.init_ai_modules)
        
        # Connect event handlers for GTK 4
        click_controller = Gtk.GestureClick.new()
        click_controller.connect("pressed", self.on_panel_clicked)
        self.panel.add_controller(click_controller)
        
        # Initialize AI models dictionary and individual models
        self.ai_models = {}
        self.vision_model = None
        self.chat_model = None
        self.memory_manager = None
        self.mcp_client = None
        
        # AI response variables
        self.ai_response_in_progress = False
        
        # Initialize core components with safe defaults
        self.safety_manager = None
        self.google_api = None
        self.google_services = None
        self.multi_api_auth = None
        
        # Initialize MCP integration
        self.mcp = None
        try:
            # Import MCPIntegration dynamically
            script_dir = os.path.dirname(os.path.abspath(__file__))
            sys.path.append(os.path.join(script_dir, 'ai'))
            from ai.mcp_integration import MCPIntegration
            self.mcp = MCPIntegration()
            print("MCP Integration initialized successfully")
        except Exception as e:
            print(f"Error initializing MCP integration: {e}")
        
        # Set input area widgets to be focusable and receive events
        self.make_widgets_interactive()

    def make_widgets_interactive(self):
        """Make all widgets in the panel interactive and focusable"""
        
        def configure_widget(widget):
            # Set the widget as focusable
            widget.set_can_focus(True)
            
            # Add controllers for GTK 4
            key_controller = Gtk.EventControllerKey.new()
            widget.add_controller(key_controller)
            
            motion_controller = Gtk.EventControllerMotion.new()
            widget.add_controller(motion_controller)
            
            click_controller = Gtk.GestureClick.new()
            widget.add_controller(click_controller)
        
        # List of possible buttons that might exist
        possible_buttons = ['send_button', 'mic_button', 'camera_button', 'screen_button', 
                          'clear_button', 'export_button']
        
        # Make sure buttons can receive events (only for buttons that exist)
        for button_name in possible_buttons:
            if hasattr(self, button_name):
                widget = getattr(self, button_name)
                if widget:
                    configure_widget(widget)
        
        # Make sure entry can receive events
        self.message_entry.set_can_focus(True)
        
        # Make model combo box interactive
        if hasattr(self, 'model_combo') and self.model_combo:
            configure_widget(self.model_combo)

    def create_message_area(self):
        """Create the message display area"""
        # Scrolled window for messages
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.set_min_content_height(400)
        
        # Message container
        self.message_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.message_container.set_margin_start(10)
        self.message_container.set_margin_end(10)
        self.message_container.set_margin_top(10)
        self.message_container.set_margin_bottom(10)
        self.scrolled_window.set_child(self.message_container)
        
        self.panel.append(self.scrolled_window)

    def create_input_area(self):
        """Create the text input area"""
        # Create text entry
        self.message_entry = Gtk.Entry()
        self.message_entry.set_placeholder_text("Type your message here...")
        
        # Connect to key event controller for GTK 4
        key_controller = Gtk.EventControllerKey.new()
        key_controller.connect("key-pressed", self.on_key_press)
        self.message_entry.add_controller(key_controller)
        
        # Create send button
        self.send_button = Gtk.Button(label="Send")
        self.send_button.connect("clicked", self.on_send_clicked)
        
        # Create container
        input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        input_box.set_spacing(5)
        input_box.set_margin_start(10)
        input_box.set_margin_end(10)
        input_box.set_margin_bottom(10)
        
        # Pack widgets
        input_box.append(self.message_entry)
        self.message_entry.set_hexpand(True)
        input_box.append(self.send_button)
        
        # Add to panel
        self.panel.append(input_box)

    def create_media_controls(self):
        """Create the media control buttons (mic, camera, etc.)"""
        media_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        media_box.set_spacing(5)
        media_box.set_margin_start(10)
        media_box.set_margin_end(10)
        media_box.set_margin_bottom(10)
        
        # Add click controller for GTK 4
        click_controller = Gtk.GestureClick.new()
        media_box.add_controller(click_controller)
        
        # Create styled buttons
        def create_styled_button(icon_name, tooltip):
            button = Gtk.Button()
            button.set_tooltip_text(tooltip)
            
            # Create an image for the icon using pixel size instead of icon size
            icon = Gtk.Image.new_from_icon_name(icon_name)
            icon.set_pixel_size(24)  # Equivalent to LARGE_TOOLBAR
            button.set_child(icon)
            
            # Add controller for GTK 4
            btn_click = Gtk.GestureClick.new()
            button.add_controller(btn_click)
            
            return button
        
        # Create media buttons
        self.mic_button = create_styled_button("microphone-sensitivity-high-symbolic", "Voice input")
        self.mic_button.connect("clicked", self.on_mic_clicked)
        
        self.camera_button = create_styled_button("camera-photo-symbolic", "Camera input")
        self.camera_button.connect("clicked", self.on_camera_clicked)
        
        self.screen_button = create_styled_button("video-display-symbolic", "Screen capture")
        self.screen_button.connect("clicked", self.on_screen_clicked)
        
        self.clear_button = create_styled_button("edit-clear-all-symbolic", "Clear conversation")
        self.clear_button.connect("clicked", self.on_clear_clicked)
        
        self.export_button = create_styled_button("document-save-symbolic", "Export conversation")
        self.export_button.connect("clicked", self.on_export_clicked)
        
        # Pack buttons
        media_box.append(self.mic_button)
        media_box.append(self.camera_button)
        media_box.append(self.screen_button)
        media_box.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        media_box.append(self.clear_button)
        media_box.append(self.export_button)
        
        # Add to panel
        self.panel.append(media_box)
    
    def create_header(self):
        """Create the chat panel header"""
        self.header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.header.set_margin_start(10)
        self.header.set_margin_end(10)
        self.header.set_margin_top(10)
        self.header.set_margin_bottom(10)
        
        # Add title
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>Chat</span>")
        title.set_halign(Gtk.Align.START)
        self.header.append(title)
        title.set_hexpand(True)
        
        # Create model selector
        model_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        model_box.set_spacing(5)
        
        model_label = Gtk.Label(label="Model:")
        model_box.append(model_label)
        
        # Create combo box for model selection
        self.model_combo = Gtk.ComboBoxText()
        # Add default models
        available_models = ["Gemini", "GPT", "Local LLM"]
        for model in available_models:
            self.model_combo.append_text(model)
        # Set active model
        active_index = available_models.index(self.current_model)
        self.model_combo.set_active(active_index)
        self.model_combo.connect("changed", self.on_model_changed)
        model_box.append(self.model_combo)
        
        self.header.append(model_box)
        self.panel.append(self.header)
    
    def on_panel_clicked(self, controller, n_press, x, y):
        """Handle panel clicks"""
        # This focus handling might not be needed in GTK 4 as the
        # widget hierarchy should handle focus automatically
        self.message_entry.grab_focus()
        return True
    
    def add_message(self, sender, text):
        """Add a message to the chat"""
        # Create message box
        message_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        message_box.set_margin_bottom(10)
        
        # Add sender label
        sender_label = Gtk.Label()
        sender_label.set_markup(f"<b>{sender}</b>")
        sender_label.set_halign(Gtk.Align.START)
        message_box.append(sender_label)
        
        # Add message text
        message_label = Gtk.Label()
        message_label.set_markup(text)
        message_label.set_halign(Gtk.Align.START)
        message_label.set_wrap(True)
        message_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        message_box.append(message_label)
        
        # Add message to container
        self.message_container.append(message_box)
        message_box.show()
        sender_label.show()
        message_label.show()
        
        # Scroll to bottom
        adj = self.scrolled_window.get_vadjustment()
        adj.set_value(adj.get_upper())
    
    def apply_styling(self):
        """Apply custom CSS styling to the chat panel"""
        css_provider = Gtk.CssProvider()
        css = """
            .chat-panel {
                background-color: rgba(0, 0, 0, 0.8);
                border-radius: 10px;
                padding: 10px;
            }
            .chat-header {
                background-color: rgba(0, 0, 0, 0.6);
                border-radius: 5px;
                padding: 5px;
                margin-bottom: 10px;
            }
            .message-entry {
                background-color: rgba(30, 30, 30, 0.9);
                color: #00ff00;
                border: 1px solid #00ff00;
                border-radius: 5px;
                padding: 5px;
                margin: 5px;
            }
            .send-button {
                background-color: rgba(0, 255, 0, 0.2);
                color: #00ff00;
                border: 1px solid #00ff00;
                border-radius: 5px;
                padding: 5px 10px;
                margin: 5px;
            }
            .send-button:hover {
                background-color: rgba(0, 255, 0, 0.4);
            }
            .media-button {
                background-color: rgba(0, 150, 255, 0.2);
                color: #0096ff;
                border: 1px solid #0096ff;
                border-radius: 5px;
                padding: 5px;
                margin: 2px;
            }
            .media-button:hover {
                background-color: rgba(0, 150, 255, 0.4);
            }
            scrolledwindow {
                border: none;
                background: transparent;
            }
            scrollbar {
                background-color: transparent;
                border: none;
            }
            scrollbar slider {
                background-color: rgba(0, 255, 0, 0.3);
                border-radius: 10px;
                min-width: 8px;
                min-height: 8px;
            }
            scrollbar slider:hover {
                background-color: rgba(0, 255, 0, 0.5);
            }
        """
        css_provider.load_from_data(css.encode())
        
        # Apply styles to widgets
        self.panel.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.panel.get_style_context().add_class("chat-panel")
        
        self.header.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.header.get_style_context().add_class("chat-header")
        
        self.message_entry.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.message_entry.get_style_context().add_class("message-entry")
        
        self.send_button.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.send_button.get_style_context().add_class("send-button")
        
        # Apply styles to media buttons if they exist
        for button in [self.mic_button, self.camera_button, self.screen_button]:
            if button:
                button.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
                button.get_style_context().add_class("media-button")
    
    def _add_welcome_message(self):
        """Add the initial welcome message"""
        welcome_text = """Welcome to Hextrix AI Assistant! I'm here to help you with:

- Natural conversations and task assistance
- File and system management
- Integration with your apps and services
- Personalized experiences and learning
- Advanced AI features including vision and voice

How can I assist you today?"""
        self.add_message("Hextrix", welcome_text)
        return False
    
    def init_ai_modules(self):
        """Initialize all AI modules"""
        try:
            # Make sure ai_models dictionary exists
            if not hasattr(self, 'ai_models'):
                self.ai_models = {}
                
            # First try to load Google API key from environment variable
            google_api_key = os.environ.get("GOOGLE_API_KEY")
            
            # If not in environment, check credentials2.json file
            if not google_api_key:
                credentials_path = '/home/jared/hextrix-ai-os-env/hud/credentials2.json'
                if os.path.exists(credentials_path):
                    with open(credentials_path, 'r') as f:
                        credentials_data = json.load(f)
                        if 'api_keys' in credentials_data and 'google' in credentials_data['api_keys']:
                            google_api_key = credentials_data['api_keys']['google']
            
            # If still not found, check ~/.config/hextrix/api_keys.json
            if not google_api_key:
                api_key_path = os.path.join(os.path.expanduser("~"), ".config", "hextrix", "api_keys.json")
                if os.path.exists(api_key_path):
                    with open(api_key_path, 'r') as f:
                        api_keys = json.load(f)
                        if "GOOGLE_API_KEY" in api_keys:
                            google_api_key = api_keys["GOOGLE_API_KEY"]
            
            # Initialize Google APIs if we have a key
            if google_api_key and AI_AVAILABLE:
                try:
                    print(f"Configuring Gemini API with key: {google_api_key[:5]}...{google_api_key[-5:]}")
                    genai.configure(api_key=google_api_key)
                    
                    # Try multiple model names in order of preference
                    gemini_model_names = [
                        'gemini-2.0-flash-exp', # Experimental version as of 2025-03-15
                        'gemini-2.0-flash-thinking-exp-01-21', #thinking version as of 2025-03-15
                        'gemini-1.5-pro',  # Fallback to 1.5 if 2.0 not available
                        'gemini-1.0-pro'   # Ultimate fallback
                    ]
                    
                    model_initialized = False
                    successful_model = None
                    
                    # Ensure ai_models dictionary exists
                    if not hasattr(self, 'ai_models'):
                        self.ai_models = {}
                    
                    for model_name in gemini_model_names:
                        try:
                            print(f"Trying to initialize Gemini model: {model_name}")
                            self.ai_models['gemini'] = genai.GenerativeModel(model_name)
                            model_initialized = True
                            successful_model = model_name
                            print(f"Successfully initialized Gemini model: {model_name}")
                            break
                        except Exception as model_err:
                            print(f"Failed to initialize model {model_name}: {model_err}")
                    
                    if not model_initialized:
                        print("Could not initialize any Gemini model. Chat functionality will be limited.")
                        self.add_message("Hextrix", "I was unable to initialize my AI models. I'll try to help in a limited capacity.")
                    else:
                        print(f"Gemini AI initialized with model: {successful_model}")
                except Exception as e:
                    print(f"Error configuring Gemini API: {e}")
                    self.add_message("Hextrix", f"There was an error configuring my AI capabilities: {str(e)}")
            else:
                print("No Google API key found or AI libraries not available. Gemini features will be limited.")
                self.add_message("Hextrix", "I'd like to provide a more intelligent response, but it seems my AI models aren't fully initialized. Please check if the necessary API keys are configured.")
            
            # Initialize core AI components if available
            try:
                # Try to import necessary modules
                sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ai'))
                
                try:
                    from ai.auth import authorize_google_apis
                    from ai.safety_module import Safety_Manager
                    from ai.mem_drive import CloudMemoryManager
                    from ai.google_api_manager import GoogleAPIManager
                    from ai.multi_api_oauth import HextrixOAuth
                    
                    # Initialize components
                    credentials_path = '/home/jared/hextrix-ai-os-env/hud/credentials2.json'
                    self.google_services = authorize_google_apis(credentials_path)
                    self.safety_manager = Safety_Manager()
                    
                    # Initialize memory manager with proper error handling
                    try:
                        memory_path = os.path.join(os.path.dirname(credentials_path), "ai", "cache", "brain_memory_cache.bin")
                        self.memory_manager = CloudMemoryManager(memory_path=memory_path)
                        # Initialize memory explicitly
                        self.memory_manager.initialize_memory()
                        print("Memory manager initialized successfully")
                    except Exception as mem_err:
                        print(f"Memory storage error: {mem_err}")
                        # Create a fallback in-memory storage
                        self.memory_manager = CloudMemoryManager(local_cache_size=1000000)
                    
                    self.google_api = GoogleAPIManager()
                    self.multi_api_auth = HextrixOAuth()
                    
                    # Additional modules if available
                    try:
                        from ai.activity_tracking import ActivityTracker
                        from ai.contacts_integration import ContactsIntegration
                        from ai.drive_integration import DriveIntegration
                        from ai.fitness_integration import FitnessIntegration
                        from ai.gmail_integration import GmailIntegration
                        from ai.photos_integration import PhotosIntegration
                        from ai.erotic_roleplay import EroticRoleplayModule
                        from ai.gender_recognition import GenderRecognitionModule
                        from ai.joi_module import JOIModule
                        
                        self.activity_tracker = ActivityTracker()
                        self.contacts_manager = ContactsIntegration(self.google_api)
                        self.drive_manager = DriveIntegration(self.google_api)
                        self.fitness_manager = FitnessIntegration(self.google_api)
                        self.gmail_manager = GmailIntegration(self.google_api)
                        self.photos_manager = PhotosIntegration(self.google_api)
                        self.erotic_roleplay = EroticRoleplayModule()
                        self.gender_recognition = GenderRecognitionModule()
                        self.joi_module = JOIModule()
                    except Exception as e:
                        print(f"Error initializing integration modules: {e}")
                    
                except Exception as e:
                    print(f"Error importing AI modules: {e}")
                
            except Exception as e:
                print(f"Critical error in AI module initialization: {e}")
            
        except Exception as e:
            print(f"Critical error in AI module initialization: {e}")

    def on_model_changed(self, combo):
        """Handle model selection change"""
        model_name = combo.get_active_text()
        self.current_model = model_name
        self.add_message("Hextrix", f"Switched to {model_name} model")
    
    def on_send_clicked(self, widget):
        """Handle sending a message"""
        text = self.message_entry.get_text().strip()
        if text:
            self.add_message("You", text)
            self.message_entry.set_text("")
            
            # Make sure processing happens in a separate thread to keep UI responsive
            thread = threading.Thread(target=self.process_ai_response, args=(text,))
            thread.daemon = True
            thread.start()
    
    def process_ai_response(self, user_text):
        """Process the user message and generate an AI response"""
        try:
            # Check safety first
            if self.safety_manager and hasattr(self.safety_manager, "content_filter"):
                if not self.safety_manager.content_filter(user_text):
                    GLib.idle_add(self.add_message, "Hextrix", "I'm sorry, but I cannot respond to that request due to safety concerns.")
                    return
                    
            # Check for MCP commands first
            mcp_response = None
            if self.mcp:
                # MCP command patterns
                mcp_command_patterns = [
                    (r"(?i)^(find|search) files?( for)? (.+)$", "search_files"),
                    (r"(?i)^(find|search) (images|photos|pictures) (.+)$", "search_media"),
                    (r"(?i)^(find|search) (videos|movies) (.+)$", "search_media"),
                    (r"(?i)^list (windows|android|native) apps$", "list_apps"),
                    (r"(?i)^(run|open|launch|start) (.+?) app$", "run_app"),
                    (r"(?i)^voice command: (.+)$", "voice_command"),
                    (r"(?i)^(mcp|/mcp|#mcp)[ :]+(.+)$", "raw_command")
                ]
                
                import re
                for pattern, command_type in mcp_command_patterns:
                    match = re.match(pattern, user_text)
                    if match:
                        try:
                            if command_type == "search_files":
                                query = match.group(3)
                                result = self.mcp.search_files(query)
                                mcp_response = f"File search results for '{query}':\n\n"
                                if 'error' in result:
                                    mcp_response += f"Error: {result['error']}"
                                else:
                                    for file in result.get('files', [])[:10]:
                                        mcp_response += f"- {file['path']}\n"
                                    if len(result.get('files', [])) > 10:
                                        mcp_response += f"\n... and {len(result.get('files', [])) - 10} more results."
                                break
                                
                            elif command_type == "search_media":
                                media_type = match.group(2).lower()
                                query = match.group(3)
                                if media_type in ["images", "photos", "pictures"]:
                                    result = self.mcp.search_files(query, file_type="image")
                                else:  # videos
                                    result = self.mcp.search_files(query, file_type="video")
                                    
                                mcp_response = f"{media_type.capitalize()} search results for '{query}':\n\n"
                                if 'error' in result:
                                    mcp_response += f"Error: {result['error']}"
                                else:
                                    for file in result.get('files', [])[:10]:
                                        mcp_response += f"- {file['path']}\n"
                                    if len(result.get('files', [])) > 10:
                                        mcp_response += f"\n... and {len(result.get('files', [])) - 10} more results."
                                break
                                
                            elif command_type == "list_apps":
                                platform = match.group(1).lower()
                                if platform == "windows":
                                    result = self.mcp.list_windows_apps()
                                elif platform == "android":
                                    result = self.mcp.list_android_apps()
                                else:  # native
                                    result = self.mcp.list_native_apps()
                                    
                                mcp_response = f"Installed {platform} applications:\n\n"
                                if 'error' in result:
                                    mcp_response += f"Error: {result['error']}"
                                else:
                                    for app in result.get('apps', [])[:20]:
                                        app_name = app.get('name', 'Unknown')
                                        app_publisher = app.get('publisher', 'Unknown')
                                        mcp_response += f"- {app_name} ({app_publisher})\n"
                                    if len(result.get('apps', [])) > 20:
                                        mcp_response += f"\n... and {len(result.get('apps', [])) - 20} more apps."
                                break
                                
                            elif command_type == "run_app":
                                app_name = match.group(2)
                                result = self.mcp.run_app(app_name)
                                if 'error' in result:
                                    mcp_response = f"Error launching {app_name}: {result['error']}"
                                else:
                                    mcp_response = f"Launched {app_name} successfully."
                                break
                                
                            elif command_type == "voice_command":
                                command = match.group(1)
                                result = self.mcp.process_voice_command(command)
                                if 'error' in result:
                                    mcp_response = f"Error processing voice command: {result['error']}"
                                else:
                                    mcp_response = f"Command result: {result.get('response', 'Completed successfully.')}"
                                break
                                
                            elif command_type == "raw_command":
                                raw_cmd = match.group(2)
                                # Process the raw command directly through MCP
                                parts = raw_cmd.split(maxsplit=1)
                                if len(parts) > 0:
                                    cmd = parts[0]
                                    args = parts[1] if len(parts) > 1 else ""
                                    
                                    if hasattr(self.mcp, cmd):
                                        try:
                                            method = getattr(self.mcp, cmd)
                                            result = method(args) if args else method()
                                            mcp_response = f"MCP command result:\n\n{json.dumps(result, indent=2)}"
                                        except Exception as e:
                                            mcp_response = f"Error executing MCP command: {str(e)}"
                                    else:
                                        mcp_response = f"Unknown MCP command: {cmd}"
                                break
                        except Exception as e:
                            mcp_response = f"Error processing MCP command: {str(e)}"
                            print(f"MCP command error: {e}")
                            break
            
            # If we got an MCP response, use that instead of calling the AI
            if mcp_response:
                GLib.idle_add(self.add_message, "Hextrix MCP", mcp_response)
                return
                
            # If no MCP response, continue with normal AI processing...
            
            # Use different AI model based on selection
            if self.current_model == "Gemini" and hasattr(self, 'ai_models') and "gemini" in self.ai_models:
                response = self.ai_models["gemini"].generate_content(user_text).text
            elif self.current_model == "GPT" and hasattr(self, 'ai_models') and "gpt" in self.ai_models:
                gpt_response = self.ai_models["gpt"].chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": user_text}]
                )
                response = gpt_response.choices[0].message.content
            elif self.current_model == "Local LLM" and hasattr(self, 'ai_models') and "local_llm" in self.ai_models:
                model_data = self.ai_models["local_llm"]
                inputs = model_data["tokenizer"](user_text, return_tensors="pt")
                outputs = model_data["model"].generate(**inputs, max_new_tokens=512)
                response = model_data["tokenizer"].decode(outputs[0], skip_special_tokens=True)
            else:
                # Fallback if no models are available
                response = f"I received your message: '{user_text}'\n\nI'd like to provide a more intelligent response, but it seems my AI models aren't fully initialized. Please check if the necessary API keys are configured."
                
            # Add to memory if available
            if self.memory_manager:
                try:
                    self.memory_manager.add_memory(
                        {"type": "conversation", "user_input": user_text, "ai_response": response}
                    )
                except Exception as mem_error:
                    print(f"Memory storage error: {mem_error}")
            
            # Display the response
            GLib.idle_add(self.add_message, "Hextrix", response)
            
        except Exception as e:
            error_message = f"I encountered an error processing your request: {str(e)}"
            GLib.idle_add(self.add_message, "Hextrix", error_message)
    
    def simulate_ai_response(self, user_text):
        """Legacy method - redirects to the new processing pipeline"""
        self.process_ai_response(user_text)
        return False
    
    def on_clear_clicked(self, widget):
        """Clear conversation messages"""
        for child in self.message_container.get_children():
            self.message_container.remove(child)
        self.messages = []
        self._add_welcome_message()
    
    def on_export_clicked(self, widget):
        """Export the conversation to a file"""
        filename = f"hextrix_conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(filename, 'w') as f:
                for message in self.messages:
                    f.write(f"{message['timestamp']} - {message['sender']}: {message['text']}\n")
            self.add_message("Hextrix", f"Conversation exported to {filename}")
        except Exception as e:
            self.add_message("Hextrix", f"Error exporting conversation: {e}")
    
    def on_mic_clicked(self, widget):
        """Handle microphone button click for voice input"""
        try:
            # If we have proper audio input capabilities
            import sounddevice as sd
            import scipy.io.wavfile as wav
            
            self.add_message("Hextrix", "Listening... (speak now)")
            
            # Record audio for 5 seconds
            fs = 44100  # Sample rate
            seconds = 5  # Duration of recording
            
            def record_audio():
                recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
                sd.wait()  # Wait until recording is finished
                
                # Save recording temporarily
                temp_path = "/tmp/hextrix_recording.wav"
                wav.write(temp_path, fs, recording)
                
                # Process with speech recognition
                try:
                    import speech_recognition as sr
                    r = sr.Recognizer()
                    with sr.AudioFile(temp_path) as source:
                        audio = r.record(source)
                    text = r.recognize_google(audio)
                    
                    # Set text to input and trigger send
                    GLib.idle_add(self.message_entry.set_text, text)
                    GLib.idle_add(self.on_send_clicked, None)
                except Exception as e:
                    GLib.idle_add(self.add_message, "Hextrix", f"Sorry, I couldn't understand what you said: {str(e)}")
            
            # Start recording in a separate thread
            threading.Thread(target=record_audio, daemon=True).start()
            
        except ImportError:
            self.add_message("Hextrix", "Voice input requires additional libraries (sounddevice, speech_recognition). Please install them to use this feature.")
    
    def on_camera_clicked(self, widget):
        """Handle camera button click for image input"""
        try:
            import cv2
            
            def capture_image():
                # Open camera
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    GLib.idle_add(self.add_message, "Hextrix", "Failed to open camera")
                    return
                
                # Capture frame
                ret, frame = cap.read()
                if not ret:
                    GLib.idle_add(self.add_message, "Hextrix", "Failed to capture image")
                    cap.release()
                    return
                
                # Save image
                temp_path = "/tmp/hextrix_capture.jpg"
                cv2.imwrite(temp_path, frame)
                cap.release()
                
                # Process with vision models if available
                if hasattr(self, 'ai_models') and "gemini" in self.ai_models and AI_AVAILABLE:
                    try:
                        # Convert to format Gemini can use
                        with open(temp_path, "rb") as f:
                            image_data = f.read()
                        
                        # Create Gemini model with vision capability
                        vision_model = genai.GenerativeModel('gemini-pro-vision')
                        response = vision_model.generate_content([
                            "Describe what you see in this image in detail:", 
                            {"mime_type": "image/jpeg", "data": image_data}
                        ])
                        
                        # Show the image analysis
                        GLib.idle_add(self.add_message, "Hextrix", "Here's what I see in the image:\n\n" + response.text)
                    except Exception as e:
                        GLib.idle_add(self.add_message, "Hextrix", f"I captured an image but couldn't analyze it: {str(e)}")
                else:
                    GLib.idle_add(self.add_message, "Hextrix", "Image captured, but I don't have vision models available to analyze it.")
            
            # Start capture in a separate thread
            threading.Thread(target=capture_image, daemon=True).start()
            
        except ImportError:
            self.add_message("Hextrix", "Camera input requires OpenCV. Please install it to use this feature.")
    
    def on_screen_clicked(self, widget):
        """Handle screen sharing button click"""
        try:
            import pyscreenshot
            
            def capture_screen():
                # Capture the screen
                image = pyscreenshot.grab()
                
                # Save image
                temp_path = "/tmp/hextrix_screen.jpg"
                image.save(temp_path)
                
                # Process with vision models if available
                if hasattr(self, 'ai_models') and "gemini" in self.ai_models and AI_AVAILABLE:
                    try:
                        # Convert to format Gemini can use
                        with open(temp_path, "rb") as f:
                            image_data = f.read()
                        
                        # Create Gemini model with vision capability
                        vision_model = genai.GenerativeModel('gemini-pro-vision')
                        response = vision_model.generate_content([
                            "Describe what you see in this screenshot. Focus on the main elements and any text that's visible:", 
                            {"mime_type": "image/jpeg", "data": image_data}
                        ])
                        
                        # Show the image analysis
                        GLib.idle_add(self.add_message, "Hextrix", "Here's what I see in your screenshot:\n\n" + response.text)
                    except Exception as e:
                        GLib.idle_add(self.add_message, "Hextrix", f"I captured your screen but couldn't analyze it: {str(e)}")
                else:
                    GLib.idle_add(self.add_message, "Hextrix", "Screenshot captured, but I don't have vision models available to analyze it.")
            
            # Start capture in a separate thread
            threading.Thread(target=capture_screen, daemon=True).start()
            
        except ImportError:
            self.add_message("Hextrix", "Screen capture requires pyscreenshot library. Please install it to use this feature.")

    def on_key_press(self, controller, keyval, keycode, state):
        """Handle key press events in the chat input"""
        # Check if Enter was pressed
        if keyval == Gdk.KEY_Return or keyval == Gdk.KEY_KP_Enter:
            self.on_send_clicked(None)
            return True
        return False