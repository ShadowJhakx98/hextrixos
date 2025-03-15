#!/bin/bash
# This script sets up a Python virtual environment for Hextrix AI OS

# Define variables
HEXTRIX_DIR="/home/jared/hextrix-ai-os-env"
CONDA_DIR="$HOME/miniconda"
ENV_NAME="hextrix-env"

# Check if conda is installed
if [ ! -d "$CONDA_DIR" ]; then
    echo "Conda not found. Installing Miniconda..."
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
    bash miniconda.sh -b -p "$CONDA_DIR"
    rm miniconda.sh
fi

# Initialize conda
echo "Initializing conda..."
eval "$(conda shell.bash hook)"

# Create or update conda environment
if conda env list | grep -q "$ENV_NAME"; then
    echo "Environment $ENV_NAME already exists, updating..."
    conda activate "$ENV_NAME"
else
    echo "Creating new environment: $ENV_NAME"
    conda create -n "$ENV_NAME" python=3.12 -y
    conda activate "$ENV_NAME"
fi

# Install Python dependencies via conda (core libraries)
echo "Installing core Python dependencies..."
conda install -y numpy scipy pandas matplotlib
conda install -c conda-forge -y pycairo pygobject

# Install additional conda packages
echo "Installing additional conda packages..."
conda install -c conda-forge -y py-opencv typing_extensions textblob cryptography
conda install -c conda-forge -y google-auth google-auth-oauthlib google-api-python-client
conda install -c conda-forge -y onnxruntime pyyaml

# Install pip packages
echo "Installing additional packages via pip..."
pip install --upgrade pip
pip install PyGObject opencv-python-headless

# Optional packages
echo "Installing optional packages..."
pip install SpeechRecognition sounddevice wheel

# Add symlinks to system GObject typelibs to make them accessible in conda
echo "Setting up GObject introspection for conda environment..."
CONDA_PREFIX=$(conda info --base)/envs/$ENV_NAME
TYPELIB_DIR="$CONDA_PREFIX/lib/girepository-1.0"
mkdir -p "$TYPELIB_DIR"

# Create symlinks to system typelib files (including VTE)
echo "Linking system GObject typelibs to conda environment..."
SYSTEM_TYPELIB_DIRS=("/usr/lib/x86_64-linux-gnu/girepository-1.0" "/usr/lib/girepository-1.0")
for SYSTEM_DIR in "${SYSTEM_TYPELIB_DIRS[@]}"; do
    if [ -d "$SYSTEM_DIR" ]; then
        for TYPELIB in "$SYSTEM_DIR"/*.typelib; do
            if [ -f "$TYPELIB" ]; then
                ln -sf "$TYPELIB" "$TYPELIB_DIR/$(basename "$TYPELIB")"
            fi
        done
    fi
done

echo "Virtual environment setup complete!"
echo "To use this environment:"
echo "  1. Run: source ~/miniconda/etc/profile.d/conda.sh"
echo "  2. Run: conda activate hextrix-env"
echo "  3. Run: ./run_hextrix.sh"
