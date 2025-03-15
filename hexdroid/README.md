# HexDroid - Android Compatibility Layer for Hextrix OS

HexDroid is a powerful Android compatibility layer for Hextrix OS that enables running Android applications directly on your Linux-based Hextrix OS system. HexDroid combines multiple Android runtime technologies to provide a seamless experience for running Android applications.

## Features

- **Dual Runtime Support**: Uses both Anbox and Waydroid as Android runtime engines
- **Smart APK Installation**: Automatically detects and installs APK files to the appropriate runtime
- **Desktop Integration**: Android apps appear in your application menu with proper icons
- **Centralized Management**: Manage all your Android applications from a single interface
- **ADB Access**: Full ADB shell access to Android environments
- **Runtime Switching**: Switch between Anbox and Waydroid based on application requirements

## Components

HexDroid consists of the following main components:

1. **Installation Script**: Sets up all required dependencies and configures Android runtime environments
2. **GUI Application Manager**: Modern GTK-based interface for managing Android applications
3. **Helper Scripts**: Command-line utilities for app installation, uninstallation, and management
4. **Runtime Integration**: Seamless integration with both Anbox and Waydroid

## Prerequisites

- Hextrix OS (Ubuntu-based version 0.5.0 or later)
- Administrator (sudo) privileges for installation
- Internet connection for downloading Android images
- At least 2GB of free storage space

## Installation

To install HexDroid, run the provided installation script:

```bash
cd /home/jared/hextrix-ai-os-env/hexdroid
./install.sh
```

The installation script will:

1. Install all required dependencies (Anbox, Waydroid, ADB, etc.)
2. Set up kernel modules required by Android runtimes
3. Download and configure Android system images
4. Create desktop integration and helper scripts
5. Add HexDroid to your application menu

## Using HexDroid

### Graphical Interface

The easiest way to use HexDroid is through its graphical interface. Launch it from your applications menu or run:

```bash
python3 /home/jared/hextrix-ai-os-env/hud/hextrix-hexdroid.py
```

The interface allows you to:
- Install new APK files
- Launch installed Android applications
- Uninstall applications you no longer need
- Switch between Anbox and Waydroid runtimes
- Access advanced options like ADB shell and package manager

### Command Line Tools

HexDroid also provides the following command-line tools:

#### Installing APK Files

```bash
~/.hexdroid/hexdroid-install.sh [OPTIONS] <app.apk>
```

Options:
- `-n, --name NAME`: Application name (optional, extracted from APK if not provided)
- `-i, --icon PATH`: Path to icon file (optional, extracted from APK if not provided)
- `-r, --runtime RUNTIME`: Runtime to use: anbox or waydroid (default: anbox)

#### Uninstalling Applications

```bash
~/.hexdroid/hexdroid-uninstall.sh <app-id>
```

To list all installed apps and their IDs:
```bash
~/.hexdroid/hexdroid-uninstall.sh --list
```

#### Listing Installed Applications

```bash
~/.hexdroid/hexdroid-list.sh
```

#### Connecting to Anbox ADB

```bash
~/.hexdroid/connect-anbox.sh
```

## Runtime Features

### Anbox

Anbox (Android in a Box) runs Android applications in containment, allowing them to integrate with the Linux system while maintaining isolation. Anbox features:

- Container-based isolation
- Direct integration with Linux graphics stack
- Shared clipboard with host system
- Networking capabilities
- Access to removable storage

### Waydroid

Waydroid is a container-based approach to boot a complete Android system on Linux. Waydroid features:

- Full Android system compatibility
- Better performance for graphics-intensive applications
- Support for Android hardware acceleration
- Native Wayland integration
- Full system services support

## Troubleshooting

### Common Issues

1. **Android apps don't launch**
   - Check if the runtime is running with `systemctl --user status anbox` or `waydroid status`
   - Restart the runtime using the HexDroid GUI or run `systemctl --user restart anbox.service`

2. **APK installation fails**
   - Ensure the APK is compatible with the Android version provided by the runtime
   - Try using the other runtime (Anbox or Waydroid)
   - Check ADB connectivity with `adb devices`

3. **Performance issues**
   - Close unused Android applications
   - Try switching to Waydroid for better hardware acceleration
   - Ensure your system has sufficient resources (RAM and CPU)

### Logs and Debugging

- Anbox logs: `journalctl --user -u anbox`
- Waydroid logs: `waydroid log`
- Installation logs: Check terminal output during installation

## Technical Details

- Android versions:
  - Anbox: Android 7.1 (Nougat)
  - Waydroid: Android 10
- File locations:
  - Configuration: `~/.hexdroid/`
  - App data: `~/.hexdroid/appdata/`
  - Icons: `~/.hexdroid/icons/`
  - Runtime data: `~/.hexdroid/anbox-data/` and `~/.hexdroid/waydroid-data/`

## Limitations

- Not all Android apps are compatible, especially those requiring specific Google services
- Some hardware features may not be available or fully functional
- Performance may vary depending on your hardware specifications
- DRM-protected content may not work properly

## Contributing

Contributions to HexDroid are welcome! Please feel free to submit issues or pull requests to the Hextrix OS repository.

## License

HexDroid is part of Hextrix OS and is distributed under the same license terms.

## Acknowledgments

HexDroid builds upon the following open-source projects:
- [Anbox](https://anbox.io/)
- [Waydroid](https://waydro.id/)
- Android Open Source Project
- Various Linux container technologies 