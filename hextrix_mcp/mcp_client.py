import requests
import json
import os

class HextrixMCPClient:
    """Python client for interacting with the Hextrix OS MCP server"""
    
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
        
    def _get(self, endpoint, params=None):
        """Helper method for GET requests to the MCP server"""
        try:
            response = requests.get(f"{self.base_url}{endpoint}", params=params)
            response.raise_for_status()  # Raise exception for 4XX/5XX responses
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def _post(self, endpoint, data=None):
        """Helper method for POST requests to the MCP server"""
        try:
            response = requests.post(f"{self.base_url}{endpoint}", json=data)
            response.raise_for_status()  # Raise exception for 4XX/5XX responses
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
        
    def get_capabilities(self):
        """Get the MCP server capabilities"""
        response = requests.get(f"{self.base_url}/.well-known/mcp-configuration")
        return response.json()
        
    def read_file(self, file_path):
        """Read a file from the filesystem"""
        response = requests.post(
            f"{self.base_url}/v1/filesystem/read",
            json={"path": file_path}
        )
        if response.status_code == 200:
            return response.json()["content"]
        else:
            error = response.json().get("error", "Unknown error")
            raise Exception(f"Failed to read file: {error}")
            
    def write_file(self, file_path, content):
        """Write content to a file in the filesystem"""
        response = requests.post(
            f"{self.base_url}/v1/filesystem/write",
            json={"path": file_path, "content": content}
        )
        if response.status_code == 200:
            return True
        else:
            error = response.json().get("error", "Unknown error")
            raise Exception(f"Failed to write file: {error}")
            
    def list_directory(self, dir_path):
        """List contents of a directory"""
        response = requests.post(
            f"{self.base_url}/v1/filesystem/list",
            json={"path": dir_path}
        )
        if response.status_code == 200:
            return response.json()["files"]
        else:
            error = response.json().get("error", "Unknown error")
            raise Exception(f"Failed to list directory: {error}")
    
    def search_files(self, dir_path, pattern, recursive=True, max_results=100):
        """Search for files matching a pattern"""
        response = requests.post(
            f"{self.base_url}/v1/filesystem/search",
            json={
                "path": dir_path, 
                "pattern": pattern,
                "recursive": recursive,
                "maxResults": max_results
            }
        )
        if response.status_code == 200:
            return response.json()["results"]
        else:
            error = response.json().get("error", "Unknown error")
            raise Exception(f"Failed to search files: {error}")
    
    def grep_files(self, dir_path, query, recursive=True, max_results=100):
        """Search for text within files"""
        response = requests.post(
            f"{self.base_url}/v1/filesystem/grep",
            json={
                "path": dir_path, 
                "query": query,
                "recursive": recursive,
                "maxResults": max_results
            }
        )
        if response.status_code == 200:
            return response.json()["results"]
        else:
            error = response.json().get("error", "Unknown error")
            raise Exception(f"Failed to grep files: {error}")
            
    def execute_command(self, command, args=None):
        """Execute a Hextrix OS command"""
        if args is None:
            args = []
            
        response = requests.post(
            f"{self.base_url}/v1/hextrix/execute",
            json={"command": command, "args": args}
        )
        if response.status_code == 200:
            return response.json()
        else:
            error = response.json().get("error", "Unknown error")
            raise Exception(f"Failed to execute command: {error}")
    
    # Hextrix Apps Methods
    
    def list_apps(self):
        """List all available Hextrix apps"""
        response = requests.get(f"{self.base_url}/v1/hextrix/apps/list")
        if response.status_code == 200:
            return response.json()["apps"]
        else:
            error = response.json().get("error", "Unknown error")
            raise Exception(f"Failed to list apps: {error}")
    
    # Notepad methods
    
    def open_notepad(self, file_path=None):
        """Open the Hextrix Notepad app, optionally with a file"""
        payload = {}
        if file_path:
            payload["filePath"] = file_path
            
        response = requests.post(
            f"{self.base_url}/v1/hextrix/apps/notepad/open",
            json=payload
        )
        if response.status_code == 200:
            return response.json()
        else:
            error = response.json().get("error", "Unknown error")
            raise Exception(f"Failed to open notepad: {error}")
    
    def create_note(self, title, content, tags=None, folder="Notes"):
        """Create a new note in the Notepad app"""
        if tags is None:
            tags = []
            
        response = requests.post(
            f"{self.base_url}/v1/hextrix/apps/notepad/create",
            json={
                "title": title,
                "content": content,
                "tags": tags,
                "folder": folder
            }
        )
        if response.status_code == 200:
            return response.json()["note"]
        else:
            error = response.json().get("error", "Unknown error")
            raise Exception(f"Failed to create note: {error}")
    
    def list_notes(self, folder="Notes", tag=None):
        """List notes, optionally filtered by folder and tag"""
        params = {"folder": folder}
        if tag:
            params["tag"] = tag
            
        response = requests.get(
            f"{self.base_url}/v1/hextrix/apps/notepad/list",
            params=params
        )
        if response.status_code == 200:
            return response.json()["notes"]
        else:
            error = response.json().get("error", "Unknown error")
            raise Exception(f"Failed to list notes: {error}")
    
    # Email methods
    
    def open_email(self):
        """Open the Hextrix Email app"""
        response = requests.post(f"{self.base_url}/v1/hextrix/apps/email/open", json={})
        if response.status_code == 200:
            return response.json()
        else:
            error = response.json().get("error", "Unknown error")
            raise Exception(f"Failed to open email app: {error}")
    
    def compose_email(self, to, subject, body, attachments=None):
        """Compose a new email draft"""
        if attachments is None:
            attachments = []
            
        response = requests.post(
            f"{self.base_url}/v1/hextrix/apps/email/compose",
            json={
                "to": to,
                "subject": subject,
                "body": body,
                "attachments": attachments
            }
        )
        if response.status_code == 200:
            return response.json()["draft"]
        else:
            error = response.json().get("error", "Unknown error")
            raise Exception(f"Failed to compose email: {error}")
    
    # Calculator methods
    
    def open_calculator(self):
        """Open the Hextrix Calculator app"""
        response = requests.post(f"{self.base_url}/v1/hextrix/apps/calculator/open", json={})
        if response.status_code == 200:
            return response.json()
        else:
            error = response.json().get("error", "Unknown error")
            raise Exception(f"Failed to open calculator app: {error}")
    
    def calculate(self, expression):
        """Perform a calculation"""
        response = requests.post(
            f"{self.base_url}/v1/hextrix/apps/calculator/calculate",
            json={"expression": expression}
        )
        if response.status_code == 200:
            return response.json()["result"]
        else:
            error = response.json().get("error", "Unknown error")
            raise Exception(f"Failed to calculate: {error}")
    
    # Health app methods
    
    def open_health(self):
        """Open the Hextrix Health app"""
        response = requests.post(f"{self.base_url}/v1/hextrix/apps/health/open", json={})
        if response.status_code == 200:
            return response.json()
        else:
            error = response.json().get("error", "Unknown error")
            raise Exception(f"Failed to open health app: {error}")
    
    def log_health_data(self, data_type, value, unit=None, timestamp=None, notes=None):
        """Log health data"""
        payload = {
            "type": data_type,
            "value": value
        }
        
        if unit:
            payload["unit"] = unit
        if timestamp:
            payload["timestamp"] = timestamp
        if notes:
            payload["notes"] = notes
            
        response = requests.post(
            f"{self.base_url}/v1/hextrix/apps/health/log",
            json=payload
        )
        if response.status_code == 200:
            return response.json()["entry"]
        else:
            error = response.json().get("error", "Unknown error")
            raise Exception(f"Failed to log health data: {error}")
    
    # Calendar methods
    
    def open_calendar(self):
        """Open the Hextrix Calendar app"""
        response = requests.post(f"{self.base_url}/v1/hextrix/apps/calendar/open", json={})
        if response.status_code == 200:
            return response.json()
        else:
            error = response.json().get("error", "Unknown error")
            raise Exception(f"Failed to open calendar app: {error}")
    
    def add_calendar_event(self, title, start, end=None, all_day=False, location=None, 
                           description=None, participants=None, reminder=15):
        """Add an event to the calendar"""
        payload = {
            "title": title,
            "start": start,
            "allDay": all_day,
            "reminder": reminder
        }
        
        if end:
            payload["end"] = end
        if location:
            payload["location"] = location
        if description:
            payload["description"] = description
        if participants:
            payload["participants"] = participants
            
        response = requests.post(
            f"{self.base_url}/v1/hextrix/apps/calendar/add-event",
            json=payload
        )
        if response.status_code == 200:
            return response.json()["event"]
        else:
            error = response.json().get("error", "Unknown error")
            raise Exception(f"Failed to add calendar event: {error}")
    
    def get_calendar_events(self, start_date=None, end_date=None):
        """Get calendar events, optionally filtered by date range"""
        params = {}
        if start_date:
            params["start"] = start_date
        if end_date:
            params["end"] = end_date
            
        response = requests.get(
            f"{self.base_url}/v1/hextrix/apps/calendar/events",
            params=params
        )
        if response.status_code == 200:
            return response.json()["events"]
        else:
            error = response.json().get("error", "Unknown error")
            raise Exception(f"Failed to get calendar events: {error}")
    
    # Contacts methods
    
    def open_contacts(self):
        """Open the Hextrix Contacts app"""
        response = requests.post(f"{self.base_url}/v1/hextrix/apps/contacts/open", json={})
        if response.status_code == 200:
            return response.json()
        else:
            error = response.json().get("error", "Unknown error")
            raise Exception(f"Failed to open contacts app: {error}")
    
    def add_contact(self, name, email=None, phone=None, address=None, company=None, notes=None, groups=None):
        """Add a new contact"""
        payload = {"name": name}
        
        if email:
            payload["email"] = email
        if phone:
            payload["phone"] = phone
        if address:
            payload["address"] = address
        if company:
            payload["company"] = company
        if notes:
            payload["notes"] = notes
        if groups:
            payload["groups"] = groups
            
        response = requests.post(
            f"{self.base_url}/v1/hextrix/apps/contacts/add",
            json=payload
        )
        if response.status_code == 200:
            return response.json()["contact"]
        else:
            error = response.json().get("error", "Unknown error")
            raise Exception(f"Failed to add contact: {error}")
    
    def search_contacts(self, query=None, group=None):
        """Search contacts by name, email, or company, and optionally filter by group"""
        params = {}
        if query:
            params["query"] = query
        if group:
            params["group"] = group
            
        response = requests.get(
            f"{self.base_url}/v1/hextrix/apps/contacts/search",
            params=params
        )
        if response.status_code == 200:
            return response.json()["contacts"]
        else:
            error = response.json().get("error", "Unknown error")
            raise Exception(f"Failed to search contacts: {error}")
    
    def open_app_center(self):
        """Open the Hextrix App Center"""
        response = requests.post(f"{self.base_url}/v1/hextrix/apps/appcenter/open", json={})
        if response.status_code == 200:
            return response.json()
        else:
            error = response.json().get("error", "Unknown error")
            raise Exception(f"Failed to open app center: {error}")

    # HexWin methods
    
    def open_hexwin(self):
        """Open the HexWin Windows Application Manager"""
        response = requests.post(f"{self.base_url}/v1/hextrix/apps/hexwin/open", json={})
        if response.status_code == 200:
            return response.json()
        else:
            error = response.json().get("error", "Unknown error")
            raise Exception(f"Failed to open HexWin: {error}")
    
    def run_windows_app(self, exe_path):
        """Run a Windows application using HexWin"""
        response = requests.post(
            f"{self.base_url}/v1/hextrix/apps/hexwin/run",
            json={"path": exe_path}
        )
        if response.status_code == 200:
            return response.json()
        else:
            error = response.json().get("error", "Unknown error")
            raise Exception(f"Failed to run Windows application: {error}")
    
    def install_windows_app(self, installer_path, app_name, category="Windows"):
        """Install a Windows application using HexWin"""
        response = requests.post(
            f"{self.base_url}/v1/hextrix/apps/hexwin/install",
            json={
                "installer": installer_path,
                "name": app_name,
                "category": category
            }
        )
        if response.status_code == 200:
            return response.json()
        else:
            error = response.json().get("error", "Unknown error")
            raise Exception(f"Failed to install Windows application: {error}")
    
    def list_windows_apps(self):
        """List installed Windows applications"""
        response = requests.get(f"{self.base_url}/v1/hextrix/apps/hexwin/list")
        if response.status_code == 200:
            return response.json()["apps"]
        else:
            error = response.json().get("error", "Unknown error")
            raise Exception(f"Failed to list Windows applications: {error}")

    # HexDroid methods
    def get_hexdroid_capabilities(self):
        """Get HexDroid capabilities from the MCP server"""
        return self._get('/api/hexdroid/capabilities')
    
    def list_android_apps(self):
        """List all installed Android applications"""
        return self._get('/api/hexdroid/list')
    
    def install_android_app(self, apk_path, runtime=None, app_name=None, icon_path=None):
        """
        Install an Android APK
        
        Args:
            apk_path (str): Path to the APK file
            runtime (str, optional): Runtime to use, 'anbox' or 'waydroid'
            app_name (str, optional): Custom name for the application
            icon_path (str, optional): Custom icon for the application
            
        Returns:
            dict: Response from the server
        """
        data = {
            'apk_path': apk_path
        }
        
        if runtime:
            data['runtime'] = runtime
        
        if app_name:
            data['app_name'] = app_name
            
        if icon_path:
            data['icon_path'] = icon_path
            
        return self._post('/api/hexdroid/install', data)
    
    def uninstall_android_app(self, app_id):
        """
        Uninstall an Android application
        
        Args:
            app_id (str): ID of the app to uninstall
            
        Returns:
            dict: Response from the server
        """
        return self._post('/api/hexdroid/uninstall', {'app_id': app_id})
    
    def launch_android_app(self, app_id, runtime=None):
        """
        Launch an installed Android application
        
        Args:
            app_id (str): ID of the app to launch
            runtime (str, optional): Override the runtime to use
            
        Returns:
            dict: Response from the server
        """
        data = {'app_id': app_id}
        
        if runtime:
            data['runtime'] = runtime
            
        return self._post('/api/hexdroid/launch', data)
    
    def restart_android_runtime(self, runtime):
        """
        Restart an Android runtime
        
        Args:
            runtime (str): Runtime to restart ('anbox' or 'waydroid')
            
        Returns:
            dict: Response from the server
        """
        return self._post('/api/hexdroid/runtime/restart', {'runtime': runtime})
    
    def get_android_runtime_status(self):
        """
        Get status of Android runtimes
        
        Returns:
            dict: Status of Anbox and Waydroid runtimes
        """
        return self._get('/api/hexdroid/runtime/status')


# Example usage
if __name__ == "__main__":
    client = HextrixMCPClient()
    
    try:
        # Get MCP capabilities
        capabilities = client.get_capabilities()
        print("MCP Capabilities:", capabilities)
        
        # Write a file
        test_content = "This is a test file created by the Hextrix MCP client"
        client.write_file("/tmp/hextrix-mcp-test.txt", test_content)
        print("File written successfully")
        
        # Read the file
        content = client.read_file("/tmp/hextrix-mcp-test.txt")
        print("File content:", content)
        
        # List directory
        files = client.list_directory("/tmp")
        print("Files in /tmp:")
        for file in files:
            print(f"  - {file['name']} ({file['type']})")
        
        # Create a note
        note = client.create_note(
            title="Test Note",
            content="This is a test note created via MCP.",
            tags=["test", "mcp"]
        )
        print(f"\nNote created: {note['title']}")
        
        # Add a calendar event
        event = client.add_calendar_event(
            title="Team Meeting",
            start="2025-04-01T10:00:00",
            end="2025-04-01T11:00:00",
            location="Conference Room"
        )
        print(f"\nEvent added: {event['title']} at {event['location']}")
        
        # Perform a calculation
        result = client.calculate("10 * 5 + 3")
        print(f"\nCalculation result: 10 * 5 + 3 = {result}")
        
        # Add a contact
        contact = client.add_contact(
            name="John Smith",
            email="john@example.com",
            phone="555-1234",
            groups=["Work"]
        )
        print(f"\nContact added: {contact['name']}, {contact['email']}")
        
        # List Windows applications
        try:
            windows_apps = client.list_windows_apps()
            print("\nInstalled Windows applications:")
            for app in windows_apps:
                print(f"  - {app['name']} ({app['type']})")
        except Exception as e:
            print(f"Windows apps listing not available: {e}")
        
    except Exception as e:
        print(f"Error: {e}") 