# Hextrix OS Model Context Protocol (MCP) Connector

This is a custom Model Context Protocol (MCP) connector for Hextrix OS, allowing Claude or Cursor to interact with your Hextrix OS environment.

## What is MCP?

Model Context Protocol (MCP) is a protocol introduced by Anthropic that allows AI assistants like Claude to access external data sources and tools. With this Hextrix OS MCP connector, Claude can:

- Access the Hextrix OS filesystem
- Execute commands on Hextrix OS
- Search and grep files
- Launch and interact with Hextrix OS applications
- Access Hextrix OS's custom apps (Notepad, Email, Calculator, etc.)

## Installation

### Prerequisites

- Node.js (for the MCP server)
- Python 3.x (for the client library)
- Hextrix OS

### Setup

1. Install the required dependencies:

```bash
cd hextrix-mcp
npm install
pip install requests
```

2. Start the MCP server:

```bash
./start_mcp.sh
```

By default, the server runs on port 3000. You can specify a different port:

```bash
./start_mcp.sh 8080
```

## Using with Claude/Cursor

To use this MCP connector with Claude or Cursor:

1. Start the MCP server on your Hextrix OS machine.

2. In the Claude Desktop app, go to Settings → Connectors → Add MCP Server, and enter:
   - URL: `http://localhost:3000`
   - Name: Hextrix OS

3. For Cursor, you can use the Claude extension and connect to the MCP server similarly.

## Features

### Filesystem Access

- Read files
- Write files
- List directory contents
- Search for files matching a pattern
- Grep for text within files

### Hextrix OS Command Execution

- Execute any Hextrix OS command and get its output

### Notepad App

- Launch Notepad (optionally with a file path)
- Create new notes with title, content, tags, and folder organization
- List and search notes by folder and tags

### Email App

- Launch Email client
- Compose new emails and save as drafts
- Attachments support

### Calculator App

- Launch Calculator
- Perform calculations through the API

### Health App

- Launch Health app
- Log health data (measurements, activities, etc.)
- Store health metrics with timestamp, units, and notes

### Calendar App

- Launch Calendar app
- Add events with title, time, location, description, and participants
- Set reminders for events
- List events with date range filtering

### Contacts App

- Launch Contacts app
- Add new contacts with complete information
- Search contacts by name, email, or company
- Filter contacts by group

### App Management

- Launch App Center
- List all available Hextrix apps

## Android Applications (HexDroid)

The MCP connector provides access to the HexDroid Android compatibility layer in Hextrix OS, allowing you to manage and interact with Android applications.

### Endpoints

- **GET /api/hexdroid/capabilities** - Get HexDroid capabilities
- **GET /api/hexdroid/list** - List all installed Android applications
- **POST /api/hexdroid/install** - Install an Android APK
- **POST /api/hexdroid/uninstall** - Uninstall an Android application
- **POST /api/hexdroid/launch** - Launch an installed Android application
- **POST /api/hexdroid/runtime/restart** - Restart an Android runtime
- **GET /api/hexdroid/runtime/status** - Get status of Android runtimes

### Example Usage with Python Client

```python
# Initialize the client
from mcp_client import MCPClient
client = MCPClient('localhost', 3000)

# List installed Android applications
response = client.list_android_apps()
if response['success']:
    for app in response['apps']:
        print(f"App: {app['name']} (ID: {app['id']}, Runtime: {app['runtime']})")

# Install an Android APK
response = client.install_android_app('/path/to/app.apk', runtime='anbox')
print(f"Installation: {'Success' if response['success'] else 'Failed'}")

# Launch an Android application
response = client.launch_android_app('app_id')
print(f"Launch: {'Success' if response['success'] else 'Failed'}")

# Uninstall an Android application
response = client.uninstall_android_app('app_id')
print(f"Uninstallation: {'Success' if response['success'] else 'Failed'}")

# Get runtime status
response = client.get_android_runtime_status()
if response['success']:
    print(f"Anbox: {response['status']['anbox']}")
    print(f"Waydroid: {response['status']['waydroid']}")

# Restart a runtime
response = client.restart_android_runtime('anbox')
print(f"Restart: {'Success' if response['success'] else 'Failed'}")
```

## Python Client Library

A Python client library is included to interact with the MCP server programmatically from within Hextrix OS:

```python
from mcp_client import HextrixMCPClient

client = HextrixMCPClient()

# Basic file operations
content = client.read_file("/path/to/file.txt")
client.write_file("/path/to/newfile.txt", "Hello, Hextrix OS!")
files = client.list_directory("/home/user")

# Search and grep
python_files = client.search_files("/home", "*.py", recursive=True)
results = client.grep_files("/home/projects", "TODO:", recursive=True)

# Execute commands
result = client.execute_command("ls", ["-la"])
print(result["stdout"])

# Notepad operations
client.open_notepad("/path/to/document.txt")
note = client.create_note(
    title="Meeting Notes",
    content="Things to discuss: ...",
    tags=["work", "meeting"],
    folder="Work"
)
notes = client.list_notes(folder="Work", tag="meeting")

# Calendar operations
client.open_calendar()
event = client.add_calendar_event(
    title="Team Meeting",
    start="2025-04-01T10:00:00",
    end="2025-04-01T11:00:00",
    location="Conference Room"
)
events = client.get_calendar_events(
    start_date="2025-04-01",
    end_date="2025-04-30"
)

# Email operations
client.open_email()
draft = client.compose_email(
    to="colleague@example.com",
    subject="Project Update",
    body="Here's the latest on our project..."
)

# Calculator operations
result = client.calculate("10 * 5 + 3")  # Returns 53

# Health tracking
client.open_health()
client.log_health_data(
    data_type="weight",
    value=70.5,
    unit="kg"
)

# Contacts management
client.open_contacts()
contact = client.add_contact(
    name="John Smith",
    email="john@example.com",
    phone="555-1234",
    groups=["Work"]
)
contacts = client.search_contacts(query="john")

# App management
client.open_app_center()
available_apps = client.list_apps()
```

## Security Considerations

This MCP connector has full access to the filesystem and can execute commands on your system. It's recommended to:

1. Only run the MCP server on a secure, local network
2. Consider adding authentication
3. Restrict access to specific directories or commands if needed
4. Be careful with the calculator's eval() function in production environments

## Extending

You can extend this MCP connector by adding more Hextrix OS-specific endpoints:

1. Add new routes to `index.js`
2. Add corresponding methods to the Python client
3. Update the capabilities in the MCP configuration

## License

[Your License Here] 