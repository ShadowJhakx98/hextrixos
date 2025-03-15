#!/usr/bin/env python3
# Hextrix HUD - File Panel

import os
from datetime import datetime

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, Gio, GLib
import cairo

class FilePanel:
    def __init__(self, parent):
        self.parent = parent
        self.current_path = os.path.expanduser("~")
        self.selected_item = None
        self.history = [self.current_path]
        self.history_position = 0
        
        self.panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        self.toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.toolbar.set_margin_start(10)
        self.toolbar.set_margin_end(10)
        self.toolbar.set_margin_top(10)
        self.toolbar.set_margin_bottom(5)
        
        self.back_button = self.create_tool_button("go-previous-symbolic", "Back", self.on_back_clicked)
        self.toolbar.append(self.back_button)
        
        self.forward_button = self.create_tool_button("go-next-symbolic", "Forward", self.on_forward_clicked)
        self.toolbar.append(self.forward_button)
        
        # Add a separator
        self.toolbar.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        
        self.up_button = self.create_tool_button("go-up-symbolic", "Up", self.on_up_clicked)
        self.toolbar.append(self.up_button)
        
        self.home_button = self.create_tool_button("go-home-symbolic", "Home", self.on_home_clicked)
        self.toolbar.append(self.home_button)
        
        self.refresh_button = self.create_tool_button("view-refresh-symbolic", "Refresh", self.on_refresh_clicked)
        self.toolbar.append(self.refresh_button)
        
        # Path entry
        self.path_entry = Gtk.Entry()
        self.path_entry.set_placeholder_text("Enter path...")
        self.path_entry.connect("activate", self.on_path_activated)
        self.toolbar.append(self.path_entry)
        self.path_entry.set_hexpand(True)
        
        # Search entry
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search...")
        self.search_entry.connect("search-changed", self.on_search_changed)
        self.toolbar.append(self.search_entry)
        
        self.panel.append(self.toolbar)
        
        self.create_file_view()
        
        # Create statusbar
        self.statusbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.statusbar.set_spacing(5)
        self.statusbar.set_margin_start(5)
        self.statusbar.set_margin_end(5)
        self.statusbar.set_margin_top(5)
        self.statusbar.set_margin_bottom(5)
        
        self.item_count_label = Gtk.Label()
        self.item_count_label.set_text("0 items")
        self.item_count_label.set_halign(Gtk.Align.START)
        self.statusbar.append(self.item_count_label)
        self.item_count_label.set_hexpand(True)
        
        self.selected_info_label = Gtk.Label()
        self.selected_info_label.set_text("")
        self.selected_info_label.set_halign(Gtk.Align.END)
        self.statusbar.append(self.selected_info_label)
        
        self.panel.append(self.statusbar)
        
        self.apply_styling()
        
        self.load_directory()
    
    def apply_styling(self):
        css_provider = Gtk.CssProvider()
        css = """
            .file-panel {
                background-color: rgba(0, 10, 30, 0.8);
                border-radius: 5px;
                border: 1px solid rgba(0, 191, 255, 0.3);
            }
            .file-panel-toolbar {
                background-color: rgba(0, 30, 60, 0.8);
                border-bottom: 1px solid rgba(0, 191, 255, 0.3);
            }
            .file-panel-statusbar {
                background-color: rgba(0, 30, 60, 0.8);
                border-top: 1px solid rgba(0, 191, 255, 0.3);
                font-size: 10px;
                color: #88DDFF;
            }
            .file-view {
                background-color: rgba(0, 15, 40, 0.7);
                color: white;
            }
            .file-view:selected {
                background-color: rgba(0, 120, 215, 0.8);
            }
            .tool-button {
                background-color: rgba(0, 40, 80, 0.7);
                border-radius: 4px;
                border: 1px solid rgba(0, 191, 255, 0.5);
                padding: 2px;
                transition: all 0.2s ease;
            }
            .tool-button:hover {
                background-color: rgba(0, 70, 130, 0.8);
                border-color: rgba(0, 255, 255, 0.8);
            }
            entry {
                background-color: rgba(0, 20, 50, 0.8);
                color: #00BFFF;
                border: 1px solid rgba(0, 191, 255, 0.5);
                border-radius: 4px;
                padding: 4px 8px;
            }
            entry:focus {
                border-color: rgba(0, 255, 255, 0.8);
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
        
        # Add classes to widgets
        self.panel.get_style_context().add_class("file-panel")
        self.toolbar.get_style_context().add_class("file-panel-toolbar")
        self.statusbar.get_style_context().add_class("file-panel-statusbar")
    
    def create_tool_button(self, icon_name, tooltip, callback):
        button = Gtk.Button()
        button.set_tooltip_text(tooltip)
        
        # Create an image for the icon using pixel size instead of icon size
        icon = Gtk.Image.new_from_icon_name(icon_name)
        icon.set_pixel_size(16)  # Equivalent to SMALL_TOOLBAR
        button.set_child(icon)
        
        # Connect to clicked signal
        button.connect("clicked", callback)
        
        return button
    
    def create_file_view(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        # In GTK 4, we need to use GdkPixbuf.Pixbuf for the icon column
        self.store = Gtk.ListStore(GdkPixbuf.Pixbuf, str, str, str, str, str)
        
        self.treeview = Gtk.TreeView(model=self.store)
        self.treeview.set_headers_visible(True)
        self.treeview.set_enable_search(True)
        self.treeview.set_search_column(1)
        self.treeview.get_style_context().add_class("file-view")
        
        self.treeview.connect("row-activated", self.on_item_activated)
        selection = self.treeview.get_selection()
        selection.connect("changed", self.on_selection_changed)
        
        renderer_icon = Gtk.CellRendererPixbuf()
        column_icon = Gtk.TreeViewColumn("", renderer_icon, pixbuf=0)
        column_icon.set_fixed_width(30)
        column_icon.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        self.treeview.append_column(column_icon)
        
        renderer_name = Gtk.CellRendererText()
        column_name = Gtk.TreeViewColumn("Name", renderer_name, text=1)
        column_name.set_expand(True)
        column_name.set_sort_column_id(1)
        self.treeview.append_column(column_name)
        
        renderer_size = Gtk.CellRendererText()
        renderer_size.set_alignment(1.0, 0.5)
        column_size = Gtk.TreeViewColumn("Size", renderer_size, text=2)
        column_size.set_fixed_width(80)
        column_size.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        column_size.set_alignment(1.0)
        column_size.set_sort_column_id(2)
        self.treeview.append_column(column_size)
        
        renderer_modified = Gtk.CellRendererText()
        column_modified = Gtk.TreeViewColumn("Modified", renderer_modified, text=3)
        column_modified.set_fixed_width(150)
        column_modified.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        column_modified.set_sort_column_id(3)
        self.treeview.append_column(column_modified)
        
        renderer_type = Gtk.CellRendererText()
        column_type = Gtk.TreeViewColumn("Type", renderer_type, text=4)
        column_type.set_fixed_width(100)
        column_type.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        column_type.set_sort_column_id(4)
        self.treeview.append_column(column_type)
        
        scrolled.set_child(self.treeview)
        self.panel.append(scrolled)
    
    def load_directory(self, directory=None):
        if directory is not None:
            self.current_path = directory
        
        self.store.clear()
        self.path_entry.set_text(self.current_path)
        
        try:
            self.back_button.set_sensitive(self.history_position > 0)
            self.forward_button.set_sensitive(self.history_position < len(self.history) - 1)
            self.up_button.set_sensitive(self.current_path != '/')
            
            contents = []
            if self.current_path != '/':
                parent_path = os.path.dirname(self.current_path)
                parent_icon = self.get_icon_for_path(parent_path, is_dir=True)
                contents.append((parent_icon, "..", "", "", "Directory", parent_path))
            
            entries = os.listdir(self.current_path)
            for entry in sorted(entries, key=lambda x: (not os.path.isdir(os.path.join(self.current_path, x)), x.lower())):
                full_path = os.path.join(self.current_path, entry)
                try:
                    stat_info = os.stat(full_path)
                    size = self.format_size(stat_info.st_size) if not os.path.isdir(full_path) else ""
                    modified = datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M')
                    if os.path.isdir(full_path):
                        icon = self.get_icon_for_path(full_path, is_dir=True)
                        file_type = "Directory"
                    else:
                        icon = self.get_icon_for_path(full_path)
                        file_type = self.get_file_type(full_path)
                    if not entry.startswith('.'):
                        contents.append((icon, entry, size, modified, file_type, full_path))
                except (PermissionError, FileNotFoundError):
                    pass
            
            for item in contents:
                self.store.append(item)
            
            file_count = len(contents) - (1 if self.current_path != '/' else 0)
            self.item_count_label.set_text(f"{file_count} items")
            
        except (PermissionError, FileNotFoundError) as e:
            error_dialog = Gtk.MessageDialog(
                transient_for=self.parent,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Error accessing directory"
            )
            error_dialog.format_secondary_text(str(e))
            error_dialog.run()
            error_dialog.destroy()
            if self.history_position > 0:
                self.history_position -= 1
                self.current_path = self.history[self.history_position]
                self.load_directory()
    
    def navigate_to(self, path):
        path = os.path.normpath(path)
        if not os.path.exists(path) or not os.path.isdir(path):
            return False
        if self.current_path != path:
            if self.history_position < len(self.history) - 1:
                self.history = self.history[:self.history_position + 1]
            self.history.append(path)
            self.history_position = len(self.history) - 1
        self.current_path = path
        self.load_directory()
        return True
    
    def get_icon_for_path(self, path, is_dir=None):
        # In GTK 4, we use the display to get the icon theme
        display = Gdk.Display.get_default()
        theme = Gtk.IconTheme.get_for_display(display)
        
        if is_dir is None:
            is_dir = os.path.isdir(path)
        
        if is_dir:
            if path == os.path.expanduser("~"):
                icon_name = "user-home"
            elif path == "/":
                icon_name = "drive-harddisk"
            else:
                icon_name = "folder"
        else:
            mime_type = Gio.content_type_guess(path, None)[0]
            if mime_type:
                icon_name = Gio.content_type_get_icon(mime_type).to_string().split()[-1]
            else:
                icon_name = "text-x-generic"
        
        # Create a default pixbuf for compatibility with our ListStore
        default_pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, 24, 24)
        default_pixbuf.fill(0x00000000)  # Transparent
        
        try:
            # In GTK 4, lookup_icon returns an IconPaintable, not a Pixbuf
            # We use the proper lookup_icon parameters for GTK 4
            icon_paintable = theme.lookup_icon(icon_name, [], 24, 1, Gtk.TextDirection.NONE, 0)
            
            if icon_paintable:
                # Get the icon file path
                icon_file = icon_paintable.get_file()
                if icon_file:
                    file_path = icon_file.get_path()
                    if file_path:
                        # Load as pixbuf from file
                        return GdkPixbuf.Pixbuf.new_from_file_at_size(file_path, 24, 24)
            
            # Fallback to create colored rectangles
            pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, 24, 24)
            if is_dir:
                # Blue for folders
                pixbuf.fill(0x3366cc80)  # RGBA
            else:
                # Gray for files
                pixbuf.fill(0x77777780)  # RGBA
            return pixbuf
            
        except Exception as e:
            print(f"Error loading icon: {e}")
            try:
                # Create a simple colored square as fallback
                pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, 24, 24)
                if is_dir:
                    # Blue for folders
                    pixbuf.fill(0x3366cc80)  # RGBA
                else:
                    # Gray for files
                    pixbuf.fill(0x77777780)  # RGBA
                return pixbuf
            except:
                return default_pixbuf
    
    def get_file_type(self, path):
        mime_type = Gio.content_type_guess(path, None)[0]
        return Gio.content_type_get_description(mime_type) if mime_type else "Unknown"
    
    def format_size(self, size_bytes):
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def on_back_clicked(self, button):
        if self.history_position > 0:
            self.history_position -= 1
            self.current_path = self.history[self.history_position]
            self.load_directory()
    
    def on_forward_clicked(self, button):
        if self.history_position < len(self.history) - 1:
            self.history_position += 1
            self.current_path = self.history[self.history_position]
            self.load_directory()
    
    def on_up_clicked(self, button):
        if self.current_path != '/':
            parent_path = os.path.dirname(self.current_path)
            self.navigate_to(parent_path)
    
    def on_home_clicked(self, button):
        home_path = os.path.expanduser("~")
        self.navigate_to(home_path)
    
    def on_refresh_clicked(self, button):
        self.load_directory()
    
    def on_path_activated(self, entry):
        path = entry.get_text()
        if not self.navigate_to(path):
            entry.set_text(self.current_path)
    
    def on_item_activated(self, treeview, path, column):
        model = treeview.get_model()
        full_path = model[path][5]
        if os.path.isdir(full_path):
            self.navigate_to(full_path)
        else:
            try:
                Gtk.show_uri_on_window(None, f"file://{full_path}", Gdk.CURRENT_TIME)
            except GLib.Error as e:
                print(f"Error opening file: {e}")
    
    def on_search_changed(self, entry):
        search_text = entry.get_text().lower()
        if not search_text:
            self.load_directory()
            return
        self.store.clear()
        try:
            entries = os.listdir(self.current_path)
            for entry in entries:
                if search_text in entry.lower():
                    full_path = os.path.join(self.current_path, entry)
                    try:
                        stat_info = os.stat(full_path)
                        size = self.format_size(stat_info.st_size) if not os.path.isdir(full_path) else ""
                        modified = datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M')
                        if os.path.isdir(full_path):
                            icon = self.get_icon_for_path(full_path, is_dir=True)
                            file_type = "Directory"
                        else:
                            icon = self.get_icon_for_path(full_path)
                            file_type = self.get_file_type(full_path)
                        self.store.append((icon, entry, size, modified, file_type, full_path))
                    except (PermissionError, FileNotFoundError):
                        pass
            result_count = len(self.store)
            self.item_count_label.set_text(f"{result_count} results")
        except (PermissionError, FileNotFoundError) as e:
            print(f"Error searching directory: {e}")
    
    def on_selection_changed(self, selection):
        """Handle changes in the file view selection."""
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            name = model[treeiter][1]
            size = model[treeiter][2]
            modified = model[treeiter][3]
            file_type = model[treeiter][4]
            self.selected_info_label.set_text(f"{name} - {file_type} - {size} - {modified}")
        else:
            self.selected_info_label.set_text("")