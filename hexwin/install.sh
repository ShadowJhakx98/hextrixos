#!/bin/bash

# HexWin - Windows Applications and Gaming for Hextrix OS
# Installation script for Wine, Proton, DXVK, VKD3D, and WinApps (QEMU) integration

echo "========================================"
echo "HexWin Installation for Hextrix OS"
echo "Enabling Windows applications and DirectX gaming on Linux"
echo "========================================"

# Create necessary directories
HEXWIN_DIR="$HOME/.hexwin"
WINE_PREFIX="$HEXWIN_DIR/wineprefix"
PROTON_DIR="$HEXWIN_DIR/proton"
WINAPPS_DIR="$HEXWIN_DIR/winapps"
APP_ICONS_DIR="$HEXWIN_DIR/icons"
SHORTCUTS_DIR="$HOME/.local/share/applications"

echo "Creating HexWin directories..."
mkdir -p "$HEXWIN_DIR"
mkdir -p "$WINE_PREFIX"
mkdir -p "$PROTON_DIR"
mkdir -p "$WINAPPS_DIR"
mkdir -p "$APP_ICONS_DIR"
mkdir -p "$SHORTCUTS_DIR"

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
    sudo apt-get install -y wine winetricks qemu qemu-kvm libvirt-daemon libvirt-clients bridge-utils virt-manager \
      vulkan-tools vulkan-validationlayers mesa-vulkan-drivers libvulkan1 wine64 wine32 \
      cabextract freetype-tools zenity curl steam git python3-pip
  elif command_exists dnf; then
    # For Fedora/RHEL-based systems
    sudo dnf install -y wine winetricks qemu qemu-kvm libvirt virt-manager virt-viewer \
      vulkan-tools vulkan-loader vulkan-validation-layers mesa-vulkan-drivers wine wine-core wine-fonts \
      cabextract freetype-tools zenity curl steam git python3-pip
  elif command_exists pacman; then
    # For Arch-based systems
    sudo pacman -S --noconfirm wine winetricks qemu libvirt virt-manager \
      vulkan-icd-loader vulkan-tools vulkan-validation-layers wine wine-mono wine-gecko \
      cabextract zenity curl steam git python3-pip
  else
    echo "Unsupported distribution. Please install the required packages manually."
    echo "Required packages: wine, winetricks, qemu, vulkan drivers, steam"
    exit 1
  fi
}

# Install required packages
install_packages

# Configure system-wide Wine prefix
echo "Configuring system-wide Wine prefix..."
export WINEPREFIX="$WINE_PREFIX"
export WINEARCH="win64"

# Initialize Wine prefix
wine wineboot --init

# Install common Windows dependencies
echo "Installing common Windows dependencies via Winetricks..."
winetricks -q corefonts vcrun2019 dotnet48 d3dx9 dxvk vkd3d

# Download and setup Proton
echo "Setting up Proton..."
if [ ! -d "$PROTON_DIR/Proton-GE" ]; then
  # Create a temporary directory
  TMP_DIR=$(mktemp -d)
  cd "$TMP_DIR"
  
  # Get the latest Proton-GE release
  echo "Downloading latest Proton-GE..."
  LATEST_PROTON_URL=$(curl -s https://api.github.com/repos/GloriousEggroll/proton-ge-custom/releases/latest | grep "browser_download_url.*tar.gz" | cut -d '"' -f 4)
  PROTON_FILENAME=$(basename "$LATEST_PROTON_URL")
  
  curl -L -o "$PROTON_FILENAME" "$LATEST_PROTON_URL"
  
  # Extract to Proton directory
  mkdir -p "$PROTON_DIR/Proton-GE"
  tar -xzf "$PROTON_FILENAME" -C "$PROTON_DIR/Proton-GE" --strip-components=1
  
  # Clean up
  cd - > /dev/null
  rm -rf "$TMP_DIR"
else
  echo "Proton-GE already installed."
fi

# Set up WinApps (for applications not compatible with Wine)
echo "Setting up WinApps for QEMU-based Windows applications..."
if [ ! -d "$WINAPPS_DIR/winapps" ]; then
  cd "$WINAPPS_DIR"
  git clone https://github.com/Fmstrat/winapps.git
  cd winapps
  
  # Create a default configuration
  cp -n installer/config.template ~/.config/winapps/winapps.conf
  
  # Download RDP icon
  if [ ! -f "$APP_ICONS_DIR/rdp.svg" ]; then
    curl -o "$APP_ICONS_DIR/rdp.svg" "https://raw.githubusercontent.com/Fmstrat/winapps/main/icons/rdp.svg"
  fi
  
  # Note for the user about WinApps configuration
  echo "NOTE: WinApps requires a Windows VM to be set up. Please follow the WinApps documentation to configure it."
  echo "WinApps configuration file: ~/.config/winapps/winapps.conf"
else
  echo "WinApps already installed."
fi

# Create HexWin helper scripts
echo "Creating HexWin helper scripts..."

# Create helper script to run Windows .exe files with Wine
cat > "$HEXWIN_DIR/hexwin-run.sh" << 'EOF'
#!/bin/bash

HEXWIN_DIR="$HOME/.hexwin"
WINE_PREFIX="$HEXWIN_DIR/wineprefix"
PROTON_DIR="$HEXWIN_DIR/proton/Proton-GE"

# Set wine prefix
export WINEPREFIX="$WINE_PREFIX"

# Function to detect if an app needs DirectX
needs_directx() {
  local exe_file="$1"
  # Simple detection: check for DirectX DLL dependencies
  objdump -p "$exe_file" 2>/dev/null | grep -i "d3d" > /dev/null
  return $?
}

# Function to run with Proton
run_with_proton() {
  local exe_file="$1"
  echo "Running with Proton for better DirectX compatibility..."
  
  # Set up Proton environment
  export STEAM_COMPAT_DATA_PATH="$HEXWIN_DIR/proton_data"
  mkdir -p "$STEAM_COMPAT_DATA_PATH"
  
  # Run with Proton
  "$PROTON_DIR/proton" run "$exe_file"
}

# Main script
EXE_FILE="$1"

if [ ! -f "$EXE_FILE" ]; then
  echo "Error: '$EXE_FILE' does not exist or is not a file."
  exit 1
fi

# Check if the file is a Windows executable
file "$EXE_FILE" | grep -i "PE32" > /dev/null
if [ $? -ne 0 ]; then
  echo "Error: '$EXE_FILE' is not a Windows executable."
  exit 1
fi

# If the executable needs DirectX, use Proton, otherwise use Wine
if needs_directx "$EXE_FILE"; then
  run_with_proton "$EXE_FILE"
else
  echo "Running with Wine..."
  wine "$EXE_FILE"
fi
EOF

# Create script to install new Windows applications
cat > "$HEXWIN_DIR/hexwin-install.sh" << 'EOF'
#!/bin/bash

HEXWIN_DIR="$HOME/.hexwin"
WINE_PREFIX="$HEXWIN_DIR/wineprefix"
APP_ICONS_DIR="$HEXWIN_DIR/icons"
SHORTCUTS_DIR="$HOME/.local/share/applications"

# Set wine prefix
export WINEPREFIX="$WINE_PREFIX"

# Usage info
usage() {
  echo "Usage: $0 [OPTIONS] <installer.exe>"
  echo "Install a Windows application and create a desktop shortcut"
  echo ""
  echo "Options:"
  echo "  -n, --name NAME       Application name (required)"
  echo "  -i, --icon PATH       Path to icon file (optional)"
  echo "  -c, --category CAT    Application category (optional)"
  echo "  -h, --help            Display this help message"
  exit 1
}

# Parse arguments
INSTALLER=""
APP_NAME=""
ICON_PATH=""
CATEGORY="Windows"

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
    -c|--category)
      CATEGORY="$2"
      shift 2
      ;;
    -h|--help)
      usage
      ;;
    *)
      INSTALLER="$1"
      shift
      ;;
  esac
done

# Validate input
if [ -z "$INSTALLER" ] || [ -z "$APP_NAME" ]; then
  echo "Error: Installer path and application name are required."
  usage
fi

if [ ! -f "$INSTALLER" ]; then
  echo "Error: Installer file '$INSTALLER' does not exist."
  exit 1
fi

# Create safe name for application
SAFE_NAME=$(echo "$APP_NAME" | tr ' ' '_' | tr -cd '[:alnum:]_-')
INSTALL_DIR="$WINE_PREFIX/drive_c/Program Files/$SAFE_NAME"

echo "Installing $APP_NAME..."
echo "This may take a while. Please follow the installation prompts."

# Run the installer
wine "$INSTALLER"

# Ask user for the path to the main executable
echo ""
echo "Please enter the path to the main executable (relative to C:\\):"
read -e APP_PATH

# Full path to the executable
EXE_PATH="$WINE_PREFIX/drive_c/$APP_PATH"

if [ ! -f "$EXE_PATH" ]; then
  echo "Error: Executable file '$EXE_PATH' does not exist."
  exit 1
fi

# Process icon
ICON_DEST="$APP_ICONS_DIR/$SAFE_NAME.png"

if [ -n "$ICON_PATH" ] && [ -f "$ICON_PATH" ]; then
  cp "$ICON_PATH" "$ICON_DEST"
else
  # Extract icon from the executable
  wrestool -x -t 14 "$EXE_PATH" | convert -resize 128x128 ico:- "$ICON_DEST"
fi

# Create .desktop file
DESKTOP_FILE="$SHORTCUTS_DIR/hexwin-$SAFE_NAME.desktop"

cat > "$DESKTOP_FILE" << EOL
[Desktop Entry]
Name=$APP_NAME
Exec=$HEXWIN_DIR/hexwin-run.sh "$EXE_PATH"
Type=Application
Icon=$ICON_DEST
Categories=$CATEGORY;
Comment=Windows application running via HexWin
EOL

chmod +x "$DESKTOP_FILE"

echo "Installation complete! $APP_NAME has been added to your application menu."
EOF

# Create script to set up QEMU/WinApps for incompatible applications
cat > "$HEXWIN_DIR/hexwin-setup-vm.sh" << 'EOF'
#!/bin/bash

HEXWIN_DIR="$HOME/.hexwin"
WINAPPS_DIR="$HEXWIN_DIR/winapps"

cd "$WINAPPS_DIR/winapps"

echo "This utility will help you set up a Windows VM for applications that don't work with Wine."
echo "You'll need a Windows 10/11 ISO and a valid license key."
echo ""
echo "Please follow the interactive setup process:"

./installer/install.sh
EOF

# Make all scripts executable
chmod +x "$HEXWIN_DIR/hexwin-run.sh"
chmod +x "$HEXWIN_DIR/hexwin-install.sh"
chmod +x "$HEXWIN_DIR/hexwin-setup-vm.sh"

# Create integration with Hextrix OS app drawer
echo "Creating integration with Hextrix OS..."

# Add to path
echo 'export PATH="$PATH:$HOME/.hexwin"' >> "$HOME/.bashrc"

echo "========================================"
echo "HexWin installation completed!"
echo "========================================"
echo ""
echo "You can now use the following commands:"
echo "  hexwin-run.sh <exe_file>        - Run a Windows executable"
echo "  hexwin-install.sh -n 'App Name' installer.exe - Install a Windows application"
echo "  hexwin-setup-vm.sh              - Set up a Windows VM for incompatible applications"
echo ""
echo "Windows applications will appear in your app drawer automatically."
echo "The system-wide Wine prefix is located at: $WINE_PREFIX"
echo "========================================" 