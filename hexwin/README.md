# HexWin - Windows Applications for Hextrix OS

HexWin is a comprehensive Windows compatibility layer for Hextrix OS that integrates Wine, Proton, and QEMU to provide the ability to run Windows applications, games, and tools directly within Hextrix OS.

## Features

- **Wine Integration**: Run standard Windows applications (.exe files) directly
- **Proton/DXVK/VKD3D Support**: Play DirectX games with excellent performance and compatibility
- **QEMU/WinApps**: For applications incompatible with Wine, run them in a seamless Windows VM
- **System-wide Wine Prefix**: Centralized Windows environment with shared components
- **App Drawer Integration**: Windows applications appear in the Hextrix OS app menu
- **Smart Compatibility Detection**: Automatically uses the best compatibility layer for each application
- **MCP API Support**: Control Windows applications via the Hextrix OS MCP connector

## Installation

To install HexWin, run the installer script:

```bash
cd /home/jared/hextrix-ai-os-env/hexwin
chmod +x install.sh
./install.sh
```

This script will:
1. Install all necessary dependencies (Wine, Winetricks, QEMU, Vulkan drivers, etc.)
2. Set up a system-wide Wine prefix with common Windows dependencies
3. Download and configure Proton-GE for gaming
4. Set up WinApps for applications that need a full Windows environment
5. Create helper scripts and desktop integration

## Usage

### Using the GUI

To open the HexWin GUI:

1. Click on the HexWin icon in the Hextrix OS app drawer
2. Use the GUI to install, run, and manage Windows applications

### Using Helper Scripts

HexWin provides several helper scripts:

- **Run a Windows application**:
  ```bash
  ~/.hexwin/hexwin-run.sh /path/to/application.exe
  ```

- **Install a Windows application**:
  ```bash
  ~/.hexwin/hexwin-install.sh -n "Application Name" -c "Category" /path/to/installer.exe
  ```

- **Set up a Windows VM for incompatible applications**:
  ```bash
  ~/.hexwin/hexwin-setup-vm.sh
  ```

### Using the MCP API

HexWin can also be controlled via the Hextrix OS MCP API:

```python
from hextrix_mcp import HextrixMCPClient

client = HextrixMCPClient()

# Open the HexWin manager
client.open_hexwin()

# Run a Windows application
client.run_windows_app("/path/to/application.exe")

# Install a Windows application
client.install_windows_app(
    installer_path="/path/to/installer.exe",
    app_name="Application Name",
    category="Game"
)

# List installed Windows applications
windows_apps = client.list_windows_apps()
for app in windows_apps:
    print(f"{app['name']} ({app['type']})")
```

## Wine Configuration

HexWin uses a system-wide Wine prefix located at `~/.hexwin/wineprefix`.

To configure Wine settings:
1. Open HexWin manager
2. Go to the "Configuration" tab
3. Click "Open Wine Configuration"

You can also use Winetricks to install additional Windows components from the Configuration tab.

## Game Support

HexWin uses Proton (from Steam) for enhanced DirectX gaming support:

- DirectX 9/10/11/12 games are supported via DXVK
- DirectX 12 games are supported via VKD3D
- Vulkan games run at near-native performance

Games that are not compatible with Wine/Proton can be run in the Windows VM using QEMU.

## Technical Details

HexWin consists of several components:

1. **Installation Script**: Sets up the environment and dependencies
2. **Wine Prefix**: Contains the Windows C: drive and registry
3. **Proton-GE**: Custom Proton version optimized for gaming
4. **WinApps**: QEMU integration for incompatible applications
5. **Helper Scripts**: Simplify common tasks
6. **GUI Application**: Provides a user-friendly interface
7. **MCP API**: Allows programmatic control

## QEMU VM Setup

For applications incompatible with Wine, HexWin uses a Windows VM:

1. Click "Setup Windows VM" in the Configuration tab
2. Follow the guided setup process (requires a Windows ISO and license key)
3. Install applications in the VM
4. WinApps will make them appear in the Hextrix OS app drawer

## Troubleshooting

Common issues and solutions:

- **Application crashes on startup**: Try running it with a different Windows version in wine configuration
- **DirectX game fails to launch**: Make sure Vulkan drivers are properly installed
- **Slow performance in the VM**: Adjust VM resources in virt-manager

## License

HexWin integrates several open-source projects, each with their own licenses:

- Wine: LGPL
- Proton: Mix of licenses (primarily Valve's Steam license)
- DXVK: zlib/libpng license
- VKD3D: LGPL
- WinApps: GPL
- QEMU: GPL 