#!/usr/bin/env python3
# Hextrix AI OS - Comprehensive Health Tracking with Apple Health Integration

import gi
import json
import os
import datetime
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
import numpy as np
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import zipfile
import xml.etree.ElementTree as ET
import shutil

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Pango

# Google Fit API scopes
SCOPES = [
    'https://www.googleapis.com/auth/fitness.activity.read',
    'https://www.googleapis.com/auth/fitness.body.read',
    'https://www.googleapis.com/auth/fitness.heart_rate.read',
    'https://www.googleapis.com/auth/fitness.sleep.read',
    'https://www.googleapis.com/auth/fitness.oxygen_saturation.read',
    'https://www.googleapis.com/auth/fitness.blood_glucose.read',
    'https://www.googleapis.com/auth/fitness.blood_pressure.read',
    'https://www.googleapis.com/auth/fitness.body_temperature.read',
    'https://www.googleapis.com/auth/fitness.nutrition.read'
]

### Google Fit Manager Class
class GoogleFitManager:
    def __init__(self):
        self.creds = None
        self.service = None
        self.authenticate()

    def authenticate(self):
        """Authenticate with Google Fit API"""
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())
        
        self.service = build('fitness', 'v1', credentials=self.creds)

    def get_user_profile(self):
        """Get user profile information"""
        try:
            return self.service.users().get(userId='me').execute()
        except HttpError as error:
            print(f'Error getting user profile: {error}')
            return None

    def get_activity_data(self, start_time, end_time):
        """Get activity data for a time range"""
        try:
            body = {
                "aggregateBy": [{"dataTypeName": "com.google.activity.summary"}],
                "bucketByTime": {"durationMillis": 86400000},  # 24 hours
                "startTimeMillis": start_time,
                "endTimeMillis": end_time
            }
            return self.service.users().dataset().aggregate(userId='me', body=body).execute()
        except HttpError as error:
            print(f'Error getting activity data: {error}')
            return None

    def get_heart_rate_data(self, start_time, end_time):
        """Get heart rate data for a time range"""
        try:
            body = {
                "aggregateBy": [{"dataTypeName": "com.google.heart_rate.bpm"}],
                "bucketByTime": {"durationMillis": 3600000},  # 1 hour
                "startTimeMillis": start_time,
                "endTimeMillis": end_time
            }
            return self.service.users().dataset().aggregate(userId='me', body=body).execute()
        except HttpError as error:
            print(f'Error getting heart rate data: {error}')
            return None

    def get_sleep_data(self, start_time, end_time):
        """Get sleep data for a time range"""
        try:
            body = {
                "aggregateBy": [{"dataTypeName": "com.google.sleep.segment"}],
                "bucketByTime": {"durationMillis": 86400000},  # 24 hours
                "startTimeMillis": start_time,
                "endTimeMillis": end_time
            }
            return self.service.users().dataset().aggregate(userId='me', body=body).execute()
        except HttpError as error:
            print(f'Error getting sleep data: {error}')
            return None

    def get_steps_data(self, start_time, end_time):
        """Get steps data for a time range"""
        try:
            body = {
                "aggregateBy": [{"dataTypeName": "com.google.step_count.delta"}],
                "bucketByTime": {"durationMillis": 86400000},  # 24 hours
                "startTimeMillis": start_time,
                "endTimeMillis": end_time
            }
            return self.service.users().dataset().aggregate(userId='me', body=body).execute()
        except HttpError as error:
            print(f'Error getting steps data: {error}')
            return None

    def get_oxygen_saturation_data(self, start_time, end_time):
        """Get oxygen saturation data for a time range"""
        try:
            body = {
                "aggregateBy": [{"dataTypeName": "com.google.oxygen_saturation"}],
                "bucketByTime": {"durationMillis": 3600000},  # 1 hour
                "startTimeMillis": start_time,
                "endTimeMillis": end_time
            }
            return self.service.users().dataset().aggregate(userId='me', body=body).execute()
        except HttpError as error:
            print(f'Error getting oxygen saturation data: {error}')
            return None

    def get_blood_glucose_data(self, start_time, end_time):
        """Get blood glucose data for a time range"""
        try:
            body = {
                "aggregateBy": [{"dataTypeName": "com.google.blood_glucose.level"}],
                "bucketByTime": {"durationMillis": 86400000},  # 24 hours
                "startTimeMillis": start_time,
                "endTimeMillis": end_time
            }
            return self.service.users().dataset().aggregate(userId='me', body=body).execute()
        except HttpError as error:
            print(f'Error getting blood glucose data: {error}')
            return None

    def get_blood_pressure_data(self, start_time, end_time):
        """Get blood pressure data for a time range"""
        try:
            body = {
                "aggregateBy": [{"dataTypeName": "com.google.blood_pressure"}],
                "bucketByTime": {"durationMillis": 86400000},  # 24 hours
                "startTimeMillis": start_time,
                "endTimeMillis": end_time
            }
            return self.service.users().dataset().aggregate(userId='me', body=body).execute()
        except HttpError as error:
            print(f'Error getting blood pressure data: {error}')
            return None

    def get_body_temperature_data(self, start_time, end_time):
        """Get body temperature data for a time range"""
        try:
            body = {
                "aggregateBy": [{"dataTypeName": "com.google.body.temperature"}],
                "bucketByTime": {"durationMillis": 3600000},  # 1 hour
                "startTimeMillis": start_time,
                "endTimeMillis": end_time
            }
            return self.service.users().dataset().aggregate(userId='me', body=body).execute()
        except HttpError as error:
            print(f'Error getting body temperature data: {error}')
            return None

    def get_nutrition_data(self, start_time, end_time):
        """Get nutrition data for a time range"""
        try:
            body = {
                "aggregateBy": [{"dataTypeName": "com.google.nutrition"}],
                "bucketByTime": {"durationMillis": 86400000},  # 24 hours
                "startTimeMillis": start_time,
                "endTimeMillis": end_time
            }
            return self.service.users().dataset().aggregate(userId='me', body=body).execute()
        except HttpError as error:
            print(f'Error getting nutrition data: {error}')
            return None

### Data Handler Class with Apple Health Import
class HextrixDataHandler:
    def __init__(self):
        self.data_dir = os.path.expanduser("~/.hextrix")
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)

    def load_data(self, filename):
        """Load data from a JSON file."""
        path = os.path.join(self.data_dir, filename)
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        return None

    def save_data(self, filename, data):
        """Save data to a JSON file."""
        path = os.path.join(self.data_dir, filename)
        with open(path, 'w') as f:
            json.dump(data, f)

    def import_apple_health_data(self, zip_path):
        """Import Apple Health data from an exported ZIP file."""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                if 'apple_health_export/export.xml' not in zip_ref.namelist():
                    raise Exception("Invalid Apple Health export ZIP: missing export.xml")
                zip_ref.extract('apple_health_export/export.xml', self.data_dir)
            xml_path = os.path.join(self.data_dir, 'apple_health_export/export.xml')
            tree = ET.parse(xml_path)
            root = tree.getroot()
            data = {}
            for record in root.findall('Record'):
                record_type = record.get('type')
                start_date = record.get('startDate')
                end_date = record.get('endDate')
                value = record.get('value')
                if record_type not in data:
                    data[record_type] = []
                data[record_type].append({
                    'start_date': start_date,
                    'end_date': end_date,
                    'value': value
                })
            import_data = {
                'last_imported': datetime.datetime.now().isoformat(),
                'data': data
            }
            self.save_data('apple_health_data.json', import_data)
            shutil.rmtree(os.path.join(self.data_dir, 'apple_health_export'))
        except Exception as e:
            raise Exception(f"Failed to import Apple Health data: {e}")

### Main Application Class
class HextrixHealth(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Hextrix Health")
        self.set_default_size(1400, 900)

        # Initialize data
        self.data_handler = HextrixDataHandler()
        self.health_data = self.load_health_data()
        self.current_view = "dashboard"
        self.settings = self.load_settings()

        # Initialize Google Fit
        try:
            self.fit_manager = GoogleFitManager()
            self.fit_enabled = True
        except Exception as e:
            print(f"Failed to initialize Google Fit: {e}")
            self.fit_enabled = False

        # Setup UI
        self.setup_css()
        self.setup_main_layout()
        self.show_all()

    def load_health_data(self):
        """Load health data from 'health_data.json'."""
        return self.data_handler.load_data('health_data.json') or {}

    def save_health_data(self):
        """Save health data to 'health_data.json'."""
        self.data_handler.save_data('health_data.json', self.health_data)

    def load_settings(self):
        """Load settings from 'settings.json'."""
        return self.data_handler.load_data('settings.json') or {}

    def save_settings(self):
        """Save settings to 'settings.json'."""
        self.data_handler.save_data('settings.json', self.settings)

    def setup_css(self):
        """Set up custom CSS styling."""
        css_provider = Gtk.CssProvider()
        css = """
            window { background-color: rgba(0, 10, 20, 0.95); }
            .header { background-color: rgba(0, 15, 30, 0.9); border-bottom: 1px solid rgba(0, 191, 255, 0.5); padding: 10px; }
            .sidebar { background-color: rgba(0, 15, 30, 0.9); border-right: 1px solid rgba(0, 191, 255, 0.5); padding: 10px; }
            .health-card { background-color: rgba(0, 20, 40, 0.8); border: 1px solid rgba(0, 191, 255, 0.3); border-radius: 15px; padding: 15px; margin: 10px; color: #00BFFF; }
            .health-card:hover { background-color: rgba(0, 100, 200, 0.5); }
            .tracker-list { background-color: rgba(0, 10, 20, 0.85); }
            .tracker-list row { padding: 8px; border-bottom: 1px solid rgba(0, 100, 200, 0.2); color: #00BFFF; }
            .tracker-list row:selected { background-color: rgba(0, 100, 200, 0.3); }
            .stats-container { background-color: rgba(0, 15, 30, 0.8); border: 1px solid rgba(0, 191, 255, 0.3); border-radius: 10px; padding: 10px; margin: 10px; }
            .settings-section { background-color: rgba(0, 20, 40, 0.8); border: 1px solid rgba(0, 191, 255, 0.3); border-radius: 10px; padding: 15px; margin: 10px; }
            .settings-label { color: #00BFFF; font-size: 14px; margin-bottom: 5px; }
            .settings-switch { margin: 5px; }
            .settings-entry { background-color: rgba(0, 30, 60, 0.7); color: #00BFFF; border: 1px solid rgba(0, 191, 255, 0.5); border-radius: 5px; padding: 5px; }
            .chart-label { color: #00BFFF; font-size: 16px; font-weight: bold; margin: 10px; }
            button { background-color: rgba(0, 40, 80, 0.7); color: #00BFFF; border: 1px solid rgba(0, 150, 255, 0.5); border-radius: 5px; padding: 8px 15px; transition: all 0.2s ease; }
            button:hover { background-color: rgba(0, 70, 130, 0.8); border-color: rgba(0, 200, 255, 0.8); }
            combobox { background-color: rgba(0, 30, 60, 0.7); color: #00BFFF; border: 1px solid rgba(0, 191, 255, 0.5); border-radius: 5px; padding: 5px; }
            entry { background-color: rgba(0, 30, 60, 0.7); color: #00BFFF; border: 1px solid rgba(0, 191, 255, 0.5); border-radius: 5px; padding: 8px; }
        """
        css_provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def setup_main_layout(self):
        """Set up the main application layout."""
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(self.main_box)
        self.setup_sidebar()
        self.setup_content()

    def setup_sidebar(self):
        """Set up the sidebar with navigation."""
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sidebar_box.set_size_request(300, -1)
        sidebar_box.get_style_context().add_class("sidebar")

        nav_items = [
            ("Dashboard", "dashboard"),
            ("Period Tracker", "period"),
            ("Sexual Health", "sexual"),
            ("Masturbation Log", "masturbation"),
            ("Horny Tracker", "horny"),
            ("Mood Tracker", "mood"),
            ("Talk to Nora", "nora"),
            ("Google Fit", "google_fit"),
            ("Apple Health", "apple_health"),  # Added Apple Health
            ("Statistics", "stats"),
            ("Settings", "settings")
        ]

        for label, view in nav_items:
            button = Gtk.Button(label=label)
            button.connect("clicked", self.on_nav_clicked, view)
            sidebar_box.pack_start(button, False, False, 5)

        self.main_box.pack_start(sidebar_box, False, False, 0)

    def setup_content(self):
        """Set up the main content area."""
        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.main_box.pack_start(self.content_box, True, True, 0)
        self.setup_dashboard()

    def setup_dashboard(self):
        """Set up the dashboard view."""
        for child in self.content_box.get_children():
            self.content_box.remove(child)

        period_status = self.health_data.get('period', {}).get('current_status', 'N/A')
        sexual_count = len(self.health_data.get('sexual_activity', []))
        masturbation_count = len(self.health_data.get('masturbation', []))

        cards = [
            ("Period Cycle", period_status),
            ("Sexual Activity", f"{sexual_count} records"),
            ("Masturbation", f"{masturbation_count} records"),
            ("Health Stats", "View Insights")
        ]

        for title, value in cards:
            card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            card.get_style_context().add_class("health-card")
            title_label = Gtk.Label()
            title_label.set_markup(f"<big>{title}</big>")
            value_label = Gtk.Label()
            value_label.set_markup(f"<span color='#00FFFF'>{value}</span>")
            card.pack_start(title_label, False, False, 0)
            card.pack_start(value_label, False, False, 0)
            self.content_box.pack_start(card, False, False, 10)

        self.content_box.show_all()

    def setup_period_tracker(self):
        """Set up period tracking view."""
        for child in self.content_box.get_children():
            self.content_box.remove(child)

        form_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        form_box.set_margin_top(20)
        form_box.set_margin_bottom(20)
        form_box.set_margin_start(20)
        form_box.set_margin_end(20)

        title_label = Gtk.Label()
        title_label.set_markup("<span font='16' weight='bold' color='#00BFFF'>Period Tracking</span>")
        form_box.pack_start(title_label, False, False, 10)

        start_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        start_label = Gtk.Label()
        start_label.set_markup("<span color='#00BFFF'>Cycle Start:</span>")
        start_label.set_size_request(120, -1)
        start_label.set_xalign(0)
        self.cycle_start = Gtk.Entry()
        self.cycle_start.set_placeholder_text("YYYY-MM-DD")
        start_box.pack_start(start_label, False, False, 0)
        start_box.pack_start(self.cycle_start, True, True, 0)

        symptoms_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        symptoms_label = Gtk.Label()
        symptoms_label.set_markup("<span color='#00BFFF'>Symptoms:</span>")
        symptoms_label.set_xalign(0)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_min_content_height(200)
        self.symptoms_entry = Gtk.TextView()
        self.symptoms_entry.set_wrap_mode(Gtk.WrapMode.WORD)
        scrolled_window.add(self.symptoms_entry)
        symptoms_box.pack_start(symptoms_label, False, False, 0)
        symptoms_box.pack_start(scrolled_window, True, True, 0)

        save_button = Gtk.Button(label="Save")
        save_button.connect("clicked", self.on_save_period)
        save_button.set_margin_top(15)

        form_box.pack_start(start_box, False, False, 0)
        form_box.pack_start(symptoms_box, True, True, 0)
        form_box.pack_start(save_button, False, False, 0)

        self.content_box.pack_start(form_box, True, True, 0)
        self.content_box.show_all()

    def on_save_period(self, button):
        """Save period tracking data."""
        period_data = {
            'date': self.cycle_start.get_text(),
            'symptoms': self.symptoms_entry.get_buffer().get_text(
                self.symptoms_entry.get_buffer().get_start_iter(),
                self.symptoms_entry.get_buffer().get_end_iter(),
                True
            )
        }
        if 'period' not in self.health_data:
            self.health_data['period'] = {}
        self.health_data['period']['current_status'] = "Active"
        self.health_data['period']['history'] = self.health_data['period'].get('history', [])
        self.health_data['period']['history'].append(period_data)
        self.save_health_data()
        self.setup_dashboard()

    def setup_sexual_health(self):
        """Set up sexual health tracking"""
        # Clear existing content
        for child in self.content_box.get_children():
            self.content_box.remove(child)
            
        # Sexual activity form
        form_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        form_box.set_margin_top(20)
        form_box.set_margin_bottom(20)
        form_box.set_margin_start(20)
        form_box.set_margin_end(20)
        
        # Form title
        title_label = Gtk.Label()
        title_label.set_markup("<span font='16' weight='bold' color='#00BFFF'>Sexual Health Tracker</span>")
        form_box.pack_start(title_label, False, False, 10)
        
        # Date
        date_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        date_label = Gtk.Label()
        date_label.set_markup("<span color='#00BFFF'>Date:</span>")
        date_label.set_size_request(120, -1)
        date_label.set_xalign(0)
        self.sex_date = Gtk.Entry()
        self.sex_date.set_placeholder_text("YYYY-MM-DD")
        self.sex_date.set_text(datetime.date.today().isoformat())
        date_box.pack_start(date_label, False, False, 0)
        date_box.pack_start(self.sex_date, True, True, 0)
        
        # Partner
        partner_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        partner_label = Gtk.Label()
        partner_label.set_markup("<span color='#00BFFF'>Partner:</span>")
        partner_label.set_size_request(120, -1)
        partner_label.set_xalign(0)
        self.partner_entry = Gtk.Entry()
        self.partner_entry.set_placeholder_text("Partner name")
        partner_box.pack_start(partner_label, False, False, 0)
        partner_box.pack_start(self.partner_entry, True, True, 0)
        
        # Partner Photos
        partner_photos_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        partner_photos_label = Gtk.Label()
        partner_photos_label.set_markup("<span color='#00BFFF'>Partner Photos:</span>")
        partner_photos_label.set_xalign(0)
        self.partner_photos_list = Gtk.ListBox()
        self.partner_photos_list.get_style_context().add_class("tracker-list")
        add_photo_button = Gtk.Button(label="Add Partner Photo")
        add_photo_button.connect("clicked", self.on_add_partner_photo)
        partner_photos_box.pack_start(partner_photos_label, False, False, 0)
        partner_photos_box.pack_start(self.partner_photos_list, True, True, 0)
        partner_photos_box.pack_start(add_photo_button, False, False, 5)
        
        # Protection
        protection_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        protection_label = Gtk.Label()
        protection_label.set_markup("<span color='#00BFFF'>Protection:</span>")
        protection_label.set_size_request(120, -1)
        protection_label.set_xalign(0)
        self.protection_combo = Gtk.ComboBoxText()
        self.protection_combo.append_text("Yes")
        self.protection_combo.append_text("No")
        self.protection_combo.set_active(0)
        protection_box.pack_start(protection_label, False, False, 0)
        protection_box.pack_start(self.protection_combo, True, True, 0)
        
        # Session Intensity
        intensity_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        intensity_label = Gtk.Label()
        intensity_label.set_markup("<span color='#00BFFF'>Session Intensity (1-10):</span>")
        intensity_label.set_xalign(0)
        self.session_intensity = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL,
            adjustment=Gtk.Adjustment(value=5, lower=1, upper=10, step_increment=1, page_increment=1, page_size=0)
        )
        self.session_intensity.set_digits(0)
        self.session_intensity.set_value_pos(Gtk.PositionType.RIGHT)
        intensity_box.pack_start(intensity_label, False, False, 0)
        intensity_box.pack_start(self.session_intensity, True, True, 0)
        
        # Satisfaction Rating
        satisfaction_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        satisfaction_label = Gtk.Label()
        satisfaction_label.set_markup("<span color='#00BFFF'>Satisfaction Rating (1-10):</span>")
        satisfaction_label.set_xalign(0)
        self.satisfaction_scale = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL,
            adjustment=Gtk.Adjustment(value=5, lower=1, upper=10, step_increment=1, page_increment=1, page_size=0)
        )
        self.satisfaction_scale.set_digits(0)
        self.satisfaction_scale.set_value_pos(Gtk.PositionType.RIGHT)
        satisfaction_box.pack_start(satisfaction_label, False, False, 0)
        satisfaction_box.pack_start(self.satisfaction_scale, True, True, 0)
        
        # Foreplay Duration
        foreplay_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        foreplay_label = Gtk.Label()
        foreplay_label.set_markup("<span color='#00BFFF'>Foreplay Duration (mins):</span>")
        foreplay_label.set_size_request(120, -1)
        foreplay_label.set_xalign(0)
        self.foreplay_duration = Gtk.Entry()
        self.foreplay_duration.set_placeholder_text("Duration in minutes")
        foreplay_box.pack_start(foreplay_label, False, False, 0)
        foreplay_box.pack_start(self.foreplay_duration, True, True, 0)
        
        # Post-Session Feelings
        feelings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        feelings_label = Gtk.Label()
        feelings_label.set_markup("<span color='#00BFFF'>Post-Session Feelings:</span>")
        feelings_label.set_xalign(0)
        feelings_scroll = Gtk.ScrolledWindow()
        feelings_scroll.set_min_content_height(100)
        self.post_session_feelings = Gtk.TextView()
        self.post_session_feelings.set_wrap_mode(Gtk.WrapMode.WORD)
        feelings_scroll.add(self.post_session_feelings)
        feelings_box.pack_start(feelings_label, False, False, 0)
        feelings_box.pack_start(feelings_scroll, True, True, 0)
        
        # Positions
        positions_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        positions_label = Gtk.Label()
        positions_label.set_markup("<span color='#00BFFF'>Positions:</span>")
        positions_label.set_xalign(0)
        self.positions_list = Gtk.FlowBox()
        self.positions_list.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
        self.positions_list.set_max_children_per_line(3)
        positions = ["Missionary", "Doggy Style", "Cowgirl", "Reverse Cowgirl", "Spooning", "69", "Oral", "Anal", "Other"]
        for position in positions:
            position_button = Gtk.ToggleButton(label=position)
            self.positions_list.add(position_button)
        positions_box.pack_start(positions_label, False, False, 0)
        positions_box.pack_start(self.positions_list, True, True, 0)
        
        # Session Photos
        session_photos_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        session_photos_label = Gtk.Label()
        session_photos_label.set_markup("<span color='#00BFFF'>Session Photos:</span>")
        session_photos_label.set_xalign(0)
        self.session_photos_list = Gtk.ListBox()
        self.session_photos_list.get_style_context().add_class("tracker-list")
        add_session_photo_button = Gtk.Button(label="Add Session Photo")
        add_session_photo_button.connect("clicked", self.on_add_session_photo)
        session_photos_box.pack_start(session_photos_label, False, False, 0)
        session_photos_box.pack_start(self.session_photos_list, True, True, 0)
        session_photos_box.pack_start(add_session_photo_button, False, False, 5)
        
        # Notes
        notes_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        notes_label = Gtk.Label()
        notes_label.set_markup("<span color='#00BFFF'>Notes:</span>")
        notes_label.set_xalign(0)
        notes_scroll = Gtk.ScrolledWindow()
        notes_scroll.set_min_content_height(100)
        self.sex_notes = Gtk.TextView()
        self.sex_notes.set_wrap_mode(Gtk.WrapMode.WORD)
        notes_scroll.add(self.sex_notes)
        notes_box.pack_start(notes_label, False, False, 0)
        notes_box.pack_start(notes_scroll, True, True, 0)
        
        # Save button
        save_button = Gtk.Button(label="Save")
        save_button.connect("clicked", self.on_save_sexual_activity)
        
        # Add everything to form
        form_box.pack_start(date_box, False, False, 0)
        form_box.pack_start(partner_box, False, False, 0)
        form_box.pack_start(partner_photos_box, False, False, 0)
        form_box.pack_start(protection_box, False, False, 0)
        form_box.pack_start(intensity_box, False, False, 0)
        form_box.pack_start(satisfaction_box, False, False, 0)
        form_box.pack_start(foreplay_box, False, False, 0)
        form_box.pack_start(positions_box, False, False, 0)
        form_box.pack_start(session_photos_box, False, False, 0)
        form_box.pack_start(notes_box, True, True, 0)
        form_box.pack_start(feelings_box, True, True, 0)
        form_box.pack_start(save_button, False, False, 0)
        
        # Recent records
        records_label = Gtk.Label()
        records_label.set_markup("<span font='14' weight='bold' color='#00BFFF'>Recent Records</span>")
        records_label.set_margin_top(20)
        form_box.pack_start(records_label, False, False, 10)
        
        # Records list
        records_scroll = Gtk.ScrolledWindow()
        records_scroll.set_min_content_height(200)
        self.records_list = Gtk.ListBox()
        self.records_list.get_style_context().add_class("tracker-list")
        
        # Populate records
        sexual_records = self.health_data.get('sexual_activity', [])
        for record in reversed(sexual_records[:10]):  # Show last 10 records
            record_row = Gtk.ListBoxRow()
            record_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            date_label = Gtk.Label()
            date_label.set_markup(f"<span color='#00FFFF'>{record.get('date', 'Unknown')}</span>")
            date_label.set_size_request(120, -1)
            partner_label = Gtk.Label(label=record.get('partner', 'Unknown'))
            protection_label = Gtk.Label()
            protection_label.set_markup(f"<span color='{'#00FF00' if record.get('protection') == 'Yes' else '#FF6666'}'>{record.get('protection', 'Unknown')}</span>")
            positions_label = Gtk.Label()
            positions_text = ", ".join(record.get('positions', []))
            positions_label.set_text(positions_text)
            positions_label.set_ellipsize(Pango.EllipsizeMode.END)
            record_box.pack_start(date_label, False, False, 0)
            record_box.pack_start(partner_label, True, True, 0)
            record_box.pack_start(protection_label, False, False, 0)
            record_box.pack_start(positions_label, True, True, 0)
            record_row.add(record_box)
            self.records_list.add(record_row)
        
        records_scroll.add(self.records_list)
        form_box.pack_start(records_scroll, True, True, 0)
        
        # Add scrollbar by wrapping form_box in a ScrolledWindow
        form_scroll = Gtk.ScrolledWindow()
        form_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        form_scroll.add(form_box)
        self.content_box.pack_start(form_scroll, True, True, 0)
        
        self.content_box.show_all()

    def on_add_partner_photo(self, button):
        """Handle adding partner photo"""
        dialog = Gtk.FileChooserDialog(
            title="Add Partner Photo",
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )
        
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        
        # Add filters for image files
        filter_images = Gtk.FileFilter()
        filter_images.set_name("Image files")
        filter_images.add_mime_type("image/*")
        dialog.add_filter(filter_images)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            try:
                # Create a copy in the app's data directory
                data_dir = os.path.expanduser("~/.hextrix/partner_photos")
                os.makedirs(data_dir, exist_ok=True)
                
                # Generate unique filename
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                new_filename = f"partner_{timestamp}_{os.path.basename(filename)}"
                new_path = os.path.join(data_dir, new_filename)
                
                # Copy the file
                import shutil
                shutil.copy2(filename, new_path)
                
                # Add to list
                row = Gtk.ListBoxRow()
                row.add(Gtk.Label(label=new_filename))
                self.partner_photos_list.add(row)
                
            except Exception as e:
                error_dialog = Gtk.MessageDialog(
                    transient_for=self,
                    flags=0,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text="Error Adding Photo"
                )
                error_dialog.format_secondary_text(str(e))
                error_dialog.run()
                error_dialog.destroy()
                
        dialog.destroy()

    def on_add_session_photo(self, button):
        """Handle adding session photo"""
        dialog = Gtk.FileChooserDialog(
            title="Add Session Photo",
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )
        
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        
        # Add filters for image files
        filter_images = Gtk.FileFilter()
        filter_images.set_name("Image files")
        filter_images.add_mime_type("image/*")
        dialog.add_filter(filter_images)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            try:
                # Create a copy in the app's data directory
                data_dir = os.path.expanduser("~/.hextrix/session_photos")
                os.makedirs(data_dir, exist_ok=True)
                
                # Generate unique filename
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                new_filename = f"session_{timestamp}_{os.path.basename(filename)}"
                new_path = os.path.join(data_dir, new_filename)
                
                # Copy the file
                import shutil
                shutil.copy2(filename, new_path)
                
                # Add to list
                row = Gtk.ListBoxRow()
                row.add(Gtk.Label(label=new_filename))
                self.session_photos_list.add(row)
                
            except Exception as e:
                error_dialog = Gtk.MessageDialog(
                    transient_for=self,
                    flags=0,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text="Error Adding Photo"
                )
                error_dialog.format_secondary_text(str(e))
                error_dialog.run()
                error_dialog.destroy()
                
        dialog.destroy()

    def on_save_sexual_activity(self, button):
        """Save sexual activity data"""
        # Get selected positions
        positions = []
        for row in self.positions_list.get_selected_rows():
            positions.append(row.get_child().get_text())
        
        # Get notes
        notes_buffer = self.sex_notes.get_buffer()
        notes_text = notes_buffer.get_text(
            notes_buffer.get_start_iter(),
            notes_buffer.get_end_iter(),
            True
        )
        
        # Get post-session feelings
        feelings_buffer = self.post_session_feelings.get_buffer()
        feelings_text = feelings_buffer.get_text(
            feelings_buffer.get_start_iter(),
            feelings_buffer.get_end_iter(),
            True
        )
        
        # Get partner photos
        partner_photos = []
        for row in self.partner_photos_list.get_children():
            partner_photos.append(row.get_child().get_text())
        
        # Get session photos
        session_photos = []
        for row in self.session_photos_list.get_children():
            session_photos.append(row.get_child().get_text())
        
        activity = {
            'date': self.sex_date.get_text(),
            'partner': self.partner_entry.get_text(),
            'protection': self.protection_combo.get_active_text(),
            'positions': positions,
            'partner_photos': partner_photos,
            'session_photos': session_photos,
            'notes': notes_text,
            'intensity': int(self.session_intensity.get_value()),
            'satisfaction': int(self.satisfaction_scale.get_value()),
            'foreplay_duration': self.foreplay_duration.get_text(),
            'post_session_feelings': feelings_text
        }
        
        self.health_data['sexual_activity'] = self.health_data.get('sexual_activity', [])
        self.health_data['sexual_activity'].append(activity)
        
        self.save_health_data()
        self.setup_dashboard()
    def setup_masturbation_tracker(self):
        """Set up masturbation tracking."""
        for child in self.content_box.get_children():
            self.content_box.remove(child)

        form_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        form_box.set_margin_top(20)
        form_box.set_margin_bottom(20)
        form_box.set_margin_start(20)
        form_box.set_margin_end(20)

        title_label = Gtk.Label()
        title_label.set_markup("<span font='16' weight='bold' color='#00BFFF'>Masturbation Log</span>")
        form_box.pack_start(title_label, False, False, 10)

        date_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        date_label = Gtk.Label()
        date_label.set_markup("<span color='#00BFFF'>Date:</span>")
        date_label.set_size_request(120, -1)
        date_label.set_xalign(0)
        self.masturbation_date = Gtk.Entry()
        self.masturbation_date.set_placeholder_text("YYYY-MM-DD")
        self.masturbation_date.set_text(datetime.date.today().isoformat())
        date_box.pack_start(date_label, False, False, 0)
        date_box.pack_start(self.masturbation_date, True, True, 0)

        duration_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        duration_label = Gtk.Label()
        duration_label.set_markup("<span color='#00BFFF'>Duration (mins):</span>")
        duration_label.set_size_request(120, -1)
        duration_label.set_xalign(0)
        self.duration_entry = Gtk.Entry()
        self.duration_entry.set_placeholder_text("Duration in minutes")
        duration_box.pack_start(duration_label, False, False, 0)
        duration_box.pack_start(self.duration_entry, True, True, 0)

        notes_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        notes_label = Gtk.Label()
        notes_label.set_markup("<span color='#00BFFF'>Notes:</span>")
        notes_label.set_xalign(0)
        notes_scroll = Gtk.ScrolledWindow()
        notes_scroll.set_min_content_height(100)
        self.notes_entry = Gtk.TextView()
        self.notes_entry.set_wrap_mode(Gtk.WrapMode.WORD)
        notes_scroll.add(self.notes_entry)
        notes_box.pack_start(notes_label, False, False, 0)
        notes_box.pack_start(notes_scroll, True, True, 0)

        save_button = Gtk.Button(label="Save")
        save_button.connect("clicked", self.on_save_masturbation)
        save_button.set_margin_top(15)

        form_box.pack_start(date_box, False, False, 0)
        form_box.pack_start(duration_box, False, False, 0)
        form_box.pack_start(notes_box, True, True, 0)
        form_box.pack_start(save_button, False, False, 0)

        records_label = Gtk.Label()
        records_label.set_markup("<span font='14' weight='bold' color='#00BFFF'>Recent Records</span>")
        records_label.set_margin_top(20)
        form_box.pack_start(records_label, False, False, 10)

        records_scroll = Gtk.ScrolledWindow()
        records_scroll.set_min_content_height(200)
        self.m_records_list = Gtk.ListBox()
        self.m_records_list.get_style_context().add_class("tracker-list")

        masturbation_records = self.health_data.get('masturbation', [])
        for record in reversed(masturbation_records[:10]):
            record_row = Gtk.ListBoxRow()
            record_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            date_label = Gtk.Label()
            date_label.set_markup(f"<span color='#00FFFF'>{record.get('date', 'Unknown')}</span>")
            date_label.set_size_request(120, -1)
            duration_label = Gtk.Label(label=f"{record.get('duration', '0')} mins")
            record_box.pack_start(date_label, False, False, 0)
            record_box.pack_start(duration_label, True, True, 0)
            record_row.add(record_box)
            self.m_records_list.add(record_row)

        records_scroll.add(self.m_records_list)
        form_box.pack_start(records_scroll, True, True, 0)

        self.content_box.pack_start(form_box, True, True, 0)
        self.content_box.show_all()

    def on_save_masturbation(self, button):
        """Save masturbation tracking data."""
        notes_buffer = self.notes_entry.get_buffer()
        notes = notes_buffer.get_text(
            notes_buffer.get_start_iter(),
            notes_buffer.get_end_iter(),
            True
        )
        record = {
            'date': self.masturbation_date.get_text(),
            'duration': self.duration_entry.get_text(),
            'notes': notes
        }
        self.health_data['masturbation'] = self.health_data.get('masturbation', [])
        self.health_data['masturbation'].append(record)
        self.save_health_data()
        self.setup_masturbation_tracker()

    def setup_horny_tracker(self):
        """Set up horny tracking view."""
        for child in self.content_box.get_children():
            self.content_box.remove(child)

        form_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        form_box.set_margin_top(20)
        form_box.set_margin_bottom(20)
        form_box.set_margin_start(20)
        form_box.set_margin_end(20)

        title_label = Gtk.Label()
        title_label.set_markup("<span font='16' weight='bold' color='#00BFFF'>Horny Tracker</span>")
        form_box.pack_start(title_label, False, False, 10)

        datetime_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        date_label = Gtk.Label()
        date_label.set_markup("<span color='#00BFFF'>Date:</span>")
        date_label.set_size_request(120, -1)
        date_label.set_xalign(0)
        self.horny_date = Gtk.Entry()
        self.horny_date.set_placeholder_text("YYYY-MM-DD")
        self.horny_date.set_text(datetime.date.today().isoformat())
        time_label = Gtk.Label()
        time_label.set_markup("<span color='#00BFFF'>Time:</span>")
        time_label.set_size_request(120, -1)
        time_label.set_xalign(0)
        self.horny_time = Gtk.Entry()
        self.horny_time.set_placeholder_text("HH:MM")
        self.horny_time.set_text(datetime.datetime.now().strftime("%H:%M"))
        datetime_box.pack_start(date_label, False, False, 0)
        datetime_box.pack_start(self.horny_date, True, True, 0)
        datetime_box.pack_start(time_label, False, False, 0)
        datetime_box.pack_start(self.horny_time, True, True, 0)

        intensity_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        intensity_label = Gtk.Label()
        intensity_label.set_markup("<span color='#00BFFF'>Intensity (1-10):</span>")
        intensity_label.set_xalign(0)
        self.intensity_scale = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL,
            adjustment=Gtk.Adjustment(value=5, lower=1, upper=10, step_increment=1, page_increment=1, page_size=0)
        )
        self.intensity_scale.set_digits(0)
        self.intensity_scale.set_value_pos(Gtk.PositionType.RIGHT)
        intensity_box.pack_start(intensity_label, False, False, 0)
        intensity_box.pack_start(self.intensity_scale, True, True, 0)

        triggers_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        triggers_label = Gtk.Label()
        triggers_label.set_markup("<span color='#00BFFF'>Triggers:</span>")
        triggers_label.set_xalign(0)
        self.triggers_entry = Gtk.Entry()
        self.triggers_entry.set_placeholder_text("What triggered this feeling?")
        triggers_box.pack_start(triggers_label, False, False, 0)
        triggers_box.pack_start(self.triggers_entry, True, True, 0)

        notes_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        notes_label = Gtk.Label()
        notes_label.set_markup("<span color='#00BFFF'>Notes:</span>")
        notes_label.set_xalign(0)
        notes_scroll = Gtk.ScrolledWindow()
        notes_scroll.set_min_content_height(100)
        self.horny_notes = Gtk.TextView()
        self.horny_notes.set_wrap_mode(Gtk.WrapMode.WORD)
        notes_scroll.add(self.horny_notes)
        notes_box.pack_start(notes_label, False, False, 0)
        notes_box.pack_start(notes_scroll, True, True, 0)

        save_button = Gtk.Button(label="Save")
        save_button.connect("clicked", self.on_save_horny)
        save_button.set_margin_top(15)

        form_box.pack_start(datetime_box, False, False, 0)
        form_box.pack_start(intensity_box, False, False, 0)
        form_box.pack_start(triggers_box, False, False, 0)
        form_box.pack_start(notes_box, True, True, 0)
        form_box.pack_start(save_button, False, False, 0)

        records_label = Gtk.Label()
        records_label.set_markup("<span font='14' weight='bold' color='#00BFFF'>Recent Records</span>")
        records_label.set_margin_top(20)
        form_box.pack_start(records_label, False, False, 10)

        records_scroll = Gtk.ScrolledWindow()
        records_scroll.set_min_content_height(200)
        self.horny_records_list = Gtk.ListBox()
        self.horny_records_list.get_style_context().add_class("tracker-list")

        horny_records = self.health_data.get('horny_tracker', [])
        for record in reversed(horny_records[:10]):
            record_row = Gtk.ListBoxRow()
            record_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            datetime_label = Gtk.Label()
            datetime_label.set_markup(f"<span color='#00FFFF'>{record.get('date', 'Unknown')} {record.get('time', '')}</span>")
            datetime_label.set_size_request(150, -1)
            intensity_label = Gtk.Label()
            intensity_label.set_markup(f"<span color='#FF00FF'>Intensity: {record.get('intensity', '0')}</span>")
            triggers_label = Gtk.Label(label=record.get('triggers', 'No triggers'))
            record_box.pack_start(datetime_label, False, False, 0)
            record_box.pack_start(intensity_label, False, False, 0)
            record_box.pack_start(triggers_label, True, True, 0)
            record_row.add(record_box)
            self.horny_records_list.add(record_row)

        records_scroll.add(self.horny_records_list)
        form_box.pack_start(records_scroll, True, True, 0)

        self.content_box.pack_start(form_box, True, True, 0)
        self.content_box.show_all()

    def on_save_horny(self, button):
        """Save horny tracking data."""
        notes_buffer = self.horny_notes.get_buffer()
        notes_text = notes_buffer.get_text(
            notes_buffer.get_start_iter(),
            notes_buffer.get_end_iter(),
            True
        )
        record = {
            'date': self.horny_date.get_text(),
            'time': self.horny_time.get_text(),
            'intensity': int(self.intensity_scale.get_value()),
            'triggers': self.triggers_entry.get_text(),
            'notes': notes_text
        }
        self.health_data['horny_tracker'] = self.health_data.get('horny_tracker', [])
        self.health_data['horny_tracker'].append(record)
        self.save_health_data()
        self.setup_horny_tracker()

    def setup_mood_tracker(self):
        """Set up mood tracking view."""
        for child in self.content_box.get_children():
            self.content_box.remove(child)

        form_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        form_box.set_margin_top(20)
        form_box.set_margin_bottom(20)
        form_box.set_margin_start(20)
        form_box.set_margin_end(20)

        title_label = Gtk.Label()
        title_label.set_markup("<span font='16' weight='bold' color='#00BFFF'>Mood Tracker</span>")
        form_box.pack_start(title_label, False, False, 10)

        datetime_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        date_label = Gtk.Label()
        date_label.set_markup("<span color='#00BFFF'>Date:</span>")
        date_label.set_size_request(120, -1)
        date_label.set_xalign(0)
        self.mood_date = Gtk.Entry()
        self.mood_date.set_placeholder_text("YYYY-MM-DD")
        self.mood_date.set_text(datetime.date.today().isoformat())
        time_label = Gtk.Label()
        time_label.set_markup("<span color='#00BFFF'>Time:</span>")
        time_label.set_size_request(120, -1)
        time_label.set_xalign(0)
        self.mood_time = Gtk.Entry()
        self.mood_time.set_placeholder_text("HH:MM")
        self.mood_time.set_text(datetime.datetime.now().strftime("%H:%M"))
        datetime_box.pack_start(date_label, False, False, 0)
        datetime_box.pack_start(self.mood_date, True, True, 0)
        datetime_box.pack_start(time_label, False, False, 0)
        datetime_box.pack_start(self.mood_time, True, True, 0)

        mood_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        mood_label = Gtk.Label()
        mood_label.set_markup("<span color='#00BFFF'>Primary Mood:</span>")
        mood_label.set_xalign(0)
        self.mood_combo = Gtk.ComboBoxText()
        moods = ["Happy", "Sad", "Angry", "Anxious", "Calm", "Excited"]
        for mood in moods:
            self.mood_combo.append_text(mood)
        self.mood_combo.set_active(0)
        mood_box.pack_start(mood_label, False, False, 0)
        mood_box.pack_start(self.mood_combo, True, True, 0)

        intensity_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        intensity_label = Gtk.Label()
        intensity_label.set_markup("<span color='#00BFFF'>Intensity (1-10):</span>")
        intensity_label.set_xalign(0)
        self.mood_intensity = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL,
            adjustment=Gtk.Adjustment(value=5, lower=1, upper=10, step_increment=1, page_increment=1, page_size=0)
        )
        self.mood_intensity.set_digits(0)
        self.mood_intensity.set_value_pos(Gtk.PositionType.RIGHT)
        intensity_box.pack_start(intensity_label, False, False, 0)
        intensity_box.pack_start(self.mood_intensity, True, True, 0)

        notes_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        notes_label = Gtk.Label()
        notes_label.set_markup("<span color='#00BFFF'>Notes:</span>")
        notes_label.set_xalign(0)
        notes_scroll = Gtk.ScrolledWindow()
        notes_scroll.set_min_content_height(100)
        self.mood_notes = Gtk.TextView()
        self.mood_notes.set_wrap_mode(Gtk.WrapMode.WORD)
        notes_scroll.add(self.mood_notes)
        notes_box.pack_start(notes_label, False, False, 0)
        notes_box.pack_start(notes_scroll, True, True, 0)

        save_button = Gtk.Button(label="Save")
        save_button.connect("clicked", self.on_save_mood)
        save_button.set_margin_top(15)

        form_box.pack_start(datetime_box, False, False, 0)
        form_box.pack_start(mood_box, False, False, 0)
        form_box.pack_start(intensity_box, False, False, 0)
        form_box.pack_start(notes_box, True, True, 0)
        form_box.pack_start(save_button, False, False, 0)

        records_label = Gtk.Label()
        records_label.set_markup("<span font='14' weight='bold' color='#00BFFF'>Recent Records</span>")
        records_label.set_margin_top(20)
        form_box.pack_start(records_label, False, False, 10)

        records_scroll = Gtk.ScrolledWindow()
        records_scroll.set_min_content_height(200)
        self.mood_records_list = Gtk.ListBox()
        self.mood_records_list.get_style_context().add_class("tracker-list")

        mood_records = self.health_data.get('mood_tracker', [])
        for record in reversed(mood_records[:10]):
            record_row = Gtk.ListBoxRow()
            record_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            datetime_label = Gtk.Label()
            datetime_label.set_markup(f"<span color='#00FFFF'>{record.get('date', 'Unknown')} {record.get('time', '')}</span>")
            datetime_label.set_size_request(150, -1)
            mood_label = Gtk.Label()
            mood_label.set_markup(f"<span color='#FF00FF'>{record.get('primary_mood', 'Unknown')}</span>")
            record_box.pack_start(datetime_label, False, False, 0)
            record_box.pack_start(mood_label, True, True, 0)
            record_row.add(record_box)
            self.mood_records_list.add(record_row)

        records_scroll.add(self.mood_records_list)
        form_box.pack_start(records_scroll, True, True, 0)

        self.content_box.pack_start(form_box, True, True, 0)
        self.content_box.show_all()

    def on_save_mood(self, button):
        """Save mood tracking data."""
        notes_buffer = self.mood_notes.get_buffer()
        notes_text = notes_buffer.get_text(
            notes_buffer.get_start_iter(),
            notes_buffer.get_end_iter(),
            True
        )
        record = {
            'date': self.mood_date.get_text(),
            'time': self.mood_time.get_text(),
            'primary_mood': self.mood_combo.get_active_text(),
            'intensity': int(self.mood_intensity.get_value()),
            'notes': notes_text
        }
        self.health_data['mood_tracker'] = self.health_data.get('mood_tracker', [])
        self.health_data['mood_tracker'].append(record)
        self.save_health_data()
        self.setup_mood_tracker()

    def setup_nora_chat(self):
        """Set up the chat interface with Nora."""
        for child in self.content_box.get_children():
            self.content_box.remove(child)

        chat_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        chat_box.set_margin_top(20)
        chat_box.set_margin_bottom(20)
        chat_box.set_margin_start(20)
        chat_box.set_margin_end(20)

        title_label = Gtk.Label()
        title_label.set_markup("<span font='18' weight='bold' color='#00BFFF'>Talk to Nora</span>")
        chat_box.pack_start(title_label, False, False, 10)

        welcome_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        welcome_box.get_style_context().add_class("health-card")
        welcome_label = Gtk.Label()
        welcome_label.set_markup("<span color='#00BFFF'>Hello! I'm Nora, your health assistant. Ask me anything!</span>")
        welcome_label.set_line_wrap(True)
        welcome_box.pack_start(welcome_label, False, False, 10)
        chat_box.pack_start(welcome_box, False, False, 10)

        chat_history_scroll = Gtk.ScrolledWindow()
        chat_history_scroll.set_min_content_height(400)
        self.chat_history = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        chat_history_scroll.add(self.chat_history)
        chat_box.pack_start(chat_history_scroll, True, True, 0)

        input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.chat_input = Gtk.Entry()
        self.chat_input.set_placeholder_text("Type your question here...")
        self.chat_input.connect("activate", self.on_send_message)
        send_button = Gtk.Button(label="Send")
        send_button.connect("clicked", self.on_send_message)
        input_box.pack_start(self.chat_input, True, True, 0)
        input_box.pack_start(send_button, False, False, 0)
        chat_box.pack_start(input_box, False, False, 0)

        self.content_box.pack_start(chat_box, True, True, 0)
        self.content_box.show_all()

        self.add_chat_message("Hi! I'm Nora. How can I assist you today?", "Nora")

    def add_chat_message(self, message, sender):
        """Add a message to the chat history."""
        message_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        message_box.get_style_context().add_class("health-card")
        sender_label = Gtk.Label()
        sender_label.set_markup(f"<span color='#00FFFF'>{sender}:</span>")
        sender_label.set_xalign(0)
        message_label = Gtk.Label()
        message_label.set_markup(f"<span color='#FFFFFF'>{message}</span>")
        message_label.set_line_wrap(True)
        message_box.pack_start(sender_label, False, False, 0)
        message_box.pack_start(message_label, False, False, 0)
        self.chat_history.pack_start(message_box, False, False, 0)
        self.chat_history.show_all()

    def on_send_message(self, widget):
        """Handle sending a message to Nora."""
        message = self.chat_input.get_text().strip()
        if not message:
            return
        self.add_chat_message(message, "You")
        self.chat_input.set_text("")
        response = self.generate_nora_response(message)
        self.add_chat_message(response, "Nora")

    def generate_nora_response(self, message):
        """Generate Nora's response to user messages."""
        msg = message.lower()
        responses = {
            "hello": "Hi there! How can I assist you today?",
            "how are you": "I'm doing great, thanks for asking! How about you?",
            "health": "I can help with health-related questions! What specifically would you like to know?",
            "goodbye": "See you later! Take care."
        }
        for keyword, response in responses.items():
            if keyword in msg:
                return response
        return "I'm not sure how to respond to that. Could you please provide more details?"

    def setup_google_fit(self):
        """Set up Google Fit integration view."""
        for child in self.content_box.get_children():
            self.content_box.remove(child)

        fit_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        fit_box.set_margin_top(20)
        fit_box.set_margin_bottom(20)
        fit_box.set_margin_start(20)
        fit_box.set_margin_end(20)

        title_label = Gtk.Label()
        title_label.set_markup("<span font='18' weight='bold' color='#00BFFF'>Google Fit Integration</span>")
        fit_box.pack_start(title_label, False, False, 10)

        if not self.fit_enabled:
            error_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            error_box.get_style_context().add_class("stats-container")
            error_label = Gtk.Label()
            error_label.set_markup("<span color='#FF6666'>Google Fit integration is not available.</span>")
            error_box.pack_start(error_label, False, False, 10)
            fit_box.pack_start(error_box, False, False, 10)
        else:
            time_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            start_label = Gtk.Label()
            start_label.set_markup("<span color='#00BFFF'>Start Date:</span>")
            self.start_date = Gtk.Entry()
            self.start_date.set_text((datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d"))
            end_label = Gtk.Label()
            end_label.set_markup("<span color='#00BFFF'>End Date:</span>")
            self.end_date = Gtk.Entry()
            self.end_date.set_text(datetime.datetime.now().strftime("%Y-%m-%d"))
            refresh_button = Gtk.Button(label="Refresh Data")
            refresh_button.connect("clicked", self.on_refresh_fit_data)
            time_box.pack_start(start_label, False, False, 0)
            time_box.pack_start(self.start_date, True, True, 0)
            time_box.pack_start(end_label, False, False, 0)
            time_box.pack_start(self.end_date, True, True, 0)
            time_box.pack_start(refresh_button, False, False, 10)
            fit_box.pack_start(time_box, False, False, 10)

            sections = [
                ("Steps", "steps"),
                ("Heart Rate", "heart_rate"),
                ("Sleep", "sleep")
            ]

            for title, section in sections:
                section_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                section_box.get_style_context().add_class("stats-container")
                section_title = Gtk.Label()
                section_title.set_markup(f"<span font='14' weight='bold' color='#00BFFF'>{title}</span>")
                section_box.pack_start(section_title, False, False, 5)
                data_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                data_container.set_name(f"fit_{section}_data")
                section_box.pack_start(data_container, True, True, 0)
                fit_box.pack_start(section_box, False, False, 10)

            self.on_refresh_fit_data(None)

        self.content_box.pack_start(fit_box, True, True, 0)
        self.content_box.show_all()

    def on_refresh_fit_data(self, button):
        """Refresh Google Fit data."""
        if not self.fit_enabled:
            return
        try:
            start_time = int(datetime.datetime.strptime(self.start_date.get_text(), "%Y-%m-%d").timestamp() * 1000)
            end_time = int(datetime.datetime.strptime(self.end_date.get_text(), "%Y-%m-%d").timestamp() * 1000)

            data_functions = {
                "steps": self.fit_manager.get_steps_data,
                "heart_rate": self.fit_manager.get_heart_rate_data,
                "sleep": self.fit_manager.get_sleep_data
            }

            for section, func in data_functions.items():
                data = func(start_time, end_time)
                self.update_fit_section(section, data)
        except Exception as e:
            print(f"Error refreshing Fit data: {e}")

    def update_fit_section(self, section, data):
        """Update a Google Fit data section in the UI."""
        container = None
        for child in self.content_box.get_children():
            for subchild in child.get_children():
                if subchild.get_name() == f"fit_{section}_data":
                    container = subchild
                    break
            if container:
                break
        if not container:
            return

        for child in container.get_children():
            container.remove(child)

        if not data or 'bucket' not in data:
            no_data_label = Gtk.Label()
            no_data_label.set_markup("<span color='#AAAAAA'>No data available</span>")
            container.pack_start(no_data_label, False, False, 5)
            container.show_all()
            return

        figure = Figure(figsize=(8, 4), dpi=100)
        figure.patch.set_facecolor((0, 0.05, 0.1, 0.9))
        ax = figure.add_subplot(111)

        dates = []
        values = []

        for bucket in data['bucket']:
            if 'dataset' in bucket and bucket['dataset']:
                for dataset in bucket['dataset']:
                    if 'point' in dataset and dataset['point']:
                        for point in dataset['point']:
                            if 'value' in point and point['value']:
                                date = datetime.datetime.fromtimestamp(int(point['startTimeNanos']) / 1000000000)
                                value = point['value'][0].get('intVal', point['value'][0].get('fpVal', 0))
                                dates.append(date)
                                values.append(value)

        if dates and values:
            ax.plot(dates, values, 'o-', color='#00BFFF')
            ax.set_xlabel('Date')
            ax.set_ylabel('Value' if section != 'steps' else 'Steps')
            ax.set_title(f'{section.title()} Over Time')
            ax.set_facecolor((0, 0.05, 0.1, 0.9))
            ax.tick_params(colors='#00BFFF')
            ax.grid(True, alpha=0.3)
            for spine in ax.spines.values():
                spine.set_color('#00BFFF')
            plt.xticks(rotation=45)
            canvas = FigureCanvas(figure)
            canvas.set_size_request(600, 300)
            container.pack_start(canvas, False, False, 10)
            avg_value = np.mean(values)
            stats_label = Gtk.Label()
            stats_label.set_markup(
                f"<span color='#FFFFFF'>Average: <span color='#00FFFF'>{avg_value:.1f}</span></span>"
            )
            container.pack_start(stats_label, False, False, 5)
        else:
            no_data_label = Gtk.Label()
            no_data_label.set_markup("<span color='#AAAAAA'>No data available</span>")
            container.pack_start(no_data_label, False, False, 5)

        container.show_all()

    def setup_apple_health(self):
        """Set up Apple Health data view."""
        for child in self.content_box.get_children():
            self.content_box.remove(child)

        health_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        health_box.set_margin_top(20)
        health_box.set_margin_bottom(20)
        health_box.set_margin_start(20)
        health_box.set_margin_end(20)

        title_label = Gtk.Label()
        title_label.set_markup("<span font='18' weight='bold' color='#00BFFF'>Apple Health Data</span>")
        health_box.pack_start(title_label, False, False, 10)

        apple_data = self.data_handler.load_data('apple_health_data.json')
        if not apple_data:
            no_data_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            no_data_box.get_style_context().add_class("stats-container")
            no_data_label = Gtk.Label()
            no_data_label.set_markup("<span color='#AAAAAA'>No Apple Health data imported. Please import data from Settings.</span>")
            no_data_box.pack_start(no_data_label, False, False, 10)
            health_box.pack_start(no_data_box, False, False, 10)
        else:
            last_imported = apple_data.get('last_imported', 'Unknown')
            import_label = Gtk.Label()
            import_label.set_markup(f"<span color='#00BFFF'>Last imported: {last_imported}</span>")
            health_box.pack_start(import_label, False, False, 5)

            if 'HKQuantityTypeIdentifierStepCount' in apple_data['data']:
                steps_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                steps_box.get_style_context().add_class("stats-container")
                steps_title = Gtk.Label()
                steps_title.set_markup("<span font='14' weight='bold' color='#00BFFF'>Steps</span>")
                steps_box.pack_start(steps_title, False, False, 5)

                steps_data = apple_data['data']['HKQuantityTypeIdentifierStepCount']
                daily_steps = {}
                for record in steps_data:
                    try:
                        date = datetime.datetime.fromisoformat(record['start_date']).date()
                        value = float(record['value'])
                        daily_steps[date] = daily_steps.get(date, 0) + value
                    except (ValueError, KeyError):
                        continue

                if daily_steps:
                    dates = sorted(daily_steps.keys())
                    values = [daily_steps[d] for d in dates]
                    figure = Figure(figsize=(8, 4), dpi=100)
                    figure.patch.set_facecolor((0, 0.05, 0.1, 0.9))
                    ax = figure.add_subplot(111)
                    ax.plot(dates, values, 'o-', color='#00BFFF')
                    ax.set_xlabel('Date')
                    ax.set_ylabel('Steps')
                    ax.set_title('Daily Steps')
                    ax.set_facecolor((0, 0.05, 0.1, 0.9))
                    ax.tick_params(colors='#00BFFF')
                    ax.grid(True, alpha=0.3)
                    for spine in ax.spines.values():
                        spine.set_color('#00BFFF')
                    plt.xticks(rotation=45)
                    canvas = FigureCanvas(figure)
                    canvas.set_size_request(600, 300)
                    steps_box.pack_start(canvas, False, False, 10)
                    avg_steps = sum(values) / len(values)
                    stats_label = Gtk.Label()
                    stats_label.set_markup(
                        f"<span color='#FFFFFF'>Average: <span color='#00FFFF'>{avg_steps:.1f}</span> steps/day</span>"
                    )
                    steps_box.pack_start(stats_label, False, False, 5)
                else:
                    no_data_label = Gtk.Label()
                    no_data_label.set_markup("<span color='#AAAAAA'>No steps data available</span>")
                    steps_box.pack_start(no_data_label, False, False, 5)
                health_box.pack_start(steps_box, False, False, 10)

        self.content_box.pack_start(health_box, True, True, 0)
        self.content_box.show_all()

    def setup_statistics(self):
        """Set up statistics view."""
        for child in self.content_box.get_children():
            self.content_box.remove(child)

        stats_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        stats_box.set_margin_top(20)
        stats_box.set_margin_bottom(20)
        stats_box.set_margin_start(20)
        stats_box.set_margin_end(20)

        title_label = Gtk.Label()
        title_label.set_markup("<span font='18' weight='bold' color='#00BFFF'>Health Statistics</span>")
        stats_box.pack_start(title_label, False, False, 10)

        if 'period' in self.health_data and 'history' in self.health_data['period']:
            period_stats = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            period_stats.get_style_context().add_class("stats-container")
            period_title = Gtk.Label()
            period_title.set_markup("<span font='14' weight='bold' color='#00BFFF'>Period Cycle Analysis</span>")
            period_stats.pack_start(period_title, False, False, 10)

            period_history = self.health_data['period']['history']
            if len(period_history) >= 2:
                cycle_lengths = []
                dates = []
                for i in range(len(period_history) - 1):
                    try:
                        start_date = datetime.datetime.strptime(period_history[i]['date'], "%Y-%m-%d").date()
                        end_date = datetime.datetime.strptime(period_history[i+1]['date'], "%Y-%m-%d").date()
                        cycle_length = (end_date - start_date).days
                        cycle_lengths.append(cycle_length)
                        dates.append(start_date)
                    except (ValueError, KeyError):
                        continue

                if cycle_lengths:
                    avg_cycle = sum(cycle_lengths) / len(cycle_lengths)
                    stats_info = Gtk.Label()
                    stats_info.set_markup(
                        f"<span color='#FFFFFF'>Average Cycle Length: <span color='#00FFFF'>{avg_cycle:.1f} days</span></span>"
                    )
                    period_stats.pack_start(stats_info, False, False, 5)

                    figure = Figure(figsize=(8, 4), dpi=100)
                    figure.patch.set_facecolor((0, 0.05, 0.1, 0.9))
                    ax = figure.add_subplot(111)
                    ax.plot(dates, cycle_lengths, 'o-', color='#00BFFF')
                    ax.set_xlabel('Start Date')
                    ax.set_ylabel('Cycle Length (days)')
                    ax.set_title('Period Cycle Lengths')
                    ax.set_facecolor((0, 0.05, 0.1, 0.9))
                    ax.tick_params(colors='#00BFFF')
                    ax.grid(True, alpha=0.3)
                    for spine in ax.spines.values():
                        spine.set_color('#00BFFF')
                    plt.xticks(rotation=45)
                    canvas = FigureCanvas(figure)
                    canvas.set_size_request(600, 300)
                    period_stats.pack_start(canvas, False, False, 10)
            else:
                no_data_label = Gtk.Label()
                no_data_label.set_markup("<span color='#AAAAAA'>Not enough period data</span>")
                period_stats.pack_start(no_data_label, False, False, 5)
            stats_box.pack_start(period_stats, False, False, 10)

        self.content_box.pack_start(stats_box, True, True, 0)
        self.content_box.show_all()

    def setup_settings(self):
        """Set up settings view."""
        for child in self.content_box.get_children():
            self.content_box.remove(child)

        settings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        settings_box.set_margin_top(20)
        settings_box.set_margin_bottom(20)
        settings_box.set_margin_start(20)
        settings_box.set_margin_end(20)

        title_label = Gtk.Label()
        title_label.set_markup("<span font='18' weight='bold' color='#00BFFF'>Settings</span>")
        settings_box.pack_start(title_label, False, False, 10)

        general_settings = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        general_settings.get_style_context().add_class("settings-section")
        general_title = Gtk.Label()
        general_title.set_markup("<span font='14' weight='bold' color='#00BFFF'>General Settings</span>")
        general_settings.pack_start(general_title, False, False, 5)

        notifications_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        notifications_label = Gtk.Label()
        notifications_label.set_markup("<span color='#FFFFFF'>Enable Notifications</span>")
        self.notifications_switch = Gtk.Switch()
        self.notifications_switch.set_active(self.settings.get('notifications_enabled', True))
        self.notifications_switch.connect("notify::active", self.on_notifications_toggled)
        notifications_box.pack_start(notifications_label, True, True, 0)
        notifications_box.pack_start(self.notifications_switch, False, False, 0)
        general_settings.pack_start(notifications_box, False, False, 5)

        settings_box.pack_start(general_settings, False, False, 10)

        data_settings = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        data_settings.get_style_context().add_class("settings-section")
        data_title = Gtk.Label()
        data_title.set_markup("<span font='14' weight='bold' color='#00BFFF'>Data Management</span>")
        data_settings.pack_start(data_title, False, False, 5)

        export_button = Gtk.Button(label="Export Health Data")
        export_button.connect("clicked", self.on_export_data)
        data_settings.pack_start(export_button, False, False, 5)

        import_button = Gtk.Button(label="Import Health Data")
        import_button.connect("clicked", self.on_import_data)
        data_settings.pack_start(import_button, False, False, 5)

        import_apple_button = Gtk.Button(label="Import Apple Health Data")
        import_apple_button.connect("clicked", self.on_import_apple_health)
        data_settings.pack_start(import_apple_button, False, False, 5)

        erase_button = Gtk.Button(label="Erase All Data")
        erase_button.connect("clicked", self.on_erase_data)
        data_settings.pack_start(erase_button, False, False, 5)

        settings_box.pack_start(data_settings, False, False, 10)

        save_button = Gtk.Button(label="Save Settings")
        save_button.connect("clicked", self.on_save_settings)
        settings_box.pack_start(save_button, False, False, 10)

        self.content_box.pack_start(settings_box, True, True, 0)
        self.content_box.show_all()

    def on_notifications_toggled(self, switch, param):
        """Handle notifications toggle."""
        self.settings['notifications_enabled'] = switch.get_active()

    def on_save_settings(self, button):
        """Save settings."""
        self.save_settings()
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Settings Saved"
        )
        dialog.run()
        dialog.destroy()

    def on_export_data(self, button):
        """Export health data to a file."""
        dialog = Gtk.FileChooserDialog(
            title="Export Health Data",
            parent=self,
            action=Gtk.FileChooserAction.SAVE
        )
        dialog.set_do_overwrite_confirmation(True)
        dialog.set_current_name("hextrix_health_data.json")
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.OK
        )
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            try:
                with open(filename, 'w') as f:
                    json.dump(self.health_data, f, indent=2)
                success_dialog = Gtk.MessageDialog(
                    transient_for=self,
                    flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text="Export Successful"
                )
                success_dialog.run()
                success_dialog.destroy()
            except Exception as e:
                error_dialog = Gtk.MessageDialog(
                    transient_for=self,
                    flags=0,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text="Export Failed"
                )
                error_dialog.format_secondary_text(str(e))
                error_dialog.run()
                error_dialog.destroy()
        dialog.destroy()

    def on_import_data(self, button):
        """Import health data from a file."""
        dialog = Gtk.FileChooserDialog(
            title="Import Health Data",
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        filter_json = Gtk.FileFilter()
        filter_json.set_name("JSON files")
        filter_json.add_mime_type("application/json")
        dialog.add_filter(filter_json)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                self.health_data = data
                self.save_health_data()
                success_dialog = Gtk.MessageDialog(
                    transient_for=self,
                    flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text="Import Successful"
                )
                success_dialog.run()
                success_dialog.destroy()
                self.setup_dashboard()
            except Exception as e:
                error_dialog = Gtk.MessageDialog(
                    transient_for=self,
                    flags=0,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text="Import Failed"
                )
                error_dialog.format_secondary_text(str(e))
                error_dialog.run()
                error_dialog.destroy()
        dialog.destroy()

    def on_import_apple_health(self, button):
        """Handle importing Apple Health data from a ZIP file."""
        dialog = Gtk.FileChooserDialog(
            title="Import Apple Health Data",
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        filter_zip = Gtk.FileFilter()
        filter_zip.set_name("ZIP files")
        filter_zip.add_mime_type("application/zip")
        dialog.add_filter(filter_zip)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            zip_path = dialog.get_filename()
            try:
                self.data_handler.import_apple_health_data(zip_path)
                success_dialog = Gtk.MessageDialog(
                    transient_for=self,
                    flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text="Import Successful"
                )
                success_dialog.format_secondary_text("Apple Health data has been imported.")
                success_dialog.run()
                success_dialog.destroy()
            except Exception as e:
                error_dialog = Gtk.MessageDialog(
                    transient_for=self,
                    flags=0,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text="Import Failed"
                )
                error_dialog.format_secondary_text(str(e))
                error_dialog.run()
                error_dialog.destroy()
        dialog.destroy()

    def on_erase_data(self, button):
        """Erase all health data."""
        confirm_dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Erase All Data"
        )
        confirm_dialog.format_secondary_text("This will delete all your health data. Continue?")
        response = confirm_dialog.run()
        confirm_dialog.destroy()
        if response == Gtk.ResponseType.YES:
            self.health_data = {}
            self.save_health_data()
            success_dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="Data Erased"
            )
            success_dialog.run()
            success_dialog.destroy()
            self.setup_dashboard()

    def on_nav_clicked(self, button, view):
        """Handle navigation button clicks."""
        self.current_view = view
        if view == "dashboard":
            self.setup_dashboard()
        elif view == "period":
            self.setup_period_tracker()
        elif view == "sexual":
            self.setup_sexual_health()
        elif view == "masturbation":
            self.setup_masturbation_tracker()
        elif view == "horny":
            self.setup_horny_tracker()
        elif view == "mood":
            self.setup_mood_tracker()
        elif view == "nora":
            self.setup_nora_chat()
        elif view == "google_fit":
            self.setup_google_fit()
        elif view == "apple_health":
            self.setup_apple_health()
        elif view == "stats":
            self.setup_statistics()
        elif view == "settings":
            self.setup_settings()

if __name__ == "__main__":
    app = HextrixHealth()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()