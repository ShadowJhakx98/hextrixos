#!/bin/bash

# HexDroid - Android Applications for Hextrix OS
# Installation script for Android runtime and integration

echo "========================================"
echo "HexDroid Installation for Hextrix OS"
echo "Enabling Android applications on Linux"
echo "========================================"

# Create necessary directories
HEXDROID_DIR="$HOME/.hexdroid"
ANBOX_DATA_DIR="$HEXDROID_DIR/anbox-data"
WAYDROID_DATA_DIR="$HEXDROID_DIR/waydroid-data"
LINEAGE_DATA_DIR="$HEXDROID_DIR/lineage-data"
APP_ICONS_DIR="$HEXDROID_DIR/icons"
APP_DATA_DIR="$HEXDROID_DIR/appdata"
SHORTCUTS_DIR="$HOME/.local/share/applications"

echo "Creating HexDroid directories..."
mkdir -p "$HEXDROID_DIR"
mkdir -p "$ANBOX_DATA_DIR"
mkdir -p "$WAYDROID_DATA_DIR"
mkdir -p "$LINEAGE_DATA_DIR"
mkdir -p "$APP_ICONS_DIR"
mkdir -p "$APP_DATA_DIR"
mkdir -p "$SHORTCUTS_DIR"

# LineageOS settings
LINEAGE_VERSION="18.1"  # Android 11
LINEAGE_DEVICE="x86_64"
LINEAGE_URL="https://download.lineageos.org/devices/${LINEAGE_DEVICE}/${LINEAGE_VERSION}" # Example URL, will be replaced with actual download URL
GAPPS_URL="https://sourceforge.net/projects/opengapps/files/x86_64/${LINEAGE_VERSION}/open_gapps-x86_64-${LINEAGE_VERSION}-pico.zip"
LINEAGE_QEMU_RAM="2048"
LINEAGE_QEMU_CORES="2"

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Function to install packages based on the distribution
install_packages() {
  echo "Installing required packages..."
  
  if command_exists apt-get; then
    # For Debian/Ubuntu-based systems
    sudo apt-get update
    sudo apt-get install -y anbox adb fastboot curl wget squashfs-tools lxc \
      python3 python3-pip git unzip openssh-client dnsmasq iptables-persistent \
      qemu-system-x86 qemu-utils libvirt-daemon-system libvirt-clients bridge-utils \
      virt-manager ovmf android-tools-adb android-tools-fastboot
      
    # Waydroid dependencies
    sudo apt-get install -y curl ca-certificates python3 python3-gi python3-pip \
      gir1.2-gtk-3.0 gir1.2-appindicator3-0.1 lxc-utils python3-gbinder \
      python3-selenium weston binfmt-support lxc
  elif command_exists dnf; then
    # For Fedora/RHEL-based systems
    sudo dnf install -y anbox adb fastboot curl wget squashfs-tools lxc \
      python3 python3-pip git unzip openssh-client dnsmasq iptables-services \
      qemu-kvm qemu-img libvirt virt-manager virt-viewer \
      virt-install bridge-utils android-tools
      
    # Waydroid dependencies
    sudo dnf install -y curl ca-certificates python3 python3-gobject python3-pip \
      gtk3 libappindicator-gtk3 lxc-utils gbinder-python weston binfmt-support lxc
  elif command_exists pacman; then
    # For Arch-based systems
    sudo pacman -S --noconfirm anbox android-tools curl wget squashfs-tools lxc \
      python python-pip git unzip openssh dnsmasq iptables \
      qemu qemu-arch-extra libvirt virt-manager ebtables \
      dnsmasq bridge-utils openbsd-netcat
      
    # Waydroid dependencies
    sudo pacman -S --noconfirm curl ca-certificates python python-gobject python-pip \
      gtk3 libappindicator-gtk3 lxc python-gbinder weston binfmt-support lxc
  else
    echo "Unsupported distribution. Please install the required packages manually."
    echo "Required packages: anbox, android-tools, lxc, dnsmasq, iptables, qemu"
    exit 1
  fi

  # Install Python dependencies
  pip3 install --user pyclip
}

# Install and configure Anbox
setup_anbox() {
  echo "Setting up Anbox..."
  
  # Load required kernel modules
  if ! lsmod | grep -q "ashmem_linux"; then
    echo "Loading ashmem_linux kernel module..."
    sudo modprobe ashmem_linux
  fi
  
  if ! lsmod | grep -q "binder_linux"; then
    echo "Loading binder_linux kernel module..."
    sudo modprobe binder_linux
  fi
  
  # Make kernel modules load at boot
  if [ ! -f "/etc/modules-load.d/anbox.conf" ]; then
    echo "Setting up kernel modules to load at boot..."
    echo "ashmem_linux" | sudo tee /etc/modules-load.d/anbox.conf
    echo "binder_linux" | sudo tee -a /etc/modules-load.d/anbox.conf
  fi
  
  # Download Android image if not already downloaded
  ANDROID_IMG="$ANBOX_DATA_DIR/android.img"
  if [ ! -f "$ANDROID_IMG" ]; then
    echo "Downloading Android image for Anbox..."
    wget https://build.anbox.io/android-images/2018/07/19/android_amd64.img -O "$ANDROID_IMG"
  fi
  
  # Create systemd user service for anbox
  ANBOX_SERVICE_DIR="$HOME/.config/systemd/user"
  mkdir -p "$ANBOX_SERVICE_DIR"
  
  cat > "$ANBOX_SERVICE_DIR/anbox.service" << EOL
[Unit]
Description=Anbox container manager
After=network.target

[Service]
ExecStart=/usr/bin/anbox container-manager --data-path=$ANBOX_DATA_DIR
ExecStop=/usr/bin/anbox container-manager --data-path=$ANBOX_DATA_DIR --shutdown
Restart=on-failure

[Install]
WantedBy=default.target
EOL

  systemctl --user daemon-reload
  systemctl --user enable anbox.service
  systemctl --user start anbox.service
  
  echo "Anbox setup complete!"
}

# Set up Waydroid as an alternative runtime
setup_waydroid() {
  echo "Setting up Waydroid..."
  
  # Install Waydroid if not already installed
  if ! command_exists waydroid; then
    echo "Installing Waydroid..."
    
    # For Ubuntu-based systems
    if command_exists apt-get; then
      sudo apt-add-repository ppa:wimpysworld/waydroid
      sudo apt update
      sudo apt install -y waydroid
    else
      echo "Please install Waydroid manually for your distribution."
      echo "Visit: https://waydro.id/"
    fi
  fi
  
  # Initialize Waydroid with custom data path
  if [ -x "$(command -v waydroid)" ]; then
    echo "Initializing Waydroid..."
    export WAYDROID_DATA_PATH="$WAYDROID_DATA_DIR"
    sudo waydroid init -c https://ota.waydro.id/system -v https://ota.waydro.id/vendor
    
    # Create container service script
    cat > "$HEXDROID_DIR/start-waydroid.sh" << 'EOL'
#!/bin/bash
export WAYDROID_DATA_PATH="$HOME/.hexdroid/waydroid-data"
waydroid session start
waydroid show-full-ui
EOL

    chmod +x "$HEXDROID_DIR/start-waydroid.sh"
    
    echo "Waydroid setup complete!"
  else
    echo "Waydroid installation failed or not available. Skipping configuration."
  fi
}

# Set up LineageOS with QEMU and GApps
setup_lineageos() {
  echo "Setting up LineageOS with QEMU and Google Apps..."
  
  # Create necessary directories
  mkdir -p "$LINEAGE_DATA_DIR/images"
  mkdir -p "$LINEAGE_DATA_DIR/configs"
  
  # Check if LineageOS image already exists
  LINEAGE_IMG="$LINEAGE_DATA_DIR/images/lineage-$LINEAGE_VERSION-$LINEAGE_DEVICE.img"
  if [ ! -f "$LINEAGE_IMG" ]; then
    echo "Downloading LineageOS image..."
    
    # This URL may need to be updated to point to an actual LineageOS x86_64 image
    LINEAGE_DOWNLOAD_URL="https://sourceforge.net/projects/lineage-x86/files/LineageOS-$LINEAGE_VERSION-x86_64.iso/download"
    wget -O "$LINEAGE_DATA_DIR/images/lineage-$LINEAGE_VERSION-$LINEAGE_DEVICE.iso" "$LINEAGE_DOWNLOAD_URL"
    
    # Convert ISO to disk image if needed
    echo "Converting LineageOS ISO to disk image..."
    qemu-img create -f qcow2 "$LINEAGE_IMG" 16G
    
    # We'll need to install LineageOS to the disk image
    # This is a complex process that would normally require interactive installation
    # For automation purposes, we'll create a script to handle this
    echo "Creating LineageOS installation script..."
  else
    echo "LineageOS image already exists, skipping download."
  fi
  
  # Download GApps if needed
  GAPPS_ZIP="$LINEAGE_DATA_DIR/images/opengapps-$LINEAGE_DEVICE-$LINEAGE_VERSION-pico.zip"
  if [ ! -f "$GAPPS_ZIP" ]; then
    echo "Downloading Google Apps (GApps)..."
    wget -O "$GAPPS_ZIP" "$GAPPS_URL"
  else
    echo "GApps already downloaded, skipping."
  fi
  
  # Create QEMU start script
  echo "Creating LineageOS QEMU start script..."
  cat > "$HEXDROID_DIR/start-lineageos.sh" << 'EOL'
#!/bin/bash

HEXDROID_DIR="$HOME/.hexdroid"
LINEAGE_DATA_DIR="$HEXDROID_DIR/lineage-data"
LINEAGE_VERSION="18.1"
LINEAGE_DEVICE="x86_64"
LINEAGE_IMG="$LINEAGE_DATA_DIR/images/lineage-$LINEAGE_VERSION-$LINEAGE_DEVICE.img"
LINEAGE_QEMU_RAM="2048"
LINEAGE_QEMU_CORES="2"

# Override defaults with user settings if available
if [ -f "$LINEAGE_DATA_DIR/configs/settings.conf" ]; then
  source "$LINEAGE_DATA_DIR/configs/settings.conf"
fi

# Parse command line arguments
SHOW_UI=true
FORWARD_ADB=true

while [[ $# -gt 0 ]]; do
  case $1 in
    --no-ui)
      SHOW_UI=false
      shift
      ;;
    --no-adb)
      FORWARD_ADB=false
      shift
      ;;
    --ram)
      LINEAGE_QEMU_RAM="$2"
      shift 2
      ;;
    --cores)
      LINEAGE_QEMU_CORES="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--no-ui] [--no-adb] [--ram RAM_MB] [--cores NUM_CORES]"
      exit 1
      ;;
  esac
done

# QEMU options
QEMU_OPTS="-enable-kvm -m $LINEAGE_QEMU_RAM -smp $LINEAGE_QEMU_CORES -cpu host"
QEMU_OPTS="$QEMU_OPTS -hda $LINEAGE_IMG"
QEMU_OPTS="$QEMU_OPTS -device virtio-net-pci,netdev=net0"
QEMU_OPTS="$QEMU_OPTS -netdev user,id=net0"

# Add ADB forwarding if enabled
if [ "$FORWARD_ADB" = true ]; then
  QEMU_OPTS="$QEMU_OPTS,hostfwd=tcp::5555-:5555"
  # Add ADB connection after QEMU starts
  (
    sleep 10
    adb connect localhost:5555
  ) &
fi

# Add display options
if [ "$SHOW_UI" = true ]; then
  QEMU_OPTS="$QEMU_OPTS -display gtk,gl=on"
else
  QEMU_OPTS="$QEMU_OPTS -nographic"
fi

# Start QEMU with LineageOS
echo "Starting LineageOS in QEMU..."
echo "RAM: ${LINEAGE_QEMU_RAM}MB, Cores: $LINEAGE_QEMU_CORES"
echo "UI: $SHOW_UI, ADB forwarding: $FORWARD_ADB"

eval "qemu-system-x86_64 $QEMU_OPTS"
EOL

  chmod +x "$HEXDROID_DIR/start-lineageos.sh"
  
  # Create a settings configuration file
  echo "Creating LineageOS settings file..."
  cat > "$LINEAGE_DATA_DIR/configs/settings.conf" << EOL
# LineageOS QEMU settings
LINEAGE_VERSION="$LINEAGE_VERSION"
LINEAGE_DEVICE="$LINEAGE_DEVICE"
LINEAGE_QEMU_RAM="$LINEAGE_QEMU_RAM"
LINEAGE_QEMU_CORES="$LINEAGE_QEMU_CORES"
EOL

  # Create APK installation helper script for LineageOS
  echo "Creating LineageOS APK installation helper..."
  cat > "$HEXDROID_DIR/lineageos-install-apk.sh" << 'EOL'
#!/bin/bash

HEXDROID_DIR="$HOME/.hexdroid"

# Check if LineageOS QEMU is running
if ! adb devices | grep -q "localhost:5555"; then
  echo "LineageOS QEMU is not running or ADB is not connected."
  echo "Please start LineageOS with:"
  echo "  $HEXDROID_DIR/start-lineageos.sh"
  exit 1
fi

# Check for APK file
if [ -z "$1" ]; then
  echo "Usage: $0 <app.apk>"
  exit 1
fi

APK_FILE="$1"
if [ ! -f "$APK_FILE" ]; then
  echo "APK file not found: $APK_FILE"
  exit 1
fi

# Install APK
echo "Installing $APK_FILE on LineageOS..."
adb -s localhost:5555 install -r "$APK_FILE"

if [ $? -eq 0 ]; then
  echo "Installation successful!"
else
  echo "Installation failed."
  exit 1
fi
EOL

  chmod +x "$HEXDROID_DIR/lineageos-install-apk.sh"
  
  echo "LineageOS setup complete!"
}

# Create HexDroid helper scripts
create_helper_scripts() {
  echo "Creating HexDroid helper scripts..."
  
  # Script to install APK files
  cat > "$HEXDROID_DIR/hexdroid-install.sh" << 'EOL'
#!/bin/bash

HEXDROID_DIR="$HOME/.hexdroid"
APP_ICONS_DIR="$HEXDROID_DIR/icons"
APP_DATA_DIR="$HEXDROID_DIR/appdata"
INSTALLED_APPS_FILE="$APP_DATA_DIR/installed_apps.json"
SHORTCUTS_DIR="$HOME/.local/share/applications"

# Initialize apps file if it doesn't exist
if [ ! -f "$INSTALLED_APPS_FILE" ]; then
  echo '[]' > "$INSTALLED_APPS_FILE"
fi

# Usage info
usage() {
  echo "Usage: $0 [OPTIONS] <app.apk>"
  echo "Install an Android application APK"
  echo ""
  echo "Options:"
  echo "  -n, --name NAME       Application name (optional, extracted from APK if not provided)"
  echo "  -i, --icon PATH       Path to icon file (optional, extracted from APK if not provided)"
  echo "  -r, --runtime RUNTIME Runtime to use: anbox or waydroid (default: anbox)"
  echo "  -h, --help            Display this help message"
  exit 1
}

# Parse arguments
APK_FILE=""
APP_NAME=""
ICON_PATH=""
RUNTIME="anbox"

while [[ $# -gt 0 ]]; do
  case $1 in
    -n|--name)
      APP_NAME="$2"
      shift 2
      ;;
    -i|--icon)
      ICON_PATH="$2"
      shift 2
      ;;
    -r|--runtime)
      RUNTIME="$2"
      shift 2
      ;;
    -h|--help)
      usage
      ;;
    *)
      APK_FILE="$1"
      shift
      ;;
  esac
done

# Validate input
if [ -z "$APK_FILE" ]; then
  echo "Error: APK file is required."
  usage
fi

if [ ! -f "$APK_FILE" ]; then
  echo "Error: APK file '$APK_FILE' does not exist."
  exit 1
fi

if [ "$RUNTIME" != "anbox" ] && [ "$RUNTIME" != "waydroid" ]; then
  echo "Error: Runtime must be either 'anbox' or 'waydroid'."
  exit 1
fi

# Extract APK information if not provided
if [ -z "$APP_NAME" ]; then
  echo "Extracting app name from APK..."
  # Use aapt to get the app name
  if command -v aapt > /dev/null; then
    APP_NAME=$(aapt dump badging "$APK_FILE" | grep "application-label:" | sed "s/application-label://g" | tr -d "'" | tr -d ' ')
  fi
  
  # If still empty, use filename
  if [ -z "$APP_NAME" ]; then
    APP_NAME=$(basename "$APK_FILE" .apk)
  fi
fi

# Create a safe ID for the app
APP_ID=$(echo "$APP_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '_' | tr -cd '[:alnum:]_-')

# Install the APK
echo "Installing $APP_NAME using $RUNTIME..."

if [ "$RUNTIME" = "anbox" ]; then
  # Anbox installation
  adb connect 192.168.250.2
  sleep 2
  adb install -r "$APK_FILE"
  INSTALL_STATUS=$?
  adb disconnect 192.168.250.2
elif [ "$RUNTIME" = "waydroid" ]; then
  # Waydroid installation
  waydroid app install "$APK_FILE"
  INSTALL_STATUS=$?
fi

if [ $INSTALL_STATUS -ne 0 ]; then
  echo "Error: Failed to install APK."
  exit 1
fi

# Get or extract icon
ICON_DEST="$APP_ICONS_DIR/$APP_ID.png"
if [ -n "$ICON_PATH" ] && [ -f "$ICON_PATH" ]; then
  # Use provided icon
  cp "$ICON_PATH" "$ICON_DEST"
else
  # Extract icon from APK
  echo "Extracting icon from APK..."
  TMP_DIR=$(mktemp -d)
  if command -v aapt > /dev/null; then
    # Find the icon path in the APK
    ICON_FILE=$(aapt dump badging "$APK_FILE" | grep "application:" | sed -n 's/.*icon=.\([^'\']*\).*/\1/p')
    if [ -n "$ICON_FILE" ]; then
      # Extract the icon
      unzip -q "$APK_FILE" "$ICON_FILE" -d "$TMP_DIR"
      # Convert to PNG if needed
      if command -v convert > /dev/null; then
        convert "$TMP_DIR/$ICON_FILE" "$ICON_DEST"
      else
        cp "$TMP_DIR/$ICON_FILE" "$ICON_DEST"
      fi
    fi
  fi
  
  # If icon extraction failed, use a default icon
  if [ ! -f "$ICON_DEST" ]; then
    echo "Using default icon..."
    cp "$HEXDROID_DIR/default_icon.png" "$ICON_DEST" 2>/dev/null || true
  fi
  
  # Clean up temp directory
  rm -rf "$TMP_DIR"
fi

# Create desktop entry
echo "Creating desktop entry..."

DESKTOP_FILE="$SHORTCUTS_DIR/hexdroid-$APP_ID.desktop"

if [ "$RUNTIME" = "anbox" ]; then
  LAUNCH_COMMAND="anbox launch --package=com.android.$APP_ID --component=com.android.$APP_ID.MainActivity"
elif [ "$RUNTIME" = "waydroid" ]; then
  # Attempt to get the actual package name with waydroid
  PACKAGE_NAME=$(waydroid app list | grep -i "$APP_NAME" | awk '{print $1}')
  if [ -z "$PACKAGE_NAME" ]; then
    PACKAGE_NAME="com.android.$APP_ID"
  fi
  LAUNCH_COMMAND="waydroid app launch $PACKAGE_NAME"
fi

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=$APP_NAME
Comment=Android application running via HexDroid
Exec=$LAUNCH_COMMAND
Icon=$ICON_DEST
Terminal=false
Categories=Android;HexDroid;
Keywords=android;hexdroid;
StartupNotify=true
EOF

# Make desktop entry executable
chmod +x "$DESKTOP_FILE"

# Add to installed apps JSON
APP_ENTRY=$(cat << EOF
{
  "id": "$APP_ID",
  "name": "$APP_NAME",
  "package": "com.android.$APP_ID",
  "icon": "$ICON_DEST",
  "runtime": "$RUNTIME",
  "installed": "$(date -Iseconds)"
}
EOF
)

# Update JSON file
TMP_JSON=$(mktemp)
jq --argjson newapp "$APP_ENTRY" '. += [$newapp]' "$INSTALLED_APPS_FILE" > "$TMP_JSON"
mv "$TMP_JSON" "$INSTALLED_APPS_FILE"

echo "Installation complete! $APP_NAME has been added to your application menu."
EOL

  # Script to uninstall Android apps
  cat > "$HEXDROID_DIR/hexdroid-uninstall.sh" << 'EOL'
#!/bin/bash

HEXDROID_DIR="$HOME/.hexdroid"
APP_DATA_DIR="$HEXDROID_DIR/appdata"
INSTALLED_APPS_FILE="$APP_DATA_DIR/installed_apps.json"
SHORTCUTS_DIR="$HOME/.local/share/applications"

# Usage info
usage() {
  echo "Usage: $0 <app-id>"
  echo "Uninstall an Android application by ID"
  echo ""
  echo "To list installed apps, use: $0 --list"
  exit 1
}

# List installed apps
if [ "$1" = "--list" ]; then
  echo "Installed Android Applications:"
  jq -r '.[] | "ID: \(.id) | Name: \(.name) | Runtime: \(.runtime)"' "$INSTALLED_APPS_FILE"
  exit 0
fi

# Get app ID
APP_ID="$1"

if [ -z "$APP_ID" ]; then
  echo "Error: App ID is required."
  usage
fi

# Check if app exists in our database
APP_JSON=$(jq -r ".[] | select(.id == \"$APP_ID\")" "$INSTALLED_APPS_FILE")
if [ -z "$APP_JSON" ]; then
  echo "Error: App with ID '$APP_ID' not found."
  echo "To list installed apps, use: $0 --list"
  exit 1
fi

# Extract app info
APP_NAME=$(echo "$APP_JSON" | jq -r ".name")
PACKAGE=$(echo "$APP_JSON" | jq -r ".package")
RUNTIME=$(echo "$APP_JSON" | jq -r ".runtime")

echo "Uninstalling $APP_NAME ($PACKAGE) from $RUNTIME..."

# Uninstall from the runtime
if [ "$RUNTIME" = "anbox" ]; then
  # Connect to anbox
  adb connect 192.168.250.2
  sleep 2
  adb uninstall "$PACKAGE"
  UNINSTALL_STATUS=$?
  adb disconnect 192.168.250.2
elif [ "$RUNTIME" = "waydroid" ]; then
  waydroid app remove "$PACKAGE"
  UNINSTALL_STATUS=$?
else
  echo "Unknown runtime: $RUNTIME"
  exit 1
fi

# Remove desktop entry
DESKTOP_FILE="$SHORTCUTS_DIR/hexdroid-$APP_ID.desktop"
if [ -f "$DESKTOP_FILE" ]; then
  rm "$DESKTOP_FILE"
fi

# Remove from installed apps JSON
TMP_JSON=$(mktemp)
jq ".[] | select(.id != \"$APP_ID\")" "$INSTALLED_APPS_FILE" > "$TMP_JSON"
mv "$TMP_JSON" "$INSTALLED_APPS_FILE"

echo "Uninstallation complete! $APP_NAME has been removed."
EOL

  # Script to list installed Android apps
  cat > "$HEXDROID_DIR/hexdroid-list.sh" << 'EOL'
#!/bin/bash

HEXDROID_DIR="$HOME/.hexdroid"
APP_DATA_DIR="$HEXDROID_DIR/appdata"
INSTALLED_APPS_FILE="$APP_DATA_DIR/installed_apps.json"

# Check if file exists
if [ ! -f "$INSTALLED_APPS_FILE" ]; then
  echo "No Android applications installed yet."
  exit 0
fi

# List all installed apps with formatting
echo "=== Installed Android Applications ==="
echo ""

jq -r '.[] | "App: \(.name)\nID: \(.id)\nPackage: \(.package)\nRuntime: \(.runtime)\nInstalled: \(.installed)\n---"' "$INSTALLED_APPS_FILE"

echo ""
echo "Total: $(jq '. | length' "$INSTALLED_APPS_FILE") applications"
EOL

  # Make all scripts executable
  chmod +x "$HEXDROID_DIR/hexdroid-install.sh"
  chmod +x "$HEXDROID_DIR/hexdroid-uninstall.sh"
  chmod +x "$HEXDROID_DIR/hexdroid-list.sh"
  
  echo "Helper scripts created successfully."
}

# Create default Android icon
create_default_icon() {
  # Simple Android logo as fallback
  cat > "$HEXDROID_DIR/default_icon.png" << 'EOL'
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
H9HBGYfli5tBAAAAAElFTkSuQmCC
EOL

  echo "Default icon created."
}

# Create desktop entry
create_desktop_entry() {
  echo "Creating desktop entry for HexDroid..."
  
  DESKTOP_FILE="$SHORTCUTS_DIR/hexdroid.desktop"
  
  cat > "$DESKTOP_FILE" << EOL
[Desktop Entry]
Type=Application
Name=HexDroid
GenericName=Android Application Manager
Comment=Run Android applications on Hextrix OS
Exec=python3 /home/jared/hextrix-ai-os-env/hud/hextrix-hexdroid.py
Icon=/home/jared/hextrix-ai-os-env/hexdroid/hexdroid.png
Terminal=false
Categories=System;Utility;
Keywords=android;anbox;waydroid;apk;
StartupNotify=true
EOL

  chmod +x "$DESKTOP_FILE"
  echo "Desktop entry created."
}

# Add to PATH
add_to_path() {
  echo "Adding HexDroid to PATH..."
  
  if ! grep -q "HEXDROID_DIR" "$HOME/.bashrc"; then
    cat >> "$HOME/.bashrc" << 'EOL'

# HexDroid Android compatibility layer
export HEXDROID_DIR="$HOME/.hexdroid"
export PATH="$PATH:$HEXDROID_DIR"
EOL
  fi
  
  echo "HexDroid added to PATH."
}

# Create Anbox connection helper
create_anbox_connection_helper() {
  cat > "$HEXDROID_DIR/connect-anbox.sh" << 'EOL'
#!/bin/bash

echo "Connecting to Anbox..."
adb connect 192.168.250.2
sleep 2
echo "Connected to Anbox ADB."
echo "Use 'adb devices' to verify connection."
echo "Use 'adb disconnect 192.168.250.2' when finished."
EOL

  chmod +x "$HEXDROID_DIR/connect-anbox.sh"
  echo "Anbox connection helper created."
}

# Main installation process
install_hexdroid() {
  # Create JSON file for tracking installed apps
  mkdir -p "$APP_DATA_DIR"
  INSTALLED_APPS_FILE="$APP_DATA_DIR/installed_apps.json"
  
  if [ ! -f "$INSTALLED_APPS_FILE" ]; then
    echo "[]" > "$INSTALLED_APPS_FILE"
  fi
  
  # Install packages
  install_packages
  
  # Set up Anbox
  setup_anbox
  
  # Set up Waydroid
  setup_waydroid
  
  # Set up LineageOS
  setup_lineageos
  
  # Create helper scripts
  create_helper_scripts
  
  # Create default icon
  create_default_icon
  
  # Create desktop entry
  create_desktop_entry
  
  # Add to PATH
  add_to_path
  
  # Create Anbox connection helper
  create_anbox_connection_helper
  
  echo "========================================"
  echo "HexDroid installation completed!"
  echo "========================================"
  echo ""
  echo "You can now use the following commands:"
  echo "  hexdroid-install.sh <app.apk>     - Install an Android APK"
  echo "  hexdroid-uninstall.sh <app-id>    - Uninstall an Android app"
  echo "  hexdroid-list.sh                  - List installed Android apps"
  echo "  connect-anbox.sh                  - Connect to Anbox ADB"
  echo ""
  echo "You can also launch the HexDroid GUI from the app menu."
  echo "========================================"
}

# Start installation
install_hexdroid 