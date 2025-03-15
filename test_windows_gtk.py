#!/usr/bin/env python3
import sys
import os
import platform

# Print system information
print(f"Python version: {sys.version}")
print(f"Platform: {platform.system()} {platform.release()}")
print(f"Architecture: {platform.architecture()}")

# Check if running on Windows
if platform.system() != "Windows":
    print("This script is intended for Windows testing. For Linux, use test_vte.py instead.")
    sys.exit(1)

try:
    import gi
    print(f"\nPyGObject (gi) version: {gi.__version__}")
except ImportError:
    print("\nPyGObject (gi) module not found!")
    print("Try reinstalling with: conda install -c conda-forge pygobject")
    sys.exit(1)

# Print GI_TYPELIB_PATH environment variable
print("\nGI_TYPELIB_PATH:")
gi_typelib_path = os.environ.get('GI_TYPELIB_PATH', 'Not set')
print(gi_typelib_path)

# Try to import GTK
try:
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk
    print("\nSuccess! GTK module was imported successfully.")
    gtk_version = Gtk.get_major_version(), Gtk.get_minor_version(), Gtk.get_micro_version()
    print(f"GTK version: {gtk_version[0]}.{gtk_version[1]}.{gtk_version[2]}")
except Exception as e:
    print(f"\nError importing GTK: {e}")
    print("\nTroubleshooting steps:")
    print("1. Make sure GTK is properly installed:")
    print("   conda install -c conda-forge gtk3 pygobject pycairo adwaita-icon-theme")
    print("\n2. Or install MSYS2 from https://www.msys2.org/ and install GTK:")
    print("   pacman -S mingw-w64-x86_64-gtk3 mingw-w64-x86_64-python-gobject")
    print("\n3. Add MSYS2 binaries to PATH:")
    print("   Add C:\\msys64\\mingw64\\bin to your Windows PATH")
    sys.exit(1)

# Try to import VTE (will likely fail on Windows, but good to check)
try:
    gi.require_version('Vte', '2.91')
    from gi.repository import Vte
    print("\nVTE module was imported successfully (unusual for Windows).")
except Exception as e:
    print("\nVTE module import failed (expected on Windows):")
    print(f"Error: {e}")
    print("\nNote: VTE terminal emulation is primarily for Linux systems.")
    print("The Hextrix application will run with limited terminal functionality.")

# Create a simple GTK window to verify
try:
    print("\nCreating a test GTK window - close it to finish the test.")
    
    def on_window_destroy(widget):
        Gtk.main_quit()
    
    window = Gtk.Window(title="GTK Test Window")
    window.connect("destroy", on_window_destroy)
    window.set_default_size(300, 200)
    
    label = Gtk.Label(label="GTK is working correctly!")
    window.add(label)
    
    window.show_all()
    Gtk.main()
    
    print("\nGTK window test successful! You should be able to run Hextrix AI OS.")
except Exception as e:
    print(f"\nError creating GTK window: {e}")
    print("There might be issues with your GTK installation.")
    sys.exit(1) 