# Hextrix AI OS

Hextrix AI OS is an advanced AI-powered operating system environment that combines multiple technologies to create a seamless, intelligent computing experience.

## Core Components

### 1. HUD (Heads-Up Display)
The main interface layer that provides:
- AI-powered chat interface with multiple model support (Gemini, OpenAI)
- System control through voice and text commands
- File management and search capabilities
- Terminal emulation with VTE support
- Modern GTK4-based user interface
- Neural network visualization using both Qt-based and native implementations
- App drawer for easy access to all applications

### 2. AI Integration
- **Multiple AI Models**: Support for various AI models including:
  - Google's Gemini
  - OpenAI's models
  - Local transformers models
- **Core AI Features**:
  - Natural language processing
  - Voice command recognition
  - File and content search
  - System control capabilities
  - Self-awareness module
  - Memory management with cloud sync
  - Emotional intelligence and ethics components

### 3. System Integration
- **MCP (Model Context Protocol)**:
  - Unified interface for system control
  - Integration with Windows and Android compatibility layers
  - File system operations (read, write, list, search, grep)
  - Application management
  - External API integrations (Trieve RAG, Perplexity, Google Search, News API)
  - Command execution capabilities
  - Python client library for programmatic access

### 4. Compatibility Layers
- **HexWin** (Windows Compatibility):
  - Run Windows applications seamlessly
  - Integrated with Wine/Proton
  - DirectX gaming capability with DXVK and VKD3D
  - QEMU/WinApps for incompatible applications
  - Automatic application management
  - Desktop integration
  
- **HexDroid** (Android Compatibility):
  - Dual runtime support (Anbox and Waydroid)
  - Smart APK installation
  - Desktop integration
  - Full Android system compatibility
  - ADB access to Android environments
  - Runtime switching based on application needs

### 5. Google Services Integration
- Activity tracking
- Contacts management
- Drive integration
- Fitness tracking
- Gmail integration
- Photos management
- OAuth authentication for Google services

## Hextrix Applications Suite
- **Notepad**: Organized notes with tags and folders
- **Email Client**: Email management with drafts and attachments support
- **Calendar**: Event scheduling with reminders
- **Contacts Manager**: Contact organization with search and groups
- **Calculator**: Advanced computation support
- **Health App**: Health metrics tracking
- **App Center**: Application discovery and management

## Setup Instructions

### Prerequisites

#### For Linux
- Linux system with GTK and VTE libraries installed
- System packages: `gir1.2-vte-2.91`, `libvte-2.91-dev`

#### For Windows
- Windows 10 or later
- PowerShell 5.1 or later
- Internet connection
- MSYS2 (recommended for GTK support)

### Installation

#### On Linux

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/hextrix-ai-os.git
   cd hextrix-ai-os-env
   ```

2. Run the setup script:
   ```bash
   chmod +x setup_venv.sh
   ./setup_venv.sh
   ```

3. Run Hextrix AI OS:
   ```bash
   ./run_hextrix.sh
   ```

#### On Windows

1. Clone the repository:
   ```powershell
   git clone https://github.com/yourusername/hextrix-ai-os.git
   cd hextrix-ai-os-env
   ```

2. Install MSYS2 and GTK libraries (recommended):
   ```powershell
   powershell -ExecutionPolicy Bypass -File install_msys2_gtk.ps1
   ```

3. Setup the environment:
   ```powershell
   powershell -ExecutionPolicy Bypass -File setup_venv.ps1
   ```

4. Run Hextrix AI OS:
   ```powershell
   powershell -ExecutionPolicy Bypass -File run_hextrix.ps1
   ```

## Features

### AI Assistant
- Natural language interaction
- Voice command support
- System control capabilities
- File and content search
- Application management
- Memory management with cloud sync
- Self-awareness and emotional intelligence capabilities

### File Management
- Advanced file search
- Content search (grep)
- Media file organization
- Cloud storage integration
- Automatic file categorization
- File carousel for visual browsing

### Application Management
- Run Windows applications through HexWin
- Android app support through HexDroid
- Native Linux application integration
- Unified application launcher
- Cross-platform compatibility

### System Integration
- Voice command system control
- File system operations
- External API integrations
- Cloud service synchronization
- Security and privacy features
- MCP server for AI assistant integration

### Development Tools
- Terminal emulation
- Development environment integration
- Version control support
- Package management
- Debugging tools

## Configuration

### API Keys
Store your API keys in `credentials2.json` in the `hud` directory:
```json
{
  "api_keys": {
    "trieve_api_key": "YOUR_TRIEVE_API_KEY",
    "perplexity": "YOUR_PERPLEXITY_API_KEY",
    "serp": "YOUR_SERPAPI_API_KEY",
    "newsapi_api_key": "YOUR_NEWSAPI_API_KEY"
  }
}
```

### Google OAuth
For Google service integration, configure OAuth credentials in the `credentials.json` file in the `hud` directory.

### Environment Variables
- `GI_TYPELIB_PATH`: Path to GObject introspection typelibs
- `PYTHONPATH`: Path to AI modules
- `GTK_CSD`: Set to 0 on Windows for native window decorations

## Troubleshooting

### VTE Module Issues (Linux)
1. Install VTE typelib:
   ```bash
   sudo apt install -y gir1.2-vte-2.91 libvte-2.91-dev
   ```

2. Set GI_TYPELIB_PATH:
   ```bash
   export GI_TYPELIB_PATH="/usr/lib/x86_64-linux-gnu/girepository-1.0:/usr/lib/girepository-1.0:$GI_TYPELIB_PATH"
   ```

### GTK Issues (Windows)
1. Use MSYS2 for reliable GTK support:
   ```powershell
   powershell -ExecutionPolicy Bypass -File install_msys2_gtk.ps1
   ```

2. Ensure PATH includes MSYS2 binaries:
   ```
   C:\msys64\mingw64\bin
   ```

### Missing Python Packages

#### For Linux
Use pip with the virtual environment:
```bash
source venv/bin/activate
pip install <package-name>
```

#### For Windows
Use MSYS2's package manager:
```bash
pacman -S mingw-w64-x86_64-python-<package-name>
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License



# LICENSE.md

**Effective Date:** March 15, 2025
**Version:** 4.0

---

# Proprietary License
Copyright (c) 2025 Jared Edwards - The Hextrix AI Project

## 1. Definitions

- **Software**: The Hextrix Ai system, including all neural architectures (e.g., GPT-4o integration, Jetson AGX Thor edge modules), ethical governance frameworks, and associated documentation.
- **Owner**: Jared Edwards, creator and sole proprietor of the Hextrix AI Project.
- **User**: Any individual or entity interacting with the Software.
- **Commercial Use**: Any deployment for revenue-generating activities, including enterprise robotics, healthcare diagnostics, or IoT monetization.

---

## 2. License Terms and Conditions

This software and associated documentation files (the "Software") are the proprietary and confidential property of Jared Edwards ("Owner"). All rights to the Software are reserved by the Owner.

### 2.1 Restrictions

1. **No Modification**: You may not modify, adapt, or create derivative works based on the Software without explicit written permission from the Owner.
2. **No Redistribution**: You may not distribute, sublicense, lease, rent, loan, sell, or otherwise transfer the Software to any third party without explicit written permission from the Owner.
3. **No Reverse Engineering**: You may not reverse engineer, decompile, disassemble, or attempt to derive the source code of the Software.
4. **No Commercial Use**: You may not use the Software for any commercial purposes without explicit written permission from the Owner.

### 2.2 Limited Permission

The Owner grants you a limited, non-exclusive, non-transferable, revocable license to use the Software for personal, non-commercial purposes only, subject to the restrictions above.

---

## 3. Intellectual Property

- **Core Ownership**: All rights to the Software, including neuro-symbolic orchestration logic, hybrid precision pipelines, and cascade failure mitigation systems remain with Jared Edwards.
- **Third-Party Components**: This project may incorporate several third-party open source components, each with their own license. The use of these components in the Software does not grant you any rights to the Software beyond those specified in this license.

---

## 4. Compliance & Ethics

### 4.1 Data Privacy Notice

This software may collect and process personal data. Users are responsible for ensuring compliance with applicable data protection laws, including obtaining appropriate consent from end users before processing their personal data.

### 4.2 Ethical Use

- **Content Generation**: NSFW capabilities disabled by default; enablement requires:
  - 18+ age verification via government ID hashing
  - Geo-fencing excluding jurisdictions with strict morality laws
- **Robotics**: Humanoid systems using Hextrix Ai must implement dual kill switches (software + physical emergency stop)

---

## 5. Disclaimer

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NONINFRINGEMENT. IN NO EVENT SHALL THE OWNER BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

## 6. Termination

This license is effective until terminated. Your rights under this license will terminate automatically without notice if you fail to comply with any of its terms.

Violation of any restrictions triggers:
- **Immediate Revocation**: All permissions to use the Software
- **Data Erasure**: User-specific model adapters and configurations
- **Penalties**: Legal action may be pursued for violations

---

## 7. Governing Law

This license shall be governed by and construed in accordance with the laws of the jurisdiction in which the Owner resides, without regard to its conflict of law provisions.

---

## 8. Contact for Permissions

For permissions to modify, distribute, or use the Software in ways not covered by this license, please contact:

Jared Edwards
Email: thehextrixai@hextrix.net
Licensing Inquiries: Allow 5-7 business days for review of permission requests.

*This document supersedes all prior versions of the Hextrix Ai license agreement.*

---

**Changes from v3.1 → v4.0:**
- Converted to a fully proprietary license model
- Clarified and strengthened core restrictions
- Updated contact information
- Simplified license structure
