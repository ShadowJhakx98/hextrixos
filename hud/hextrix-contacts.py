import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio, GdkPixbuf
from ai.google_api_manager import GoogleAPIManager
from ai.contacts_integration import ContactsIntegration

class HextrixContacts(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Hextrix Contacts")
        self.set_default_size(800, 600)

        # Initialize Google API
        self.api_manager = GoogleAPIManager()
        if self.api_manager.authenticate():
            self.contacts_integration = ContactsIntegration(self.api_manager)
            self.contacts = self.contacts_integration.get_contacts(max_results=100)
        else:
            print("Authentication failed")
            self.contacts_integration = None
            self.contacts = []

        self.current_contact = None

        # Main layout
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.add(self.main_box)

        # Sidebar
        self.setup_sidebar()

        # Contact details
        self.setup_contact_details()

        # Apply CSS
        self.apply_css()

    def setup_sidebar(self):
        """Set up the sidebar with contact list and search."""
        self.sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.sidebar.set_size_request(250, -1)
        self.main_box.pack_start(self.sidebar, False, True, 0)

        # Search entry
        search_entry = Gtk.SearchEntry()
        search_entry.connect("search-changed", self.on_search_changed)
        self.sidebar.pack_start(search_entry, False, False, 10)

        # New Contact button
        new_contact_button = Gtk.Button(label="New Contact")
        new_contact_button.connect("clicked", self.on_new_contact)
        self.sidebar.pack_start(new_contact_button, False, False, 10)

        # Contact list
        self.contact_list = Gtk.ListBox()
        self.contact_list.connect("row-activated", self.on_contact_selected)
        scrolled = Gtk.ScrolledWindow()
        scrolled.add(self.contact_list)
        self.sidebar.pack_start(scrolled, True, True, 0)

        self.populate_contact_list()

    def setup_contact_details(self):
        """Set up the contact details view."""
        self.details_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.details_box.set_size_request(550, -1)
        self.main_box.pack_start(self.details_box, True, True, 0)

        # Photo
        self.photo_button = Gtk.Button()
        self.photo_button.set_image(Gtk.Image.new_from_icon_name(
            "avatar-default-symbolic", Gtk.IconSize.DND))
        self.photo_button.connect("clicked", self.on_change_photo)
        self.details_box.pack_start(self.photo_button, False, False, 10)

        # Fields
        self.fields = {}
        for field in ["name", "phone", "email", "address", "company"]:
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            label = Gtk.Label(label=f"{field.capitalize()}:")
            entry = Gtk.Entry()
            self.fields[field] = entry
            box.pack_start(label, False, False, 0)
            box.pack_start(entry, True, True, 0)
            self.details_box.pack_start(box, False, False, 5)

        # Notes
        notes_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        notes_label = Gtk.Label(label="Notes:")
        notes_text = Gtk.TextView()
        self.fields["notes"] = notes_text
        notes_box.pack_start(notes_label, False, False, 0)
        notes_box.pack_start(notes_text, True, True, 0)
        self.details_box.pack_start(notes_box, True, True, 5)

        # Buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        save_button = Gtk.Button(label="Save")
        save_button.connect("clicked", self.on_save_contact)
        delete_button = Gtk.Button(label="Delete")
        delete_button.connect("clicked", self.on_delete_contact)
        button_box.pack_start(save_button, True, True, 0)
        button_box.pack_start(delete_button, True, True, 0)
        self.details_box.pack_start(button_box, False, False, 10)

    def apply_css(self):
        """Apply CSS styling."""
        css = b"""
        window { background-color: #f5f5f5; }
        listbox { background-color: #ffffff; border: 1px solid #ddd; }
        entry, textview { border: 1px solid #ccc; border-radius: 3px; }
        button { padding: 5px 10px; }
        """
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            self.get_screen(), style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def populate_contact_list(self):
        """Populate the contact list with contacts."""
        for child in self.contact_list.get_children():
            self.contact_list.remove(child)
        for contact in self.contacts:
            row = Gtk.ListBoxRow()
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            avatar = Gtk.Image.new_from_icon_name("avatar-default-symbolic", Gtk.IconSize.LARGE_TOOLBAR)
            name = Gtk.Label(label=contact.get("display_name", "Unnamed"))
            box.pack_start(avatar, False, False, 5)
            box.pack_start(name, True, True, 5)
            row.add(box)
            row.contact = contact
            self.contact_list.add(row)
        self.contact_list.show_all()

    def display_contact_details(self, contact):
        """Display the selected contact's details."""
        self.current_contact = contact
        self.fields["name"].set_text(contact.get("display_name", ""))
        self.fields["phone"].set_text(contact.get("primary_phone", ""))
        self.fields["email"].set_text(contact.get("primary_email", ""))
        addresses = contact.get("addresses", [])
        address = addresses[0]["value"] if addresses else ""
        self.fields["address"].set_text(address)
        self.fields["company"].set_text(contact.get("organization", ""))
        self.fields["notes"].get_buffer().set_text(contact.get("biography", ""))

    def clear_contact_details(self):
        """Clear the contact details view."""
        for field in self.fields.values():
            if isinstance(field, Gtk.Entry):
                field.set_text("")
            else:
                field.get_buffer().set_text("")
        self.photo_button.set_image(Gtk.Image.new_from_icon_name(
            "avatar-default-symbolic", Gtk.IconSize.DND))

    def on_contact_selected(self, listbox, row):
        """Handle contact selection."""
        self.display_contact_details(row.contact)

    def on_search_changed(self, entry):
        """Handle search input changes."""
        search_text = entry.get_text()
        if search_text and self.contacts_integration:
            self.contacts = self.contacts_integration.search_contacts(search_text)
        elif self.contacts_integration:
            self.contacts = self.contacts_integration.get_contacts()
        self.populate_contact_list()

    def on_new_contact(self, button):
        """Handle new contact creation."""
        self.current_contact = None
        self.clear_contact_details()

    def on_save_contact(self, button):
        """Save or update the current contact."""
        if not self.contacts_integration:
            return

        name = self.fields["name"].get_text()
        name_parts = name.split()
        given_name = name_parts[0] if name_parts else ""
        family_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        contact_data = {
            "given_name": given_name,
            "family_name": family_name,
            "email": self.fields["email"].get_text(),
            "phone": self.fields["phone"].get_text(),
            "address": self.fields["address"].get_text(),
            "organization": self.fields["company"].get_text(),
            "biography": self.fields["notes"].get_buffer().get_text(
                self.fields["notes"].get_buffer().get_start_iter(),
                self.fields["notes"].get_buffer().get_end_iter(),
                True
            )
        }

        if self.current_contact:
            # Update existing contact
            updated_contact = self.contacts_integration.update_contact(
                self.current_contact["resource_name"], contact_data
            )
            if updated_contact:
                for i, contact in enumerate(self.contacts):
                    if contact["resource_name"] == updated_contact["resource_name"]:
                        self.contacts[i] = updated_contact
                        break
                self.current_contact = updated_contact
        else:
            # Create new contact
            created_contact = self.contacts_integration.create_contact(contact_data)
            if created_contact:
                self.contacts.append(created_contact)
                self.current_contact = created_contact
        self.populate_contact_list()

    def on_delete_contact(self, button):
        """Delete the current contact."""
        if not self.current_contact or not self.contacts_integration:
            return
        if self.contacts_integration.delete_contact(self.current_contact["resource_name"]):
            self.contacts = [c for c in self.contacts if c["resource_name"] != self.current_contact["resource_name"]]
            self.current_contact = None
            self.populate_contact_list()
            self.clear_contact_details()

    def on_change_photo(self, button):
        """Change the contact's photo."""
        if not self.current_contact or not self.contacts_integration:
            return
        dialog = Gtk.FileChooserDialog(
            title="Select Photo",
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            photo_path = dialog.get_filename()
            self.contacts_integration.update_contact_photo(self.current_contact["resource_name"], photo_path)
        dialog.destroy()

if __name__ == "__main__":
    win = HextrixContacts()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()