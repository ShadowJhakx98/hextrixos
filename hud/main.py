#!/usr/bin/env python3
# Hextrix HUD - Main Entry Point

import os
import sys
import platform

# Add project directory to path to ensure modules can be found
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
sys.path.append(project_dir)
# Also add the hud directory itself to the path
sys.path.append(script_dir)

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, Gio

# Import the main application window and file panel
from hextrix_hud import HextrixHUD
from file_panel import FilePanel

class HextrixApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.hextrix.hud",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        # Create and load the CSS provider for the window background
        css_provider = Gtk.CssProvider()
        css = """
            window {
                background-color: rgba(0, 10, 30, 0.85);
            }
            
            button {
                background-color: rgba(0, 10, 50, 0.7);
                border-radius: 5px;
                padding: 5px;
            }
            
            button:hover {
                background-color: rgba(0, 100, 200, 0.6);
            }
            
            .overlay-box {
                background-color: rgba(0, 10, 30, 0.85);
                border-radius: 8px;
                border: 1px solid rgba(0, 150, 255, 0.5);
            }
        """
        css_provider.load_from_data(css.encode())
        
        # Apply CSS to the default display - GTK4 style
        display = Gdk.Display.get_default()
        Gtk.StyleContext.add_provider_for_display(
            display, 
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        # Create the window
        win = HextrixHUD()
        win.set_application(self)
        
        # Make sure the chat panel starts hidden
        win.chat_panel.panel.set_visible(False)
        
        # Show the window
        win.present()

if __name__ == "__main__":
    app = HextrixApplication()
    app.run(sys.argv)