# PowerShell script to run Hextrix AI OS using the system Python installation
# This version doesn't use conda

# Define the project directory
$HEXTRIX_DIR = $PWD.Path

# Enable execution policy for script
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Print current PATH for debugging
Write-Host "`nDEBUG - Current PATH:" -ForegroundColor Cyan
$env:Path -split ";" | ForEach-Object { Write-Host "  $_" }

# Check for MSYS2 installation - required for GTK on Windows
$msys2Path = "C:\msys64\mingw64\bin"
if (Test-Path $msys2Path) {
    Write-Host "`nMSYS2 installation found, using its libraries (recommended)" -ForegroundColor Green
    # Add MSYS2 to the beginning of PATH to prioritize its DLLs
    $env:Path = "$msys2Path;$env:Path"
    Write-Host "Added MSYS2 to PATH for this session" -ForegroundColor Green
} else {
    Write-Host "`nWARNING: MSYS2 installation not found at $msys2Path" -ForegroundColor Yellow
    Write-Host "GTK functionality might be limited or not work at all" -ForegroundColor Yellow
    Write-Host "Please run install_system_deps_windows.ps1 to install MSYS2" -ForegroundColor Yellow
}

# Set GI_TYPELIB_PATH for Windows (typelib location depends on MSYS2)
Write-Host "`nSetting up GObject introspection paths..." -ForegroundColor Cyan
if (Test-Path "C:\msys64\mingw64\lib\girepository-1.0") {
    $env:GI_TYPELIB_PATH = "C:\msys64\mingw64\lib\girepository-1.0"
    Write-Host "Set MSYS2 typelib path: C:\msys64\mingw64\lib\girepository-1.0" -ForegroundColor Green
}

# Add the AI modules to Python path
$env:PYTHONPATH = "$env:PYTHONPATH;$HEXTRIX_DIR;$HEXTRIX_DIR\ai"

# Use GTK_CSD=0 to force Windows-style decorations instead of client-side decorations
$env:GTK_CSD = 0

# Verify MSYS2 DLLs can be found
if (Test-Path $msys2Path) {
    $gdkPixbufDll = "$msys2Path\libgdk_pixbuf-2.0-0.dll"
    if (Test-Path $gdkPixbufDll) {
        Write-Host "`nGDK Pixbuf DLL found at: $gdkPixbufDll" -ForegroundColor Green
    } else {
        Write-Host "`nWARNING: GDK Pixbuf DLL not found at expected location: $gdkPixbufDll" -ForegroundColor Yellow
        Write-Host "This might cause 'Failed to load shared library 'gdk_pixbuf-2.0-0.dll'' errors" -ForegroundColor Yellow
    }
}

# Print environment variables for debugging
Write-Host "`nDEBUG - Environment Variables:" -ForegroundColor Cyan
Write-Host "  PYTHONPATH = $env:PYTHONPATH" 
Write-Host "  GI_TYPELIB_PATH = $env:GI_TYPELIB_PATH"
Write-Host "  GTK_CSD = $env:GTK_CSD"

# Run the application with error handling
Write-Host "`nStarting Hextrix AI OS..." -ForegroundColor Green
try {
    python "$HEXTRIX_DIR\hud\hextrix-hud2.py"
} catch {
    Write-Host "`nError running Hextrix AI OS: $_" -ForegroundColor Red
    Write-Host "`nTroubleshooting suggestions:" -ForegroundColor Yellow
    Write-Host "1. Run the installation script: .\install_system_deps_windows.ps1" -ForegroundColor Yellow
    Write-Host "2. Make sure MSYS2 is installed and its bin directory is in your PATH" -ForegroundColor Yellow
    Write-Host "3. Check if Python packages are installed correctly" -ForegroundColor Yellow
    
    # Keep the window open
    Read-Host "`nPress Enter to exit"
} 