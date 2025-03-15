#!/usr/bin/env python3
# Hextrix AI OS - Decentralized Email Client

import gi
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import json
import os
import threading

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Pango
from hextrix_data_handler import HextrixDataHandler

class HextrixEmail(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Hextrix Email with Gemini")
        self.set_default_size(1400, 900)
        
        # Initialize data
        self.accounts = self.load_accounts()
        self.current_account = None
        self.contacts = self.load_contacts()
        self.current_thread = None
        self.messages = []
        
        # Initialize Gemini
        self.gemini_initialized = False
        self.gemini_api_key = self.load_gemini_api_key()
        self.gemini_model = None
        
        # Setup UI
        self.setup_css()
        self.setup_main_layout()
        
        # Initialize Gemini if API key exists
        if self.gemini_api_key:
            threading.Thread(target=self.initialize_gemini).start()
        
        self.show_all()
        
    def setup_css(self):
        """Set up custom CSS styling"""
        css_provider = Gtk.CssProvider()
        css = """
            window {
                background-color: rgba(0, 5, 15, 0.92);
                background-image: radial-gradient(rgba(0, 191, 255, 0.15) 2px, transparent 2px),
                                 radial-gradient(rgba(0, 255, 255, 0.15) 2px, transparent 2px);
                background-size: 30px 30px;
                background-position: 0 0, 15px 15px;
            }
            
            .header {
                background-color: rgba(0, 10, 25, 0.85);
                border-bottom: 1px solid rgba(0, 210, 255, 0.6);
                padding: 10px;
                box-shadow: 0 0 20px rgba(0, 190, 255, 0.3);
                transition: all 250ms ease-in-out;
            }
            
            .sidebar {
                background-color: rgba(0, 12, 25, 0.85);
                border-right: 1px solid rgba(0, 210, 255, 0.6);
                padding: 10px;
                box-shadow: 0 5px 25px rgba(0, 150, 255, 0.3);
                transition: all 250ms ease-in-out;
            }
            
            .message-bubble {
                background-color: rgba(0, 25, 50, 0.75);
                border: 1px solid rgba(0, 210, 255, 0.4);
                border-radius: 15px;
                padding: 12px;
                margin: 12px;
                color: #B8E8FF;
                transition: all 0.2s ease;
                box-shadow: 0 0 15px rgba(0, 120, 255, 0.25);
            }
            
            .message-bubble:hover {
                background-color: rgba(0, 35, 70, 0.85);
                border-color: rgba(0, 255, 255, 0.7);
                box-shadow: 0 0 20px rgba(0, 190, 255, 0.4);
            }
            
            .message-bubble.sent {
                background-color: rgba(0, 60, 120, 0.7);
                border-radius: 15px 15px 15px 0;
                border: 1px solid rgba(0, 210, 255, 0.6);
                box-shadow: 0 0 15px rgba(0, 150, 255, 0.3);
            }
            
            .message-bubble.received {
                background-color: rgba(0, 35, 70, 0.7);
                border-radius: 15px 15px 0 15px;
                border: 1px solid rgba(0, 170, 255, 0.5);
                box-shadow: 0 0 12px rgba(0, 120, 255, 0.25);
            }
            
            .contact-list {
                background-color: rgba(0, 15, 30, 0.8);
                transition: all 250ms ease-in-out;
                border-radius: 10px;
                margin: 5px;
                box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.3);
            }
            
            .contact-list row {
                padding: 12px;
                border-bottom: 1px solid rgba(0, 130, 255, 0.25);
                color: #B8E8FF;
                transition: all 0.2s ease;
            }
            
            .contact-list row:hover {
                background-color: rgba(0, 100, 200, 0.25);
                box-shadow: inset 0 0 10px rgba(0, 150, 255, 0.15);
            }
            
            .contact-list row:selected {
                background-color: rgba(0, 120, 230, 0.35);
                box-shadow: inset 0 0 10px rgba(0, 210, 255, 0.3), 0 0 15px rgba(0, 150, 255, 0.3);
            }
            
            entry {
                background-color: rgba(0, 25, 60, 0.75);
                color: #B8E8FF;
                border: 1px solid rgba(0, 210, 255, 0.6);
                border-radius: 8px;
                padding: 10px;
                box-shadow: inset 0 0 8px rgba(0, 0, 20, 0.5), 0 0 5px rgba(0, 150, 255, 0.2);
                transition: all 0.25s ease;
            }
            
            entry:focus {
                border-color: rgba(0, 255, 255, 0.8);
                box-shadow: 0 0 15px rgba(0, 210, 255, 0.4), inset 0 0 8px rgba(0, 0, 20, 0.5);
            }
            
            textview {
                background-color: rgba(0, 25, 60, 0.75);
                color: #B8E8FF;
                border: 1px solid rgba(0, 210, 255, 0.6);
                border-radius: 8px;
                padding: 8px;
                box-shadow: inset 0 0 8px rgba(0, 0, 20, 0.5), 0 0 5px rgba(0, 150, 255, 0.2);
            }
            
            textview text {
                background-color: transparent;
                color: #B8E8FF;
            }
            
            button {
                background-color: rgba(0, 50, 100, 0.7);
                color: #E6F7FF;
                border: 1px solid rgba(0, 180, 255, 0.6);
                border-radius: 8px;
                padding: 10px 15px;
                transition: all 250ms ease-in-out;
                box-shadow: 0 0 10px rgba(0, 150, 255, 0.2);
            }
            
            button:hover {
                background-color: rgba(0, 80, 160, 0.8);
                border-color: rgba(0, 255, 255, 0.8);
                box-shadow: 0 0 15px rgba(0, 210, 255, 0.4);
            }
            
            button:active {
                background-color: rgba(0, 120, 220, 0.9);
                box-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
            }
            
            scrollbar {
                background-color: rgba(0, 15, 35, 0.5);
                border-radius: 10px;
                border: none;
            }

            scrollbar slider {
                background-color: rgba(0, 170, 255, 0.4);
                border-radius: 10px;
                min-width: 6px;
                min-height: 6px;
                transition: all 0.2s ease;
            }

            scrollbar slider:hover {
                background-color: rgba(0, 210, 255, 0.6);
                box-shadow: 0 0 10px rgba(0, 180, 255, 0.3);
            }

            scrollbar slider:active {
                background-color: rgba(0, 255, 255, 0.7);
                box-shadow: 0 0 15px rgba(0, 210, 255, 0.4);
            }
            
            .compose-area {
                background-color: rgba(0, 15, 35, 0.85);
                border-top: 1px solid rgba(0, 210, 255, 0.5);
                padding: 15px;
                box-shadow: 0 -5px 20px rgba(0, 50, 100, 0.4);
                border-radius: 0 0 10px 10px;
            }
            
            .send-button {
                background: linear-gradient(to bottom, rgba(0, 120, 230, 0.7), rgba(0, 80, 180, 0.7));
                border-radius: 8px;
                border: 1px solid rgba(0, 180, 255, 0.6);
                padding: 10px 20px;
                font-weight: bold;
                box-shadow: 0 0 15px rgba(0, 150, 255, 0.3);
                transition: all 0.25s ease;
                color: #E6F7FF;
            }
            
            .send-button:hover {
                background: linear-gradient(to bottom, rgba(0, 140, 255, 0.8), rgba(0, 100, 210, 0.8));
                box-shadow: 0 0 20px rgba(0, 210, 255, 0.4);
            }
            
            .send-button:active {
                background: linear-gradient(to bottom, rgba(0, 160, 255, 0.9), rgba(0, 120, 230, 0.9));
                box-shadow: 0 0 25px rgba(0, 255, 255, 0.5);
            }
            
            label {
                color: #B8E8FF;
                text-shadow: 0 0 5px rgba(0, 150, 255, 0.3);
            }
            
            /* Additional futuristic elements */
            .header, .sidebar, .compose-area {
                background-image: linear-gradient(to bottom, 
                                 rgba(0, 50, 100, 0.1) 0%, 
                                 rgba(0, 20, 40, 0.1) 50%, 
                                 rgba(0, 50, 100, 0.1) 100%);
            }
            
            .message-list {
                background-color: rgba(0, 10, 20, 0.7);
                background-image: linear-gradient(to bottom, 
                                 rgba(0, 40, 80, 0.05) 0%, 
                                 rgba(0, 10, 20, 0.05) 100%);
            }
            
            .gemini-button {
                background: linear-gradient(to right, rgba(0, 120, 230, 0.7), rgba(0, 180, 255, 0.7));
                border-radius: 8px;
                border: 1px solid rgba(0, 180, 255, 0.6);
                padding: 8px 15px;
                margin: 5px;
                box-shadow: 0 0 15px rgba(0, 150, 255, 0.3);
                transition: all 0.25s ease;
                color: #E6F7FF;
            }
            
            .gemini-button:hover {
                background: linear-gradient(to right, rgba(0, 140, 255, 0.8), rgba(0, 210, 255, 0.8));
                box-shadow: 0 0 20px rgba(0, 210, 255, 0.4);
            }
            
            .gemini-panel {
                background-color: rgba(0, 20, 45, 0.8);
                border: 1px solid rgba(0, 180, 255, 0.5);
                border-radius: 10px;
                padding: 15px;
                margin: 10px;
                box-shadow: 0 0 20px rgba(0, 120, 255, 0.3);
            }
            
            .gemini-suggestion {
                background-color: rgba(0, 40, 80, 0.7);
                border: 1px solid rgba(0, 180, 255, 0.4);
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
                color: #E6F7FF;
                transition: all 0.2s ease;
            }
            
            .gemini-suggestion:hover {
                background-color: rgba(0, 60, 120, 0.8);
                border-color: rgba(0, 210, 255, 0.6);
                box-shadow: 0 0 15px rgba(0, 150, 255, 0.3);
            }
        """
        css_provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
    def setup_main_layout(self):
        """Set up the main application layout"""
        # Main container
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(self.main_box)
        
        # Sidebar
        self.setup_sidebar()
        
        # Main content
        self.setup_content()
        
    def setup_sidebar(self):
        """Set up the sidebar with accounts and contacts"""
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sidebar_box.set_size_request(300, -1)
        sidebar_box.get_style_context().add_class("sidebar")
        
        # Accounts list
        self.accounts_list = Gtk.ListBox()
        self.accounts_list.get_style_context().add_class("contact-list")
        for account in self.accounts:
            row = Gtk.ListBoxRow()
            label = Gtk.Label(label=account['email'])
            row.add(label)
            self.accounts_list.add(row)
        self.accounts_list.connect("row-activated", self.on_account_selected)
        
        # Contacts list
        self.contacts_list = Gtk.ListBox()
        self.contacts_list.get_style_context().add_class("contact-list")
        for contact in self.contacts:
            row = Gtk.ListBoxRow()
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            avatar = Gtk.Label(label=contact['name'][0].upper())
            avatar.get_style_context().add_class("message-bubble")
            name = Gtk.Label(label=contact['name'])
            box.pack_start(avatar, False, False, 0)
            box.pack_start(name, True, True, 0)
            row.add(box)
            self.contacts_list.add(row)
        self.contacts_list.connect("row-activated", self.on_contact_selected)
        
        # Add to sidebar
        sidebar_box.pack_start(self.accounts_list, True, True, 0)
        sidebar_box.pack_start(self.contacts_list, True, True, 0)
        
        self.main_box.pack_start(sidebar_box, False, False, 0)
        
    def setup_content(self):
        """Set up the main content area"""
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # Message view
        self.setup_message_view()
        content_box.pack_start(self.message_box, True, True, 0)
        
        # Compose area
        self.setup_compose_area()
        content_box.pack_start(self.compose_box, False, False, 0)
        
        self.main_box.pack_start(content_box, True, True, 0)
        
    def setup_message_view(self):
        """Set up the message view"""
        self.message_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        self.message_scroll = Gtk.ScrolledWindow()
        self.message_list = Gtk.ListBox()
        self.message_list.set_selection_mode(Gtk.SelectionMode.NONE)
        
        self.message_scroll.add(self.message_list)
        self.message_box.pack_start(self.message_scroll, True, True, 0)
        
    def setup_compose_area(self):
        """Set up the compose area"""
        self.compose_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.compose_box.set_margin_top(10)
        self.compose_box.set_margin_bottom(10)
        self.compose_box.set_margin_start(10)
        self.compose_box.set_margin_end(10)
        self.compose_box.get_style_context().add_class("compose-area")
        
        # Subject
        subject_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        subject_label = Gtk.Label(label="Subject:")
        subject_label.set_markup("<span foreground='#B8E8FF'>Subject:</span>")
        self.subject_entry = Gtk.Entry()
        subject_box.pack_start(subject_label, False, False, 0)
        subject_box.pack_start(self.subject_entry, True, True, 0)
        
        # Message
        self.message_text = Gtk.TextView()
        self.message_text.set_wrap_mode(Gtk.WrapMode.WORD)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.message_text)
        scroll.set_size_request(-1, 150)
        
        # Gemini AI tools
        gemini_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        
        # Gemini status label
        self.gemini_status_label = Gtk.Label(label="Initializing Gemini AI...")
        gemini_box.pack_start(self.gemini_status_label, False, False, 0)
        
        # Gemini buttons
        self.smart_reply_button = Gtk.Button(label="Smart Reply")
        self.smart_reply_button.get_style_context().add_class("gemini-button")
        self.smart_reply_button.connect("clicked", self.on_smart_reply)
        gemini_box.pack_end(self.smart_reply_button, False, False, 0)
        
        self.email_draft_button = Gtk.Button(label="Draft Email")
        self.email_draft_button.get_style_context().add_class("gemini-button")
        self.email_draft_button.connect("clicked", self.on_email_draft)
        gemini_box.pack_end(self.email_draft_button, False, False, 0)
        
        self.proofread_button = Gtk.Button(label="Proofread")
        self.proofread_button.get_style_context().add_class("gemini-button")
        self.proofread_button.connect("clicked", self.on_proofread)
        gemini_box.pack_end(self.proofread_button, False, False, 0)
        
        # Gemini suggestions panel (hidden by default)
        self.gemini_suggestions_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.gemini_suggestions_box.get_style_context().add_class("gemini-panel")
        self.gemini_suggestions_box.set_no_show_all(True)
        self.gemini_suggestions_box.hide()
        
        # Send button
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        send_button = Gtk.Button(label="Send")
        send_button.get_style_context().add_class("send-button")
        send_button.connect("clicked", self.on_send_message)
        button_box.pack_end(send_button, False, False, 0)
        
        self.compose_box.pack_start(subject_box, False, False, 0)
        self.compose_box.pack_start(scroll, True, True, 0)
        self.compose_box.pack_start(gemini_box, False, False, 0)
        self.compose_box.pack_start(self.gemini_suggestions_box, False, False, 0)
        self.compose_box.pack_start(button_box, False, False, 0)
        
    def on_account_selected(self, listbox, row):
        """Handle account selection"""
        self.current_account = self.accounts[row.get_index()]
        self.load_messages()
        
    def on_contact_selected(self, listbox, row):
        """Handle contact selection"""
        contact = self.contacts[row.get_index()]
        self.current_thread = f"{self.current_account['email']}-{contact['email']}"
        self.load_thread_messages()
        
    def load_messages(self):
        """Load messages for the selected account"""
        if not self.current_account:
            return
            
        # Clear existing messages
        self.message_list.foreach(lambda widget: self.message_list.remove(widget))
        
        # Connect to IMAP server
        try:
            mail = imaplib.IMAP4_SSL(self.current_account['imap_server'])
            mail.login(self.current_account['email'], self.current_account['password'])
            mail.select('inbox')
            
            # Search for messages
            status, messages = mail.search(None, 'ALL')
            if status == 'OK':
                for num in messages[0].split():
                    status, data = mail.fetch(num, '(RFC822)')
                    if status == 'OK':
                        email_message = email.message_from_bytes(data[0][1])
                        self.add_message_to_view(email_message, 'received')
                        
            mail.logout()
        except Exception as e:
            print(f"Error loading messages: {e}")
            
    def load_thread_messages(self):
        """Load messages for the current thread"""
        if not self.current_thread:
            return
            
        # Clear existing messages
        self.message_list.foreach(lambda widget: self.message_list.remove(widget))
        
        # Load messages from thread
        thread_file = os.path.join(os.path.dirname(__file__), "threads", f"{self.current_thread}.json")
        if os.path.exists(thread_file):
            with open(thread_file, 'r') as f:
                messages = json.load(f)
                for message in messages:
                    self.add_message_to_view(message)
                    
    def add_message_to_view(self, message, direction=None):
        """Add a message to the view"""
        row = Gtk.ListBoxRow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.get_style_context().add_class("message-bubble")
        
        if direction:
            box.get_style_context().add_class(direction)
            
        # Sender and date
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        sender = Gtk.Label(label=message['from'])
        date = Gtk.Label(label=message['date'])
        header_box.pack_start(sender, True, True, 0)
        header_box.pack_start(date, False, False, 0)
        
        # Message content
        content = Gtk.Label(label=message['content'])
        content.set_line_wrap(True)
        content.set_xalign(0)
        
        box.pack_start(header_box, False, False, 0)
        box.pack_start(content, True, True, 0)
        row.add(box)
        self.message_list.add(row)
        self.message_list.show_all()
        
    def on_send_message(self, button):
        """Handle sending a message"""
        if not self.current_account or not self.current_thread:
            return
            
        # Get message content
        subject = self.subject_entry.get_text()
        buffer = self.message_text.get_buffer()
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()
        content = buffer.get_text(start_iter, end_iter, True)
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = self.current_account['email']
        msg['To'] = self.current_thread.split('-')[1]
        msg['Subject'] = subject
        msg.attach(MIMEText(content, 'plain'))
        
        # Send message
        try:
            server = smtplib.SMTP(self.current_account['smtp_server'], 587)
            server.starttls()
            server.login(self.current_account['email'], self.current_account['password'])
            server.send_message(msg)
            server.quit()
            
            # Save to thread
            self.save_message_to_thread({
                'from': self.current_account['email'],
                'to': self.current_thread.split('-')[1],
                'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'subject': subject,
                'content': content
            })
            
            # Clear compose area
            self.subject_entry.set_text("")
            buffer.set_text("")
            
            # Reload messages
            self.load_thread_messages()
        except Exception as e:
            print(f"Error sending message: {e}")
            
    def save_message_to_thread(self, message):
        """Save message to thread file"""
        thread_file = os.path.join(os.path.dirname(__file__), "threads", f"{self.current_thread}.json")
        messages = []
        
        if os.path.exists(thread_file):
            with open(thread_file, 'r') as f:
                messages = json.load(f)
                
        messages.append(message)
        
        with open(thread_file, 'w') as f:
            json.dump(messages, f)
            
    def load_accounts(self):
        """Load email accounts"""
        accounts_file = os.path.join(os.path.dirname(__file__), "accounts.json")
        if os.path.exists(accounts_file):
            with open(accounts_file, 'r') as f:
                return json.load(f)
        return []
        
    def load_contacts(self):
        """Load contacts"""
        contacts_file = os.path.join(os.path.dirname(__file__), "contacts.json")
        if os.path.exists(contacts_file):
            with open(contacts_file, 'r') as f:
                return json.load(f)
        return []
        
    def check_for_shared_data(self):
        """Check for shared data from other apps"""
        # Check for contact export
        contact_export = self.data_handler.load_data("email_contact_export.json")
        if contact_export:
            self.import_contact(contact_export)
            os.remove(os.path.join(self.data_handler.data_dir, "email_contact_export.json"))
            
        # Check for event invites
        event_invite = self.data_handler.load_data("email_event_invite.json")
        if event_invite:
            self.create_email_from_event(event_invite)
            os.remove(os.path.join(self.data_handler.data_dir, "email_event_invite.json"))
            
    def import_contact(self, contact_data):
        """Import contact from shared data"""
        if not any(c['email'] == contact_data['email'] for c in self.contacts):
            self.contacts.append(contact_data)
            self.data_handler.save_data("shared_contacts.json", self.contacts)
            self.update_contacts_list()
            
    def create_email_from_event(self, event_data):
        """Create email from event data"""
        self.current_thread = f"{self.current_account['email']}-{event_data['recipients'][0]}"
        self.subject_entry.set_text(event_data['subject'])
        buffer = self.message_text.get_buffer()
        buffer.set_text(event_data['body'])
        
    def load_gemini_api_key(self):
        """Load Gemini API key from config file"""
        config_file = os.path.join(os.path.dirname(__file__), "gemini_config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    return config.get("api_key", "")
            except Exception as e:
                print(f"Error loading Gemini API key: {e}")
        return ""
        
    def initialize_gemini(self):
        """Initialize Gemini AI model"""
        try:
            try:
                import google.generativeai as genai
                
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                self.gemini_initialized = True
                GLib.idle_add(self.update_gemini_ui)
                print("Gemini AI initialized successfully")
            except ImportError:
                print("Google Generative AI package not found. Gemini features will be disabled.")
                GLib.idle_add(self.update_gemini_ui_unavailable)
        except Exception as e:
            print(f"Error initializing Gemini: {e}")
            GLib.idle_add(self.update_gemini_ui_error, str(e))
            
    def update_gemini_ui(self):
        """Update UI to show Gemini features are available"""
        if hasattr(self, 'gemini_status_label'):
            self.gemini_status_label.set_text("Gemini AI Ready")
            
    def update_gemini_ui_unavailable(self):
        """Update UI to show Gemini features are unavailable"""
        if hasattr(self, 'gemini_status_label'):
            self.gemini_status_label.set_text("Gemini AI Unavailable - Package not installed")
            # Disable Gemini buttons
            if hasattr(self, 'smart_reply_button'):
                self.smart_reply_button.set_sensitive(False)
            if hasattr(self, 'email_draft_button'):
                self.email_draft_button.set_sensitive(False)
            if hasattr(self, 'proofread_button'):
                self.proofread_button.set_sensitive(False)
            
    def update_gemini_ui_error(self, error_message):
        """Update UI to show Gemini features had an error"""
        if hasattr(self, 'gemini_status_label'):
            self.gemini_status_label.set_text(f"Gemini AI Error: {error_message}")
            # Disable Gemini buttons
            if hasattr(self, 'smart_reply_button'):
                self.smart_reply_button.set_sensitive(False)
            if hasattr(self, 'email_draft_button'):
                self.email_draft_button.set_sensitive(False)
            if hasattr(self, 'proofread_button'):
                self.proofread_button.set_sensitive(False)
            
    def on_smart_reply(self, button):
        """Generate smart reply suggestions using Gemini"""
        if not self.gemini_initialized or not self.current_thread:
            return
            
        # Clear previous suggestions
        for child in self.gemini_suggestions_box.get_children():
            self.gemini_suggestions_box.remove(child)
            
        # Add a loading label
        loading_label = Gtk.Label(label="Generating smart replies...")
        self.gemini_suggestions_box.pack_start(loading_label, False, False, 0)
        self.gemini_suggestions_box.show_all()
        
        # Get context from the thread
        thread_context = self.get_thread_context()
        
        # Start thread to get suggestions from Gemini
        threading.Thread(target=self.get_smart_replies, args=(thread_context,)).start()
        
    def get_thread_context(self):
        """Get context from the current thread to send to Gemini"""
        context = ""
        thread_file = os.path.join(os.path.dirname(__file__), "threads", f"{self.current_thread}.json")
        if os.path.exists(thread_file):
            with open(thread_file, 'r') as f:
                messages = json.load(f)
                # Get the last 5 messages for context
                for message in messages[-5:]:
                    context += f"From: {message['from']}\n"
                    context += f"Subject: {message.get('subject', '')}\n"
                    context += f"{message['content']}\n\n"
        return context
        
    def get_smart_replies(self, context):
        """Get smart reply suggestions from Gemini AI"""
        try:
            # Generate suggestions
            response = self.gemini_model.generate_content(
                f"You are an email assistant helping to draft smart replies to this conversation. Generate 3 short, professional responses based on this email thread:\n\n{context}"
            )
            
            suggestions = response.text.split('\n\n')
            # Clean up the suggestions
            suggestions = [s.strip().replace('1. ', '').replace('2. ', '').replace('3. ', '') for s in suggestions if s.strip()]
            
            # Update UI
            GLib.idle_add(self.update_suggestions, suggestions)
        except Exception as e:
            print(f"Error generating smart replies: {e}")
            GLib.idle_add(self.update_error, f"Error generating suggestions: {str(e)}")
            
    def update_suggestions(self, suggestions):
        """Update UI with generated suggestions"""
        # Clear loading message
        for child in self.gemini_suggestions_box.get_children():
            self.gemini_suggestions_box.remove(child)
            
        # Add title
        title = Gtk.Label(label="Gemini AI Suggestions:")
        title.set_markup("<b>Gemini AI Suggestions:</b>")
        title.set_xalign(0)
        self.gemini_suggestions_box.pack_start(title, False, False, 0)
        
        # Add each suggestion as a clickable button
        for suggestion in suggestions:
            suggestion_button = Gtk.Button(label=suggestion)
            suggestion_button.get_style_context().add_class("gemini-suggestion")
            suggestion_button.connect("clicked", self.on_suggestion_clicked, suggestion)
            self.gemini_suggestions_box.pack_start(suggestion_button, False, False, 0)
            
        self.gemini_suggestions_box.show_all()
        
    def update_error(self, error_message):
        """Show error message in suggestions panel"""
        # Clear loading message
        for child in self.gemini_suggestions_box.get_children():
            self.gemini_suggestions_box.remove(child)
            
        error_label = Gtk.Label(label=error_message)
        self.gemini_suggestions_box.pack_start(error_label, False, False, 0)
        self.gemini_suggestions_box.show_all()
        
    def on_suggestion_clicked(self, button, suggestion):
        """Handle user clicking on a suggestion"""
        # Insert suggestion into the message text
        buffer = self.message_text.get_buffer()
        buffer.set_text(suggestion)
        
    def on_email_draft(self, button):
        """Generate a complete email draft using Gemini"""
        if not self.gemini_initialized or not self.current_thread:
            return
            
        # Get the subject
        subject = self.subject_entry.get_text()
        
        # Clear previous suggestions
        for child in self.gemini_suggestions_box.get_children():
            self.gemini_suggestions_box.remove(child)
            
        # Add a loading label
        loading_label = Gtk.Label(label="Drafting email...")
        self.gemini_suggestions_box.pack_start(loading_label, False, False, 0)
        self.gemini_suggestions_box.show_all()
        
        # Get thread context
        thread_context = self.get_thread_context()
        
        # Start thread to get draft from Gemini
        threading.Thread(target=self.get_email_draft, args=(thread_context, subject)).start()
        
    def get_email_draft(self, context, subject):
        """Get email draft from Gemini AI"""
        try:
            # Generate draft
            response = self.gemini_model.generate_content(
                f"You are an email assistant helping to draft an email. Create a professional email about this subject: {subject}\n\nPrevious conversation context:\n{context}"
            )
            
            draft = response.text.strip()
            
            # Update UI
            GLib.idle_add(self.update_email_draft, draft)
        except Exception as e:
            print(f"Error generating email draft: {e}")
            GLib.idle_add(self.update_error, f"Error generating email draft: {str(e)}")
            
    def update_email_draft(self, draft):
        """Update UI with generated email draft"""
        # Set the draft to the message text
        buffer = self.message_text.get_buffer()
        buffer.set_text(draft)
        
        # Clear suggestions box
        for child in self.gemini_suggestions_box.get_children():
            self.gemini_suggestions_box.remove(child)
            
        # Add confirmation
        confirm_label = Gtk.Label(label="Email draft generated! You can edit it before sending.")
        self.gemini_suggestions_box.pack_start(confirm_label, False, False, 0)
        self.gemini_suggestions_box.show_all()
        
    def on_proofread(self, button):
        """Proofread and improve the current email text using Gemini"""
        if not self.gemini_initialized:
            return
            
        # Get current message text
        buffer = self.message_text.get_buffer()
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()
        current_text = buffer.get_text(start_iter, end_iter, True)
        
        if not current_text.strip():
            return
            
        # Clear previous suggestions
        for child in self.gemini_suggestions_box.get_children():
            self.gemini_suggestions_box.remove(child)
            
        # Add a loading label
        loading_label = Gtk.Label(label="Proofreading email...")
        self.gemini_suggestions_box.pack_start(loading_label, False, False, 0)
        self.gemini_suggestions_box.show_all()
        
        # Start thread to get proofread version from Gemini
        threading.Thread(target=self.get_proofread_text, args=(current_text,)).start()
        
    def get_proofread_text(self, text):
        """Get proofread version of text from Gemini AI"""
        try:
            # Generate proofread version
            response = self.gemini_model.generate_content(
                f"Proofread and improve this email text while keeping the original meaning and tone:\n\n{text}"
            )
            
            improved_text = response.text.strip()
            
            # Update UI
            GLib.idle_add(self.update_proofread_text, improved_text)
        except Exception as e:
            print(f"Error proofreading text: {e}")
            GLib.idle_add(self.update_error, f"Error proofreading text: {str(e)}")
            
    def update_proofread_text(self, improved_text):
        """Update UI with proofread text"""
        # Clear suggestions box
        for child in self.gemini_suggestions_box.get_children():
            self.gemini_suggestions_box.remove(child)
            
        # Add title
        title = Gtk.Label(label="Improved Version:")
        title.set_markup("<b>Improved Version:</b>")
        title.set_xalign(0)
        self.gemini_suggestions_box.pack_start(title, False, False, 0)
        
        # Add the improved text with an apply button
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_size_request(-1, 100)
        
        improved_view = Gtk.TextView()
        improved_view.set_wrap_mode(Gtk.WrapMode.WORD)
        improved_view.set_editable(False)
        improved_buffer = improved_view.get_buffer()
        improved_buffer.set_text(improved_text)
        
        scroll.add(improved_view)
        self.gemini_suggestions_box.pack_start(scroll, True, True, 0)
        
        # Add apply button
        apply_button = Gtk.Button(label="Apply Changes")
        apply_button.get_style_context().add_class("gemini-button")
        apply_button.connect("clicked", self.on_apply_proofread, improved_text)
        
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button_box.pack_end(apply_button, False, False, 0)
        self.gemini_suggestions_box.pack_start(button_box, False, False, 0)
        
        self.gemini_suggestions_box.show_all()
        
    def on_apply_proofread(self, button, improved_text):
        """Apply the proofread text to the message"""
        buffer = self.message_text.get_buffer()
        buffer.set_text(improved_text)
        
        # Hide suggestions box after applying
        self.gemini_suggestions_box.hide()

if __name__ == "__main__":
    app = HextrixEmail()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()