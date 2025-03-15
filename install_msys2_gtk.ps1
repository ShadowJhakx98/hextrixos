# PowerShell script to install MSYS2 and GTK libraries for Windows
# This is the most reliable way to get GTK working on Windows

# Define variables
$MSYS2_INSTALLER_URL = "https://github.com/msys2/msys2-installer/releases/download/2023-07-18/msys2-x86_64-20230718.exe"
$MSYS2_INSTALLER = "$env:TEMP\msys2-installer.exe"
$MSYS2_DIR = "C:\msys64"

Write-Host "Hextrix AI OS - MSYS2 GTK Installation Helper" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Check if MSYS2 is already installed
if (Test-Path $MSYS2_DIR) {
    Write-Host "MSYS2 is already installed at $MSYS2_DIR" -ForegroundColor Green
    $reinstall = Read-Host "Do you want to reinstall the GTK libraries anyway? (y/n)"
    if ($reinstall -ne "y") {
        Write-Host "Skipping MSYS2 installation. Make sure your PATH includes $MSYS2_DIR\mingw64\bin"
        exit 0
    }
} else {
    # Download MSYS2 installer
    Write-Host "Downloading MSYS2 installer..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Uri $MSYS2_INSTALLER_URL -OutFile $MSYS2_INSTALLER
    } catch {
        Write-Host "Failed to download MSYS2 installer: $_" -ForegroundColor Red
        Write-Host "Please download and install MSYS2 manually from https://www.msys2.org/"
        exit 1
    }

    # Install MSYS2
    Write-Host "Installing MSYS2..." -ForegroundColor Yellow
    Write-Host "Please follow the installer prompts. Use the default installation path if possible." -ForegroundColor Yellow
    Start-Process -FilePath $MSYS2_INSTALLER -ArgumentList "/S" -Wait
    Remove-Item $MSYS2_INSTALLER

    if (-not (Test-Path $MSYS2_DIR)) {
        Write-Host "MSYS2 installation failed or was installed to a different location." -ForegroundColor Red
        Write-Host "Please install MSYS2 manually from https://www.msys2.org/"
        exit 1
    }

    Write-Host "MSYS2 installed successfully." -ForegroundColor Green
    
    # Initial MSYS2 setup
    Write-Host "Performing initial MSYS2 setup..." -ForegroundColor Yellow
    Start-Process -FilePath "$MSYS2_DIR\mingw64.exe" -ArgumentList "pacman -Syu --noconfirm" -Wait
}

# Install GTK3 libraries
Write-Host "Installing GTK3 and required libraries..." -ForegroundColor Yellow
$commands = @(
    "pacman -S --noconfirm mingw-w64-x86_64-gtk3",
    "pacman -S --noconfirm mingw-w64-x86_64-python-gobject",
    "pacman -S --noconfirm mingw-w64-x86_64-gdk-pixbuf2",
    "pacman -S --noconfirm mingw-w64-x86_64-librsvg",
    "pacman -S --noconfirm mingw-w64-x86_64-adwaita-icon-theme",
    "pacman -S --noconfirm mingw-w64-x86_64-cairo",
    "pacman -S --noconfirm mingw-w64-x86_64-pango"
)

foreach ($cmd in $commands) {
    Write-Host "Running: $cmd" -ForegroundColor Yellow
    Start-Process -FilePath "$MSYS2_DIR\mingw64.exe" -ArgumentList $cmd -Wait
}

# Add MSYS2 to PATH if not already there
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
if ($currentPath -notlike "*$MSYS2_DIR\mingw64\bin*") {
    Write-Host "Adding MSYS2 to system PATH..." -ForegroundColor Yellow
    try {
        [Environment]::SetEnvironmentVariable(
            "PATH", 
            "$MSYS2_DIR\mingw64\bin;$currentPath", 
            "Machine"
        )
        Write-Host "MSYS2 path added successfully. You may need to restart your computer for changes to take effect." -ForegroundColor Green
    } catch {
        Write-Host "Failed to add MSYS2 to PATH automatically. Please add it manually:" -ForegroundColor Red
        Write-Host "   $MSYS2_DIR\mingw64\bin" -ForegroundColor Yellow
    }
} else {
    Write-Host "MSYS2 is already in your system PATH." -ForegroundColor Green
}

Write-Host "`nInstallation complete!" -ForegroundColor Green
Write-Host "You should now be able to run Hextrix AI OS with GTK support."
Write-Host "Run ./run_hextrix.ps1 to start the application." 