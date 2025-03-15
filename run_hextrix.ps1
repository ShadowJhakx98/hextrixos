# Create a new file named run_hextrix.ps1
$env:Path = "C:\msys64\mingw64\bin;$env:Path"
$env:GI_TYPELIB_PATH = "C:\msys64\mingw64\lib\girepository-1.0"
$env:GTK_CSD = 0
$env:PYTHONPATH = "$PWD;$PWD\ai"

# Use the virtual environment Python with the MSYS2 GTK environment
& "$PWD\.venv\Scripts\python.exe" "$PWD\hud\hextrix-hud2.py"