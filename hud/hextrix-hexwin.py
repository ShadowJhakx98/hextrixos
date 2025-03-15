#!/usr/bin/env python3
# HexWin - Windows Applications Manager for Hextrix OS
# GUI interface for managing Windows applications on Linux

import os
import sys
import subprocess
import json
import shutil
import threading
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk, GdkPixbuf, Pango

# Configuration and directories
HOME_DIR = os.path.expanduser("~")
HEXWIN_DIR = os.path.join(HOME_DIR, ".hexwin")
WINE_PREFIX = os.path.join(HEXWIN_DIR, "wineprefix")
PROTON_DIR = os.path.join(HEXWIN_DIR, "proton")
WINAPPS_DIR = os.path.join(HEXWIN_DIR, "winapps")
APP_ICONS_DIR = os.path.join(HEXWIN_DIR, "icons")
APP_DATA_DIR = os.path.join(HEXWIN_DIR, "appdata")
INSTALLED_APPS_FILE = os.path.join(APP_DATA_DIR, "installed_apps.json")

# Ensure directories exist
os.makedirs(APP_DATA_DIR, exist_ok=True)
os.makedirs(APP_ICONS_DIR, exist_ok=True)

# Ensure installed apps file exists
if not os.path.exists(INSTALLED_APPS_FILE):
    with open(INSTALLED_APPS_FILE, 'w') as f:
        json.dump([], f)


class HexWinApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.hextrix.hexwin")
        self.connect("activate", self.on_activate)
        
    def on_activate(self, app):
        # Create main window
        self.win = HexWinWindow(application=app)
        self.win.present()


class HexWinWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title("HexWin - Windows Applications Manager")
        self.set_default_size(900, 600)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # Load CSS
        css_provider = Gtk.CssProvider()
        css = """
        .cyberpunk-bg {
            background-color: #0a0a1a;
            color: #00ffcc;
        }
        .app-button {
            background-color: #222244;
            color: #00ffcc;
            border-radius: 5px;
            padding: 8px;
            margin: 4px;
        }
        .app-button:hover {
            background-color: #333366;
        }
        .header-label {
            font-size: 18px;
            font-weight: bold;
            color: #00ffcc;
        }
        .action-button {
            background-color: #3d3d6b;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            margin: 4px;
        }
        .action-button:hover {
            background-color: #4f4f8f;
        }
        .install-button {
            background-color: #006644;
            color: white;
        }
        .install-button:hover {
            background-color: #00995a;
        }
        .delete-button {
            background-color: #660022;
            color: white;
        }
        .delete-button:hover {
            background-color: #990033;
        }
        .terminal-output {
            font-family: monospace;
            background-color: #0a0a12;
            color: #00cc88;
            padding: 10px;
            border-radius: 5px;
        }
        """
        css_provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        # Set up main container
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.main_box.get_style_context().add_class("cyberpunk-bg")
        self.main_box.set_margin_top(10)
        self.main_box.set_margin_bottom(10)
        self.main_box.set_margin_start(10)
        self.main_box.set_margin_end(10)
        self.add(self.main_box)
        
        # Header
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        # Add logo/icon if available
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size("/home/jared/hextrix-ai-os-env/assets/windows_logo.png", 48, 48)
            logo = Gtk.Image.new_from_pixbuf(pixbuf)
            header_box.pack_start(logo, False, False, 5)
        except:
            # If logo not found, create text-based logo
            logo_label = Gtk.Label()
            logo_label.set_markup("<span font='24' foreground='#00ffcc'><b>⊟</b></span>")
            header_box.pack_start(logo_label, False, False, 5)
        
        # Header text
        title_label = Gtk.Label()
        title_label.set_markup("<span font='20' foreground='#00ffcc'><b>HexWin</b></span>")
        title_label.get_style_context().add_class("header-label")
        header_box.pack_start(title_label, False, False, 5)
        
        # Add subtitle
        subtitle_label = Gtk.Label()
        subtitle_label.set_markup("<span foreground='#88ffdd'>Windows Applications for Hextrix OS</span>")
        header_box.pack_start(subtitle_label, False, False, 10)
        
        # Add spacer
        header_box.pack_start(Gtk.Label(), True, True, 0)
        
        self.main_box.pack_start(header_box, False, False, 10)
        
        # Add horizontal separator
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.main_box.pack_start(separator, False, False, 5)
        
        # Main content area (notebook with tabs)
        self.notebook = Gtk.Notebook()
        self.notebook.get_style_context().add_class("cyberpunk-bg")
        self.main_box.pack_start(self.notebook, True, True, 0)
        
        # Tab 1: Installed Applications
        self.apps_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.apps_page.set_margin_top(10)
        self.apps_page.set_margin_bottom(10)
        self.apps_page.set_margin_start(10)
        self.apps_page.set_margin_end(10)
        
        # Controls for apps page
        controls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        install_btn = Gtk.Button(label="Install New Windows App")
        install_btn.get_style_context().add_class("action-button")
        install_btn.get_style_context().add_class("install-button")
        install_btn.connect("clicked", self.on_install_app_clicked)
        controls_box.pack_start(install_btn, False, False, 0)
        
        refresh_btn = Gtk.Button(label="Refresh List")
        refresh_btn.get_style_context().add_class("action-button")
        refresh_btn.connect("clicked", self.on_refresh_clicked)
        controls_box.pack_start(refresh_btn, False, False, 0)
        
        controls_box.pack_start(Gtk.Label(), True, True, 0)  # Spacer
        
        # Search functionality
        search_label = Gtk.Label(label="Search:")
        controls_box.pack_start(search_label, False, False, 0)
        
        self.search_entry = Gtk.Entry()
        self.search_entry.connect("changed", self.on_search_changed)
        controls_box.pack_start(self.search_entry, False, False, 0)
        
        self.apps_page.pack_start(controls_box, False, False, 0)
        
        # ScrolledWindow for the apps list
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        # Flow box for the apps grid
        self.apps_flow = Gtk.FlowBox()
        self.apps_flow.set_valign(Gtk.Align.START)
        self.apps_flow.set_max_children_per_line(4)
        self.apps_flow.set_selection_mode(Gtk.SelectionMode.NONE)
        self.apps_flow.set_homogeneous(True)
        scrolled.add(self.apps_flow)
        
        self.apps_page.pack_start(scrolled, True, True, 0)
        
        self.notebook.append_page(self.apps_page, Gtk.Label(label="Installed Applications"))
        
        # Tab 2: Install App
        self.install_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.install_page.set_margin_top(10)
        self.install_page.set_margin_bottom(10)
        self.install_page.set_margin_start(10)
        self.install_page.set_margin_end(10)
        
        # Installation form
        form_grid = Gtk.Grid()
        form_grid.set_column_spacing(10)
        form_grid.set_row_spacing(10)
        
        # App Name
        name_label = Gtk.Label(label="Application Name:")
        name_label.set_halign(Gtk.Align.START)
        form_grid.attach(name_label, 0, 0, 1, 1)
        
        self.name_entry = Gtk.Entry()
        form_grid.attach(self.name_entry, 1, 0, 1, 1)
        
        # Installer path
        installer_label = Gtk.Label(label="Installer (.exe):")
        installer_label.set_halign(Gtk.Align.START)
        form_grid.attach(installer_label, 0, 1, 1, 1)
        
        installer_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.installer_entry = Gtk.Entry()
        installer_box.pack_start(self.installer_entry, True, True, 0)
        
        browse_btn = Gtk.Button(label="Browse...")
        browse_btn.connect("clicked", self.on_browse_clicked)
        installer_box.pack_start(browse_btn, False, False, 0)
        
        form_grid.attach(installer_box, 1, 1, 1, 1)
        
        # Category
        category_label = Gtk.Label(label="Category:")
        category_label.set_halign(Gtk.Align.START)
        form_grid.attach(category_label, 0, 2, 1, 1)
        
        self.category_combo = Gtk.ComboBoxText()
        for category in ["Windows", "Office", "Development", "Game", "Graphics", "Internet", "Multimedia", "Utility"]:
            self.category_combo.append_text(category)
        self.category_combo.set_active(0)
        form_grid.attach(self.category_combo, 1, 2, 1, 1)
        
        # Installation method
        method_label = Gtk.Label(label="Installation Method:")
        method_label.set_halign(Gtk.Align.START)
        form_grid.attach(method_label, 0, 3, 1, 1)
        
        self.method_combo = Gtk.ComboBoxText()
        self.method_combo.append_text("Wine (Default)")
        self.method_combo.append_text("Proton (for DirectX games)")
        self.method_combo.append_text("QEMU VM (for incompatible apps)")
        self.method_combo.set_active(0)
        form_grid.attach(self.method_combo, 1, 3, 1, 1)
        
        # Install button
        install_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        install_box.set_margin_top(10)
        
        start_install_btn = Gtk.Button(label="Start Installation")
        start_install_btn.get_style_context().add_class("action-button")
        start_install_btn.get_style_context().add_class("install-button")
        start_install_btn.connect("clicked", self.on_start_install_clicked)
        install_box.pack_end(start_install_btn, False, False, 0)
        
        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect("clicked", self.on_cancel_install_clicked)
        install_box.pack_end(cancel_btn, False, False, 0)
        
        # Section for output
        output_label = Gtk.Label(label="Installation Output:")
        output_label.set_halign(Gtk.Align.START)
        
        self.output_textview = Gtk.TextView()
        self.output_textview.set_editable(False)
        self.output_textview.get_style_context().add_class("terminal-output")
        scrolled_output = Gtk.ScrolledWindow()
        scrolled_output.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_output.add(self.output_textview)
        scrolled_output.set_size_request(-1, 200)
        
        self.install_page.pack_start(form_grid, False, False, 0)
        self.install_page.pack_start(install_box, False, False, 0)
        self.install_page.pack_start(output_label, False, False, 10)
        self.install_page.pack_start(scrolled_output, True, True, 0)
        
        self.notebook.append_page(self.install_page, Gtk.Label(label="Install New Application"))
        
        # Tab 3: Configuration
        self.config_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.config_page.set_margin_top(10)
        self.config_page.set_margin_bottom(10)
        self.config_page.set_margin_start(10)
        self.config_page.set_margin_end(10)
        
        # Configuration options
        config_frame = Gtk.Frame(label="Wine Configuration")
        config_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        config_box.set_margin_top(10)
        config_box.set_margin_bottom(10)
        config_box.set_margin_start(10)
        config_box.set_margin_end(10)
        
        # Wine config button
        wine_config_btn = Gtk.Button(label="Open Wine Configuration")
        wine_config_btn.get_style_context().add_class("action-button")
        wine_config_btn.connect("clicked", self.on_wine_config_clicked)
        config_box.pack_start(wine_config_btn, False, False, 0)
        
        # Wine tricks button
        winetricks_btn = Gtk.Button(label="Open Winetricks")
        winetricks_btn.get_style_context().add_class("action-button")
        winetricks_btn.connect("clicked", self.on_winetricks_clicked)
        config_box.pack_start(winetricks_btn, False, False, 0)
        
        # Wine regedit button
        regedit_btn = Gtk.Button(label="Open Registry Editor")
        regedit_btn.get_style_context().add_class("action-button")
        regedit_btn.connect("clicked", self.on_regedit_clicked)
        config_box.pack_start(regedit_btn, False, False, 0)
        
        config_frame.add(config_box)
        self.config_page.pack_start(config_frame, False, False, 0)
        
        # VM Configuration
        vm_frame = Gtk.Frame(label="Windows VM Configuration (for incompatible apps)")
        vm_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vm_box.set_margin_top(10)
        vm_box.set_margin_bottom(10)
        vm_box.set_margin_start(10)
        vm_box.set_margin_end(10)
        
        vm_setup_btn = Gtk.Button(label="Setup Windows VM")
        vm_setup_btn.get_style_context().add_class("action-button")
        vm_setup_btn.connect("clicked", self.on_vm_setup_clicked)
        vm_box.pack_start(vm_setup_btn, False, False, 0)
        
        # VM Manager button
        vm_manager_btn = Gtk.Button(label="Open VM Manager")
        vm_manager_btn.get_style_context().add_class("action-button")
        vm_manager_btn.connect("clicked", self.on_vm_manager_clicked)
        vm_box.pack_start(vm_manager_btn, False, False, 0)
        
        vm_frame.add(vm_box)
        self.config_page.pack_start(vm_frame, False, False, 0)
        
        # About HexWin
        about_frame = Gtk.Frame(label="About HexWin")
        about_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        about_box.set_margin_top(10)
        about_box.set_margin_bottom(10)
        about_box.set_margin_start(10)
        about_box.set_margin_end(10)
        
        about_label = Gtk.Label()
        about_label.set_markup(
            "<b>HexWin</b> provides Windows application compatibility for Hextrix OS.\n\n"
            "It combines <b>Wine</b>, <b>Proton</b> (for DirectX), and <b>QEMU</b> (for incompatible apps)\n"
            "to give you the best Windows compatibility on Linux."
        )
        about_label.set_line_wrap(True)
        about_box.pack_start(about_label, False, False, 0)
        
        about_frame.add(about_box)
        self.config_page.pack_start(about_frame, False, False, 0)
        
        self.notebook.append_page(self.config_page, Gtk.Label(label="Configuration"))
        
        # Refresh the apps list
        self.load_installed_apps()
        
        self.show_all()
    
    def load_installed_apps(self):
        # Clear existing children
        for child in self.apps_flow.get_children():
            self.apps_flow.remove(child)
        
        try:
            with open(INSTALLED_APPS_FILE, 'r') as f:
                apps = json.load(f)
            
            for app in apps:
                app_box = self.create_app_box(app)
                self.apps_flow.add(app_box)
            
            self.apps_flow.show_all()
        except Exception as e:
            print(f"Error loading installed apps: {e}")
    
    def create_app_box(self, app):
        # Create a box for each app
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        box.set_margin_top(5)
        box.set_margin_bottom(5)
        box.set_margin_start(5)
        box.set_margin_end(5)
        box.set_size_request(200, 180)
        box.get_style_context().add_class("app-button")
        
        # App icon
        if os.path.exists(app['icon']):
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(app['icon'], 64, 64)
                icon = Gtk.Image.new_from_pixbuf(pixbuf)
            except:
                icon = Gtk.Image.new_from_icon_name("application-x-executable", Gtk.IconSize.DIALOG)
        else:
            icon = Gtk.Image.new_from_icon_name("application-x-executable", Gtk.IconSize.DIALOG)
        
        box.pack_start(icon, False, False, 5)
        
        # App name
        name_label = Gtk.Label(label=app['name'])
        name_label.set_line_wrap(True)
        name_label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        name_label.set_max_width_chars(20)
        box.pack_start(name_label, False, False, 5)
        
        # App type (Wine/Proton/VM)
        type_label = Gtk.Label()
        if app['type'] == 'wine':
            type_label.set_markup("<small>Wine</small>")
        elif app['type'] == 'proton':
            type_label.set_markup("<small>Proton</small>")
        else:
            type_label.set_markup("<small>Windows VM</small>")
        box.pack_start(type_label, False, False, 0)
        
        # Run button
        run_btn = Gtk.Button(label="Run")
        run_btn.get_style_context().add_class("action-button")
        run_btn.connect("clicked", self.on_run_app_clicked, app)
        box.pack_start(run_btn, False, False, 5)
        
        # Buttons container
        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        
        # Uninstall button
        uninstall_btn = Gtk.Button(label="Uninstall")
        uninstall_btn.get_style_context().add_class("delete-button")
        uninstall_btn.connect("clicked", self.on_uninstall_app_clicked, app)
        buttons_box.pack_start(uninstall_btn, True, True, 0)
        
        box.pack_start(buttons_box, False, False, 0)
        
        return box
    
    def on_run_app_clicked(self, button, app):
        try:
            if app['type'] == 'wine' or app['type'] == 'proton':
                subprocess.Popen([os.path.join(HEXWIN_DIR, "hexwin-run.sh"), app['exe']])
            elif app['type'] == 'vm':
                # For VM apps, use WinApps
                subprocess.Popen([os.path.join(WINAPPS_DIR, "winapps", "bin", "winapps"), app['alias']])
        except Exception as e:
            self.show_error_dialog(f"Error launching application: {e}")
    
    def on_uninstall_app_clicked(self, button, app):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Uninstall {app['name']}?"
        )
        dialog.format_secondary_text(
            "This will remove the application from HexWin. The Windows program files will remain in the Wine prefix."
        )
        response = dialog.run()
        
        if response == Gtk.ResponseType.YES:
            self.uninstall_app(app)
        
        dialog.destroy()
    
    def uninstall_app(self, app):
        try:
            # Remove desktop entry
            desktop_file = f"hexwin-{app['id']}.desktop"
            desktop_path = os.path.join(os.path.expanduser("~/.local/share/applications"), desktop_file)
            if os.path.exists(desktop_path):
                os.remove(desktop_path)
            
            # Remove from installed apps list
            with open(INSTALLED_APPS_FILE, 'r') as f:
                apps = json.load(f)
            
            apps = [a for a in apps if a['id'] != app['id']]
            
            with open(INSTALLED_APPS_FILE, 'w') as f:
                json.dump(apps, f, indent=2)
            
            # Refresh list
            self.load_installed_apps()
            
        except Exception as e:
            self.show_error_dialog(f"Error uninstalling application: {e}")
    
    def on_install_app_clicked(self, button):
        self.notebook.set_current_page(1)
    
    def on_refresh_clicked(self, button):
        self.load_installed_apps()
    
    def on_search_changed(self, entry):
        search_text = entry.get_text().lower()
        
        for child in self.apps_flow.get_children():
            flow_child = child.get_child()
            # Get the app name label (second child of the box)
            app_name = flow_child.get_children()[1].get_text().lower()
            
            if search_text in app_name:
                child.set_visible(True)
            else:
                child.set_visible(False)
    
    def on_browse_clicked(self, button):
        dialog = Gtk.FileChooserDialog(
            title="Select Windows Installer", 
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        
        filter_exe = Gtk.FileFilter()
        filter_exe.set_name("Windows Executables")
        filter_exe.add_pattern("*.exe")
        dialog.add_filter(filter_exe)
        
        filter_any = Gtk.FileFilter()
        filter_any.set_name("All Files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.installer_entry.set_text(dialog.get_filename())
        
        dialog.destroy()
    
    def on_start_install_clicked(self, button):
        app_name = self.name_entry.get_text()
        installer_path = self.installer_entry.get_text()
        category = self.category_combo.get_active_text()
        method_idx = self.method_combo.get_active()
        
        if not app_name:
            self.show_error_dialog("Please enter an application name.")
            return
        
        if not installer_path or not os.path.exists(installer_path):
            self.show_error_dialog("Please select a valid installer file.")
            return
        
        # Clear output
        buffer = self.output_textview.get_buffer()
        buffer.set_text("")
        
        # Start installation in a thread
        if method_idx == 0 or method_idx == 1:
            # Wine or Proton installation
            install_thread = threading.Thread(
                target=self.install_app_wine,
                args=(app_name, installer_path, category, 'proton' if method_idx == 1 else 'wine')
            )
            install_thread.daemon = True
            install_thread.start()
        elif method_idx == 2:
            # QEMU VM installation
            self.append_output("VM installation is not yet fully automated.\n")
            self.append_output("Please follow these steps:\n")
            self.append_output("1. First, make sure your Windows VM is set up (Configuration tab -> Setup Windows VM)\n")
            self.append_output("2. Follow the WinApps documentation to install the application in the VM\n")
            self.append_output("3. Configure the application in WinApps\n")
    
    def install_app_wine(self, app_name, installer_path, category, install_type):
        try:
            self.append_output(f"Starting installation of {app_name} using {install_type.upper()}...\n")
            
            # Generate a unique ID for the app
            app_id = app_name.lower().replace(" ", "-")
            
            # Create arguments
            args = [
                os.path.join(HEXWIN_DIR, "hexwin-install.sh"),
                "-n", app_name,
                "-c", category,
                installer_path
            ]
            
            # Execute the installation process
            process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Read output
            for line in process.stdout:
                self.append_output(line)
            
            # Wait for completion
            process.wait()
            
            if process.returncode == 0:
                self.append_output("\nInstallation completed successfully!\n")
                
                # Get the executable path from the output or ask user
                exe_path = None
                # Here we would parse the output to find the exe_path
                # This is a simplified version where we assume the path is in the process output
                
                # For demonstration, let's manually save this app
                safe_name = app_name.replace(" ", "_").lower()
                icon_path = os.path.join(APP_ICONS_DIR, f"{safe_name}.png")
                
                new_app = {
                    'id': app_id,
                    'name': app_name,
                    'exe': os.path.join(WINE_PREFIX, "drive_c", "Program Files", safe_name, f"{safe_name}.exe"),
                    'icon': icon_path,
                    'type': install_type,
                    'category': category
                }
                
                with open(INSTALLED_APPS_FILE, 'r') as f:
                    apps = json.load(f)
                
                apps.append(new_app)
                
                with open(INSTALLED_APPS_FILE, 'w') as f:
                    json.dump(apps, f, indent=2)
                
                # Refresh the apps list
                GLib.idle_add(self.load_installed_apps)
                GLib.idle_add(self.notebook.set_current_page, 0)
                
            else:
                self.append_output("\nInstallation failed. Please check the output for errors.\n")
                
        except Exception as e:
            self.append_output(f"\nError during installation: {e}\n")
    
    def append_output(self, text):
        GLib.idle_add(self._append_output_idle, text)
    
    def _append_output_idle(self, text):
        buffer = self.output_textview.get_buffer()
        end_iter = buffer.get_end_iter()
        buffer.insert(end_iter, text)
        # Scroll to end
        self.output_textview.scroll_to_iter(buffer.get_end_iter(), 0.0, False, 0.0, 0.0)
        return False
    
    def on_cancel_install_clicked(self, button):
        self.notebook.set_current_page(0)
        
    def on_wine_config_clicked(self, button):
        env = os.environ.copy()
        env['WINEPREFIX'] = WINE_PREFIX
        subprocess.Popen(['wine', 'winecfg'], env=env)
    
    def on_winetricks_clicked(self, button):
        env = os.environ.copy()
        env['WINEPREFIX'] = WINE_PREFIX
        subprocess.Popen(['winetricks'], env=env)
    
    def on_regedit_clicked(self, button):
        env = os.environ.copy()
        env['WINEPREFIX'] = WINE_PREFIX
        subprocess.Popen(['wine', 'regedit'], env=env)
    
    def on_vm_setup_clicked(self, button):
        subprocess.Popen([os.path.join(HEXWIN_DIR, "hexwin-setup-vm.sh")])
    
    def on_vm_manager_clicked(self, button):
        subprocess.Popen(['virt-manager'])
    
    def show_error_dialog(self, message):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text="Error"
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()


if __name__ == "__main__":
    app = HexWinApp()
    app.run(sys.argv) 