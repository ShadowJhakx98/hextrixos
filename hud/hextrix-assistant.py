#!/usr/bin/env python3
# Hextrix AI Assistant - Voice and Text UI for Hextrix OS

import os
import sys
import json
import subprocess
import threading
import time
import gi
import requests
from urllib.parse import quote

gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk, Gdk, GLib, WebKit2

# Import the MCP client library
sys.path.append('/home/jared/hextrix-ai-os-env/hextrix-mcp')
try:
    from mcp_client import HextrixMCPClient
except ImportError:
    print("Error: Could not import HextrixMCPClient from MCP")
    
# Configuration
HOME_DIR = os.path.expanduser("~")
ASSISTANT_DIR = os.path.join('/home/jared/hextrix-ai-os-env/hud/hextrix-assistant')
ASSISTANT_DATA_DIR = os.path.join(HOME_DIR, '.hextrix-assistant')
ICONS_DIR = os.path.join(ASSISTANT_DATA_DIR, 'icons')
CONFIG_FILE = os.path.join(ASSISTANT_DATA_DIR, 'config.json')
HISTORY_FILE = os.path.join(ASSISTANT_DATA_DIR, 'history.json')
ICON_PATH = os.path.join('/home/jared/hextrix-ai-os-env/hud/hextrix-assistant', 'assistant-icon.png')

# Ensure directories exist
os.makedirs(ASSISTANT_DATA_DIR, exist_ok=True)
os.makedirs(ICONS_DIR, exist_ok=True)

# Initialize MCP client
mcp_client = HextrixMCPClient(base_url="http://localhost:3000")

# Main application class
class HextrixAssistant(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.hextrix.assistant")
        self.connect("activate", self.on_activate)
        
    def on_activate(self, app):
        self.win = HextrixAssistantWindow(application=app)
        self.win.show_all()

class HextrixAssistantWindow(Gtk.ApplicationWindow):
    def __init__(self, application):
        super().__init__(application=application, title="Hextrix AI Assistant")
        self.set_default_size(800, 600)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # Try to set the icon
        try:
            self.set_icon_from_file(ICON_PATH)
        except:
            print("Warning: Could not load assistant icon")
            
        # Initialize UI components
        self.create_header_bar()
        self.create_main_ui()
        
    def create_header_bar(self):
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "Hextrix AI Assistant"
        self.set_titlebar(header)
        
        # Settings button
        settings_button = Gtk.Button()
        settings_icon = Gtk.Image.new_from_icon_name("preferences-system-symbolic", Gtk.IconSize.BUTTON)
        settings_button.add(settings_icon)
        settings_button.set_tooltip_text("Settings")
        settings_button.connect("clicked", self.on_settings_clicked)
        header.pack_end(settings_button)
        
    def create_main_ui(self):
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(self.main_box)
        
        # Create WebKit view for Claude integration
        self.web_view = WebKit2.WebView()
        self.web_view.load_uri("https://claude.ai")
        
        # Create chat interface
        self.chat_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.chat_box.set_margin_top(10)
        self.chat_box.set_margin_bottom(10)
        self.chat_box.set_margin_start(10)
        self.chat_box.set_margin_end(10)
        
        # Chat display scrollable window
        chat_scroll = Gtk.ScrolledWindow()
        chat_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        # Input area
        input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.text_input = Gtk.Entry()
        self.text_input.set_placeholder_text("Ask me anything...")
        self.text_input.connect("activate", self.on_text_submit)
        
        send_button = Gtk.Button()
        send_icon = Gtk.Image.new_from_icon_name("document-send-symbolic", Gtk.IconSize.BUTTON)
        send_button.add(send_icon)
        send_button.connect("clicked", self.on_text_submit)
        
        mic_button = Gtk.Button()
        mic_icon = Gtk.Image.new_from_icon_name("audio-input-microphone-symbolic", Gtk.IconSize.BUTTON)
        mic_button.add(mic_icon)
        mic_button.connect("clicked", self.on_mic_clicked)
        
        input_box.pack_start(self.text_input, True, True, 0)
        input_box.pack_start(mic_button, False, False, 0)
        input_box.pack_start(send_button, False, False, 0)
        
        # Create the stack
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(300)
        
        # Add web view and chat interface to stack
        self.stack.add_named(self.web_view, "claude")
        self.stack.add_named(self.chat_box, "hextrix")
        
        # Stack switcher
        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(self.stack)
        
        # Add everything to the main box
        self.main_box.pack_start(stack_switcher, False, False, 0)
        self.main_box.pack_start(self.stack, True, True, 0)
        self.main_box.pack_start(input_box, False, False, 10)
        
    def on_text_submit(self, widget):
        """Handle text submission"""
        text = self.text_input.get_text().strip()
        if not text:
            return
            
        # Process the command
        self.process_command(text)
        
        # Clear the input
        self.text_input.set_text("")
        
    def on_mic_clicked(self, button):
        """Handle microphone button click"""
        # To be implemented with speech recognition
        print("Microphone clicked - voice recognition to be implemented")
        
    def on_settings_clicked(self, button):
        """Open settings dialog"""
        # To be implemented
        print("Settings clicked - to be implemented")
        
    def process_command(self, text):
        """Process text command"""
        # Basic command handling to be expanded
        print(f"Processing command: {text}")
        
# Entry point
def main():
    app = HextrixAssistant()
    app.run(sys.argv)

if __name__ == "__main__":
    main() 