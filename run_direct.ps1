# PowerShell script to run Hextrix AI OS using MSYS2's Python directly
# This is the most reliable approach for GTK on Windows

# Define the project directory
$HEXTRIX_DIR = $PWD.Path

# Enable execution policy for script
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Check for MSYS2 installation
$msys2Path = "C:\msys64"
$msys2MinGWPath = "$msys2Path\mingw64"
$msys2BinPath = "$msys2MinGWPath\bin"

if (-not (Test-Path $msys2Path)) {
    Write-Host "MSYS2 not found at $msys2Path. Please install MSYS2 first." -ForegroundColor Red
    Write-Host "Download from https://www.msys2.org and install it." -ForegroundColor Yellow
    exit 1
}

# Add MSYS2 to the PATH for this session
$env:Path = "$msys2BinPath;$env:Path"
Write-Host "Added MSYS2 to PATH: $msys2BinPath" -ForegroundColor Green

# Set up environment variables
$env:PYTHONPATH = "$HEXTRIX_DIR;$HEXTRIX_DIR\ai"
$env:GI_TYPELIB_PATH = "$msys2MinGWPath\lib\girepository-1.0"
$env:GTK_CSD = 0

# Install required MSYS2 packages
Write-Host "Installing required MSYS2 packages..." -ForegroundColor Yellow

# Create a bash script to run inside MSYS2 shell
$tempScriptPath = "$env:TEMP\msys2_install.sh"
@"
#!/bin/bash
echo "Updating MSYS2 package database..."
pacman -Syu --noconfirm

echo "Installing required packages..."
pacman -S --noconfirm mingw-w64-x86_64-gtk3 mingw-w64-x86_64-python mingw-w64-x86_64-python-gobject mingw-w64-x86_64-python-numpy mingw-w64-x86_64-python-pip mingw-w64-x86_64-python-psutil mingw-w64-x86_64-gdk-pixbuf2

echo "Installing Python dependencies..."
/mingw64/bin/pip install requests matplotlib scipy torch pillow
"@ | Out-File -FilePath $tempScriptPath -Encoding ASCII

# Make the script executable and run it in MSYS2 shell
Write-Host "Running MSYS2 installation script..." -ForegroundColor Yellow
Start-Process -FilePath "$msys2Path\mingw64.exe" -ArgumentList "-c", "bash `"$tempScriptPath`"" -Wait -NoNewWindow

# Clean up
Remove-Item $tempScriptPath

# Verify MSYS2 Python and PyGObject are working
Write-Host "Verifying MSYS2 Python setup..." -ForegroundColor Yellow
$verifyScript = "$env:TEMP\verify_python.sh"
@"
#!/bin/bash
echo "Python version:"
/mingw64/bin/python --version

echo "Testing PyGObject import:"
/mingw64/bin/python -c "import gi; print('PyGObject version:', gi.__version__); gi.require_version('Gtk', '3.0'); from gi.repository import Gtk; print('GTK available:', Gtk)"

echo "Testing psutil import:"
/mingw64/bin/python -c "import psutil; print('psutil version:', psutil.__version__)"

echo "Checking PATH:"
echo `$PATH
"@ | Out-File -FilePath $verifyScript -Encoding ASCII

Start-Process -FilePath "$msys2Path\mingw64.exe" -ArgumentList "-c", "bash `"$verifyScript`"" -Wait -NoNewWindow
Remove-Item $verifyScript

# Run the application using MSYS2's Python with output visible
Write-Host "`nStarting Hextrix AI OS using MSYS2's Python..." -ForegroundColor Green
try {
    # Create a simple script to run the application and capture any errors
    $runScript = "$env:TEMP\run_hextrix.sh"
    @"
#!/bin/bash
cd "$HEXTRIX_DIR"
echo "Running from directory: `$(pwd)"
echo "Python executable: `$(command -v python)"
echo "PATH: `$PATH"
echo "PYTHONPATH: `$PYTHONPATH"
echo "GI_TYPELIB_PATH: `$GI_TYPELIB_PATH"

# Run with error output visible
echo "Starting application..."
python ./hud/hextrix-hud2.py

# Check exit code
if [ `$? -ne 0 ]; then
  echo "Application failed with error code `$?"
  echo "Press Enter to close this window"
  read
fi
"@ | Out-File -FilePath $runScript -Encoding ASCII

    # Run the script in the MSYS2 shell - with a visible window
    Write-Host "Opening MSYS2 window to run the application..."
    Start-Process -FilePath "$msys2Path\mingw64.exe" -ArgumentList "-c", "bash `"$runScript`""

    # Clean up
    Start-Sleep -Seconds 2
    Remove-Item $runScript
} catch {
    Write-Host "Error running Hextrix AI OS: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
} 