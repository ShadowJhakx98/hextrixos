#!/bin/bash
# This script installs system-level dependencies required for Hextrix AI OS

# Update package lists
echo "Updating package lists..."
sudo apt update

# Install GTK and related dependencies
echo "Installing GTK and GUI dependencies..."
sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0
sudo apt install -y libgirepository1.0-dev gcc libcairo2-dev pkg-config
sudo apt install -y libvte-2.91-dev gir1.2-vte-2.91
# Install VTE terminal library
sudo apt install -y gir1.2-vte-2.91 libvte-2.91-dev

# Install audio/video dependencies
echo "Installing audio/video dependencies..."
sudo apt install -y portaudio19-dev python3-pyaudio
sudo apt install -y ffmpeg

# Install image processing libraries
echo "Installing image processing libraries..."
sudo apt install -y libopencv-dev

echo "System dependencies installed successfully!"
