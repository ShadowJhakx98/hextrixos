#!/usr/bin/env python3
# HexDroid - Android Application Manager for Hextrix OS
# GUI application for managing Android applications

import os
import sys
import json
import subprocess
import threading
import time
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Pango

# Configuration
HOME_DIR = os.path.expanduser("~")
HEXDROID_DIR = os.path.join(HOME_DIR, ".hexdroid")
APP_DATA_DIR = os.path.join(HEXDROID_DIR, "appdata")
APP_ICONS_DIR = os.path.join(HEXDROID_DIR, "icons")
ANBOX_DATA_DIR = os.path.join(HEXDROID_DIR, "anbox-data")
WAYDROID_DATA_DIR = os.path.join(HEXDROID_DIR, "waydroid-data")
LINEAGE_DATA_DIR = os.path.join(HEXDROID_DIR, "lineage-data")
INSTALLED_APPS_FILE = os.path.join(APP_DATA_DIR, "installed_apps.json")
HEXDROID_SCRIPTS_DIR = HEXDROID_DIR
DEFAULT_ICON = os.path.join(HEXDROID_DIR, "default_icon.png")
HEXDROID_ICON = os.path.join("/home/jared/hextrix-ai-os-env/hexdroid", "hexdroid.png")

# Ensure app data directory exists
os.makedirs(APP_DATA_DIR, exist_ok=True)
os.makedirs(APP_ICONS_DIR, exist_ok=True)
os.makedirs(ANBOX_DATA_DIR, exist_ok=True)
os.makedirs(WAYDROID_DATA_DIR, exist_ok=True)
os.makedirs(LINEAGE_DATA_DIR, exist_ok=True)

# Create installed apps file if it doesn't exist
if not os.path.exists(INSTALLED_APPS_FILE):
    with open(INSTALLED_APPS_FILE, "w") as f:
        f.write("[]")

# Primary colors from Hextrix OS theme
HEXTRIX_BLUE = "#2389DE"
HEXTRIX_DARK = "#263238"
HEXTRIX_LIGHT = "#F5F5F5"
HEXTRIX_ACCENT = "#FF5722"
HEXTRIX_GREEN = "#4CAF50"
HEXTRIX_RED = "#F44336"

class HexDroidApp:
    def __init__(self):
        self.create_css()
        self.builder = Gtk.Builder()
        
        # Set up the main window
        self.window = Gtk.Window(title="HexDroid - Android Application Manager")
        self.window.set_default_size(900, 600)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        
        try:
            self.window.set_icon_from_file(HEXDROID_ICON)
        except:
            pass
            
        self.window.connect("destroy", Gtk.main_quit)
        
        # Set up header bar
        self.header = Gtk.HeaderBar()
        self.header.set_show_close_button(True)
        self.header.props.title = "HexDroid"
        self.header.props.subtitle = "Android Application Manager for Hextrix OS"
        self.window.set_titlebar(self.header)
        
        # Refresh button
        refresh_button = Gtk.Button()
        refresh_icon = Gtk.Image.new_from_icon_name("view-refresh-symbolic", Gtk.IconSize.BUTTON)
        refresh_button.add(refresh_icon)
        refresh_button.set_tooltip_text("Refresh Application List")
        refresh_button.connect("clicked", self.on_refresh_clicked)
        self.header.pack_start(refresh_button)
        
        # Install button
        install_button = Gtk.Button()
        install_icon = Gtk.Image.new_from_icon_name("list-add-symbolic", Gtk.IconSize.BUTTON)
        install_button.add(install_icon)
        install_button.set_tooltip_text("Install Android Application")
        install_button.connect("clicked", self.on_install_clicked)
        self.header.pack_start(install_button)
        
        # Runtime selection
        self.runtime_combo = Gtk.ComboBoxText()
        self.runtime_combo.append_text("Anbox")
        self.runtime_combo.append_text("Waydroid")
        self.runtime_combo.append_text("LineageOS")
        self.runtime_combo.set_active(0)
        self.runtime_combo.set_tooltip_text("Select Android Runtime")
        self.runtime_combo.connect("changed", self.on_runtime_changed)
        self.header.pack_end(self.runtime_combo)
        
        # Main content area with paned view
        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.window.add(paned)
        
        # Left side: App list
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        left_box.set_border_width(10)
        
        # Search entry
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        search_label = Gtk.Label(label="Search:")
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search applications...")
        self.search_entry.connect("search-changed", self.on_search_changed)
        search_box.pack_start(search_label, False, False, 0)
        search_box.pack_start(self.search_entry, True, True, 0)
        left_box.pack_start(search_box, False, False, 0)
        
        # Create app list
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_min_content_width(300)
        
        self.app_store = Gtk.ListStore(str, str, str, str, str, GdkPixbuf.Pixbuf)  # id, name, package, runtime, date, icon
        self.app_filter = self.app_store.filter_new()
        self.app_filter.set_visible_func(self.filter_apps)
        
        self.app_list = Gtk.TreeView.new_with_model(self.app_filter)
        self.app_list.set_headers_visible(True)
        
        # App icon column
        renderer_pixbuf = Gtk.CellRendererPixbuf()
        column_pixbuf = Gtk.TreeViewColumn("", renderer_pixbuf, pixbuf=5)
        self.app_list.append_column(column_pixbuf)
        
        # App name column
        renderer_text = Gtk.CellRendererText()
        renderer_text.set_property("ellipsize", Pango.EllipsizeMode.END)
        column_text = Gtk.TreeViewColumn("Application", renderer_text, text=1)
        column_text.set_resizable(True)
        column_text.set_expand(True)
        self.app_list.append_column(column_text)
        
        # Runtime column
        renderer_runtime = Gtk.CellRendererText()
        column_runtime = Gtk.TreeViewColumn("Runtime", renderer_runtime, text=3)
        self.app_list.append_column(column_runtime)
        
        # Selection
        select = self.app_list.get_selection()
        select.connect("changed", self.on_app_selected)
        
        scrolled_window.add(self.app_list)
        left_box.pack_start(scrolled_window, True, True, 0)
        
        # Stats label
        self.stats_label = Gtk.Label()
        self.stats_label.set_xalign(0)
        left_box.pack_start(self.stats_label, False, False, 0)
        
        paned.add1(left_box)
        
        # Right side: App details
        self.detail_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.detail_box.set_border_width(20)
        
        # App header with icon and name
        self.app_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.app_icon = Gtk.Image()
        self.app_icon.set_pixel_size(64)
        self.app_header.pack_start(self.app_icon, False, False, 0)
        
        self.app_title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.app_name_label = Gtk.Label()
        self.app_name_label.set_xalign(0)
        self.app_name_label.set_markup("<span size='x-large' weight='bold'>Select an Application</span>")
        self.app_package_label = Gtk.Label()
        self.app_package_label.set_xalign(0)
        
        self.app_title_box.pack_start(self.app_name_label, False, False, 0)
        self.app_title_box.pack_start(self.app_package_label, False, False, 0)
        self.app_header.pack_start(self.app_title_box, True, True, 0)
        
        self.detail_box.pack_start(self.app_header, False, False, 0)
        
        # App details grid
        self.details_grid = Gtk.Grid()
        self.details_grid.set_column_spacing(20)
        self.details_grid.set_row_spacing(10)
        self.details_grid.set_margin_top(20)
        
        # Runtime label
        runtime_label = Gtk.Label(label="Runtime:")
        runtime_label.set_xalign(0)
        self.details_grid.attach(runtime_label, 0, 0, 1, 1)
        
        self.app_runtime_label = Gtk.Label()
        self.app_runtime_label.set_xalign(0)
        self.details_grid.attach(self.app_runtime_label, 1, 0, 1, 1)
        
        # Install date label
        install_date_label = Gtk.Label(label="Installed:")
        install_date_label.set_xalign(0)
        self.details_grid.attach(install_date_label, 0, 1, 1, 1)
        
        self.app_install_date_label = Gtk.Label()
        self.app_install_date_label.set_xalign(0)
        self.details_grid.attach(self.app_install_date_label, 1, 1, 1, 1)
        
        self.detail_box.pack_start(self.details_grid, False, False, 0)
        
        # Action buttons
        self.action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.action_box.set_margin_top(30)
        
        self.launch_button = Gtk.Button(label="Launch")
        self.launch_button.connect("clicked", self.on_launch_clicked)
        self.launch_button.set_sensitive(False)
        self.action_box.pack_start(self.launch_button, True, True, 0)
        
        self.uninstall_button = Gtk.Button(label="Uninstall")
        self.uninstall_button.connect("clicked", self.on_uninstall_clicked)
        self.uninstall_button.set_sensitive(False)
        self.action_box.pack_start(self.uninstall_button, True, True, 0)
        
        self.detail_box.pack_start(self.action_box, False, False, 0)
        
        # Advanced options
        self.advanced_expander = Gtk.Expander(label="Advanced Options")
        self.advanced_expander.set_margin_top(20)
        
        advanced_grid = Gtk.Grid()
        advanced_grid.set_column_spacing(10)
        advanced_grid.set_row_spacing(10)
        advanced_grid.set_margin_top(10)
        
        # ADB Shell button
        self.adb_shell_button = Gtk.Button(label="ADB Shell")
        self.adb_shell_button.connect("clicked", self.on_adb_shell_clicked)
        self.adb_shell_button.set_tooltip_text("Open ADB shell to the Android environment")
        advanced_grid.attach(self.adb_shell_button, 0, 0, 1, 1)
        
        # Package manager button
        self.package_manager_button = Gtk.Button(label="Package Manager")
        self.package_manager_button.connect("clicked", self.on_package_manager_clicked)
        self.package_manager_button.set_tooltip_text("Open Android package manager")
        advanced_grid.attach(self.package_manager_button, 1, 0, 1, 1)
        
        # Runtime restart button
        self.restart_runtime_button = Gtk.Button(label="Restart Runtime")
        self.restart_runtime_button.connect("clicked", self.on_restart_runtime_clicked)
        self.restart_runtime_button.set_tooltip_text("Restart the Android runtime")
        advanced_grid.attach(self.restart_runtime_button, 0, 1, 1, 1)
        
        # Settings button
        self.settings_button = Gtk.Button(label="Runtime Settings")
        self.settings_button.connect("clicked", self.on_settings_clicked)
        self.settings_button.set_tooltip_text("Configure Android runtime settings")
        advanced_grid.attach(self.settings_button, 1, 1, 1, 1)
        
        # LineageOS start button
        self.start_lineageos_button = Gtk.Button(label="Start LineageOS")
        self.start_lineageos_button.connect("clicked", self.on_start_lineageos_clicked)
        self.start_lineageos_button.set_tooltip_text("Start LineageOS with QEMU")
        advanced_grid.attach(self.start_lineageos_button, 0, 2, 2, 1)
        
        self.advanced_expander.add(advanced_grid)
        self.detail_box.pack_start(self.advanced_expander, False, False, 0)
        
        # Help text when no app is selected
        self.help_label = Gtk.Label()
        self.help_label.set_line_wrap(True)
        self.help_label.set_max_width_chars(40)
        self.help_label.set_markup(
            "<span size='large'>Welcome to HexDroid</span>\n\n"
            "Use this application to manage your Android apps on Hextrix OS.\n\n"
            "• Install Android applications (.apk files)\n"
            "• Launch installed Android apps\n"
            "• Uninstall applications you no longer need\n"
            "• Switch between Anbox and Waydroid runtimes\n\n"
            "Click the '+' button in the header bar to install a new application."
        )
        self.help_label.set_justify(Gtk.Justification.CENTER)
        self.help_label.set_valign(Gtk.Align.CENTER)
        self.help_label.set_halign(Gtk.Align.CENTER)
        
        self.help_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.help_box.pack_start(self.help_label, True, True, 0)
        
        # Status bar
        self.statusbar = Gtk.Statusbar()
        self.statusbar.push(0, "Ready")
        self.detail_box.pack_end(self.statusbar, False, False, 0)
        
        self.stack = Gtk.Stack()
        self.stack.add_named(self.help_box, "help")
        self.stack.add_named(self.detail_box, "details")
        self.stack.set_visible_child_name("help")
        
        paned.add2(self.stack)
        
        # Runtime status
        self.runtime_status = "Initializing..."
        self.update_runtime_status_thread = threading.Thread(target=self.update_runtime_status, daemon=True)
        self.update_runtime_status_thread.start()
        
        # Load initial apps
        self.selected_app = None
        self.load_apps()
        
        # Show all
        self.window.show_all()
    
    def create_css(self):
        """Apply custom CSS styling"""
        css_provider = Gtk.CssProvider()
        css = f"""
        headerbar {{
            background-color: {HEXTRIX_BLUE};
            color: white;
        }}
        
        .titlebar {{
            background-color: {HEXTRIX_BLUE};
            color: white;
        }}
        
        button {{
            border-radius: 4px;
        }}
        
        button.suggested-action {{
            background-color: {HEXTRIX_GREEN};
            color: white;
        }}
        
        button.destructive-action {{
            background-color: {HEXTRIX_RED};
            color: white;
        }}
        """
        css_provider.load_from_data(css.encode())
        screen = Gdk.Screen.get_default()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    
    def load_apps(self):
        """Load installed Android applications"""
        self.app_store.clear()
        try:
            with open(INSTALLED_APPS_FILE, "r") as f:
                apps = json.load(f)
                
            for app in apps:
                app_id = app.get("id", "")
                app_name = app.get("name", "Unknown")
                app_package = app.get("package", "")
                app_runtime = app.get("runtime", "anbox").capitalize()
                app_install_date = app.get("installed", "")
                
                # Load app icon
                icon_path = app.get("icon", DEFAULT_ICON)
                if not os.path.exists(icon_path):
                    icon_path = DEFAULT_ICON
                
                try:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(icon_path, 32, 32, True)
                except:
                    # Use fallback icon if loading fails
                    pixbuf = Gtk.IconTheme.get_default().load_icon("application-x-executable", 32, 0)
                
                self.app_store.append([app_id, app_name, app_package, app_runtime, app_install_date, pixbuf])
            
            # Update stats
            self.update_stats()
            
        except Exception as e:
            print(f"Error loading apps: {e}")
            self.statusbar.push(0, f"Error loading apps: {e}")
    
    def update_stats(self):
        """Update application statistics label"""
        total_apps = len(self.app_store)
        anbox_apps = sum(1 for row in self.app_store if row[3] == "Anbox")
        waydroid_apps = sum(1 for row in self.app_store if row[3] == "Waydroid")
        lineageos_apps = sum(1 for row in self.app_store if row[3] == "LineageOS")
        
        stats_text = f"Total: {total_apps} apps (Anbox: {anbox_apps}, Waydroid: {waydroid_apps}, LineageOS: {lineageos_apps})"
        self.stats_label.set_text(stats_text)
    
    def filter_apps(self, model, iter, data):
        """Filter function for the app list search"""
        search_text = self.search_entry.get_text().lower()
        if not search_text:
            return True
            
        app_name = model[iter][1].lower()
        app_package = model[iter][2].lower()
        
        return search_text in app_name or search_text in app_package
    
    def on_search_changed(self, widget):
        """Handle search entry changes"""
        self.app_filter.refilter()
    
    def on_app_selected(self, selection):
        """Handle app selection in the list"""
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            app_id = model[treeiter][0]
            app_name = model[treeiter][1]
            app_package = model[treeiter][2]
            app_runtime = model[treeiter][3]
            app_date = model[treeiter][4]
            
            # Find full app info from JSON
            try:
                with open(INSTALLED_APPS_FILE, "r") as f:
                    apps = json.load(f)
                    app_info = next((app for app in apps if app["id"] == app_id), None)
                    
                    if app_info:
                        self.selected_app = app_info
                        
                        # Update app details
                        self.app_name_label.set_markup(f"<span size='x-large' weight='bold'>{app_name}</span>")
                        self.app_package_label.set_text(app_package)
                        self.app_runtime_label.set_text(app_runtime)
                        
                        # Format date for display
                        try:
                            # Try to parse ISO date and format it
                            from datetime import datetime
                            date_obj = datetime.fromisoformat(app_date.replace('Z', '+00:00'))
                            formatted_date = date_obj.strftime("%B %d, %Y %I:%M %p")
                            self.app_install_date_label.set_text(formatted_date)
                        except:
                            # Fall back to raw date string if parsing fails
                            self.app_install_date_label.set_text(app_date)
                        
                        # Load app icon (larger version for details panel)
                        icon_path = app_info.get("icon", DEFAULT_ICON)
                        if not os.path.exists(icon_path):
                            icon_path = DEFAULT_ICON
                            
                        try:
                            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(icon_path, 64, 64, True)
                            self.app_icon.set_from_pixbuf(pixbuf)
                        except:
                            self.app_icon.set_from_icon_name("application-x-executable", Gtk.IconSize.DIALOG)
                        
                        # Enable action buttons
                        self.launch_button.set_sensitive(True)
                        self.uninstall_button.set_sensitive(True)
                        
                        # Show details panel
                        self.stack.set_visible_child_name("details")
                        
                        return
            except Exception as e:
                print(f"Error loading app details: {e}")
                self.statusbar.push(0, f"Error loading app details: {e}")
        
        # No app selected or error loading details
        self.selected_app = None
        self.launch_button.set_sensitive(False)
        self.uninstall_button.set_sensitive(False)
        self.stack.set_visible_child_name("help")
    
    def on_refresh_clicked(self, button):
        """Refresh app list"""
        self.statusbar.push(0, "Refreshing application list...")
        self.load_apps()
        self.statusbar.push(0, "Application list refreshed")
    
    def on_install_clicked(self, button):
        """Show file chooser for installing APK files"""
        dialog = Gtk.FileChooserDialog(
            title="Select Android APK to Install",
            parent=self.window,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        
        # Add filters
        apk_filter = Gtk.FileFilter()
        apk_filter.set_name("Android Package (APK)")
        apk_filter.add_pattern("*.apk")
        dialog.add_filter(apk_filter)
        
        all_filter = Gtk.FileFilter()
        all_filter.set_name("All Files")
        all_filter.add_pattern("*")
        dialog.add_filter(all_filter)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            apk_path = dialog.get_filename()
            runtime = "anbox" if self.runtime_combo.get_active() == 0 else "waydroid"
            dialog.destroy()
            
            # Show progress dialog
            self.show_progress_dialog("Installing Application", "Installing Android application. This may take a few moments...")
            
            # Run installation in a separate thread
            threading.Thread(target=self.install_apk, args=(apk_path, runtime), daemon=True).start()
        else:
            dialog.destroy()
    
    def install_apk(self, apk_path, runtime):
        """Install an Android APK"""
        try:
            if runtime == "lineageos":
                # For LineageOS, we use the lineageos-install-apk.sh script
                install_script = os.path.join(HEXDROID_SCRIPTS_DIR, "lineageos-install-apk.sh")
                cmd = [install_script, apk_path]
                
                process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True
                )
                stdout, stderr = process.communicate()
                
                # Check if LineageOS is running
                if process.returncode != 0 and "not running" in stderr:
                    GLib.idle_add(self.hide_progress_dialog)
                    GLib.idle_add(self.show_message_dialog, "LineageOS Not Running", 
                                 "LineageOS is not running. Please start it first using the LineageOS runtime.")
                    return
                
                # Create app metadata manually since the script doesn't do it
                if process.returncode == 0:
                    # Extract app name from APK
                    app_name = os.path.basename(apk_path).replace('.apk', '')
                    try:
                        # Try to get app name using aapt if available
                        aapt_result = subprocess.run(
                            ["aapt", "dump", "badging", apk_path], 
                            capture_output=True, 
                            text=True
                        )
                        if aapt_result.returncode == 0:
                            for line in aapt_result.stdout.splitlines():
                                if line.startswith('application-label:'):
                                    app_name = line.split('\'')[1]
                                    break
                    except:
                        pass
                    
                    # Extract package name
                    package_name = "unknown"
                    try:
                        aapt_result = subprocess.run(
                            ["aapt", "dump", "badging", apk_path], 
                            capture_output=True, 
                            text=True
                        )
                        if aapt_result.returncode == 0:
                            for line in aapt_result.stdout.splitlines():
                                if line.startswith('package:'):
                                    for part in line.split(' '):
                                        if part.startswith('name='):
                                            package_name = part.split('\'')[1]
                                            break
                    except:
                        pass
                    
                    # Create a safe ID for the app
                    app_id = "".join(c for c in app_name if c.isalnum() or c in ('_', '-')).lower()
                    
                    # Create app entry
                    app_entry = {
                        "id": app_id,
                        "name": app_name,
                        "package": package_name,
                        "runtime": "lineageos",
                        "installed": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                    }
                    
                    # Add to installed apps JSON
                    with open(INSTALLED_APPS_FILE, "r") as f:
                        apps = json.load(f)
                    
                    apps.append(app_entry)
                    
                    with open(INSTALLED_APPS_FILE, "w") as f:
                        json.dump(apps, f, indent=2)
            else:
                # For Anbox and Waydroid, use the regular installation script
                install_script = os.path.join(HEXDROID_SCRIPTS_DIR, "hexdroid-install.sh")
                cmd = [install_script, "--runtime", runtime, apk_path]
                
                process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True
                )
                stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                GLib.idle_add(self.hide_progress_dialog)
                GLib.idle_add(self.show_message_dialog, "Installation Complete", "The Android application was successfully installed.")
                GLib.idle_add(self.load_apps)
            else:
                error_msg = stderr if stderr else "Unknown error occurred"
                GLib.idle_add(self.hide_progress_dialog)
                GLib.idle_add(self.show_message_dialog, "Installation Failed", f"Failed to install application: {error_msg}")
        
        except Exception as e:
            GLib.idle_add(self.hide_progress_dialog)
            GLib.idle_add(self.show_message_dialog, "Installation Error", f"Error installing application: {str(e)}")
    
    def on_launch_clicked(self, button):
        """Launch the selected Android application"""
        if not self.selected_app:
            return
            
        app_id = self.selected_app.get("id", "")
        app_name = self.selected_app.get("name", "")
        app_package = self.selected_app.get("package", "")
        runtime = self.selected_app.get("runtime", "anbox").lower()
        
        try:
            self.statusbar.push(0, f"Launching {app_name}...")
            
            if runtime == "anbox":
                # Format: anbox launch --package=com.package.name --component=com.package.name.MainActivity
                cmd = ["anbox", "launch", f"--package={app_package}", f"--component={app_package}.MainActivity"]
            elif runtime == "waydroid":
                # Format: waydroid app launch com.package.name
                cmd = ["waydroid", "app", "launch", app_package]
            elif runtime == "lineageos":
                # For LineageOS, we use adb to launch the app
                # First check if LineageOS is running
                adb_devices = subprocess.run(["adb", "devices"], capture_output=True, text=True)
                if "localhost:5555" not in adb_devices.stdout:
                    self.show_message_dialog(
                        "LineageOS Not Running", 
                        "LineageOS is not running. Please start it first using the LineageOS runtime."
                    )
                    return
                    
                # Launch the app through ADB
                cmd = [
                    "adb", "-s", "localhost:5555", "shell", 
                    f"am start -n {app_package}/{app_package}.MainActivity"
                ]
            
            subprocess.Popen(cmd)
            self.statusbar.push(0, f"Launched {app_name}")
        except Exception as e:
            self.statusbar.push(0, f"Error launching application: {e}")
            self.show_message_dialog("Launch Error", f"Error launching application: {str(e)}")
    
    def on_uninstall_clicked(self, button):
        """Uninstall the selected Android application"""
        if not self.selected_app:
            return
            
        app_id = self.selected_app.get("id", "")
        app_name = self.selected_app.get("name", "")
        
        # Confirm uninstallation
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Uninstall {app_name}?"
        )
        dialog.format_secondary_text(
            "This will permanently remove the application and all of its data. This action cannot be undone."
        )
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.YES:
            # Show progress dialog
            self.show_progress_dialog("Uninstalling Application", f"Uninstalling {app_name}. This may take a moment...")
            
            # Run uninstallation in a separate thread
            threading.Thread(target=self.uninstall_app, args=(app_id,), daemon=True).start()
    
    def uninstall_app(self, app_id):
        """Uninstall an Android application"""
        try:
            # Get the app info first to check runtime
            with open(INSTALLED_APPS_FILE, "r") as f:
                apps = json.load(f)
            
            app_info = next((app for app in apps if app.get("id") == app_id), None)
            if not app_info:
                GLib.idle_add(self.hide_progress_dialog)
                GLib.idle_add(self.show_message_dialog, "Uninstallation Error", "Application not found in database.")
                return
            
            runtime = app_info.get("runtime", "anbox").lower()
            package = app_info.get("package", "")
            
            if runtime == "lineageos":
                # For LineageOS, uninstall via ADB
                # First check if LineageOS is running
                adb_devices = subprocess.run(["adb", "devices"], capture_output=True, text=True)
                if "localhost:5555" not in adb_devices.stdout:
                    GLib.idle_add(self.hide_progress_dialog)
                    GLib.idle_add(self.show_message_dialog, "LineageOS Not Running", 
                                 "LineageOS is not running. Please start it first.")
                    return
                
                # Uninstall the app
                uninstall_cmd = ["adb", "-s", "localhost:5555", "uninstall", package]
                process = subprocess.Popen(
                    uninstall_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate()
                
                if process.returncode == 0 or "Success" in stdout:
                    # Remove from JSON database
                    apps = [app for app in apps if app.get("id") != app_id]
                    with open(INSTALLED_APPS_FILE, "w") as f:
                        json.dump(apps, f, indent=2)
                    
                    GLib.idle_add(self.hide_progress_dialog)
                    GLib.idle_add(self.show_message_dialog, "Uninstallation Complete", 
                                 "The Android application was successfully uninstalled.")
                    GLib.idle_add(self.load_apps)
                    GLib.idle_add(self.stack.set_visible_child_name, "help")
                else:
                    error_msg = stderr if stderr else "Unknown error occurred"
                    GLib.idle_add(self.hide_progress_dialog)
                    GLib.idle_add(self.show_message_dialog, "Uninstallation Failed", 
                                 f"Failed to uninstall application: {error_msg}")
            else:
                # For Anbox and Waydroid, use the existing uninstall script
                uninstall_script = os.path.join(HEXDROID_SCRIPTS_DIR, "hexdroid-uninstall.sh")
                cmd = [uninstall_script, app_id]
                
                process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True
                )
                stdout, stderr = process.communicate()
                
                if process.returncode == 0:
                    GLib.idle_add(self.hide_progress_dialog)
                    GLib.idle_add(self.show_message_dialog, "Uninstallation Complete", 
                                 "The Android application was successfully uninstalled.")
                    GLib.idle_add(self.load_apps)
                    GLib.idle_add(self.stack.set_visible_child_name, "help")
                else:
                    error_msg = stderr if stderr else "Unknown error occurred"
                    GLib.idle_add(self.hide_progress_dialog)
                    GLib.idle_add(self.show_message_dialog, "Uninstallation Failed", 
                                 f"Failed to uninstall application: {error_msg}")
        
        except Exception as e:
            GLib.idle_add(self.hide_progress_dialog)
            GLib.idle_add(self.show_message_dialog, "Uninstallation Error", f"Error uninstalling application: {str(e)}")
    
    def on_runtime_changed(self, combo):
        """Handle runtime selection change"""
        runtime_index = combo.get_active()
        if runtime_index == 0:
            runtime = "Anbox"
        elif runtime_index == 1:
            runtime = "Waydroid"
        else:
            runtime = "LineageOS"
        
        self.statusbar.push(0, f"Changed default runtime to {runtime}")
    
    def on_adb_shell_clicked(self, button):
        """Open an ADB shell to the Android environment"""
        runtime_index = self.runtime_combo.get_active()
        if runtime_index == 0:
            runtime = "anbox"
        elif runtime_index == 1:
            runtime = "waydroid"
        else:
            runtime = "lineageos"
        
        try:
            if runtime == "anbox":
                # For Anbox, first connect to ADB
                subprocess.run(["adb", "connect", "192.168.250.2"])
                # Then open a terminal with an ADB shell
                subprocess.Popen(["x-terminal-emulator", "-e", "adb shell"])
            elif runtime == "waydroid":
                # For Waydroid, open a terminal with waydroid shell
                subprocess.Popen(["x-terminal-emulator", "-e", "waydroid shell"])
            elif runtime == "lineageos":
                # For LineageOS, connect to ADB on localhost:5555
                # First check if it's running
                adb_devices = subprocess.run(["adb", "devices"], capture_output=True, text=True)
                if "localhost:5555" not in adb_devices.stdout:
                    self.show_message_dialog("LineageOS Not Running", 
                                           "LineageOS is not running. Please start it first.")
                    return
                    
                # Open a terminal with an ADB shell
                subprocess.Popen(["x-terminal-emulator", "-e", "adb -s localhost:5555 shell"])
        except Exception as e:
            self.show_message_dialog("Error", f"Failed to open shell: {str(e)}")
    
    def on_package_manager_clicked(self, button):
        """Open Android package manager"""
        runtime = "anbox" if self.runtime_combo.get_active() == 0 else "waydroid"
        
        try:
            if runtime == "anbox":
                # For Anbox, launch package manager activity
                subprocess.Popen(["anbox", "launch", "--package=com.android.settings", "--component=com.android.settings.ManageApplications"])
            else:  # waydroid
                # For Waydroid, launch settings app
                subprocess.Popen(["waydroid", "app", "launch", "com.android.settings"])
        except Exception as e:
            self.show_message_dialog("Error", f"Failed to open package manager: {str(e)}")
    
    def on_restart_runtime_clicked(self, button):
        """Restart the Android runtime"""
        runtime_index = self.runtime_combo.get_active()
        if runtime_index == 0:
            runtime = "anbox"
        elif runtime_index == 1:
            runtime = "waydroid"
        else:
            runtime = "lineageos"
        
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Restart {runtime.capitalize()} Runtime?"
        )
        dialog.format_secondary_text(
            f"This will stop and restart the {runtime.capitalize()} service. Any running Android applications will be closed."
        )
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.YES:
            self.show_progress_dialog(f"Restarting {runtime.capitalize()}", f"Restarting {runtime.capitalize()} Android runtime. This may take a moment...")
            
            # Run restart in a separate thread
            threading.Thread(target=self.restart_runtime, args=(runtime,), daemon=True).start()
    
    def restart_runtime(self, runtime):
        """Restart the specified Android runtime"""
        try:
            if runtime == "anbox":
                # Restart Anbox
                subprocess.run(["systemctl", "--user", "restart", "anbox.service"])
            elif runtime == "waydroid":
                # Restart Waydroid
                subprocess.run(["waydroid", "session", "stop"])
                time.sleep(2)
                subprocess.run(["waydroid", "session", "start"])
            elif runtime == "lineageos":
                # For LineageOS, we need to stop QEMU process and restart it
                # First, check if it's running
                adb_devices = subprocess.run(["adb", "devices"], capture_output=True, text=True)
                if "localhost:5555" in adb_devices.stdout:
                    # Disconnect ADB
                    subprocess.run(["adb", "disconnect", "localhost:5555"])
                    
                    # Find QEMU process and kill it
                    ps_result = subprocess.run(["ps", "-ef"], capture_output=True, text=True)
                    for line in ps_result.stdout.splitlines():
                        if "qemu-system-x86_64" in line and f"-hda {LINEAGE_DATA_DIR}/images/lineage-" in line:
                            pid = line.split()[1]
                            try:
                                subprocess.run(["kill", pid])
                            except:
                                pass
            
                # Wait a moment for processes to terminate
                time.sleep(3)
                
                # Start LineageOS
                start_script = os.path.join(HEXDROID_DIR, "start-lineageos.sh")
                if os.path.exists(start_script):
                    subprocess.Popen([start_script, "--no-ui"])
                
            # Update runtime status
            self.update_runtime_status()
            
            GLib.idle_add(self.hide_progress_dialog)
            GLib.idle_add(self.show_message_dialog, "Restart Complete", f"{runtime.capitalize()} runtime has been restarted.")
        
        except Exception as e:
            GLib.idle_add(self.hide_progress_dialog)
            GLib.idle_add(self.show_message_dialog, "Restart Error", f"Error restarting {runtime}: {str(e)}")
    
    def on_settings_clicked(self, button):
        """Open runtime settings"""
        runtime_index = self.runtime_combo.get_active()
        if runtime_index == 0:
            runtime = "anbox"
        elif runtime_index == 1:
            runtime = "waydroid"
        else:
            runtime = "lineageos"
        
        try:
            if runtime == "anbox":
                # For Anbox, launch Android settings
                subprocess.Popen(["anbox", "launch", "--package=com.android.settings", "--component=com.android.settings.Settings"])
            elif runtime == "waydroid":
                # For Waydroid, open settings
                subprocess.Popen(["waydroid", "show-full-ui"])
                time.sleep(2)
                subprocess.Popen(["waydroid", "app", "launch", "com.android.settings"])
            elif runtime == "lineageos":
                # For LineageOS, use ADB to launch settings
                # First check if it's running
                adb_devices = subprocess.run(["adb", "devices"], capture_output=True, text=True)
                if "localhost:5555" not in adb_devices.stdout:
                    self.show_message_dialog("LineageOS Not Running", 
                                           "LineageOS is not running. Please start it first.")
                    return
                
                # Launch settings
                subprocess.Popen([
                    "adb", "-s", "localhost:5555", "shell", 
                    "am start -n com.android.settings/.Settings"
                ])
        except Exception as e:
            self.show_message_dialog("Error", f"Failed to open settings: {str(e)}")
    
    def on_start_lineageos_clicked(self, button):
        """Start LineageOS with QEMU"""
        # Check if LineageOS is already running
        adb_devices = subprocess.run(["adb", "devices"], capture_output=True, text=True)
        if "localhost:5555" in adb_devices.stdout:
            self.show_message_dialog("LineageOS Running", 
                                   "LineageOS is already running.")
            return
        
        # Show configuration dialog
        dialog = Gtk.Dialog(
            title="Start LineageOS",
            transient_for=self.window,
            flags=0,
            buttons=(
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OK, Gtk.ResponseType.OK
            )
        )
        dialog.set_default_size(400, 200)
        
        box = dialog.get_content_area()
        box.set_spacing(10)
        box.set_border_width(10)
        
        # RAM configuration
        ram_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        ram_label = Gtk.Label(label="RAM (MB):")
        ram_adjustment = Gtk.Adjustment(value=2048, lower=1024, upper=8192, step_increment=512)
        ram_spin = Gtk.SpinButton()
        ram_spin.set_adjustment(ram_adjustment)
        ram_box.pack_start(ram_label, False, False, 0)
        ram_box.pack_start(ram_spin, True, True, 0)
        box.add(ram_box)
        
        # CPU cores configuration
        cores_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        cores_label = Gtk.Label(label="CPU Cores:")
        cores_adjustment = Gtk.Adjustment(value=2, lower=1, upper=8, step_increment=1)
        cores_spin = Gtk.SpinButton()
        cores_spin.set_adjustment(cores_adjustment)
        cores_box.pack_start(cores_label, False, False, 0)
        cores_box.pack_start(cores_spin, True, True, 0)
        box.add(cores_box)
        
        # Display mode
        display_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        display_label = Gtk.Label(label="Display Mode:")
        display_combo = Gtk.ComboBoxText()
        display_combo.append_text("Show UI")
        display_combo.append_text("Headless (No UI)")
        display_combo.set_active(0)
        display_box.pack_start(display_label, False, False, 0)
        display_box.pack_start(display_combo, True, True, 0)
        box.add(display_box)
        
        # Show dialog
        box.show_all()
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            # Get configuration values
            ram = ram_spin.get_value_as_int()
            cores = cores_spin.get_value_as_int()
            show_ui = display_combo.get_active() == 0
            
            # Close dialog
            dialog.destroy()
            
            # Show progress dialog
            self.show_progress_dialog("Starting LineageOS", "Starting LineageOS with QEMU. This may take a moment...")
            
            # Run in background thread
            threading.Thread(target=self.start_lineageos, args=(ram, cores, show_ui), daemon=True).start()
        else:
            dialog.destroy()

    def start_lineageos(self, ram, cores, show_ui):
        """Start LineageOS with QEMU in a separate thread"""
        try:
            # Build command
            start_script = os.path.join(HEXDROID_DIR, "start-lineageos.sh")
            cmd = [start_script, f"--ram", str(ram), f"--cores", str(cores)]
            
            if not show_ui:
                cmd.append("--no-ui")
            
            # Start LineageOS
            if show_ui:
                # If showing UI, just run it normally
                subprocess.Popen(cmd)
            else:
                # If headless, run and wait to check for errors
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Wait a bit for QEMU to start
                time.sleep(10)
                
                # Check if ADB can connect
                adb_devices = subprocess.run(["adb", "devices"], capture_output=True, text=True)
                if "localhost:5555" in adb_devices.stdout:
                    GLib.idle_add(self.hide_progress_dialog)
                    GLib.idle_add(self.show_message_dialog, "LineageOS Started", 
                                "LineageOS has been started successfully in headless mode.")
                else:
                    GLib.idle_add(self.hide_progress_dialog)
                    GLib.idle_add(self.show_message_dialog, "LineageOS Warning", 
                                "LineageOS was started, but ADB connection was not detected. Check the runtime status.")
            
            if show_ui:
                GLib.idle_add(self.hide_progress_dialog)
        
        except Exception as e:
            GLib.idle_add(self.hide_progress_dialog)
            GLib.idle_add(self.show_message_dialog, "LineageOS Error", f"Error starting LineageOS: {str(e)}")

    def update_runtime_status(self):
        """Update runtime status in background thread"""
        while True:
            try:
                # Check Anbox status
                anbox_status = "Stopped"
                try:
                    result = subprocess.run(["systemctl", "--user", "is-active", "anbox.service"], capture_output=True, text=True)
                    if result.stdout.strip() == "active":
                        anbox_status = "Running"
                except:
                    pass
                
                # Check Waydroid status
                waydroid_status = "Stopped"
                try:
                    result = subprocess.run(["waydroid", "status"], capture_output=True, text=True)
                    if "RUNNING" in result.stdout:
                        waydroid_status = "Running"
                except:
                    pass
                
                # Check LineageOS QEMU status
                lineageos_status = "Stopped"
                try:
                    # Check if LineageOS QEMU is running by checking if ADB can connect to it
                    result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
                    if "localhost:5555" in result.stdout:
                        lineageos_status = "Running"
                except:
                    pass
                
                status_text = f"Anbox: {anbox_status}, Waydroid: {waydroid_status}, LineageOS: {lineageos_status}"
                GLib.idle_add(self.statusbar.push, 0, status_text)
            
            except Exception as e:
                print(f"Error updating runtime status: {e}")
            
            # Update every 10 seconds
            time.sleep(10)

    def show_progress_dialog(self, title, message):
        """Show a progress dialog"""
        self.progress_dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.NONE,
            text=title
        )
        self.progress_dialog.format_secondary_text(message)
        
        spinner = Gtk.Spinner()
        spinner.start()
        content_area = self.progress_dialog.get_content_area()
        content_area.add(spinner)
        
        self.progress_dialog.show_all()

    def hide_progress_dialog(self):
        """Hide the progress dialog"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.destroy()
            delattr(self, 'progress_dialog')

    def show_message_dialog(self, title, message):
        """Show a message dialog"""
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=title
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

def main():
    app = HexDroidApp()
    Gtk.main()

if __name__ == "__main__":
    main() 