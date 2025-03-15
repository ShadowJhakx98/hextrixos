# PowerShell script to set up a Python virtual environment for Hextrix AI OS on Windows

# Define variables
$HEXTRIX_DIR = $PWD.Path
$CONDA_DIR = "$env:USERPROFILE\miniconda3"
$ENV_NAME = "hextrix-env"

# Check if conda is installed
if (-not (Test-Path $CONDA_DIR)) {
    Write-Host "Conda not found. Installing Miniconda..."
    $MINICONDA_URL = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
    $MINICONDA_INSTALLER = "$env:TEMP\miniconda.exe"
    Invoke-WebRequest -Uri $MINICONDA_URL -OutFile $MINICONDA_INSTALLER
    Start-Process -FilePath $MINICONDA_INSTALLER -ArgumentList "/S /D=$CONDA_DIR" -Wait
    Remove-Item $MINICONDA_INSTALLER
}

# Initialize conda
Write-Host "Initializing conda..."
# Import conda into the PowerShell session
$condaPath = "$CONDA_DIR\Scripts\conda.exe"
function global:conda-hook {
    $env:Path = "$CONDA_DIR;$CONDA_DIR\Library\mingw-w64\bin;$CONDA_DIR\Library\usr\bin;$CONDA_DIR\Library\bin;$CONDA_DIR\Scripts;$env:Path"
}
conda-hook

# Create or update conda environment
$envExists = (& $condaPath env list) | Select-String $ENV_NAME
if ($envExists) {
    Write-Host "Environment $ENV_NAME already exists, updating..."
    & "$CONDA_DIR\Scripts\activate.bat" $ENV_NAME
} else {
    Write-Host "Creating new environment: $ENV_NAME"
    & $condaPath create -n $ENV_NAME python=3.12 -y
    & "$CONDA_DIR\Scripts\activate.bat" $ENV_NAME
}

# Install Python dependencies via conda (core libraries)
Write-Host "Installing core Python dependencies..."
& $condaPath install -y numpy scipy pandas matplotlib
& $condaPath install -c conda-forge -y pycairo pygobject gtk3

# Install PyGObject for Windows with GTK
Write-Host "Installing GTK for Windows..."
& $condaPath install -c conda-forge -y gtk3 pygobject pycairo adwaita-icon-theme

# Install missing dependencies (psutil and other required packages)
Write-Host "Installing psutil and other required packages..."
& $condaPath install -c conda-forge -y psutil requests pillow

# Install additional conda packages
Write-Host "Installing additional conda packages..."
& $condaPath install -c conda-forge -y py-opencv typing_extensions textblob cryptography
& $condaPath install -c conda-forge -y google-auth google-auth-oauthlib google-api-python-client
& $condaPath install -c conda-forge -y onnxruntime pyyaml torch torchvision

# Install pip packages
Write-Host "Installing additional packages via pip..."
& $condaPath run -n $ENV_NAME pip install --upgrade pip
& $condaPath run -n $ENV_NAME pip install opencv-python-headless

# Optional packages
Write-Host "Installing optional packages..."
& $condaPath run -n $ENV_NAME pip install SpeechRecognition sounddevice wheel

# MSYS2 instructions (if needed for native GTK libraries)
Write-Host "`nIMPORTANT: For GTK to work properly on Windows, you might need to additionally:`n"
Write-Host "1. Install MSYS2 from https://www.msys2.org/ if you encounter GTK module issues"
Write-Host "2. In MSYS2 terminal, run: pacman -S mingw-w64-x86_64-gtk3 mingw-w64-x86_64-python-gobject mingw-w64-x86_64-gdk-pixbuf2"
Write-Host "3. Add MSYS2 binary path (e.g. C:\msys64\mingw64\bin) to your Windows PATH"

Write-Host "`nVirtual environment setup complete!"
Write-Host "To use this environment:"
Write-Host "  1. Open PowerShell"
Write-Host "  2. Run: & '$CONDA_DIR\Scripts\activate.bat'"
Write-Host "  3. Run: conda activate $ENV_NAME"
Write-Host "  4. Run: .\run_hextrix.ps1" 