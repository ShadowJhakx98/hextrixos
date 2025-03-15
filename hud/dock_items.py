import os
import subprocess

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

class DockCategory:
    def __init__(self, name, icon):
        self.name = name
        self.icon = icon
        self.items = []
    
    def add_item(self, item):
        self.items.append(item)
    
    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)

class DockItem:
    def __init__(self, name, icon_path, command, desktop_id, category):
        self.name = name
        self.icon_path = icon_path
        self.command = command
        self.desktop_id = desktop_id
        self.category = category
    
    def to_dict(self):
        return {
            "name": self.name,
            "icon_path": self.icon_path,
            "command": self.command,
            "desktop_id": self.desktop_id,
            "category": self.category
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            data.get("name", "Unknown"),
            data.get("icon_path", ""),
            data.get("command", ""),
            data.get("desktop_id", ""),
            data.get("category", "Utilities")
        )
        
    def launch(self, parent=None):
        """Launch the application"""
        try:
            if self.name == "Cyberpunk Explorer" and parent and hasattr(parent, 'launch_cyberpunk_explorer'):
                parent.launch_cyberpunk_explorer()
            else:
                # Get project directory for CWD
                script_dir = os.path.dirname(os.path.abspath(__file__))
                project_dir = os.path.dirname(script_dir)
                subprocess.Popen(self.command.split(), cwd=project_dir)
        except Exception as e:
            if parent:
                error_dialog = Gtk.MessageDialog(
                    transient_for=parent,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text=f"Error launching {self.name}"
                )
                error_dialog.format_secondary_text(str(e))
                error_dialog.run()
                error_dialog.destroy()