import os
import subprocess

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
                from pathlib import Path
                project_dir = Path(__file__).resolve().parent
                subprocess.Popen(self.command.split(), cwd=project_dir)
        except Exception as e:
            if parent:
                import gi
                gi.require_version('Gtk', '3.0')
                from gi.repository import Gtk
                
                error_dialog = Gtk.MessageDialog(
                    transient_for=parent,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text=f"Error launching {self.name}"
                )
                error_dialog.format_secondary_text(str(e))
                error_dialog.run()
                error_dialog.destroy()