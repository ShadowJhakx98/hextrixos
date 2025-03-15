import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk
import threading
import subprocess
import apt

class SoftwareCenter(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Hextrix OS Software Center")
        self.set_default_size(800, 600)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_child(self.box)  # Use set_child for Gtk.Window
        self.search_entry = Gtk.Entry()
        self.search_entry.connect("changed", self.on_search_changed)
        self.box.append(self.search_entry)  # Use append for Gtk.Box
        self.search_entry.set_hexpand(False)  # Prevent horizontal expansion
        self.notebook = Gtk.Notebook()
        self.box.append(self.notebook)
        self.notebook.set_hexpand(True)  # Allow notebook to expand horizontally
        self.notebook.set_vexpand(True)  # Allow notebook to expand vertically

        # Sets to track installed apps
        self.installed_apt = set()
        self.installed_flatpak = set()
        self.installed_snap = set()
        self.refresh_installed()

        # Initialize tabs with reference to self
        self.ubuntu_tab = UbuntuAppsTab(self)
        self.add_tab("Ubuntu Apps", self.ubuntu_tab)
        self.flatpak_tab = FlatpakAppsTab(self)
        self.add_tab("Flatpak Apps", self.flatpak_tab)
        self.snap_tab = SnapAppsTab(self)
        self.add_tab("Snap Apps", self.snap_tab)
        self.installed_tab = InstalledAppsTab(self)
        self.add_tab("Installed Apps", self.installed_tab)

        # Add PPAs on first run
        self.add_ppas()

    def add_tab(self, label, tab_content):
        """Add a tab to the notebook."""
        self.notebook.append_page(tab_content, Gtk.Label(label=label))

    def add_ppas(self):
        """Add Microsoft and Multiverse PPAs and update APT cache."""
        ppas = ["ppa:microsoft/ppa", "multiverse"]
        for ppa in ppas:
            threading.Thread(target=self.run_command, args=(["add-apt-repository", "-y", ppa],)).start()
        threading.Thread(target=self.run_command, args=(["apt", "update"],)).start()

    def on_search_changed(self, entry):
        """Update all tabs based on the search query."""
        query = entry.get_text()
        for tab in [self.ubuntu_tab, self.flatpak_tab, self.snap_tab, self.installed_tab]:
            tab.search(query)

    def run_command(self, command):
        """Execute a command with elevated privileges using pkexec and show progress."""
        dialog = ProgressDialog(self, command)
        dialog.show_all()
        threading.Thread(target=dialog.run_command).start()

    def refresh_installed(self):
        """Update the sets of installed apps."""
        # APT installed packages
        cache = apt.cache.Cache()
        self.installed_apt = {pkg.name for pkg in cache if pkg.is_installed}
        # Flatpak installed apps
        try:
            output = subprocess.check_output(["flatpak", "list", "--columns=name"]).decode("utf-8")
            self.installed_flatpak = set(line.strip() for line in output.splitlines())
        except subprocess.CalledProcessError:
            self.installed_flatpak = set()
        # Snap installed apps
        try:
            output = subprocess.check_output(["snap", "list"]).decode("utf-8")
            self.installed_snap = set(line.split()[0] for line in output.splitlines()[1:])  # Skip header
        except subprocess.CalledProcessError:
            self.installed_snap = set()

    def get_upgradable_apt(self):
        """Get list of upgradable APT packages."""
        cache = apt.cache.Cache()
        return [pkg.name for pkg in cache if pkg.is_upgradable]

    def get_upgradable_flatpak(self):
        """Get list of upgradable Flatpak apps."""
        try:
            output = subprocess.check_output(["flatpak", "update", "--list"]).decode("utf-8")
            return [line.strip() for line in output.splitlines() if line.strip()]
        except subprocess.CalledProcessError:
            return []

    def get_upgradable_snap(self):
        """Get list of upgradable Snap apps."""
        try:
            output = subprocess.check_output(["snap", "refresh", "--list"]).decode("utf-8")
            return [line.split()[0] for line in output.splitlines()[1:]]  # Skip header
        except subprocess.CalledProcessError:
            return []

    def show_details(self, app_type, app_name):
        """Show detailed information about an app."""
        dialog = AppDetailsDialog(self, app_type, app_name)
        dialog.run()
        dialog.destroy()

class ProgressDialog(Gtk.Dialog):
    def __init__(self, parent, command):
        super().__init__(title="Progress", transient_for=parent, flags=0)
        self.command = command
        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.scrolledwindow = Gtk.ScrolledWindow()
        self.scrolledwindow.set_child(self.textview)  # Use set_child for Gtk.ScrolledWindow
        self.set_child(self.scrolledwindow)  # Use set_child for Gtk.Dialog
        self.add_button("Close", Gtk.ResponseType.CLOSE)
        self.set_response_sensitive(Gtk.ResponseType.CLOSE, False)

    def run_command(self):
        """Run the command and update the text view with output."""
        process = subprocess.Popen(["pkexec"] + self.command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in iter(process.stdout.readline, ''):
            GLib.idle_add(self.append_text, line)
        process.wait()
        if process.returncode == 0:
            GLib.idle_add(self.append_text, "Operation completed successfully.")
            GLib.idle_add(self.refresh_after_command)
        else:
            GLib.idle_add(self.append_text, f"Operation failed with return code {process.returncode}.")
        GLib.idle_add(self.set_response_sensitive, Gtk.ResponseType.CLOSE, True)

    def append_text(self, text):
        buffer = self.textview.get_buffer()
        buffer.insert(buffer.get_end_iter(), text)

    def refresh_after_command(self):
        parent = self.get_transient_for()
        parent.refresh_installed()
        for tab in [parent.ubuntu_tab, parent.flatpak_tab, parent.snap_tab, parent.installed_tab]:
            tab.refresh()

class AppDetailsDialog(Gtk.Dialog):
    def __init__(self, parent, app_type, app_name):
        super().__init__(title="App Details", transient_for=parent, flags=0)
        self.app_type = app_type
        self.app_name = app_name
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_child(self.vbox)  # Use set_child for Gtk.Dialog
        self.fetch_details()
        self.add_button("Close", Gtk.ResponseType.CLOSE)

    def fetch_details(self):
        if self.app_type == "apt":
            cache = apt.cache.Cache()
            pkg = cache[self.app_name]
            details = f"Name: {pkg.name}\nVersion: {pkg.installed.version if pkg.is_installed else pkg.candidate.version}\nDescription: {pkg.summary}\nSize: {pkg.installed_size if pkg.is_installed else pkg.candidate.size} bytes"
        elif self.app_type == "flatpak":
            try:
                output = subprocess.check_output(["flatpak", "info", self.app_name]).decode("utf-8")
                details = output
            except subprocess.CalledProcessError:
                details = "Error fetching details"
        elif self.app_type == "snap":
            try:
                output = subprocess.check_output(["snap", "info", self.app_name]).decode("utf-8")
                details = output
            except subprocess.CalledProcessError:
                details = "Error fetching details"
        else:
            details = "Unknown app type"
        label = Gtk.Label(label=details)
        self.vbox.append(label)  # Use append for Gtk.Box

class AppTab(Gtk.Box):
    def __init__(self, software_center):
        self.software_center = software_center
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.listbox = Gtk.ListBox()
        self.append(self.listbox)  # Use append for Gtk.Box

    def add_message(self, message):
        row = Gtk.ListBoxRow()
        label = Gtk.Label(label=message)
        row.set_child(label)
        self.listbox.insert(row, -1)

    def add_app(self, name, description, action, action_label, details_callback, update_action=None, update_label=None):
        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        row.set_child(hbox)
        label = Gtk.Label(label=f"{name} - {description}", xalign=0)
        label.set_hexpand(True)
        hbox.append(label)
        if action_label:
            button = Gtk.Button(label=action_label)
            if action:
                button.connect("clicked", action)
            else:
                button.set_sensitive(False)
            hbox.append(button)
        if update_label:
            update_button = Gtk.Button(label=update_label)
            if update_action:
                update_button.connect("clicked", update_action)
            else:
                update_button.set_sensitive(False)
            hbox.append(update_button)
        details_button = Gtk.Button(label="Details")
        details_button.connect("clicked", details_callback)
        hbox.append(details_button)
        self.listbox.insert(row, -1)

    def search(self, query):
        """Clear and repopulate the listbox based on the search query."""
        self.listbox.foreach(self.listbox.remove)
        if query:
            self.populate_search(query)
        else:
            self.add_message("Enter a search query to find apps")

    def populate_search(self, query):
        """To be implemented by subclasses."""
        pass


    def refresh(self):
        """Refresh the tab based on the current search query."""
        query = self.software_center.search_entry.get_text()
        self.search(query)

class UbuntuAppsTab(AppTab):
    def __init__(self, software_center):
        super().__init__(software_center)
        sections = ["All"] + self.get_apt_sections()
        self.section_dropdown = Gtk.DropDown.new_from_strings(sections)
        self.section_dropdown.connect("notify::selected", self.on_section_changed)
        self.append(self.section_dropdown)
        self.section_dropdown.set_hexpand(False)
        self.current_section = None
        self.section_dropdown.set_selected(0)  # Select "All"

    def get_apt_sections(self):
        cache = apt.cache.Cache()
        sections = set()
        for pkg in cache:
            if pkg.candidate:
                sections.add(pkg.candidate.section)
        return sorted(sections)

    def on_section_changed(self, dropdown, pspec):
        selected = dropdown.get_selected()
        if selected != Gtk.INVALID_LIST_POSITION:
            section = dropdown.get_model().get_string(selected)
            self.current_section = None if section == "All" else section
            self.refresh()

    def search(self, query):
        while self.listbox.get_first_child() is not None:
            self.listbox.remove(self.listbox.get_first_child())
        cache = apt.cache.Cache()
        for pkg in cache:
            if pkg.candidate and (self.current_section is None or pkg.candidate.section == self.current_section) and query.lower() in pkg.name.lower():
                if pkg.name in self.software_center.installed_apt:
                    self.add_app(pkg.name, pkg.summary or "No description", None, "Installed", lambda: self.software_center.show_details("apt", pkg.name))
                else:
                    self.add_app(pkg.name, pkg.summary or "No description", lambda: self.install(pkg.name), "Install", lambda: self.software_center.show_details("apt", pkg.name))

class FlatpakAppsTab(AppTab):
    def populate_search(self, query):
        try:
            output = subprocess.check_output(["flatpak", "search", query]).decode("utf-8")
            for line in output.splitlines():
                parts = line.split("\t")
                if len(parts) >= 3:  # Name, Description, Application ID
                    name = parts[0]
                    description = parts[1]
                    app_id = parts[2]
                    if app_id in self.software_center.installed_flatpak:
                        self.add_app(app_id, description, None, "Installed", lambda: self.software_center.show_details("flatpak", app_id))
                    else:
                        self.add_app(app_id, description, lambda: self.install(app_id), "Install", lambda: self.software_center.show_details("flatpak", app_id))
        except subprocess.CalledProcessError:
            self.add_message("Error fetching Flatpak apps")

    def install(self, app):
        threading.Thread(target=self.software_center.run_command, args=(["flatpak", "install", "--system", "-y", "flathub", app],)).start()

class SnapAppsTab(AppTab):
    def populate_search(self, query):
        try:
            output = subprocess.check_output(["snap", "find", query]).decode("utf-8")
            for line in output.splitlines()[1:]:  # Skip header
                parts = line.split()
                if len(parts) >= 3:  # Name, Version, Publisher, Notes, Summary
                    name = parts[0]
                    description = " ".join(parts[4:]) if len(parts) > 4 else "No description"
                    if name in self.software_center.installed_snap:
                        self.add_app(name, description, None, "Installed", lambda: self.software_center.show_details("snap", name))
                    else:
                        self.add_app(name, description, lambda: self.install(name), "Install", lambda: self.software_center.show_details("snap", name))
        except subprocess.CalledProcessError:
            self.add_message("Error fetching Snap apps")

    def install(self, snap):
        threading.Thread(target=self.software_center.run_command, args=(["snap", "install", snap],)).start()

class InstalledAppsTab(AppTab):
    def search(self, query):
        while self.listbox.get_row_at_index(0) is not None:
            self.listbox.remove(self.listbox.get_row_at_index(0))
        if query:
            self.populate_search(query)
        else:
            self.populate()

    def populate(self):
        upgradable_apt = self.software_center.get_upgradable_apt()
        upgradable_flatpak = self.software_center.get_upgradable_flatpak()
        upgradable_snap = self.software_center.get_upgradable_snap()

        # APT installed packages
        cache = apt.cache.Cache()
        for pkg in cache:
            if pkg.is_installed:
                update_action = lambda: self.update_apt(pkg.name) if pkg.name in upgradable_apt else None
                update_label = "Update" if pkg.name in upgradable_apt else None
                self.add_app(pkg.name, pkg.summary or "No description", lambda: self.remove_apt(pkg.name), "Remove", lambda: self.software_center.show_details("apt", pkg.name), update_action, update_label)

        # Flatpak installed apps
        try:
            output = subprocess.check_output(["flatpak", "list", "--columns=name,description"]).decode("utf-8")
            for line in output.splitlines():
                parts = line.split("\t", 1)
                if len(parts) == 2:
                    name, description = parts
                    update_action = lambda: self.update_flatpak(name) if name in upgradable_flatpak else None
                    update_label = "Update" if name in upgradable_flatpak else None
                    self.add_app(name, description, lambda: self.remove_flatpak(name), "Remove", lambda: self.software_center.show_details("flatpak", name), update_action, update_label)
        except subprocess.CalledProcessError:
            self.add_message("Error listing Flatpak apps")

        # Snap installed apps
        try:
            output = subprocess.check_output(["snap", "list"]).decode("utf-8")
            for line in output.splitlines()[1:]:  # Skip header
                parts = line.split()
                if parts:
                    name = parts[0]
                    update_action = lambda: self.update_snap(name) if name in upgradable_snap else None
                    update_label = "Update" if name in upgradable_snap else None
                    self.add_app(name, "Snap application", lambda: self.remove_snap(name), "Remove", lambda: self.software_center.show_details("snap", name), update_action, update_label)
        except subprocess.CalledProcessError:
            self.add_message("Error listing Snap apps")

    def populate_search(self, query):
        upgradable_apt = self.software_center.get_upgradable_apt()
        upgradable_flatpak = self.software_center.get_upgradable_flatpak()
        upgradable_snap = self.software_center.get_upgradable_snap()

        # APT installed packages
        cache = apt.cache.Cache()
        for pkg in cache:
            if pkg.is_installed and query.lower() in pkg.name.lower():
                update_action = lambda: self.update_apt(pkg.name) if pkg.name in upgradable_apt else None
                update_label = "Update" if pkg.name in upgradable_apt else None
                self.add_app(pkg.name, pkg.summary or "No description", lambda: self.remove_apt(pkg.name), "Remove", lambda: self.software_center.show_details("apt", pkg.name), update_action, update_label)

        # Flatpak installed apps
        try:
            output = subprocess.check_output(["flatpak", "list", "--columns=name,description"]).decode("utf-8")
            for line in output.splitlines():
                parts = line.split("\t", 1)
                if len(parts) == 2:
                    name, description = parts
                    if query.lower() in name.lower():
                        update_action = lambda: self.update_flatpak(name) if name in upgradable_flatpak else None
                        update_label = "Update" if name in upgradable_flatpak else None
                        self.add_app(name, description, lambda: self.remove_flatpak(name), "Remove", lambda: self.software_center.show_details("flatpak", name), update_action, update_label)
        except subprocess.CalledProcessError:
            pass

        # Snap installed apps
        try:
            output = subprocess.check_output(["snap", "list"]).decode("utf-8")
            for line in output.splitlines()[1:]:
                parts = line.split()
                if parts and query.lower() in parts[0].lower():
                    name = parts[0]
                    update_action = lambda: self.update_snap(name) if name in upgradable_snap else None
                    update_label = "Update" if name in upgradable_snap else None
                    self.add_app(name, "Snap application", lambda: self.remove_snap(name), "Remove", lambda: self.software_center.show_details("snap", name), update_action, update_label)
        except subprocess.CalledProcessError:
            pass

    def remove_apt(self, package):
        threading.Thread(target=self.software_center.run_command, args=(["apt", "remove", "-y", package],)).start()

    def remove_flatpak(self, app):
        threading.Thread(target=self.software_center.run_command, args=(["flatpak", "uninstall", "--system", "-y", app],)).start()

    def remove_snap(self, snap):
        threading.Thread(target=self.software_center.run_command, args=(["snap", "remove", snap],)).start()

    def update_apt(self, package):
        threading.Thread(target=self.software_center.run_command, args=(["apt", "install", "--only-upgrade", "-y", package],)).start()

    def update_flatpak(self, app):
        threading.Thread(target=self.software_center.run_command, args=(["flatpak", "update", "-y", app],)).start()

    def update_snap(self, snap):
        threading.Thread(target=self.software_center.run_command, args=(["snap", "refresh", snap],)).start()


if __name__ == "__main__":
    win = SoftwareCenter()
    win.connect("destroy", Gtk.main_quit)
    win.show()  # Use show instead of show_all
    Gtk.main()