# PowerShell script to install missing dependencies for Hextrix AI OS

# Enable execution policy for script
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Define variables
$CONDA_DIR = "$env:USERPROFILE\miniconda3"
$ENV_NAME = "hextrix-env"

# Import conda into the PowerShell session
function global:conda-hook {
    $env:Path = "$CONDA_DIR;$CONDA_DIR\Library\mingw-w64\bin;$CONDA_DIR\Library\usr\bin;$CONDA_DIR\Library\bin;$CONDA_DIR\Scripts;$env:Path"
}
conda-hook

# Activate conda environment
$envExists = (& "$CONDA_DIR\Scripts\conda.exe" env list) | Select-String $ENV_NAME
if ($envExists) {
    Write-Host "Activating $ENV_NAME conda environment..."
    & "$CONDA_DIR\Scripts\activate.bat" $ENV_NAME
} else {
    Write-Host "Conda environment not found. Please run setup_venv.ps1 first."
    exit 1
}

# Install missing dependencies
Write-Host "Installing missing dependencies..." -ForegroundColor Cyan

# Install psutil (which was reported as missing)
Write-Host "Installing psutil..."
& conda install -c conda-forge -y psutil

# Install other potentially required packages 
Write-Host "Installing other potentially required packages..."
& conda install -c conda-forge -y requests pillow torch torchvision

Write-Host "`nDependencies installation complete!" -ForegroundColor Green
Write-Host "Now try running: .\run_hextrix.ps1" 