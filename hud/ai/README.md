# Hextrix AI System Control

This extension adds system control capabilities to the Hextrix AI assistant, allowing you to control your entire system with voice and text commands.

## Features

- **Voice Commands**: Control your system using natural language voice commands
- **Windows App Management**: Launch and manage Windows applications (via HexWin)
- **Android App Management**: Launch and manage Android applications (via HexDroid)
- **Native App Management**: Launch and manage native Linux applications
- **File Operations**: Find files, search for text in files, and locate media

## Supported Commands

### Application Management

- `list windows apps` - List all installed Windows applications
- `list android apps` - List all installed Android applications
- `list native apps` - List all installed native Linux applications
- `run [app name] app` - Run an application (supports Windows, Android, and native)
- `open [app name] app` - Same as run
- `launch [app name] app` - Same as run
- `start [app name] app` - Same as run

### File Operations

- `find files [query]` - Find files matching a query
- `search files for [query]` - Same as find files
- `find images [query]` - Find images matching a query
- `find videos [query]` - Find videos matching a query
- `find documents [query]` - Find documents matching a query

### Direct Voice Commands

- `voice command: [command]` - Process a direct voice command
  - Example: `voice command: open calculator`
  - Example: `voice command: show photos from yesterday`

## Installation

To install the MCP integration:

1. Ensure all files are in the correct locations:
   - `/home/jared/hextrix-ai-os-env/hud/ai/mcp_integration.py`
   - `/home/jared/hextrix-ai-os-env/hud/ai/app_mcp_extension.py`
   - `/home/jared/hextrix-ai-os-env/hud/ai/setup_mcp_integration.py`

2. Run the setup script:
   ```bash
   cd /home/jared/hextrix-ai-os-env/hud/ai
   python3 setup_mcp_integration.py
   ```

3. Install the desktop entry:
   ```bash
   cp /home/jared/hextrix-ai-os-env/hud/hextrix-ai-system-control.desktop ~/.local/share/applications/
   ```

## Using the AI Assistant

You can launch the AI Assistant by:

1. Clicking on the "Hextrix AI System Control" icon in your application menu
2. Running the app directly:
   ```bash
   python3 /home/jared/hextrix-ai-os-env/hud/ai/app.py
   ```

Once launched, you can interact with the AI using text or voice commands.

## How It Works

The integration connects the Hextrix AI with the Model Context Protocol (MCP) server, which provides:

1. **Access to HexWin** - The Windows compatibility layer
2. **Access to HexDroid** - The Android compatibility layer
3. **File system operations** - For finding and managing files
4. **Command execution** - For running system commands

When you give a command, the AI:
1. Processes the command to understand your intent
2. Routes the request to the appropriate MCP function
3. Executes the action on your system
4. Returns the results to you

## Troubleshooting

If you encounter any issues:

1. Ensure the MCP server is running:
   ```bash
   cd /home/jared/hextrix-ai-os-env/hextrix-mcp
   ./start_mcp.sh
   ```

2. Check that all necessary services are running:
   - For Windows apps: Ensure Wine/Proton is installed
   - For Android apps: Ensure Anbox/Waydroid/LineageOS is running

3. If commands are not being recognized, try being more specific or using the exact command formats shown in the Supported Commands section.

## Extending

To add more functionality to the system:

1. Edit `/home/jared/hextrix-ai-os-env/hud/ai/mcp_integration.py` to add new integration functions
2. Edit `/home/jared/hextrix-ai-os-env/hud/ai/app_mcp_extension.py` to add new command patterns and handlers
3. Run the setup script again to apply changes:
   ```bash
   python3 /home/jared/hextrix-ai-os-env/hud/ai/setup_mcp_integration.py
   ``` 