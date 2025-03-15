#!/usr/bin/env python3
# Hextrix HUD - Main Window

import os
import sys
import json
import threading
import subprocess
import time
from datetime import datetime

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GLib, Pango, Gio, GdkPixbuf

# Import local modules
from neural_network_visualization import NeuralNetworkVisualization
from chat_panel import ChatPanel
from terminal_panel import TerminalPanel
from file_panel import FilePanel
from dock_items import DockCategory, DockItem
from mcp_panel import MCPPanel

# Try to import Qt-based visualization
try:
    from qt_neural_vis import WebNeuralVisualization, QTWEBKIT_AVAILABLE
    WEB_VIS_AVAILABLE = QTWEBKIT_AVAILABLE
    if WEB_VIS_AVAILABLE:
        print("Qt-based neural visualization is available and will be used")
    else:
        print("Qt-based neural visualization is not available, will use fallback")
except ImportError:
    print("Qt neural visualization not available. Using fallback.")
    WEB_VIS_AVAILABLE = False

# Try to import AppDrawer
try:
    from app_drawer import AppDrawer
except ImportError:
    print("Warning: Could not import AppDrawer module. App Drawer functionality will be disabled.")
    AppDrawer = None

class HextrixHUD(Gtk.Window):
    def __init__(self):
        # Initialize GTK Window
        Gtk.Window.__init__(self, title="Hextrix OS Neural Interface")
        self.set_default_size(1920, 1080)
        
        # Make window transparent and borderless in GTK 4.0
        self.set_decorated(False)
        
        # Apply CSS to make the window background transparent
        css_provider = Gtk.CssProvider()
        css = """
            window {
                background-color: rgba(0, 10, 30, 0.85);
            }
        """
        css_provider.load_from_data(css.encode())
        
        # Apply CSS to the window
        self.get_style_context().add_provider(
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        # Start in fullscreen mode
        self.fullscreen()
        
        # Initialize app widgets list
        self.app_widgets = []
        self.current_category = "Hextrix"
        
        # Track running processes
        self.running_processes = {}
        
        # Main container structure (horizontal layout)
        self.main_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.main_container.get_style_context().add_class("main-container")
        self.set_child(self.main_container)
        
        # Terminal panel revealer (left side)
        self.terminal_panel_revealer = Gtk.Revealer()
        self.terminal_panel_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_RIGHT)
        self.terminal_panel_revealer.set_transition_duration(300)
        self.terminal_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.terminal_panel.get_style_context().add_class("terminal-panel")
        self.terminal_panel_revealer.set_child(self.terminal_panel)
        self.terminal_panel.set_size_request(500, -1)
        self.main_container.append(self.terminal_panel_revealer)
        
        # Connect to panel reveal signals
        self.terminal_panel_revealer.connect("notify::child-revealed", self.on_panel_visibility_changed)
        
        # Terminal panel header
        self.terminal_panel_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.terminal_panel_header.set_margin_top(10)
        self.terminal_panel_header.set_margin_start(10)
        self.terminal_panel_header.set_margin_end(10)
        self.terminal_panel_header.set_margin_bottom(5)
        self.terminal_panel_title = Gtk.Label()
        self.terminal_panel_title.set_markup("<span foreground='#00BFFF' font='14'>Terminal</span>")
        self.terminal_panel_title.set_halign(Gtk.Align.START)
        self.terminal_panel_header.append(self.terminal_panel_title)
        self.terminal_panel_close = self.create_tool_button("window-close-symbolic", "Close", self.on_terminal_panel_close)
        self.terminal_panel_header.append(self.terminal_panel_close)
        self.terminal_panel.append(self.terminal_panel_header)
        
        # Central area with the overlay (right side)
        self.central_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.central_area.get_style_context().add_class("central-area")
        self.central_area.set_hexpand(True)
        self.central_area.set_vexpand(True)
        self.main_container.append(self.central_area)
        
        # Top dock container
        self.dock_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.dock_container.set_margin_top(5)
        self.dock_container.set_margin_bottom(5)
        self.dock_container.set_margin_start(5)
        self.dock_container.set_margin_end(5)
        self.dock_container.set_halign(Gtk.Align.CENTER)
        self.dock_container.get_style_context().add_class("dock-container")
        self.central_area.append(self.dock_container)
        
        # Create dock categories
        self.dock_categories = {}
        self.build_dock_categories()
        
        # Load dock items
        self.load_dock_items()
        
        # Main overlay container
        self.overlay = Gtk.Overlay()
        self.central_area.append(self.overlay)
        
        # Neural network visualization (background)
        if WEB_VIS_AVAILABLE:
            # Use the web-based visualization if available
            self.visualization = WebNeuralVisualization()
            self.overlay.set_child(self.visualization)
            
            # No need for animation timer or resize handling with web-based visualization
            self.using_web_vis = True
        else:
            # Fallback to the original visualization
            self.using_web_vis = False
            self.neural_network = NeuralNetworkVisualization(1920, 1080)
            self.visualization = Gtk.DrawingArea()
            
            # Make the drawing area expand to fill available space
            self.visualization.set_hexpand(True)
            self.visualization.set_vexpand(True)
            
            # In GTK 4.0, the draw signal is replaced with set_draw_func
            self.visualization.set_draw_func(self.on_draw_func, None)
            
            # Connect to size allocation for resize handling
            self.visualization.connect("resize", self.on_visualization_resize)
            
            # Add to overlay
            self.overlay.set_child(self.visualization)
            
            # Animation timer
            GLib.timeout_add(50, self.update_animation)
        
        # Create modal panels
        self.chat_panel = ChatPanel(self)
        self.terminal_panel_content = TerminalPanel(self)
        self.file_panel_content = FilePanel(self)
        
        # Add terminal content to the terminal panel
        self.terminal_panel.append(self.terminal_panel_content.panel)
        
        # Desktop/File panel revealer (right side)
        self.desktop_panel_revealer = Gtk.Revealer()
        self.desktop_panel_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_LEFT)
        self.desktop_panel_revealer.set_transition_duration(300)
        self.desktop_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.desktop_panel.get_style_context().add_class("desktop-panel")
        self.desktop_panel_revealer.set_child(self.desktop_panel)
        self.desktop_panel.set_size_request(400, -1)
        self.main_container.append(self.desktop_panel_revealer)
        
        # Connect to panel reveal signals
        self.desktop_panel_revealer.connect("notify::child-revealed", self.on_panel_visibility_changed)
        
        # Desktop panel header
        self.desktop_panel_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.desktop_panel_header.set_margin_top(10)
        self.desktop_panel_header.set_margin_start(10)
        self.desktop_panel_header.set_margin_end(10)
        self.desktop_panel_header.set_margin_bottom(5)
        self.desktop_panel_title = Gtk.Label()
        self.desktop_panel_title.set_text("File Browser")
        self.desktop_panel_title.set_markup("<span foreground='#00BFFF' font='14'>File Browser</span>")
        self.desktop_panel_title.set_halign(Gtk.Align.START)
        self.desktop_panel_header.append(self.desktop_panel_title)
        self.desktop_panel_close = self.create_tool_button("window-close-symbolic", "Close", self.on_desktop_panel_close)
        self.desktop_panel_header.append(self.desktop_panel_close)
        self.desktop_panel.append(self.desktop_panel_header)
        
        # Add file content to desktop panel
        self.desktop_panel.append(self.file_panel_content.panel)
        
        # MCP panel revealer (bottom side)
        self.mcp_panel_revealer = Gtk.Revealer()
        self.mcp_panel_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_UP)
        self.mcp_panel_revealer.set_transition_duration(300)
        self.mcp_panel_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.mcp_panel_container.get_style_context().add_class("mcp-panel")
        self.mcp_panel_revealer.set_child(self.mcp_panel_container)
        self.mcp_panel_container.set_size_request(-1, 600)  # Height of 600px
        
        # Create position container for MCP panel
        self.mcp_position_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.mcp_position_box.set_hexpand(True)
        self.mcp_position_box.set_vexpand(True)
        self.mcp_position_box.set_halign(Gtk.Align.CENTER)
        self.mcp_position_box.set_valign(Gtk.Align.END)
        self.mcp_position_box.append(self.mcp_panel_revealer)
        self.main_container.append(self.mcp_position_box)
        
        # Connect to panel reveal signals
        self.mcp_panel_revealer.connect("notify::child-revealed", self.on_panel_visibility_changed)
        
        # MCP panel header
        self.mcp_panel_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.mcp_panel_header.set_margin_top(10)
        self.mcp_panel_header.set_margin_start(10)
        self.mcp_panel_header.set_margin_end(10)
        self.mcp_panel_header.set_margin_bottom(5)
        self.mcp_panel_title = Gtk.Label()
        self.mcp_panel_title.set_markup("<span foreground='#00BFFF' font='14'>Model Context Protocol</span>")
        self.mcp_panel_title.set_halign(Gtk.Align.START)
        self.mcp_panel_header.append(self.mcp_panel_title)
        self.mcp_panel_close = self.create_tool_button("window-close-symbolic", "Close", self.on_mcp_panel_close)
        self.mcp_panel_header.append(self.mcp_panel_close)
        self.mcp_panel_container.append(self.mcp_panel_header)
        
        # Create and add MCP panel content
        self.mcp_panel_content = MCPPanel(self)
        self.mcp_panel_container.append(self.mcp_panel_content.panel)
        
        # Initialize dock items
        self.dock_items = []
        self.load_dock_items()
        
        # Create app drawer
        if AppDrawer is not None:
            self.app_drawer = AppDrawer(self, self.dock_items)
            self.overlay.add_overlay(self.app_drawer.get_drawer())
        else:
            self.app_drawer = None
        
        # Top buttons (UI and HUD)
        self.top_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.top_buttons.set_halign(Gtk.Align.CENTER)
        self.top_buttons.set_valign(Gtk.Align.START)
        self.top_buttons.set_margin_top(20)
        
        self.ui_button = self.create_circle_button("UI", self.on_ui_clicked)
        self.top_buttons.append(self.ui_button)
        
        self.hud_button = self.create_circle_button("HUD", self.on_hud_clicked)
        self.top_buttons.append(self.hud_button)
        
        self.overlay.add_overlay(self.top_buttons)
        
        # Bottom buttons (Term, Files, Apps, Full)
        self.bottom_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.bottom_buttons.set_halign(Gtk.Align.CENTER)
        self.bottom_buttons.set_valign(Gtk.Align.END)
        self.bottom_buttons.set_margin_bottom(20)
        
        self.term_button = self.create_circle_button("Term", self.on_term_clicked)
        self.bottom_buttons.append(self.term_button)
        
        self.files_button = self.create_circle_button("Files", self.on_files_clicked)
        self.bottom_buttons.append(self.files_button)
        
        self.chat_button = self.create_circle_button("Chat", self.on_chat_clicked)
        self.bottom_buttons.append(self.chat_button)
        
        self.apps_button = self.create_circle_button("Apps", self.on_apps_clicked)
        self.bottom_buttons.append(self.apps_button)
        
        self.mcp_button = self.create_circle_button("MCP", self.on_mcp_clicked)
        self.bottom_buttons.append(self.mcp_button)
        
        self.overlay.add_overlay(self.bottom_buttons)
        
        # Full button (bottom right)
        self.full_button = self.create_circle_button("Full", self.on_full_clicked)
        self.full_button.set_halign(Gtk.Align.END)
        self.full_button.set_valign(Gtk.Align.END)
        self.full_button.set_margin_end(20)
        self.full_button.set_margin_bottom(20)
        
        self.overlay.add_overlay(self.full_button)
        
        # Set up chat panel positioning
        self.chat_panel.panel.set_halign(Gtk.Align.CENTER)
        self.chat_panel.panel.set_valign(Gtk.Align.CENTER)
        self.chat_panel.panel.set_margin_top(50)
        self.chat_panel.panel.set_margin_bottom(50)
        self.chat_panel.panel.set_margin_start(100)
        self.chat_panel.panel.set_margin_end(100)
        # Use a percentage of the screen instead of fixed size
        width = self.get_width() * 0.6 if self.get_width() > 0 else 800
        height = self.get_height() * 0.6 if self.get_height() > 0 else 600
        self.chat_panel.panel.set_size_request(int(width), int(height))
        
        # Add styling to the chat panel
        style_provider = Gtk.CssProvider()
        css = """
            .chat-panel {
                background-color: rgba(0, 10, 30, 0.85);
                border-radius: 8px;
                border: 1px solid rgba(0, 150, 255, 0.5);
            }
            
            .chat-panel:focus {
                border-color: rgba(0, 255, 255, 0.8);
                box-shadow: 0 0 20px rgba(0, 150, 255, 0.3);
            }
        """
        style_provider.load_from_data(css.encode())
        self.chat_panel.panel.get_style_context().add_provider(
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        self.chat_panel.panel.get_style_context().add_class("chat-panel")
        
        # Enable input events for the chat panel
        self.chat_panel.panel.set_can_focus(True)
        
        # In GTK 4.0, we use event controllers instead of add_events
        # Add a motion controller to handle mouse events for the chat panel
        motion_controller = Gtk.EventControllerMotion.new()
        self.chat_panel.panel.add_controller(motion_controller)
        
        # Add a key controller to handle keyboard events for the chat panel
        key_controller = Gtk.EventControllerKey.new()
        self.chat_panel.panel.add_controller(key_controller)
        
        # In GTK 4.0, set_no_show_all is replaced with set_visible
        self.chat_panel.panel.set_visible(False)
        
        self.overlay.add_overlay(self.chat_panel.panel)
        
        # Connect key events - GTK 4.0 style for the entire window
        self.key_controller = Gtk.EventControllerKey.new()
        self.key_controller.connect("key-pressed", self.on_key_press)
        self.add_controller(self.key_controller)
        
        # Default visibility states
        self.terminal_panel_revealer.set_reveal_child(False)
        self.desktop_panel_revealer.set_reveal_child(False)
        self.mcp_panel_revealer.set_reveal_child(False)
        if self.app_drawer:
            self.app_drawer.hide()
        self.chat_panel.panel.set_visible(False)
        
        # Initialize focus
        self.chat_panel.message_entry.grab_focus()
        
        # Add styling for entire window
        style_provider = Gtk.CssProvider()
        css = """
            .main-container {
                background-color: rgba(0, 10, 30, 0.85);
            }
            
            .terminal-panel {
                background-color: rgba(0, 15, 40, 0.95);
                border-right: 1px solid rgba(0, 150, 255, 0.5);
            }
            
            .desktop-panel {
                background-color: rgba(0, 15, 40, 0.95);
                border-left: 1px solid rgba(0, 150, 255, 0.5);
            }
            
            .central-area {
                background-color: transparent;
            }
            
            .dock-container {
                background-color: rgba(0, 20, 50, 0.4);
                border-radius: 15px;
                border: 1px solid rgba(0, 200, 255, 0.3);
                padding: 5px;
                box-shadow: 0 0 10px rgba(0, 150, 255, 0.2);
            }
            
            @keyframes pulse-glow {
                0% { box-shadow: 0 0 2px rgba(0, 255, 255, 0.5), 0 0 5px rgba(0, 255, 255, 0.2); }
                50% { box-shadow: 0 0 5px rgba(0, 255, 255, 0.8), 0 0 10px rgba(0, 255, 255, 0.5); }
                100% { box-shadow: 0 0 2px rgba(0, 255, 255, 0.5), 0 0 5px rgba(0, 255, 255, 0.2); }
            }
            
            button.circle-button {
                border-radius: 50%;
                background: rgba(0, 15, 40, 0.4);
                border: 1px solid #00FFFF;
                padding: 6px;
                margin: 5px;
                animation: pulse-glow 2s infinite ease-in-out;
                transition: all 300ms ease-in-out;
            }
            
            button.circle-button:hover {
                background: rgba(0, 191, 255, 0.4);
                border-color: #FFFFFF;
                box-shadow: 0 0 10px rgba(0, 255, 255, 0.8), 0 0 20px rgba(0, 255, 255, 0.4);
            }
            
            button.circle-button:active {
                background: rgba(0, 100, 200, 0.6);
            }
            
            /* Ensure overlay items don't overlap */
            overlay > widget {
                margin: 5px;
            }
            
            /* Make drawing area take up full space */
            drawing-area {
                background-color: transparent;
                min-width: 100%;
                min-height: 100%;
            }
            
            label {
                margin: 3px;
            }
        """
        style_provider.load_from_data(css.encode())
        self.get_style_context().add_provider(
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    
    def load_dock_items(self):
        """Load dock items from configuration"""
        # Get project directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(script_dir)
        
        # Default configuration file path
        config_path = os.path.join(project_dir, "config", "dock_items.json")
        
        # Create sample items if no config exists
        if not os.path.exists(config_path):
            # Create sample dock items
            sample_items = [
                DockItem("Terminal", "utilities-terminal", "xterm", "xterm.desktop", "Utilities"),
                DockItem("File Manager", "system-file-manager", "thunar", "thunar.desktop", "System"),
                DockItem("Web Browser", "web-browser", "firefox", "firefox.desktop", "Internet"),
                DockItem("Text Editor", "accessories-text-editor", "gedit", "gedit.desktop", "Development"),
                DockItem("Cyberpunk Explorer", "folder-cyan", "python cyberpunk_explorer.py", "cyberpunk-explorer.desktop", "Utilities")
            ]
            
            # Add sample items to categories
            for item in sample_items:
                if item.category in self.dock_categories:
                    self.dock_categories[item.category].add_item(item)
            
            # Create config directory if it doesn't exist
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # Save sample configuration
            try:
                with open(config_path, 'w') as f:
                    items_dict = [item.to_dict() for cat in self.dock_categories.values() for item in cat.items]
                    json.dump(items_dict, f, indent=2)
            except Exception as e:
                print(f"Error saving dock configuration: {e}")
        else:
            # Load dock items from config
            try:
                with open(config_path, 'r') as f:
                    items_data = json.load(f)
                    for item_data in items_data:
                        item = DockItem.from_dict(item_data)
                        if item.category in self.dock_categories:
                            self.dock_categories[item.category].add_item(item)
            except Exception as e:
                print(f"Error loading dock configuration: {e}")
                
            # Add cyberpunk explorer if not already in config
            cyberpunk_exists = False
            for cat in self.dock_categories.values():
                for item in cat.items:
                    if item.name == "Cyberpunk Explorer":
                        cyberpunk_exists = True
                        break
                if cyberpunk_exists:
                    break
            
            if not cyberpunk_exists:
                cyberpunk_item = DockItem("Cyberpunk Explorer", "folder-cyan", "python cyberpunk_explorer.py", "cyberpunk-explorer.desktop", "Utilities")
                if "Utilities" in self.dock_categories:
                    self.dock_categories["Utilities"].add_item(cyberpunk_item)
                    # Save updated configuration
                    try:
                        with open(config_path, 'w') as f:
                            items_dict = [item.to_dict() for cat in self.dock_categories.values() for item in cat.items]
                            json.dump(items_dict, f, indent=2)
                    except Exception as e:
                        print(f"Error saving updated dock configuration: {e}")
    
    def on_apps_clicked(self, button):
        """Toggle the app drawer visibility"""
        if self.app_drawer and hasattr(self.app_drawer, 'toggle'):
            self.app_drawer.toggle()
        else:
            print("Warning: App drawer toggle method not available")
    
    def create_circle_button(self, label_text, callback):
        button = Gtk.Button()
        button.set_size_request(64, 64)  # Fixed size for circular appearance
        
        # Create a label with custom styling
        label = Gtk.Label()
        label.set_markup(f"<span foreground='#00FFFF' font='12'>{label_text}</span>")
        button.set_child(label)
        
        # Connect the callback
        button.connect("clicked", callback)
        
        # Add CSS class
        button.get_style_context().add_class("circle-button")
        
        return button
    
    def on_visualization_resize(self, widget, width, height):
        # Skip if using web visualization
        if hasattr(self, 'using_web_vis') and self.using_web_vis:
            return
            
        # Update neural network visualization size
        self.neural_network.resize(width, height)
        # Queue a redraw
        self.visualization.queue_draw()
    
    def on_window_resize(self, widget, allocation):
        # Skip if using web visualization
        if hasattr(self, 'using_web_vis') and self.using_web_vis:
            return
            
        # Update visualization size when window is resized
        # In GTK 4.0, we use get_width() and get_height() instead of get_allocation()
        width = self.visualization.get_width()
        height = self.visualization.get_height()
        if width > 0 and height > 0:
            self.neural_network.resize(width, height)
            # Queue a redraw
            self.visualization.queue_draw()
    
    def on_panel_visibility_changed(self, revealer, param):
        # Skip if using web visualization
        if hasattr(self, 'using_web_vis') and self.using_web_vis:
            return
            
        # Update visualization with the current width and height
        # In GTK 4.0, we use get_width() and get_height() instead of get_allocation()
        width = self.visualization.get_width()
        height = self.visualization.get_height()
        if width > 0 and height > 0:
            self.neural_network.resize(width, height)
            # Queue a redraw
            self.visualization.queue_draw()
    
    def update_animation(self):
        # Skip if using web visualization
        if hasattr(self, 'using_web_vis') and self.using_web_vis:
            return True
            
        self.neural_network.update()
        self.visualization.queue_draw()
        return True  # Continue the timer
    
    def on_draw_func(self, drawing_area, cr, width, height, data):
        """GTK 4.0 drawing function for the visualization"""
        # Skip if using web visualization
        if hasattr(self, 'using_web_vis') and self.using_web_vis:
            return
            
        self.neural_network.draw(cr, width, height)
        return True
    
    def on_ui_clicked(self, button):
        visible = self.chat_panel.panel.get_visible()
        self.chat_panel.panel.set_visible(not visible)
    
    def on_hud_clicked(self, button):
        pass
    
    def on_term_clicked(self, button):
        currently_visible = self.terminal_panel_revealer.get_reveal_child()
        self.terminal_panel_revealer.set_reveal_child(not currently_visible)
    
    def on_files_clicked(self, button):
        currently_visible = self.desktop_panel_revealer.get_reveal_child()
        self.desktop_panel_revealer.set_reveal_child(not currently_visible)
    
    def on_full_clicked(self, button):
        # In GTK 4.0, we need to check the fullscreen state differently
        # and use is_fullscreen() method
        if self.is_fullscreen():
            self.unfullscreen()
        else:
            self.fullscreen()
    
    def on_terminal_panel_close(self, button):
        self.terminal_panel_revealer.set_reveal_child(False)
    
    def on_desktop_panel_close(self, button):
        self.desktop_panel_revealer.set_reveal_child(False)
    
    def on_mcp_panel_close(self, button):
        """Close the MCP panel"""
        self.mcp_panel_revealer.set_reveal_child(False)
        
        # Clear any ongoing operations if necessary
        if hasattr(self.mcp_panel_content, 'clear_search_results'):
            self.mcp_panel_content.clear_search_results()
    
    def on_key_press(self, controller, keyval, keycode, state):
        """Handle keyboard events"""
        if keyval == Gdk.KEY_Escape:
            self.chat_panel.panel.set_visible(False)
            self.terminal_panel_revealer.set_reveal_child(False)
            self.desktop_panel_revealer.set_reveal_child(False)
            if self.app_drawer:
                self.app_drawer.hide()
            return True
        
        if keyval in (Gdk.KEY_F11, Gdk.KEY_f, Gdk.KEY_F):
            self.on_full_clicked(None)
            return True
        
        if keyval == Gdk.KEY_Tab and state & Gdk.ModifierType.CONTROL_MASK:
            if self.chat_panel.panel.get_visible():
                self.chat_panel.panel.set_visible(False)
                self.terminal_panel_revealer.set_reveal_child(True)
                self.desktop_panel_revealer.set_reveal_child(False)
            elif self.terminal_panel_revealer.get_reveal_child():
                self.terminal_panel_revealer.set_reveal_child(False)
                self.desktop_panel_revealer.set_reveal_child(True)
                self.chat_panel.panel.set_visible(False)
            elif self.desktop_panel_revealer.get_reveal_child():
                self.desktop_panel_revealer.set_reveal_child(False)
                self.chat_panel.panel.set_visible(True)
                self.terminal_panel_revealer.set_reveal_child(False)
            else:
                self.chat_panel.panel.set_visible(True)
            return True
        return False

    def create_tool_button(self, icon_name, tooltip_text, callback):
        button = Gtk.Button()
        # In GTK 4.0, IconSize enum is removed, use set_icon_size instead
        icon = Gtk.Image.new_from_icon_name(icon_name)
        icon.set_pixel_size(16)  # Equivalent to BUTTON size in GTK 3
        button.set_child(icon)
        button.set_tooltip_text(tooltip_text)
        button.connect("clicked", callback)
        
        # Style the tool button
        style_provider = Gtk.CssProvider()
        css = """
            button {
                padding: 4px;
                background: transparent;
                border: none;
                transition: all 200ms ease-in-out;
            }
            button:hover {
                background: rgba(255, 255, 255, 0.1);
            }
            button:active {
                background: rgba(255, 255, 255, 0.2);
            }
        """
        style_provider.load_from_data(css.encode())
        button.get_style_context().add_provider(
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        return button

    def on_chat_clicked(self, button):
        """Toggle the chat panel visibility"""
        currently_visible = self.chat_panel.panel.get_visible()
        self.chat_panel.panel.set_visible(not currently_visible)
        if not currently_visible:
            # When showing chat, hide other panels
            self.terminal_panel_revealer.set_reveal_child(False)
            self.desktop_panel_revealer.set_reveal_child(False)
            if self.app_drawer:
                self.app_drawer.hide()
            # Set focus to the message entry
            self.chat_panel.message_entry.grab_focus()

    def build_dock_categories(self):
        """Initialize the dock categories"""
        # Create default categories
        self.dock_categories = {
            "Hextrix": DockCategory("Hextrix", "applications-system"),
            "System": DockCategory("System", "computer"),
            "Internet": DockCategory("Internet", "web-browser"),
            "Media": DockCategory("Media", "multimedia"),
            "Development": DockCategory("Development", "applications-development"),
            "Office": DockCategory("Office", "applications-office"),
            "Utilities": DockCategory("Utilities", "applications-utilities")
        }
        
        # Create dock items container
        self.dock_items_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.dock_items_container.set_spacing(5)
        self.dock_container.append(self.dock_items_container)
        
        # Add categories to dock container
        for category_id, category in self.dock_categories.items():
            # Create category button
            button = Gtk.Button()
            button.set_tooltip_text(category.name)
            # In GTK 4.0, IconSize enum is removed, use set_icon_size instead
            icon = Gtk.Image.new_from_icon_name(category.icon)
            icon.set_pixel_size(24)  # Equivalent to LARGE_TOOLBAR size in GTK 3
            button.set_child(icon)
            button.connect("clicked", self.on_category_clicked, category_id)
            
            # Add button to dock
            self.dock_container.append(button)
    
    def on_category_clicked(self, button, category_id):
        """Handle dock category button click"""
        self.current_category = category_id
        print(f"Selected category: {category_id}")
        
        # Clear existing items
        # In GTK 4.0, we need to iterate through children differently
        child = self.dock_items_container.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.dock_items_container.remove(child)
            child = next_child
        
        # Add items for selected category
        if category_id in self.dock_categories:
            category = self.dock_categories[category_id]
            for item in category.items:
                item_button = Gtk.Button()
                item_button.set_tooltip_text(item.name)
                
                # Create box for vertical layout
                box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
                box.set_margin_top(5)
                box.set_margin_bottom(5)
                
                # Add icon
                # In GTK 4.0, IconSize enum is removed, use set_icon_size instead
                icon = Gtk.Image.new_from_icon_name(item.icon_path)
                icon.set_pixel_size(24)  # Equivalent to LARGE_TOOLBAR size in GTK 3
                box.append(icon)
                
                # Add label
                label = Gtk.Label()
                label.set_text(item.name)
                label.set_max_width_chars(15)
                label.set_ellipsize(Pango.EllipsizeMode.END)
                box.append(label)
                
                item_button.set_child(box)
                item_button.connect("clicked", self.on_dock_item_clicked, item)
                
                # Style the button
                style_provider = Gtk.CssProvider()
                css = """
                    button {
                        padding: 8px;
                        background: rgba(0, 40, 80, 0.7);
                        border: 1px solid rgba(0, 191, 255, 0.5);
                        border-radius: 5px;
                        transition: all 200ms ease-in-out;
                    }
                    button:hover {
                        background: rgba(0, 70, 130, 0.8);
                        border-color: rgba(0, 255, 255, 0.8);
                    }
                    label {
                        color: #00BFFF;
                        font-size: 12px;
                    }
                """
                style_provider.load_from_data(css.encode())
                item_button.get_style_context().add_provider(
                    style_provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )
                
                self.dock_items_container.append(item_button)
    
    def on_dock_item_clicked(self, button, item):
        """Handle dock item click"""
        print(f"Launching {item.name}")
        item.launch(self)

    def launch_cyberpunk_explorer(self):
        """Launch the cyberpunk file explorer"""
        try:
            # Get script directory for proper path resolution
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(script_dir)
            
            # Close existing instance if running
            if 'cyberpunk_explorer' in self.running_processes:
                self.close_cyberpunk_explorer()
            
            # Launch new instance
            process = subprocess.Popen(["python", "cyberpunk_explorer.py"], cwd=project_dir)
            self.running_processes['cyberpunk_explorer'] = process
            
            # Add close button to dock if not exists
            close_button = None
            # In GTK 4.0, we need to iterate through children differently
            child = self.dock_items_container.get_first_child()
            while child:
                if isinstance(child, Gtk.Button) and child.get_tooltip_text() == "Close Cyberpunk Explorer":
                    close_button = child
                    break
                child = child.get_next_sibling()
            
            if not close_button:
                close_button = Gtk.Button()
                close_button.set_tooltip_text("Close Cyberpunk Explorer")
                
                # Create box for vertical layout
                box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
                box.set_margin_top(5)
                box.set_margin_bottom(5)
                
                # Add icon
                # In GTK 4.0, IconSize enum is removed, use set_icon_size instead
                icon = Gtk.Image.new_from_icon_name("window-close-symbolic")
                icon.set_pixel_size(24)  # Equivalent to LARGE_TOOLBAR size in GTK 3
                box.append(icon)
                
                # Add label
                label = Gtk.Label()
                label.set_text("Close")
                label.set_max_width_chars(15)
                label.set_ellipsize(Pango.EllipsizeMode.END)
                box.append(label)
                
                close_button.set_child(box)
                close_button.connect("clicked", lambda btn: self.close_cyberpunk_explorer())
                
                # Style the button
                style_provider = Gtk.CssProvider()
                css = """
                    button {
                        padding: 8px;
                        background: rgba(80, 0, 0, 0.7);
                        border: 1px solid rgba(255, 0, 0, 0.5);
                        border-radius: 5px;
                        transition: all 200ms ease-in-out;
                    }
                    button:hover {
                        background: rgba(130, 0, 0, 0.8);
                        border-color: rgba(255, 0, 0, 0.8);
                    }
                    label {
                        color: #FF4444;
                        font-size: 12px;
                    }
                """
                style_provider.load_from_data(css.encode())
                close_button.get_style_context().add_provider(
                    style_provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )
                
                self.dock_items_container.append(close_button)
                # In GTK 4.0, widgets are shown by default
                
        except Exception as e:
            error_dialog = Gtk.MessageDialog(
                transient_for=self,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Error launching Cyberpunk Explorer"
            )
            error_dialog.format_secondary_text(str(e))
            error_dialog.run()
            error_dialog.destroy()
    
    def close_cyberpunk_explorer(self):
        """Close the cyberpunk file explorer"""
        if 'cyberpunk_explorer' in self.running_processes:
            process = self.running_processes['cyberpunk_explorer']
            try:
                process.terminate()
                process.wait(timeout=3)  # Wait up to 3 seconds for graceful termination
            except subprocess.TimeoutExpired:
                process.kill()  # Force kill if it doesn't terminate
            except Exception as e:
                print(f"Error closing Cyberpunk Explorer: {e}")
            finally:
                del self.running_processes['cyberpunk_explorer']
            
            # Remove close button
            # In GTK 4.0, we need to iterate through children differently
            child = self.dock_items_container.get_first_child()
            while child:
                next_child = child.get_next_sibling()
                if isinstance(child, Gtk.Button) and child.get_tooltip_text() == "Close Cyberpunk Explorer":
                    self.dock_items_container.remove(child)
                    break
                child = next_child

    def toggle_terminal_panel(self):
        """Toggle terminal panel visibility"""
        currently_visible = self.terminal_panel_revealer.get_reveal_child()
        self.terminal_panel_revealer.set_reveal_child(not currently_visible)
    
    def toggle_desktop_panel(self):
        """Toggle desktop panel visibility"""
        currently_visible = self.desktop_panel_revealer.get_reveal_child()
        self.desktop_panel_revealer.set_reveal_child(not currently_visible)
        
    def toggle_mcp_panel(self):
        """Toggle MCP panel visibility"""
        currently_visible = self.mcp_panel_revealer.get_reveal_child()
        self.mcp_panel_revealer.set_reveal_child(not currently_visible)
        
    def toggle_chat_panel(self):
        """Toggle chat panel visibility"""
        currently_visible = self.chat_panel.panel.get_visible()
        self.chat_panel.panel.set_visible(not currently_visible)

    def on_mcp_clicked(self, button):
        """Toggle MCP panel visibility"""
        # If the MCP panel is currently visible, hide it
        if self.mcp_panel_revealer.get_reveal_child():
            self.mcp_panel_revealer.set_reveal_child(False)
        else:
            # Hide other panels first for clean UI
            self.chat_panel.panel.set_visible(False)
            self.terminal_panel_revealer.set_reveal_child(False)
            self.desktop_panel_revealer.set_reveal_child(False)
            if self.app_drawer:
                self.app_drawer.hide()
            
            # Show the MCP panel
            self.mcp_panel_revealer.set_reveal_child(True)
            
            # Initialize MCP capabilities if they haven't been loaded yet
            if hasattr(self.mcp_panel_content, 'refresh_capabilities'):
                self.mcp_panel_content.refresh_capabilities()