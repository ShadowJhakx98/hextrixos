#!/usr/bin/env python3
# app_drawer.py - Hextrix OS App Drawer Module
# Place this file in the same directory as hextrix-hud2.py or in your Python path

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GLib, Pango, GdkPixbuf, Gio
import os
import subprocess
import math
import cairo
import shlex
# ... rest of the code ...
class AppDrawer:
    """App Drawer component for Hextrix OS
    
    This class provides a searchable application drawer UI component
    that displays all available applications in a grid layout.
    
    Usage:
        # Create an instance with parent window reference and application items
        app_drawer = AppDrawer(parent_window, dock_items)
        
        # Add the drawer to a container
        container.pack_start(app_drawer.drawer, False, False, 0)
        
        # Use the toggle method to show/hide the drawer
        app_drawer.toggle()
    """
    
    def __init__(self, parent, dock_items, keybind=None):
        """Initialize the App Drawer with parent reference and application items
        
        Args:
            parent: Parent window or widget reference
            dock_items: List of application objects with name, command, and icon properties
            keybind: Optional key to use for launching apps (default: None - double-click only)
        """
        self.parent = parent
        self.dock_items = []
        self.load_system_applications()  # Load system apps first
        self.dock_items.extend(dock_items)  # Add dock items after
        self.filtered_items = []
        self.search_text = ""
        self.keybind = keybind
        
        # Create the main drawer container
        self.drawer = Gtk.Revealer()
        self.drawer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        self.drawer.set_transition_duration(300)
        
        # Create the content box with transparency
        self.content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        # Apply styling
        self.content.get_style_context().add_class("app-drawer")
        self.drawer.set_child(self.content)
        
        # Header with search
        self.header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.header.set_margin_start(20)
        self.header.set_margin_end(20)
        self.header.set_margin_top(15)
        self.header.set_margin_bottom(10)
        
        # Title
        self.title = Gtk.Label()
        self.title.set_text("Applications")
        self.title.set_markup("<span font='16' weight='bold' color='#00BFFF'>Applications</span>")
        self.title.set_halign(Gtk.Align.START)
        self.header.append(self.title)
        
        # Search entry
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search applications...")
        self.search_entry.set_size_request(250, -1)
        self.search_entry.connect("search-changed", self.on_search_changed)
        self.header.append(self.search_entry)
        
        # Close button
        self.close_button = Gtk.Button()
        self.close_button.set_tooltip_text("Close App Drawer")
        close_icon = Gtk.Image.new_from_icon_name("window-close-symbolic")
        close_icon.set_pixel_size(16)  # Equivalent to BUTTON size
        self.close_button.set_child(close_icon)
        self.close_button.connect("clicked", self.hide)
        self.close_button.get_style_context().add_class("drawer-close-button")
        self.header.append(self.close_button)
        
        self.content.append(self.header)
        
        # Create scrolled window for apps
        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled.set_min_content_height(400)
        self.scrolled.set_max_content_height(500)
        
        # Apps container (FlowBox)
        self.apps_container = Gtk.FlowBox()
        self.apps_container.set_valign(Gtk.Align.START)
        self.apps_container.set_max_children_per_line(8)
        self.apps_container.set_min_children_per_line(3)
        self.apps_container.set_selection_mode(Gtk.SelectionMode.NONE)
        self.apps_container.set_homogeneous(True)
        self.apps_container.set_row_spacing(20)
        self.apps_container.set_column_spacing(10)
        self.apps_container.set_margin_start(20)
        self.apps_container.set_margin_end(20)
        self.apps_container.set_margin_top(10)
        self.apps_container.set_margin_bottom(20)
        
        self.scrolled.set_child(self.apps_container)
        self.content.append(self.scrolled)
        
        # Footer
        self.footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.footer.set_margin_start(20)
        self.footer.set_margin_end(20)
        self.footer.set_margin_top(10)
        self.footer.set_margin_bottom(15)
        
        # App count
        self.app_count_label = Gtk.Label()
        self.app_count_label.set_text("")
        self.footer.append(self.app_count_label)
        
        # Settings button
        self.settings_button = Gtk.Button()
        self.settings_button.set_label("Settings")
        settings_icon = Gtk.Image.new_from_icon_name("preferences-system-symbolic")
        settings_icon.set_pixel_size(16)  # Equivalent to BUTTON size
        
        # In GTK 4.0, we need to create a box to hold the icon and label
        settings_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        settings_box.append(settings_icon)
        settings_label = Gtk.Label(label="Settings")
        settings_box.append(settings_label)
        
        self.settings_button.set_child(settings_box)
        self.settings_button.connect("clicked", self.on_settings_clicked)
        self.footer.append(self.settings_button)
        
        # Add to favorites button
        self.favorites_button = Gtk.Button()
        
        # In GTK 4.0, we need to create a box to hold the icon and label
        favorites_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        favorites_icon = Gtk.Image.new_from_icon_name("list-add-symbolic")
        favorites_icon.set_pixel_size(16)  # Equivalent to BUTTON size
        favorites_box.append(favorites_icon)
        favorites_label = Gtk.Label(label="Add to Dock")
        favorites_box.append(favorites_label)
        
        self.favorites_button.set_child(favorites_box)
        self.favorites_button.set_sensitive(False)  # Initially disabled
        self.favorites_button.connect("clicked", self.on_add_to_favorites)
        self.footer.append(self.favorites_button)
        
        self.content.append(self.footer)
        
        # Currently selected app (for favorites)
        self.selected_app = None
        
        # Apply styling
        self.apply_styling()
        
        # Populate apps
        self.populate_apps()
        
        # Connect key events - GTK 4.0 style
        self.key_controller = Gtk.EventControllerKey.new()
        self.key_controller.connect("key-pressed", self.on_key_press)
        self.content.add_controller(self.key_controller)
        
        # Register in the parent's app widgets list
        if hasattr(parent, 'app_widgets'):
            parent.app_widgets.append(self.drawer)

    def apply_styling(self):
        """Apply CSS styling to the app drawer components"""
        css_provider = Gtk.CssProvider()
        css = """
            .app-drawer {
                background-color: rgba(0, 15, 40, 0.95);
                border-radius: 15px;
                border: 1px solid rgba(0, 150, 255, 0.5);
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8);
                margin: 50px;
            }
            
            .app-item {
                background-color: rgba(0, 30, 60, 0.7);
                border-radius: 10px;
                border: 1px solid rgba(0, 150, 255, 0.4);
                padding: 10px;
                transition: all 250ms ease-in-out;
            }
            
            .app-item:hover {
                background-color: rgba(0, 50, 90, 0.8);
                border-color: rgba(0, 180, 255, 0.6);
                box-shadow: 0 0 15px rgba(0, 150, 255, 0.4);
            }
            
            .app-item.selected {
                background-color: rgba(0, 80, 120, 0.9);
                border-color: rgba(0, 220, 255, 0.8);
                box-shadow: 0 0 20px rgba(0, 180, 255, 0.6);
            }
            
            .app-label {
                color: #FFFFFF;
                font-size: 12px;
                margin-top: 5px;
            }
            
            .drawer-close-button {
                background-color: rgba(60, 60, 80, 0.7);
                border-radius: 50%;
                border: 1px solid rgba(150, 150, 200, 0.3);
                padding: 2px;
            }
            
            .drawer-close-button:hover {
                background-color: rgba(80, 80, 100, 0.8);
                border-color: rgba(180, 180, 220, 0.5);
            }
            
            entry {
                background-color: rgba(0, 20, 50, 0.8);
                color: #00BFFF;
                border: 1px solid rgba(0, 150, 255, 0.5);
                border-radius: 20px;
                padding: 6px 12px;
            }
            
            entry:focus {
                border-color: rgba(0, 200, 255, 0.8);
                box-shadow: 0 0 10px rgba(0, 150, 255, 0.4);
            }
            
            button {
                background-color: rgba(0, 40, 80, 0.7);
                color: #FFFFFF;
                border-radius: 5px;
                border: 1px solid rgba(0, 150, 255, 0.4);
                padding: 5px 10px;
                transition: all 250ms ease-in-out;
            }
            
            button:hover {
                background-color: rgba(0, 60, 110, 0.8);
                border-color: rgba(0, 180, 255, 0.6);
            }
            
            button:disabled {
                background-color: rgba(30, 30, 50, 0.5);
                color: rgba(150, 150, 150, 0.5);
                border-color: rgba(80, 80, 100, 0.3);
            }
            
            scrollbar {
                background-color: rgba(0, 10, 30, 0.5);
                border-radius: 10px;
                border: none;
            }
            
            scrollbar slider {
                background-color: rgba(0, 150, 255, 0.3);
                border-radius: 10px;
                min-width: 6px;
                min-height: 6px;
            }
            
            scrollbar slider:hover {
                background-color: rgba(0, 180, 255, 0.5);
            }
        """
        css_provider.load_from_data(css.encode())
        
        self.content.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.search_entry.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.close_button.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.settings_button.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.favorites_button.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    
    def load_system_applications(self):
        """Load all installed system applications"""
        app_list = []
        
        # Get default applications
        apps = Gio.AppInfo.get_all()
        
        for app in apps:
            if not app.should_show():
                continue
                
            name = app.get_display_name()
            icon = app.get_icon()
            desktop_id = app.get_id()
            
            # Create a dictionary for the app
            app_dict = {
                'name': name,
                'icon': icon.to_string() if icon else 'application-x-executable',
                'command': app.get_commandline(),
                'desktop_id': desktop_id,
                'category': 'Applications'
            }
            
            app_list.append(app_dict)
            
        # Sort apps by name
        app_list.sort(key=lambda x: x['name'].lower())
        self.dock_items.extend(app_list)
    
    def create_app_button(self, app_item):
        """Create a button for an application item"""
        # In GTK 4.0, we don't need EventBox since all widgets can receive events
        button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        button_box.set_size_request(100, 100)
        
        # Get app properties
        name = app_item.name if hasattr(app_item, 'name') else app_item.get('name', '')
        icon_name = app_item.icon_path if hasattr(app_item, 'icon_path') else app_item.get('icon', '')
        
        # Try to load icon in different ways
        icon = None
        if isinstance(icon_name, str):
            if icon_name.endswith('.desktop'):
                desktop_id = icon_name
                app_info = Gio.DesktopAppInfo.new(desktop_id)
                if app_info:
                    icon = app_info.get_icon()
            elif '/' in icon_name:  # Path to icon file
                try:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(icon_name, 48, 48)
                    icon = Gtk.Image.new_from_pixbuf(pixbuf)
                except:
                    icon = Gtk.Image.new_from_icon_name('application-x-executable')
                    icon.set_pixel_size(48)  # Equivalent to DIALOG size
            else:  # Icon name
                icon = Gtk.Image.new_from_icon_name(icon_name)
                icon.set_pixel_size(48)  # Equivalent to DIALOG size
        
        if not icon:
            icon = Gtk.Image.new_from_icon_name('application-x-executable')
            icon.set_pixel_size(48)  # Equivalent to DIALOG size
        
        icon.set_pixel_size(48)
        button_box.append(icon)
        
        # Create label
        label = Gtk.Label()
        label.set_text(name)
        label.set_wrap(True)
        label.set_justify(Gtk.Justification.CENTER)
        label.set_max_width_chars(15)
        label.set_lines(2)
        label.set_ellipsize(Pango.EllipsizeMode.END)
        button_box.append(label)
        
        # Store app item reference
        button_box.app_item = app_item
        
        # Style the button
        button_box.get_style_context().add_class("app-item")
        
        # Connect signals - GTK 4.0 style - directly to the button box
        gesture = Gtk.GestureClick.new()
        gesture.connect("pressed", self.on_app_box_clicked, button_box)
        button_box.add_controller(gesture)
        
        return button_box
    
    def populate_apps(self):
        """Populate the app drawer with application items"""
        # Clear existing items
        while True:
            child = self.apps_container.get_first_child()
            if child is None:
                break
            self.apps_container.remove(child)
        
        # Filter and sort items
        items_to_show = []
        for item in self.dock_items:
            # Handle both DockItem objects and dictionaries
            if isinstance(item, dict):
                name = item.get('name', '')
                if not self.search_text or self.search_text.lower() in name.lower():
                    items_to_show.append(item)
            else:  # DockItem object
                name = getattr(item, 'name', '')
                if not self.search_text or self.search_text.lower() in name.lower():
                    items_to_show.append(item)
        
        # Sort items by name
        sorted_items = sorted(items_to_show, key=lambda x: x.name.lower() if hasattr(x, 'name') else x.get('name', '').lower())
        
        # Create buttons for each app
        for item in sorted_items:
            button_box = self.create_app_button(item)
            self.apps_container.append(button_box)
        
        # Update app count
        self.app_count_label.set_text(f"{len(sorted_items)} applications")
        
        # Widgets are visible by default in GTK 4
        
        # Reset selected app
        self.selected_app = None
        self.favorites_button.set_sensitive(False)
    
    def on_search_changed(self, entry):
        """Filter apps based on search text
        
        Args:
            entry: The search entry widget
        """
        self.search_text = entry.get_text().lower()
        if self.search_text:
            self.filtered_items = [
                item for item in self.dock_items 
                if self.search_text in item.name.lower() or 
                   (hasattr(item, 'command') and item.command and 
                    self.search_text in item.command.lower())
            ]
        else:
            self.filtered_items = []
        
        self.populate_apps()
    
    def on_app_box_clicked(self, gesture, n_press, x, y, button_box):
        """Handle click events on app buttons"""
        # Get button number from gesture
        button = gesture.get_current_button()
        
        # Left click launches the app
        if button == 1:
            app_item = button_box.app_item  # Get app item directly from button_box
            self.launch_app(app_item)
            self.hide()
        # Right click selects for favorites
        elif button == 3:
            # Remove selected class from all buttons
            child = self.apps_container.get_first_child()
            while child:
                # In GTK 4.0, we're directly using the button_box, not an EventBox wrapper
                child.get_style_context().remove_class("selected")
                child = child.get_next_sibling()
            
            # Add selected class to clicked button
            button_box.get_style_context().add_class("selected")
            self.selected_app = button_box.app_item
            self.favorites_button.set_sensitive(True)
    
    def launch_app(self, app_item):
        """Launch an application"""
        try:
            # Get command based on whether app_item is a DockItem or dictionary
            command = app_item.command if hasattr(app_item, 'command') else app_item.get('command', '')
            
            if command:
                # Launch the application in the background
                subprocess.Popen(shlex.split(command), start_new_session=True)
            else:
                print(f"No command found for {app_item.name if hasattr(app_item, 'name') else app_item.get('name', 'Unknown app')}")
        except Exception as e:
            print(f"Error launching application: {e}")
            
            # Show error in status bar if available
            if hasattr(self, 'status_label'):
                self.status_label.set_text(f"Error launching application: {e}")
                GLib.timeout_add(3000, self.reset_status_message)
    
    def on_settings_clicked(self, button):
        """Open system settings
        
        Args:
            button: The button widget
        """
        try:
            subprocess.Popen(["gnome-control-center"])
        except Exception as e:
            print(f"Error opening settings: {e}")
    
    def on_add_to_favorites(self, button):
        """Add selected app to dock favorites
        
        Args:
            button: The button widget
        """
        if not self.selected_app:
            return
            
        if hasattr(self.parent, 'add_to_favorites') and callable(getattr(self.parent, 'add_to_favorites')):
            # Call the parent's add_to_favorites method if available
            self.parent.add_to_favorites(self.selected_app)
        elif hasattr(self.parent, 'categories') and 'Favorites' in self.parent.categories:
            # Direct access to parent's categories
            for category in self.parent.categories.values():
                if self.selected_app in category.items:
                    category.remove_item(self.selected_app)
            
            self.parent.categories['Favorites'].add_item(self.selected_app)
            
            # Refresh the dock if possible
            if hasattr(self.parent, 'populate_dock') and callable(getattr(self.parent, 'populate_dock')):
                self.parent.populate_dock()
            
            # Save config if possible
            if hasattr(self.parent, 'save_dock_config') and callable(getattr(self.parent, 'save_dock_config')):
                self.parent.save_dock_config()
        
        # Show feedback and reset selection
        self.app_count_label.set_markup(f"<span color='#00FF88'>Added {self.selected_app.name} to Dock</span>")
        GLib.timeout_add(2000, self.reset_status_message)
    
    def reset_status_message(self):
        """Reset the status message in the footer"""
        items_to_show = self.filtered_items if self.search_text else self.dock_items
        app_count = len(items_to_show)
        count_text = f"{app_count} application{'s' if app_count != 1 else ''} available"
        self.app_count_label.set_markup(f"<span color='#88CCFF'>{count_text}</span>")
        return False
    
    def on_key_press(self, controller, keyval, keycode, state):
        """Handle keyboard events
        
        Args:
            controller: The event controller
            keyval: The key value
            keycode: The key code
            state: The key state
            
        Returns:
            bool: True if the event was handled
        """
        if keyval == Gdk.KEY_Escape:
            self.hide()
            return True
            
        # Only use custom keybind if configured
        if self.keybind is not None and keyval == self.keybind and self.selected_app:
            self.launch_app(self.selected_app)
            return True
            
        return False
    
    def get_drawer(self):
        """Get the drawer widget for adding to containers"""
        return self.drawer
    
    def show(self, widget=None):
        """Show the app drawer"""
        self.drawer.set_reveal_child(True)
        self.search_entry.grab_focus()
    
    def hide(self, widget=None):
        """Hide the app drawer"""
        self.drawer.set_reveal_child(False)
        self.search_entry.set_text("")
    
    def toggle(self, widget=None):
        """Toggle the app drawer visibility"""
        if self.drawer.get_reveal_child():
            self.hide()
        else:
            self.show()