# PowerShell script to install dependencies for Hextrix AI OS without conda
# Uses the system Python installation directly

# Enable execution policy for script
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

Write-Host "Hextrix AI OS - Windows System Installation" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found. Please install Python 3.10 or later." -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/downloads/windows/" -ForegroundColor Red
    exit 1
}

# Check if pip is installed
try {
    $pipVersion = pip --version
    Write-Host "Found pip: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "pip not found. Please ensure pip is installed with Python." -ForegroundColor Red
    exit 1
}

# MSYS2 INSTALLATION SECTION - THIS MUST BE DONE FIRST
Write-Host "`nChecking for MSYS2 installation (required for GTK)..." -ForegroundColor Yellow
$msys2Path = "C:\msys64\mingw64\bin"

$needToInstallMSYS2 = $false
if (-not (Test-Path $msys2Path)) {
    Write-Host "MSYS2 not found. GTK will not work properly without it." -ForegroundColor Red
    Write-Host "MSYS2 installation is REQUIRED for PyGObject to work on Windows." -ForegroundColor Red
    $install = Read-Host "Install MSYS2 now? (y/n)"
    
    if ($install -eq "y") {
        $needToInstallMSYS2 = $true
    } else {
        Write-Host "Cannot continue without MSYS2. Installation aborted." -ForegroundColor Red
        exit 1
    }
}

if ($needToInstallMSYS2) {
    # Variables for MSYS2 installation
    $MSYS2_INSTALLER_URL = "https://github.com/msys2/msys2-installer/releases/download/2023-07-18/msys2-x86_64-20230718.exe"
    $MSYS2_INSTALLER = "$env:TEMP\msys2-installer.exe"
    
    # Download MSYS2 installer
    Write-Host "Downloading MSYS2 installer..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Uri $MSYS2_INSTALLER_URL -OutFile $MSYS2_INSTALLER
    } catch {
        Write-Host "Failed to download MSYS2 installer: $_" -ForegroundColor Red
        Write-Host "Please download and install MSYS2 manually from https://www.msys2.org/" -ForegroundColor Yellow
        exit 1
    }
    
    # Install MSYS2
    Write-Host "Installing MSYS2..." -ForegroundColor Yellow
    Start-Process -FilePath $MSYS2_INSTALLER -ArgumentList "/S" -Wait
    Remove-Item $MSYS2_INSTALLER
    
    # Wait a moment for installation to complete
    Start-Sleep -Seconds 5
    
    if (-not (Test-Path "C:\msys64")) {
        Write-Host "MSYS2 installation failed. Please install manually from https://www.msys2.org/" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "MSYS2 installed successfully." -ForegroundColor Green
}

# Install GTK packages through MSYS2
Write-Host "`nInstalling GTK packages through MSYS2..." -ForegroundColor Yellow
$msys2Shell = "C:\msys64\mingw64.exe"

if (-not (Test-Path $msys2Shell)) {
    Write-Host "MSYS2 shell not found at $msys2Shell" -ForegroundColor Red
    Write-Host "Please check your MSYS2 installation." -ForegroundColor Red
    exit 1
}

# First update MSYS2
Write-Host "Updating MSYS2 package database (this might take a while)..." -ForegroundColor Yellow
Start-Process -FilePath $msys2Shell -ArgumentList "pacman -Syu --noconfirm" -Wait

# Install required GTK packages
Write-Host "Installing GTK libraries through MSYS2 (this might take a while)..." -ForegroundColor Yellow
$commands = @(
    "pacman -S --noconfirm mingw-w64-x86_64-gtk3",
    "pacman -S --noconfirm mingw-w64-x86_64-python-gobject",
    "pacman -S --noconfirm mingw-w64-x86_64-gdk-pixbuf2",
    "pacman -S --noconfirm mingw-w64-x86_64-librsvg",
    "pacman -S --noconfirm mingw-w64-x86_64-adwaita-icon-theme"
)

foreach ($cmd in $commands) {
    Write-Host "Running: $cmd" -ForegroundColor Yellow
    Start-Process -FilePath $msys2Shell -ArgumentList $cmd -Wait
}

# Add MSYS2 to PATH for this session
$env:Path = "C:\msys64\mingw64\bin;$env:Path"

# Try to add to permanent PATH (will require admin rights)
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
if ($currentPath -notlike "*C:\msys64\mingw64\bin*") {
    try {
        [Environment]::SetEnvironmentVariable(
            "PATH", 
            "C:\msys64\mingw64\bin;$currentPath", 
            "Machine"
        )
        Write-Host "MSYS2 path added to system PATH successfully." -ForegroundColor Green
    } catch {
        Write-Host "Could not add MSYS2 to system PATH (requires admin rights)." -ForegroundColor Yellow
        Write-Host "Please add it manually, or the application won't work in new PowerShell windows." -ForegroundColor Yellow
        Write-Host "Path to add: C:\msys64\mingw64\bin" -ForegroundColor Yellow
    }
}

# Now with MSYS2 installed, we can install Python packages
Write-Host "`nInstalling core Python dependencies..." -ForegroundColor Yellow
pip install numpy scipy pandas matplotlib

# PyGObject should now install correctly since MSYS2 is set up
Write-Host "`nInstalling PyGObject (should work now that MSYS2 is set up)..." -ForegroundColor Yellow
pip install pycairo
pip install pygobject

# Install other required packages
Write-Host "`nInstalling other required packages..." -ForegroundColor Yellow
pip install psutil requests pillow opencv-python-headless
pip install typing_extensions textblob cryptography
pip install google-auth google-auth-oauthlib google-api-python-client
pip install onnxruntime pyyaml torch torchvision
pip install SpeechRecognition sounddevice wheel

Write-Host "`nInstallation complete! You can now run Hextrix AI OS with:" -ForegroundColor Green
Write-Host "   .\run_hextrix_system.ps1" -ForegroundColor Cyan
Write-Host "`nNOTE: If you open a new PowerShell window, make sure MSYS2 is in your PATH:" -ForegroundColor Yellow
Write-Host "   C:\msys64\mingw64\bin" -ForegroundColor Yellow 