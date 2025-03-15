# Simple script to install required libraries and run Hextrix

# Check for MSYS2 installation
$msys2Path = "C:\msys64"
if (-not (Test-Path $msys2Path)) {
    Write-Host "MSYS2 not found. Installing MSYS2 is required for GTK on Windows." -ForegroundColor Red
    Write-Host "Please download and install MSYS2 from https://www.msys2.org/" -ForegroundColor Yellow
    exit 1
}

# Add MSYS2 to PATH
$msys2BinPath = "$msys2Path\mingw64\bin"
$env:Path = "$msys2BinPath;$env:Path"

# Simple install script
$script = @"
#!/bin/bash
echo "Installing required packages..."
pacman -S --noconfirm mingw-w64-x86_64-gtk3 mingw-w64-x86_64-python-gobject mingw-w64-x86_64-python-psutil mingw-w64-x86_64-gdk-pixbuf2
echo "Done!"
"@

$scriptPath = "$env:TEMP\simple_install.sh"
$script | Out-File -FilePath $scriptPath -Encoding ASCII
Start-Process -FilePath "$msys2Path\mingw64.exe" -ArgumentList "-c", "bash $scriptPath" -Wait -NoNewWindow
Remove-Item $scriptPath

# Set environment variables
$env:GI_TYPELIB_PATH = "$msys2Path\mingw64\lib\girepository-1.0"
$env:PYTHONPATH = "$PWD;$PWD\ai"
$env:GTK_CSD = 0

# Run the application
Write-Host "Running Hextrix..." -ForegroundColor Green
Start-Process -FilePath "$msys2Path\mingw64.exe" -ArgumentList "-c", "cd '$PWD' && python ./hud/hextrix-hud2.py" 