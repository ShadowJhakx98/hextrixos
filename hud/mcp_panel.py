#!/usr/bin/env python3
# MCP Panel for Hextrix HUD

import os
import sys
import json
import threading
import subprocess
import re
from datetime import datetime

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GLib, Pango

# Import MCP integration
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ai'))
try:
    from ai.mcp_integration import MCPIntegration
    from ai.app_mcp_extension import HextrixMCPExtension
    from file_carousel import FileCarousel
    MCP_AVAILABLE = True
except ImportError as e:
    print(f"MCP integration not available: {e}")
    MCP_AVAILABLE = False

class MCPPanel:
    """Panel for controlling and interacting with the MCP (Model Context Protocol)"""
    
    def __init__(self, parent):
        """Initialize the MCP panel"""
        self.parent = parent
        self.panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # Initialize MCP integration
        self.mcp = None
        self.mcp_integration = None
        if MCP_AVAILABLE:
            try:
                print("Initializing MCP integration...")
                self.mcp_integration = MCPIntegration()
                print(f"MCP integration initialized: {self.mcp_integration}")
                
                self.mcp = self.mcp_integration.mcp
                print(f"MCP client: {self.mcp}")
                
                if self.mcp:
                    print(f"MCP client type: {type(self.mcp)}")
                    print(f"MCP client has search_files: {hasattr(self.mcp, 'search_files')}")
                    
                    # Test MCP capabilities
                    try:
                        capabilities = self.mcp.get_capabilities()
                        print(f"MCP capabilities: {capabilities}")
                    except Exception as e:
                        print(f"Error getting MCP capabilities: {e}")
            except Exception as e:
                import traceback
                print(f"Error initializing MCP integration: {e}")
                print(traceback.format_exc())
        
        # Create the main content area
        self.content_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.content_area.set_hexpand(True)
        self.content_area.set_vexpand(True)
        
        # Create the status bar
        self.status_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.status_bar.set_margin_start(10)
        self.status_bar.set_margin_end(10)
        self.status_bar.set_margin_top(5)
        self.status_bar.set_margin_bottom(5)
        
        # Create status label
        self.status_label = Gtk.Label()
        self.status_label.set_markup("<b>Status:</b> Initializing...")
        self.status_label.set_halign(Gtk.Align.START)
        self.status_label.set_hexpand(True)
        self.status_bar.append(self.status_label)
        
        # Create refresh button
        self.refresh_button = Gtk.Button.new_from_icon_name("view-refresh-symbolic")
        self.refresh_button.set_tooltip_text("Refresh MCP capabilities")
        self.refresh_button.connect("clicked", self.on_refresh_clicked)
        self.status_bar.append(self.refresh_button)
        
        # Add status bar to panel
        self.panel.append(self.status_bar)
        
        # Create notebook for different sections
        self.notebook = Gtk.Notebook()
        self.notebook.set_hexpand(True)
        self.notebook.set_vexpand(True)
        
        # Create search page
        search_page = self.create_search_area()
        search_label = Gtk.Label(label="Search")
        self.notebook.append_page(search_page, search_label)
        
        # Create app control page
        app_page = self.create_app_controls()
        app_label = Gtk.Label(label="Apps")
        self.notebook.append_page(app_page, app_label)
        
        # Create command page
        command_page = self.create_command_area()
        command_label = Gtk.Label(label="Commands")
        self.notebook.append_page(command_page, command_label)
        
        # Add notebook to panel
        self.panel.append(self.notebook)
        
        # Refresh capabilities
        self.refresh_capabilities()
    
    def create_header(self):
        """Create the panel header"""
        self.header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.header.set_margin_start(10)
        self.header.set_margin_end(10)
        self.header.set_margin_top(10)
        self.header.set_margin_bottom(10)
        
        # Add title
        title = Gtk.Label()
        title.set_markup("<span size='large' weight='bold'>Model Context Protocol</span>")
        title.set_halign(Gtk.Align.START)
        self.header.append(title)
        title.set_hexpand(True)
        
        # Add view logs button
        self.logs_button = self.create_tool_button("document-properties-symbolic", "View Logs", self.on_view_logs_clicked)
        self.header.append(self.logs_button)
        
        # Add refresh button
        self.refresh_button = self.create_tool_button("view-refresh-symbolic", "Refresh Capabilities", self.on_refresh_clicked)
        self.header.append(self.refresh_button)
        
        self.panel.append(self.header)
    
    def create_status_area(self):
        """Create the status display area"""
        # Create frame for status
        status_frame = Gtk.Frame()
        status_frame.set_margin_start(10)
        status_frame.set_margin_end(10)
        status_frame.set_margin_bottom(10)
        
        # Add label to frame
        self.status_label = Gtk.Label()
        self.status_label.set_margin_start(10)
        self.status_label.set_margin_end(10)
        self.status_label.set_margin_top(10)
        self.status_label.set_margin_bottom(10)
        self.status_label.set_halign(Gtk.Align.START)
        self.status_label.set_wrap(True)
        self.status_label.set_markup("<b>Status:</b> Initializing MCP...")
        
        status_frame.set_child(self.status_label)
        self.panel.append(status_frame)
    
    def create_search_area(self):
        """Create the search area for the MCP panel"""
        # Create search area container
        self.search_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.search_area.set_margin_top(10)
        self.search_area.set_margin_start(10)
        self.search_area.set_margin_end(10)
        self.search_area.set_margin_bottom(10)
        
        # Create search title
        search_title = Gtk.Label()
        search_title.set_markup("<span foreground='#00BFFF' font='12'>Search Files</span>")
        search_title.set_halign(Gtk.Align.START)
        search_title.set_margin_bottom(5)
        self.search_area.append(search_title)
        
        # Create search instructions
        search_instructions = Gtk.Label()
        search_instructions.set_markup("<span font='10'>Use prefixes for advanced search: news:, web:, research:, rag:</span>")
        search_instructions.set_halign(Gtk.Align.START)
        search_instructions.set_margin_bottom(10)
        self.search_area.append(search_instructions)
        
        # Create search input
        self.search_input = Gtk.Entry()
        self.search_input.set_placeholder_text("Search files...")
        self.search_input.connect("activate", self.on_search_activate)
        self.search_area.append(self.search_input)
        
        # Create search button
        search_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        search_button_box.set_halign(Gtk.Align.END)
        search_button_box.set_margin_top(5)
        search_button_box.set_margin_bottom(10)
        
        self.search_button = Gtk.Button.new_with_label("Search")
        self.search_button.connect("clicked", self.on_search_clicked)
        search_button_box.append(self.search_button)
        
        self.search_area.append(search_button_box)
        
        # Create search status
        self.search_status = Gtk.Label()
        self.search_status.set_markup("<span font='10'>Enter a search query to find files</span>")
        self.search_status.set_halign(Gtk.Align.START)
        self.search_status.set_margin_top(5)
        self.search_status.set_margin_bottom(5)
        self.search_area.append(self.search_status)
        
        # Create file carousel for visual display of search results
        self.file_carousel = FileCarousel()
        self.file_carousel.set_margin_top(10)
        self.file_carousel.set_margin_bottom(10)
        self.file_carousel.set_vexpand(True)
        self.search_area.append(self.file_carousel)
        
        # Create search results scrolled window (for text results)
        self.search_scroll = Gtk.ScrolledWindow()
        self.search_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.search_scroll.set_min_content_height(100)
        self.search_scroll.set_vexpand(True)
        
        # Create search results text view
        self.search_buffer = Gtk.TextBuffer()
        self.search_result = Gtk.TextView.new_with_buffer(self.search_buffer)
        self.search_result.set_editable(False)
        self.search_result.set_cursor_visible(False)
        self.search_result.set_wrap_mode(Gtk.WrapMode.WORD)
        self.search_scroll.set_child(self.search_result)
        
        # Create stack to switch between carousel and text view
        self.search_results_stack = Gtk.Stack()
        self.search_results_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.search_results_stack.set_transition_duration(300)
        
        self.search_results_stack.add_titled(self.file_carousel, "carousel", "Carousel View")
        self.search_results_stack.add_titled(self.search_scroll, "text", "Text View")
        
        self.search_area.append(self.search_results_stack)
        
        # Create view switcher
        self.view_switcher = Gtk.StackSwitcher()
        self.view_switcher.set_stack(self.search_results_stack)
        self.view_switcher.set_halign(Gtk.Align.CENTER)
        self.view_switcher.set_margin_top(5)
        self.search_area.append(self.view_switcher)
        
        # Create open button for the selected file
        self.open_file_button = Gtk.Button.new_with_label("Open Selected File")
        self.open_file_button.connect("clicked", self.on_open_file_clicked)
        self.open_file_button.set_halign(Gtk.Align.CENTER)
        self.open_file_button.set_margin_top(10)
        self.search_area.append(self.open_file_button)
        
        return self.search_area
    
    def create_app_controls(self):
        """Create the app control area"""
        # Create app control container
        self.app_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.app_area.set_margin_top(10)
        self.app_area.set_margin_start(10)
        self.app_area.set_margin_end(10)
        self.app_area.set_margin_bottom(10)
        
        # Create app control title
        app_title = Gtk.Label()
        app_title.set_markup("<span foreground='#00BFFF' font='12'>Application Control</span>")
        app_title.set_halign(Gtk.Align.START)
        app_title.set_margin_bottom(10)
        self.app_area.append(app_title)
        
        # Create app type selector
        app_type_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        app_type_box.set_spacing(10)
        app_type_box.set_margin_bottom(10)
        
        app_type_label = Gtk.Label(label="App Type:")
        app_type_box.append(app_type_label)
        
        self.app_type_combo = Gtk.ComboBoxText()
        self.app_type_combo.append_text("Native")
        self.app_type_combo.append_text("Windows")
        self.app_type_combo.append_text("Android")
        self.app_type_combo.set_active(0)
        self.app_type_combo.connect("changed", self.on_app_type_changed)
        app_type_box.append(self.app_type_combo)
        
        self.app_area.append(app_type_box)
        
        # Create app search box
        app_search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        app_search_box.set_spacing(10)
        app_search_box.set_margin_bottom(10)
        
        self.app_search_entry = Gtk.Entry()
        self.app_search_entry.set_placeholder_text("Search for apps...")
        self.app_search_entry.set_hexpand(True)
        self.app_search_entry.connect("activate", self.on_app_search_activate)
        app_search_box.append(self.app_search_entry)
        
        self.app_search_button = Gtk.Button.new_with_label("Search")
        self.app_search_button.connect("clicked", self.on_app_search_clicked)
        app_search_box.append(self.app_search_button)
        
        self.app_area.append(app_search_box)
        
        # Create app action buttons
        app_action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        app_action_box.set_spacing(10)
        app_action_box.set_margin_bottom(10)
        
        self.app_launch_button = Gtk.Button.new_with_label("Launch")
        self.app_launch_button.connect("clicked", self.on_app_launch_clicked)
        app_action_box.append(self.app_launch_button)
        
        self.app_install_button = Gtk.Button.new_with_label("Install")
        self.app_install_button.connect("clicked", self.on_app_install_clicked)
        app_action_box.append(self.app_install_button)
        
        self.app_uninstall_button = Gtk.Button.new_with_label("Uninstall")
        self.app_uninstall_button.connect("clicked", self.on_app_uninstall_clicked)
        app_action_box.append(self.app_uninstall_button)
        
        self.app_area.append(app_action_box)
        
        # Create app results area
        self.app_scroll = Gtk.ScrolledWindow()
        self.app_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.app_scroll.set_min_content_height(200)
        self.app_scroll.set_vexpand(True)
        
        self.app_buffer = Gtk.TextBuffer()
        self.app_result = Gtk.TextView.new_with_buffer(self.app_buffer)
        self.app_result.set_editable(False)
        self.app_result.set_cursor_visible(False)
        self.app_result.set_wrap_mode(Gtk.WrapMode.WORD)
        self.app_scroll.set_child(self.app_result)
        
        self.app_area.append(self.app_scroll)
        
        return self.app_area

    def create_command_area(self):
        """Create the command execution area"""
        # Create command area container
        self.command_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.command_area.set_margin_top(10)
        self.command_area.set_margin_start(10)
        self.command_area.set_margin_end(10)
        self.command_area.set_margin_bottom(10)
        
        # Create command title
        command_title = Gtk.Label()
        command_title.set_markup("<span foreground='#00BFFF' font='12'>Execute Commands</span>")
        command_title.set_halign(Gtk.Align.START)
        command_title.set_margin_bottom(5)
        self.command_area.append(command_title)
        
        # Create command instructions
        command_instructions = Gtk.Label()
        command_instructions.set_markup("<span font='10'>Enter system commands to execute</span>")
        command_instructions.set_halign(Gtk.Align.START)
        command_instructions.set_margin_bottom(10)
        self.command_area.append(command_instructions)
        
        # Create command input
        self.command_input = Gtk.Entry()
        self.command_input.set_placeholder_text("Enter command...")
        self.command_input.connect("activate", self.on_command_activate)
        self.command_area.append(self.command_input)
        
        # Create command button
        command_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        command_button_box.set_halign(Gtk.Align.END)
        command_button_box.set_margin_top(5)
        command_button_box.set_margin_bottom(10)
        
        self.command_button = Gtk.Button.new_with_label("Execute")
        self.command_button.connect("clicked", self.on_command_clicked)
        command_button_box.append(self.command_button)
        
        self.command_area.append(command_button_box)
        
        # Create command status
        self.command_status = Gtk.Label()
        self.command_status.set_markup("<span font='10'>Enter a command to execute</span>")
        self.command_status.set_halign(Gtk.Align.START)
        self.command_status.set_margin_top(5)
        self.command_status.set_margin_bottom(5)
        self.command_area.append(self.command_status)
        
        # Create command results area
        self.command_scroll = Gtk.ScrolledWindow()
        self.command_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.command_scroll.set_min_content_height(200)
        self.command_scroll.set_vexpand(True)
        
        self.command_buffer = Gtk.TextBuffer()
        self.command_result = Gtk.TextView.new_with_buffer(self.command_buffer)
        self.command_result.set_editable(False)
        self.command_result.set_cursor_visible(False)
        self.command_result.set_wrap_mode(Gtk.WrapMode.WORD)
        self.command_scroll.set_child(self.command_result)
        
        self.command_area.append(self.command_scroll)
        
        return self.command_area
    
    def apply_styling(self):
        """Apply custom CSS styling to the panel"""
        css_provider = Gtk.CssProvider()
        css = """
            frame {
                border-radius: 6px;
                border: 1px solid rgba(0, 191, 255, 0.3);
            }
            
            entry {
                background-color: rgba(30, 30, 30, 0.9);
                color: #00ff00;
                border: 1px solid #00bfff;
                border-radius: 4px;
                padding: 5px;
            }
            
            button {
                background-color: rgba(0, 191, 255, 0.2);
                color: #00bfff;
                border: 1px solid #00bfff;
                border-radius: 4px;
                padding: 5px 10px;
            }
            
            button:hover {
                background-color: rgba(0, 191, 255, 0.4);
            }
            
            textview {
                background-color: rgba(0, 0, 0, 0.6);
                color: #ffffff;
                border: 1px solid rgba(0, 191, 255, 0.3);
                border-radius: 4px;
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
                background-color: rgba(0, 191, 255, 0.3);
                border-radius: 10px;
                min-width: 8px;
                min-height: 8px;
            }
            
            scrollbar slider:hover {
                background-color: rgba(0, 191, 255, 0.5);
            }
        """
        css_provider.load_from_data(css.encode())
        
        # Apply styles to the panel
        self.panel.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    
    def create_tool_button(self, icon_name, tooltip_text, callback):
        """Create a tool button with an icon"""
        button = Gtk.Button()
        button.set_tooltip_text(tooltip_text)
        
        # Create an image for the icon
        icon = Gtk.Image.new_from_icon_name(icon_name)
        icon.set_pixel_size(16)
        button.set_child(icon)
        
        # Connect button click
        button.connect("clicked", callback)
        
        return button
    
    def on_refresh_clicked(self, button):
        """Handle refresh button click"""
        self.refresh_capabilities()
    
    def refresh_capabilities(self):
        """Refresh MCP capabilities"""
        if not self.mcp:
            self.status_label.set_markup("<b>Status:</b> MCP integration not available")
            return
        
        def _refresh_thread():
            try:
                # Check if the MCP client has a refresh_capabilities method
                if hasattr(self.mcp, 'refresh_capabilities'):
                    success = self.mcp.refresh_capabilities()
                    if success:
                        capabilities = self.mcp.capabilities
                        GLib.idle_add(self._update_status_success, capabilities)
                    else:
                        GLib.idle_add(self._update_status_error, "Failed to refresh capabilities")
                # If not, try to get capabilities directly
                elif hasattr(self.mcp, 'get_capabilities'):
                    capabilities = self.mcp.get_capabilities()
                    GLib.idle_add(self._update_status_success, capabilities)
                # If the MCP integration has capabilities, use those
                elif self.mcp_integration and hasattr(self.mcp_integration, 'capabilities'):
                    capabilities = self.mcp_integration.capabilities
                    GLib.idle_add(self._update_status_success, capabilities)
                else:
                    GLib.idle_add(self._update_status_error, "MCP client does not support capabilities")
            except Exception as e:
                GLib.idle_add(self._update_status_error, str(e))
        
        # Show refreshing status
        self.status_label.set_markup("<b>Status:</b> Refreshing MCP capabilities...")
        
        # Run in background thread
        threading.Thread(target=_refresh_thread, daemon=True).start()
    
    def _update_status_success(self, capabilities):
        """Update status with capability information"""
        if not capabilities:
            self.status_label.set_markup("<b>Status:</b> No capabilities found")
            return
        
        # Create capability summary
        status_text = "<b>Status:</b> MCP Ready\n\n<b>Capabilities:</b>\n"
        
        if "fileSystem" in capabilities:
            status_text += "• File System Operations\n"
        if "windows" in capabilities:
            status_text += "• Windows App Management\n"
        if "android" in capabilities:
            status_text += "• Android App Management\n"
        if "voice" in capabilities:
            status_text += "• Voice Commands\n"
        if "systemInfo" in capabilities:
            status_text += "• System Information\n"
        if "trieveRAG" in capabilities:
            status_text += "• Trieve RAG Knowledge Base\n"
        if "perplexityResearch" in capabilities:
            status_text += "• Perplexity Deep Research\n"
        if "googleSearch" in capabilities:
            status_text += "• Google Search via SerpAPI\n"
        if "newsSearch" in capabilities:
            status_text += "• News Search via NewsAPI\n"
        
        self.status_label.set_markup(status_text)
    
    def _update_status_error(self, error_msg):
        """Update status with error message"""
        self.status_label.set_markup(f"<b>Status:</b> Error: {error_msg}")
    
    def on_search_clicked(self, button):
        """Handle search button click"""
        query = self.search_input.get_text()
        if not query:
            self._update_search_status("Please enter a search query")
            return
        
        # Clear previous results
        self.search_buffer.set_text("")
        self.file_carousel.set_files([])
        
        # Update status to show search is starting
        self._update_search_status(f"Starting search for: {query}...")
        
        # Start search in a separate thread
        threading.Thread(target=self._perform_search, args=(query,), daemon=True).start()

    def on_search_activate(self, entry):
        """Handle search activation (Enter key)"""
        self.on_search_clicked(None)

    def _perform_search(self, query):
        """Perform the search operation"""
        try:
            if not self.mcp:
                self._update_search_error("MCP integration not available")
                return
            
            # Update status to show search is in progress
            GLib.idle_add(self._update_search_status, f"Searching for: {query}...")
            
            # Check if this is a specialized search (with prefix)
            is_specialized = any(query.startswith(prefix) for prefix in ["news:", "web:", "research:", "rag:"])
            
            # For specialized searches, we might need to wait longer
            if is_specialized:
                GLib.idle_add(self._update_search_status, f"Performing specialized search for: {query}... (This may take a moment)")
            elif "." in query and " " not in query:
                # This looks like a filename search
                GLib.idle_add(self._update_search_status, f"Searching for file: {query}... (Checking exact matches first)")
            else:
                # Regular search
                GLib.idle_add(self._update_search_status, f"Searching for: {query}... (This may take a few seconds)")
            
            # Check if we're using the MCP integration directly or through the mcp_integration
            if hasattr(self.mcp, 'search_files'):
                # Using HextrixMCPClient directly
                print(f"Using HextrixMCPClient.search_files directly for query: {query}")
                # Default to home directory
                directory = os.path.expanduser("~")
                result = self.mcp.search_files(directory, query, recursive=True)
            elif self.mcp_integration and hasattr(self.mcp_integration, 'search_files'):
                # Using MCPIntegration
                print(f"Using MCPIntegration.search_files for query: {query}")
                result = self.mcp_integration.search_files(query)
            else:
                self._update_search_error("Search functionality not available")
                return
            
            # Update the UI with the results
            GLib.idle_add(self._update_search_results, result)
        except Exception as e:
            import traceback
            print(f"Error in _perform_search: {e}")
            print(traceback.format_exc())
            GLib.idle_add(self._update_search_error, str(e))

    def _update_search_status(self, status):
        """Update search status"""
        self.search_status.set_text(status)
    
    def _update_search_results(self, result):
        """Update search results"""
        # Clear the search status
        self._update_search_status("")
        
        # Check if result is an error dictionary
        if isinstance(result, dict) and 'error' in result:
            self.search_buffer.set_text(f"Error: {result['error']}")
            return
        
        # Handle different result formats based on source
        
        # Handle case where result is directly a list of files (file search)
        if isinstance(result, list):
            files = result
            if not files:
                self.search_buffer.set_text("No files found matching query")
                return
                
            # Format file results
            result_text = f"Found {len(files)} files:\n\n"
            
            # Process files based on their type
            carousel_files = []
            for file in files:
                if isinstance(file, dict):
                    # Handle dictionary format
                    file_path = file.get('path', '')
                    file_content = file.get('content', '')
                    
                    if file_path:
                        # Check if this is a grep result (content starts with "Line X:")
                        if file_content and file_content.startswith("Line "):
                            result_text += f"📄 {file_path}\n   {file_content}\n"
                        else:
                            result_text += f"📄 {file_path}\n"
                        
                        # Add to carousel with content
                        carousel_files.append({
                            'path': file_path,
                            'content': file_content
                        })
                elif isinstance(file, str):
                    # Handle string format
                    result_text += f"📄 {file}\n"
                    carousel_files.append({
                        'path': file,
                        'content': ''
                    })
            
            self.search_buffer.set_text(result_text)
            
            # Update the carousel with the files
            self.file_carousel.set_files(carousel_files)
            
            # Update status with success message
            self._update_search_status(f"Found {len(files)} files")
            return
            
        # Handle result dictionary with 'files' key (standard MCP file search)
        if isinstance(result, dict) and 'files' in result:
            files = result.get('files', [])
            if not files:
                self.search_buffer.set_text("No files found matching query")
                return
                
            # Format file results
            result_text = f"Found {len(files)} files:\n\n"
            
            # Process files for carousel
            carousel_files = []
            for file in files:
                if isinstance(file, dict):
                    file_path = file.get('path', '')
                    file_content = file.get('content', '')
                    
                    if file_path:
                        result_text += f"📄 {file_path}\n"
                        carousel_files.append({
                            'path': file_path,
                            'content': file_content
                        })
                else:
                    result_text += f"📄 {file}\n"
                    carousel_files.append({
                        'path': str(file),
                        'content': ''
                    })
            
            self.search_buffer.set_text(result_text)
            
            # Update the carousel with the files
            self.file_carousel.set_files(carousel_files)
            
            # Update status with success message
            self._update_search_status(f"Found {len(files)} files")
            return
            
        # Handle web search or research results (dictionary with 'results' key)
        if isinstance(result, dict) and 'results' in result:
            results = result.get('results', [])
            source = result.get('source', 'Search')
            
            if not results:
                self.search_buffer.set_text(f"No {source} results found")
                return
                
            # Format web/research results
            result_text = f"{source} Results:\n\n"
            
            # Convert results to a format suitable for the carousel
            carousel_files = []
            
            for item in results:
                if isinstance(item, dict):
                    # Extract title and URL or content from item
                    title = item.get('title', '')
                    url = item.get('url', '')
                    snippet = item.get('snippet', item.get('content', ''))
                    
                    if title:
                        result_text += f"📌 {title}\n"
                    if url:
                        result_text += f"🔗 {url}\n"
                    if snippet:
                        result_text += f"{snippet}\n"
                    result_text += "\n"
                    
                    # Add to carousel files
                    carousel_files.append({
                        'path': url or title,
                        'content': snippet,
                        'title': title
                    })
                else:
                    # Simple string result
                    result_text += f"• {item}\n"
                    carousel_files.append({
                        'path': str(item),
                        'content': str(item),
                        'title': 'Result'
                    })
            
            self.search_buffer.set_text(result_text)
            
            # Update the carousel with the results
            self.file_carousel.set_files(carousel_files)
            
            # Update status with success message
            self._update_search_status(f"Found {len(results)} {source.lower()} results")
            return
            
        # Handle news results (dictionary with 'articles' key)
        if isinstance(result, dict) and 'articles' in result:
            articles = result.get('articles', [])
            
            if not articles:
                self.search_buffer.set_text("No news articles found")
                return
                
            # Format news results
            result_text = f"News Results:\n\n"
            
            # Convert articles to a format suitable for the carousel
            carousel_files = []
            
            for article in articles:
                if isinstance(article, dict):
                    title = article.get('title', '')
                    source = article.get('source', {}).get('name', '')
                    url = article.get('url', '')
                    description = article.get('description', '')
                    
                    if title:
                        result_text += f"📰 {title}\n"
                    if source:
                        result_text += f"📚 Source: {source}\n"
                    if url:
                        result_text += f"🔗 {url}\n"
                    if description:
                        result_text += f"{description}\n"
                    result_text += "\n"
                    
                    # Add to carousel files
                    carousel_files.append({
                        'path': url or title,
                        'content': description,
                        'title': title
                    })
            
            self.search_buffer.set_text(result_text)
            
            # Update the carousel with the articles
            self.file_carousel.set_files(carousel_files)
            
            # Update status with success message
            self._update_search_status(f"Found {len(articles)} news articles")
            return
            
        # Default case - just convert to string
        self.search_buffer.set_text(str(result))
    
    def _update_search_error(self, error_msg):
        """Update search with error message"""
        self.search_buffer.set_text(f"Error: {error_msg}")
    
    def on_app_type_changed(self, combo):
        """Handle app type selection change"""
        app_type = combo.get_active_text()
        self.app_buffer.set_text(f"Selected app type: {app_type}")

    def on_app_search_activate(self, entry):
        """Handle app search activation (Enter key)"""
        self.on_app_search_clicked(None)

    def on_app_search_clicked(self, button):
        """Handle app search button click"""
        query = self.app_search_entry.get_text()
        if not query:
            self.app_buffer.set_text("Please enter an app name to search")
            return
        
        app_type = self.app_type_combo.get_active_text()
        self.app_buffer.set_text(f"Searching for {query} in {app_type} apps...")
        
        # Start search in a separate thread
        threading.Thread(target=self._perform_app_search, args=(app_type, query), daemon=True).start()

    def _perform_app_search(self, app_type, query):
        """Perform app search based on type"""
        try:
            if not self.mcp_integration:
                GLib.idle_add(lambda: self.app_buffer.set_text("MCP integration not available"))
                return
            
            result = None
            if app_type == "Native":
                result = self.mcp_integration.list_native_apps()
            elif app_type == "Windows":
                result = self.mcp_integration.list_windows_apps()
            elif app_type == "Android":
                result = self.mcp_integration.list_android_apps()
            
            # Filter results by query
            if result and "apps" in result:
                apps = result["apps"]
                filtered_apps = []
                for app in apps:
                    if query.lower() in app.get("name", "").lower():
                        filtered_apps.append(app)
                
                # Update UI with filtered results
                GLib.idle_add(self._update_app_results, filtered_apps, app_type)
            else:
                GLib.idle_add(lambda: self.app_buffer.set_text(f"Error: {result.get('error', 'Unknown error')}"))
        except Exception as e:
            GLib.idle_add(lambda: self.app_buffer.set_text(f"Error: {str(e)}"))

    def _update_app_results(self, apps, app_type):
        """Update app search results"""
        if not apps:
            self.app_buffer.set_text(f"No {app_type} apps found matching the query")
            return
        
        result_text = f"Found {len(apps)} {app_type} apps:\n\n"
        for app in apps:
            name = app.get("name", "Unknown")
            if app_type == "Native":
                command = app.get("command", "")
                result_text += f"📱 {name} - {command}\n"
            elif app_type == "Windows":
                exe = app.get("exe", "")
                result_text += f"🪟 {name} - {exe}\n"
            elif app_type == "Android":
                app_id = app.get("id", "")
                result_text += f"📱 {name} - {app_id}\n"
        
        self.app_buffer.set_text(result_text)

    def on_app_launch_clicked(self, button):
        """Handle app launch button click"""
        # Get selected app from text view
        buffer = self.app_result.get_buffer()
        bounds = buffer.get_selection_bounds()
        
        if not bounds:
            self.app_buffer.set_text("Please select an app to launch")
            return
        
        # Get the selected text
        start, end = bounds
        selected_text = buffer.get_text(start, end, False)
        
        # Extract app name
        app_type = self.app_type_combo.get_active_text()
        app_name = None
        
        if app_type == "Native":
            match = re.search(r"📱 (.*?) -", selected_text)
            if match:
                app_name = match.group(1).strip()
        elif app_type == "Windows":
            match = re.search(r"🪟 (.*?) -", selected_text)
            if match:
                app_name = match.group(1).strip()
        elif app_type == "Android":
            match = re.search(r"📱 (.*?) -", selected_text)
            if match:
                app_name = match.group(1).strip()
        
        if not app_name:
            self.app_buffer.set_text("Could not extract app name from selection")
            return
        
        # Launch the app
        self.app_buffer.set_text(f"Launching {app_name}...")
        
        # Start launch in a separate thread
        threading.Thread(target=self._perform_app_launch, args=(app_type, app_name), daemon=True).start()

    def _perform_app_launch(self, app_type, app_name):
        """Launch the selected app"""
        try:
            if not self.mcp_integration:
                GLib.idle_add(lambda: self.app_buffer.set_text("MCP integration not available"))
                return
            
            result = None
            if app_type == "Native":
                result = self.mcp_integration.launch_native_app(app_name)
            elif app_type == "Windows":
                result = self.mcp_integration.run_windows_app(app_name)
            elif app_type == "Android":
                result = self.mcp_integration.launch_android_app(app_name)
            
            # Update UI with result
            if result and "error" in result:
                GLib.idle_add(lambda: self.app_buffer.set_text(f"Error launching {app_name}: {result['error']}"))
            else:
                GLib.idle_add(lambda: self.app_buffer.set_text(f"Successfully launched {app_name}"))
        except Exception as e:
            GLib.idle_add(lambda: self.app_buffer.set_text(f"Error launching {app_name}: {str(e)}"))

    def on_app_install_clicked(self, button):
        """Handle app install button click"""
        # This would typically open a file chooser dialog
        self.app_buffer.set_text("App installation not implemented yet")

    def on_app_uninstall_clicked(self, button):
        """Handle app uninstall button click"""
        # Get selected app from text view
        buffer = self.app_result.get_buffer()
        bounds = buffer.get_selection_bounds()
        
        if not bounds:
            self.app_buffer.set_text("Please select an app to uninstall")
            return
        
        # Get the selected text
        start, end = bounds
        selected_text = buffer.get_text(start, end, False)
        
        # Extract app name
        app_type = self.app_type_combo.get_active_text()
        app_name = None
        
        if app_type == "Native":
            match = re.search(r"📱 (.*?) -", selected_text)
            if match:
                app_name = match.group(1).strip()
        elif app_type == "Windows":
            match = re.search(r"🪟 (.*?) -", selected_text)
            if match:
                app_name = match.group(1).strip()
        elif app_type == "Android":
            match = re.search(r"📱 (.*?) -", selected_text)
            if match:
                app_name = match.group(1).strip()
        
        if not app_name:
            self.app_buffer.set_text("Could not extract app name from selection")
            return
        
        # Confirm uninstall
        self.app_buffer.set_text(f"Uninstall functionality not implemented yet for {app_name}")

    def on_command_activate(self, entry):
        """Handle command activation (Enter key)"""
        self.on_command_clicked(None)

    def on_command_clicked(self, button):
        """Handle command button click"""
        command = self.command_input.get_text()
        if not command:
            self.command_status.set_text("Please enter a command to execute")
            return
        
        self.command_status.set_text(f"Executing: {command}...")
        
        # Start command execution in a separate thread
        threading.Thread(target=self._perform_command, args=(command,), daemon=True).start()

    def _perform_command(self, command):
        """Execute the command"""
        try:
            if not self.mcp_integration:
                GLib.idle_add(lambda: self.command_buffer.set_text("MCP integration not available"))
                return
            
            # Check if this is a voice command
            if command.lower().startswith(("find", "search", "open", "launch", "research")):
                result = self.mcp_integration.process_voice_command(command)
            else:
                # Execute as a system command
                if self.mcp:
                    result = self.mcp.execute_command(command)
                else:
                    # Fall back to local execution
                    import subprocess
                    process = subprocess.run(command, shell=True, capture_output=True, text=True)
                    result = {
                        "output": process.stdout,
                        "error": process.stderr,
                        "returncode": process.returncode
                    }
            
            # Update UI with result
            GLib.idle_add(self._update_command_result, result)
        except Exception as e:
            GLib.idle_add(lambda: self.command_buffer.set_text(f"Error executing command: {str(e)}"))

    def _update_command_result(self, result):
        """Update command execution result"""
        if isinstance(result, dict):
            if "error" in result and result["error"]:
                self.command_buffer.set_text(f"Error: {result['error']}")
            elif "output" in result:
                self.command_buffer.set_text(result["output"])
            elif "response" in result:
                self.command_buffer.set_text(result["response"])
                
                # If there are results, display them
                if "results" in result:
                    results = result["results"]
                    if isinstance(results, list):
                        result_text = self.command_buffer.get_text(
                            self.command_buffer.get_start_iter(),
                            self.command_buffer.get_end_iter(),
                            False
                        )
                        
                        result_text += "\n\nResults:\n"
                        for item in results:
                            if isinstance(item, dict):
                                title = item.get("title", "")
                                content = item.get("content", "")
                                if title:
                                    result_text += f"\n{title}\n"
                                if content:
                                    result_text += f"{content}\n"
                            else:
                                result_text += f"\n{item}\n"
                        
                        self.command_buffer.set_text(result_text)
            else:
                self.command_buffer.set_text(str(result))
        else:
            self.command_buffer.set_text(str(result))
        
        self.command_status.set_text("Command executed successfully")

    def on_open_file_clicked(self, button):
        """Handle open file button click"""
        if self.search_results_stack.get_visible_child_name() == "carousel":
            # Open the file from the carousel
            self.file_carousel.open_current_file()
        else:
            # Get selected text from the text view
            buffer = self.search_result.get_buffer()
            bounds = buffer.get_selection_bounds()
            
            if bounds:
                # Get the selected text
                start, end = bounds
                selected_text = buffer.get_text(start, end, False)
                
                # Try to extract a URL or file path
                import re
                url_match = re.search(r'🔗\s*(https?://\S+)', selected_text)
                file_match = re.search(r'📄\s*(/\S+)', selected_text)
                
                if url_match:
                    url = url_match.group(1)
                    # Open URL in browser
                    subprocess.Popen(['xdg-open', url])
                elif file_match:
                    file_path = file_match.group(1)
                    # Open file with default application
                    subprocess.Popen(['xdg-open', file_path])
                else:
                    self._update_search_status("No valid URL or file path selected")
            else:
                self._update_search_status("Please select a file or URL to open")

    def clear_search_results(self):
        """Clear all search results and status messages when closing the panel"""
        # Clear search results
        self.search_buffer.set_text("")
        self.search_status.set_text("")
        
        # Clear carousel
        self.file_carousel.set_files([])
        
        # Clear app results
        self.app_buffer.set_text("")
        
        # Clear command results
        self.command_buffer.set_text("")

    def on_view_logs_clicked(self, button):
        """Handle view logs button click"""
        # Define the log file path
        log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs/mcp_integration.log')
        
        if not os.path.exists(log_file):
            self._update_status_error(f"Log file not found at {log_file}")
            return
        
        # Create a dialog to display logs
        dialog = Gtk.Dialog(title="MCP Integration Logs", transient_for=self.parent.window, modal=True)
        dialog.set_default_size(800, 600)
        
        # Add content area
        content_area = dialog.get_content_area()
        content_area.set_margin_start(10)
        content_area.set_margin_end(10)
        content_area.set_margin_top(10)
        content_area.set_margin_bottom(10)
        
        # Create scrolled window for logs
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        
        # Create text view for logs
        buffer = Gtk.TextBuffer()
        text_view = Gtk.TextView.new_with_buffer(buffer)
        text_view.set_editable(False)
        text_view.set_cursor_visible(False)
        text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        scroll.set_child(text_view)
        
        # Load log file content
        try:
            with open(log_file, 'r') as f:
                log_content = f.read()
                buffer.set_text(log_content)
                
                # Scroll to the end (most recent logs)
                text_view.scroll_to_iter(buffer.get_end_iter(), 0.0, False, 0.0, 0.0)
        except Exception as e:
            buffer.set_text(f"Error loading log file: {str(e)}")
        
        content_area.append(scroll)
        
        # Add refresh button
        refresh_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        refresh_box.set_halign(Gtk.Align.END)
        refresh_box.set_margin_top(10)
        
        refresh_button = Gtk.Button.new_with_label("Refresh Logs")
        refresh_button.connect("clicked", lambda b: self._refresh_logs(buffer, log_file, text_view))
        refresh_box.append(refresh_button)
        
        content_area.append(refresh_box)
        
        # Show the dialog
        dialog.present()

    def _refresh_logs(self, buffer, log_file, text_view):
        """Refresh the logs in the dialog"""
        try:
            with open(log_file, 'r') as f:
                log_content = f.read()
                buffer.set_text(log_content)
                
                # Scroll to the end (most recent logs)
                text_view.scroll_to_iter(buffer.get_end_iter(), 0.0, False, 0.0, 0.0)
        except Exception as e:
            buffer.set_text(f"Error loading log file: {str(e)}") 