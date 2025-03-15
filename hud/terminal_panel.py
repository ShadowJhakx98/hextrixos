import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, GLib, Pango
import platform
import shlex
import subprocess
import sys
import os
import psutil

# Make VTE import conditional since it may not be available on Windows
VTE_AVAILABLE = False
try:
    if platform.system() != "Windows":
        # Try to use VTE version that's compatible with GTK 4.0
        try:
            gi.require_version('Vte', '3.91')  # Try newer version first
            from gi.repository import Vte
            VTE_AVAILABLE = True
            print("Using VTE 3.91 with GTK 4.0")
        except (ValueError, ImportError):
            try:
                gi.require_version('Vte', '2.91')  # Fall back to older version
                from gi.repository import Vte
                VTE_AVAILABLE = True
                print("Using VTE 2.91 with GTK 4.0")
            except (ValueError, ImportError) as e:
                print(f"VTE terminal not available: {e}")
                print("Terminal functionality will be limited.")
except (ValueError, ImportError) as e:
    print(f"VTE terminal not available: {e}")
    print("Terminal functionality will be limited.")

class TerminalPanel:
    def __init__(self, parent):
        self.parent = parent
        self.panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # Initialize vte_available first, before any method that might use it
        self.vte_available = VTE_AVAILABLE

        self.toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.toolbar.set_spacing(3)
        self.toolbar.set_margin_top(3)
        self.toolbar.set_margin_bottom(3)
        self.toolbar.set_margin_start(3)
        self.toolbar.set_margin_end(3)
        
        # Command history
        self.command_history = []
        self.history_position = -1
        self.HISTORY_MAX = 20

        self.new_tab_button = self.create_tool_button("tab-new-symbolic", "New Tab", self.on_new_tab)
        self.toolbar.append(self.new_tab_button)

        self.copy_button = self.create_tool_button("edit-copy-symbolic", "Copy", self.on_copy)
        self.toolbar.append(self.copy_button)

        self.paste_button = self.create_tool_button("edit-paste-symbolic", "Paste", self.on_paste)
        self.toolbar.append(self.paste_button)

        self.clear_button = self.create_tool_button("edit-clear-all-symbolic", "Clear", self.on_clear)
        self.toolbar.append(self.clear_button)

        self.font_smaller_button = self.create_tool_button("zoom-out-symbolic", "Decrease Font Size", self.on_font_smaller)
        self.toolbar.append(self.font_smaller_button)

        self.font_larger_button = self.create_tool_button("zoom-in-symbolic", "Increase Font Size", self.on_font_larger)
        self.toolbar.append(self.font_larger_button)

        # Add history navigation buttons
        self.history_up_button = self.create_tool_button("go-up-symbolic", "Previous Command", self.on_history_up)
        self.toolbar.append(self.history_up_button)

        self.history_down_button = self.create_tool_button("go-down-symbolic", "Next Command", self.on_history_down)
        self.toolbar.append(self.history_down_button)

        # Command entry
        self.cmd_entry = Gtk.Entry()
        self.cmd_entry.set_placeholder_text("Enter command...")
        self.cmd_entry.connect("activate", self.on_cmd_activated)
        
        # Add key controller for GTK 4
        key_controller = Gtk.EventControllerKey.new()
        key_controller.connect("key-pressed", self.on_cmd_keypress)
        self.cmd_entry.add_controller(key_controller)
        
        self.toolbar.append(self.cmd_entry)
        self.cmd_entry.set_hexpand(True)

        # Run button
        self.run_button = self.create_tool_button("system-run-symbolic", "Run Command", self.on_run_command)
        self.toolbar.append(self.run_button)

        # Help button
        self.help_button = self.create_tool_button("help-browser-symbolic", "Help", self.on_help)
        self.toolbar.append(self.help_button)

        self.panel.append(self.toolbar)

        self.notebook = Gtk.Notebook()
        self.notebook.set_scrollable(True)
        self.notebook.set_show_border(False)
        self.notebook.connect("switch-page", self.on_tab_switched)
        self.panel.append(self.notebook)

        self.terminals = []
        self.create_terminal_tab("Terminal")

        self.apply_styling()

        self.font_size = 12
        self.update_font()

        # Initialize custom commands
        self.init_custom_commands()

        # Initialize terminal availability
        self.vte_available = VTE_AVAILABLE

    def init_custom_commands(self):
        """Initialize custom commands from Hextrix OS shell"""
        # Debug message to confirm function is called
        print("Initializing custom commands")
        self.custom_commands = {
            # Shell commands
            "help": {
                "description": "Show available commands",
                "handler": self.cmd_help
            },
            "clear": {
                "description": "Clear the screen",
                "handler": self.cmd_clear
            },
            "echo": {
                "description": "Display text",
                "handler": self.cmd_echo
            },
            "history": {
                "description": "Show command history",
                "handler": self.cmd_history
            },
            "version": {
                "description": "Show OS version",
                "handler": self.cmd_version
            },
            "exit": {
                "description": "Exit the shell",
                "handler": self.cmd_exit
            },
            
            # File system commands
            "ls": {
                "description": "List files in directory",
                "handler": self.cmd_ls
            },
            "cat": {
                "description": "Display file contents",
                "handler": self.cmd_cat
            },
            "rm": {
                "description": "Delete a file",
                "handler": self.cmd_rm
            },
            "pwd": {
                "description": "Show current directory",
                "handler": self.cmd_pwd
            },
            "cd": {
                "description": "Change current directory",
                "handler": self.cmd_cd
            },
            "mkdir": {
                "description": "Create a directory",
                "handler": self.cmd_mkdir
            },
            "write": {
                "description": "Create/edit a file",
                "handler": self.cmd_write
            },
            
            # System info commands
            "meminfo": {
                "description": "Display memory usage",
                "handler": self.cmd_meminfo
            },
            "ps": {
                "description": "List running processes",
                "handler": self.cmd_ps
            },
            "kill": {
                "description": "Terminate a process",
                "handler": self.cmd_kill
            },
            "sleep": {
                "description": "Sleep for milliseconds",
                "handler": self.cmd_sleep
            },
            "diag": {
                "description": "Run system diagnostics",
                "handler": self.cmd_diag
            },
        }

    def apply_styling(self):
        css_provider = Gtk.CssProvider()
        css = """
            .terminal-panel {
                background-color: rgba(0, 10, 30, 0.8);
                border-radius: 5px;
                border: 1px solid rgba(0, 191, 255, 0.3);
            }
            .terminal-panel-toolbar {
                background-color: rgba(0, 30, 60, 0.8);
                border-bottom: 1px solid rgba(0, 191, 255, 0.3);
            }
            .tool-button {
                background-color: rgba(0, 40, 80, 0.7);
                border-radius: 4px;
                border: 1px solid rgba(0, 191, 255, 0.5);
                padding: 2px;
                transition: all 0.2s ease;
            }
            .tool-button:hover {
                background-color: rgba(0, 70, 130, 0.8);
                border-color: rgba(0, 255, 255, 0.8);
            }
            notebook tab {
                background-color: rgba(0, 20, 50, 0.7);
                padding: 2px 8px;
                border: 1px solid rgba(0, 191, 255, 0.3);
                color: #00BFFF;
            }
            notebook tab:checked {
                background-color: rgba(0, 40, 90, 0.8);
                border-bottom: 1px solid #00BFFF;
            }
            entry {
                background-color: rgba(0, 20, 50, 0.8);
                color: #00BFFF;
                border: 1px solid rgba(0, 191, 255, 0.5);
                border-radius: 4px;
                padding: 4px 8px;
            }
            entry:focus {
                border-color: rgba(0, 255, 255, 0.8);
            }
        """
        css_provider.load_from_data(css.encode())
        
        # Apply CSS to the default display - GTK4 style
        display = Gdk.Display.get_default()
        Gtk.StyleContext.add_provider_for_display(
            display, 
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def create_tool_button(self, icon_name, tooltip, callback):
        button = Gtk.Button()
        button.set_tooltip_text(tooltip)
        
        # Create an image for the icon using pixel size instead of icon size
        icon = Gtk.Image.new_from_icon_name(icon_name)
        icon.set_pixel_size(16)  # Equivalent to SMALL_TOOLBAR
        button.set_child(icon)
        
        # Connect to clicked signal
        button.connect("clicked", callback)
        
        return button

    def create_terminal_tab(self, tab_title="Terminal"):
        if not self.vte_available:
            # Create a placeholder if VTE is not available
            scrolled_window = Gtk.ScrolledWindow()
            scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            
            label = Gtk.Label()
            label.set_markup("<span foreground='#ff5555'>Terminal emulation not available on this platform.\nVTE module could not be loaded.</span>")
            label.set_justify(Gtk.Justification.CENTER)
            
            content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            content_box.append(label)
            label.set_hexpand(True)
            scrolled_window.set_child(content_box)
            
            self.notebook.append_page(scrolled_window, Gtk.Label(label=tab_title))
            return scrolled_window
            
        # Original terminal creation code for Linux
        terminal = Vte.Terminal()
        terminal.set_cursor_blink_mode(Vte.CursorBlinkMode.ON)
        terminal.set_mouse_autohide(True)
        
        # Make sure terminal receives input events
        terminal.set_can_focus(True)
        
        # In GTK 4.0, add_events is replaced with event controllers
        # Add motion controller
        motion_controller = Gtk.EventControllerMotion.new()
        terminal.add_controller(motion_controller)
        
        # Add key controller
        key_controller = Gtk.EventControllerKey.new()
        terminal.add_controller(key_controller)
        
        # Add scroll controller
        scroll_controller = Gtk.EventControllerScroll.new(Gtk.EventControllerScrollFlags.BOTH_AXES)
        terminal.add_controller(scroll_controller)
        
        # Set terminal colors - use rgba() method instead of direct RGBA constructor in GTK 4
        fg_color = Gdk.RGBA()
        fg_color.parse("rgb(204,229,255)") # Light blue text
        bg_color = Gdk.RGBA()
        bg_color.parse("rgba(0,13,26,0.9)") # Dark blue background
        
        # Set colors using the appropriate method for the VTE version
        if hasattr(terminal, 'set_colors'):
            terminal.set_colors(fg_color, bg_color, None)
        elif hasattr(terminal, 'set_color_foreground'):
            terminal.set_color_foreground(fg_color)
            terminal.set_color_background(bg_color)
        
        # Create scrolled window for terminal
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(terminal)
        
        # Create tab with close button
        tab_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        tab_label = Gtk.Label(label=tab_title)
        tab_box.append(tab_label)
        tab_label.set_hexpand(True)
        
        close_icon = Gtk.Image.new_from_icon_name("window-close-symbolic")
        close_icon.set_pixel_size(16) # Equivalent to MENU size in GTK 3
        close_button = Gtk.Button()
        close_button.set_child(close_icon)
        close_button.connect("clicked", self.on_tab_close, scrolled)
        tab_box.append(close_button)
        
        page_index = self.notebook.append_page(scrolled, tab_box)
        self.notebook.set_current_page(page_index)
        
        # Try different spawn methods based on what's available in this VTE version
        try:
            if hasattr(terminal, 'spawn_async'):
                terminal.spawn_async(
                    Vte.PtyFlags.DEFAULT,
                    os.environ['HOME'],
                    ["/bin/bash"],
                    [],
                    GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                    None,
                    None,
                    -1,
                    None,
                    None
                )
            else:
                terminal.spawn_sync(
                    Vte.PtyFlags.DEFAULT,
                    os.environ['HOME'],
                    ["/bin/bash"],
                    [],
                    GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                    None,
                    None,
                )
        except Exception as e:
            print(f"Error spawning terminal: {e}")
            error_label = Gtk.Label()
            error_label.set_markup(f"<span foreground='#ff5555'>Error spawning terminal:\n{e}</span>")
            terminal.set_child(error_label)

        # Connect exit signal
        if hasattr(terminal, 'connect'):
            terminal.connect("child-exited", self.on_terminal_exit)

        self.terminals.append(terminal)
        return terminal

    def get_current_terminal(self):
        page_num = self.notebook.get_current_page()
        if page_num >= 0 and page_num < len(self.terminals):
            return self.terminals[page_num]
        return None

    def update_font(self):
        for terminal in self.terminals:
            font_desc = Pango.FontDescription(f"Monospace {self.font_size}")
            terminal.set_font(font_desc)

    def on_new_tab(self, button):
        self.create_terminal_tab(f"Terminal {len(self.terminals)}")

    def on_tab_close(self, button, widget):
        page_num = self.notebook.page_num(widget)
        if page_num >= 0:
            if len(self.terminals) > 1:
                del self.terminals[page_num]
                self.notebook.remove_page(page_num)
            else:
                self.terminals[0].reset(True, True)

    def on_tab_switched(self, notebook, page, page_num):
        pass

    def on_copy(self, button):
        term = self.get_current_terminal()
        if term and hasattr(term, 'get_has_selection') and term.get_has_selection():
            # For GTK 4.0 compatible VTE
            if hasattr(term, 'copy_clipboard_format'):
                term.copy_clipboard_format(Vte.Format.TEXT)
            # Fallback for older VTE
            elif hasattr(term, 'copy_clipboard'):
                term.copy_clipboard()
            else:
                print("Copy operation not supported in this VTE version")

    def on_paste(self, button):
        term = self.get_current_terminal()
        if term:
            # For GTK 4.0 compatible VTE
            if hasattr(term, 'paste_clipboard'):
                term.paste_clipboard()
            else:
                # Try alternate methods for newer VTE
                clipboard = Gdk.Display.get_default().get_clipboard()
                clipboard.read_text_async(None, self._on_clipboard_text_received, term)
    
    def _on_clipboard_text_received(self, clipboard, result, terminal):
        try:
            text = clipboard.read_text_finish(result)
            if text and terminal and hasattr(terminal, 'feed_child'):
                # Convert text to bytes if needed
                if hasattr(terminal, 'feed_child'):
                    try:
                        terminal.feed_child(text.encode('utf-8'))
                    except (TypeError, AttributeError):
                        try:
                            terminal.feed_child(text)
                        except Exception as e:
                            print(f"Error pasting text: {e}")
        except Exception as e:
            print(f"Error reading clipboard: {e}")

    def on_clear(self, button):
        term = self.get_current_terminal()
        if term:
            term.reset(True, True)

    def on_font_smaller(self, button):
        if self.font_size > 6:
            self.font_size -= 1
            self.update_font()

    def on_font_larger(self, button):
        if self.font_size < 24:
            self.font_size += 1
            self.update_font()

    def on_help(self, button):
        self.cmd_help([])

    def on_history_up(self, button):
        self.navigate_history("up")
    
    def on_history_down(self, button):
        self.navigate_history("down")
        
    def navigate_history(self, direction):
        """Navigate through command history"""
        if not self.command_history:
            return
            
        if direction == "up":
            # Move up in history (older commands)
            self.history_position = max(0, self.history_position - 1)
        elif direction == "down":
            # Move down in history (newer commands)
            self.history_position = min(len(self.command_history), self.history_position + 1)
            
        if self.history_position < len(self.command_history):
            self.cmd_entry.set_text(self.command_history[self.history_position])
        else:
            self.cmd_entry.set_text("")

    def on_cmd_keypress(self, controller, keyval, keycode, state):
        """Handle key presses in the command entry"""
        # Handle up/down arrow keys for history navigation
        if keyval == Gdk.KEY_Up:
            self.navigate_history("up")
            return True
        elif keyval == Gdk.KEY_Down:
            self.navigate_history("down")
            return True
        return False

    def on_cmd_activated(self, entry):
        self.run_command()
        
    def on_run_command(self, button):
        self.run_command()

    def run_command(self):
        command_text = self.cmd_entry.get_text().strip()
        if not command_text:
            return

        # Add command to history
        self.command_history.append(command_text)
        self.history_position = len(self.command_history)

        # Clear the command entry
        self.cmd_entry.set_text("")

        # Process custom commands
        cmd_parts = shlex.split(command_text)
        cmd = cmd_parts[0].lower()
        args = cmd_parts[1:] if len(cmd_parts) > 1 else []

        # Check if it's a custom command
        if cmd in self.custom_commands:
            self.write_to_terminal(f"> {command_text}\n")
            self.custom_commands[cmd]["handler"](args)
            return

        # If VTE is not available, show a message for system commands
        if not self.vte_available:
            self.write_to_terminal(f"> {command_text}\n")
            self.write_to_terminal("External command execution not available on this platform.\n")
            return

        # Original command execution code for Linux
        term = self.get_current_terminal()
        if term:
            term.feed_child((command_text + "\n").encode())

    def write_to_terminal(self, text):
        """Write text directly to the current terminal."""
        term = self.get_current_terminal()
        if term:
            # Use feed_child instead of feed for compatibility with different Vte versions
            term.feed_child(text.encode())

    def ensure_terminal_focus(self):
        term = self.get_current_terminal()
        if term:
            term.grab_focus()

    def on_terminal_exit(self, terminal, status):
        terminal.spawn_sync(
            Vte.PtyFlags.DEFAULT,
            os.environ['HOME'],
            ["/bin/bash"],
            [],
            GLib.SpawnFlags.DO_NOT_REAP_CHILD,
            None,
            None,
        )

    # Custom command handlers
    def cmd_help(self, args):
        """Show help for available commands."""
        if args:
            cmd_name = args[0]
            if cmd_name in self.custom_commands:
                cmd = self.custom_commands[cmd_name]
                self.write_to_terminal(f"{cmd_name} - {cmd['description']}\n")
            else:
                self.write_to_terminal(f"Unknown command: {cmd_name}\n")
            return

        # Group commands by category
        categories = {
            "File System": ["ls", "cat", "rm", "pwd", "cd", "mkdir", "write"],
            "System Info": ["meminfo", "ps", "kill", "diag"],
            "Shell": ["help", "clear", "echo", "history", "version", "exit", "sleep"]
        }
        
        # Find the max command name length for pretty formatting
        max_name_len = max(len(name) for name in self.custom_commands.keys())
        
        self.write_to_terminal("Available commands:\n\n")
        
        for category, cmds in categories.items():
            self.write_to_terminal(f"{category}:\n")
            for cmd_name in cmds:
                if cmd_name in self.custom_commands:
                    padding = " " * (max_name_len - len(cmd_name) + 2)
                    self.write_to_terminal(f"  {cmd_name}{padding}- {self.custom_commands[cmd_name]['description']}\n")
            self.write_to_terminal("\n")
            
        self.write_to_terminal("Type 'help <command>' for more information on a specific command.\n")

    def cmd_clear(self, args):
        """Clear the terminal screen."""
        term = self.get_current_terminal()
        if term:
            term.reset(True, True)
    
    def cmd_echo(self, args):
        """Display text."""
        self.write_to_terminal(" ".join(args) + "\n")
    
    def cmd_history(self, args):
        """Show command history."""
        if not self.command_history:
            self.write_to_terminal("No command history\n")
            return
            
        self.write_to_terminal("Command History:\n")
        for i, cmd in enumerate(self.command_history):
            self.write_to_terminal(f"{i+1}: {cmd}\n")
    
    def cmd_version(self, args):
        """Show system version."""
        self.write_to_terminal("Hextrix OS HUD Terminal v1.0.0\n")
        self.write_to_terminal(f"Running on {platform.system()} {platform.release()}\n")
        self.write_to_terminal("Enhanced Shell with command history and tab completion\n")
    
    def cmd_exit(self, args):
        """Exit the shell."""
        self.write_to_terminal("Exiting shell...\n")
        term = self.get_current_terminal()
        if term:
            term.reset(True, True)
    
    def cmd_ls(self, args):
        """List files in directory."""
        try:
            target_dir = args[0] if args else "."
            output = subprocess.check_output(["ls", "-la", target_dir], universal_newlines=True)
            self.write_to_terminal(output)
        except subprocess.CalledProcessError as e:
            self.write_to_terminal(f"Error: {e.stderr if e.stderr else e}\n")
        except FileNotFoundError:
            self.write_to_terminal(f"Error: Directory not found\n")
    
    def cmd_cat(self, args):
        """Display file contents."""
        if not args:
            self.write_to_terminal("Usage: cat <filename>\n")
            return
            
        try:
            with open(args[0], 'r') as f:
                content = f.read()
                self.write_to_terminal(content)
                if not content.endswith('\n'):
                    self.write_to_terminal('\n')
        except FileNotFoundError:
            self.write_to_terminal(f"File '{args[0]}' not found\n")
        except IsADirectoryError:
            self.write_to_terminal(f"'{args[0]}' is a directory\n")
        except PermissionError:
            self.write_to_terminal(f"Permission denied: '{args[0]}'\n")
        except Exception as e:
            self.write_to_terminal(f"Error: {str(e)}\n")
    
    def cmd_rm(self, args):
        """Delete a file."""
        if not args:
            self.write_to_terminal("Usage: rm <filename>\n")
            return
            
        try:
            os.remove(args[0])
            self.write_to_terminal(f"Deleted '{args[0]}'\n")
        except FileNotFoundError:
            self.write_to_terminal(f"File '{args[0]}' not found\n")
        except IsADirectoryError:
            self.write_to_terminal(f"'{args[0]}' is a directory. Use 'rm -r' to remove directories.\n")
        except PermissionError:
            self.write_to_terminal(f"Permission denied: '{args[0]}'\n")
        except Exception as e:
            self.write_to_terminal(f"Error: {str(e)}\n")
    
    def cmd_pwd(self, args):
        """Show current directory."""
        self.write_to_terminal(f"{os.getcwd()}\n")
    
    def cmd_cd(self, args):
        """Change current directory."""
        target_dir = args[0] if args else os.path.expanduser("~")
        
        try:
            os.chdir(target_dir)
            self.write_to_terminal(f"{os.getcwd()}\n")
        except FileNotFoundError:
            self.write_to_terminal(f"Directory '{target_dir}' not found\n")
        except NotADirectoryError:
            self.write_to_terminal(f"'{target_dir}' is not a directory\n")
        except PermissionError:
            self.write_to_terminal(f"Permission denied: '{target_dir}'\n")
        except Exception as e:
            self.write_to_terminal(f"Error: {str(e)}\n")
    
    def cmd_mkdir(self, args):
        """Create a directory."""
        if not args:
            self.write_to_terminal("Usage: mkdir <directory>\n")
            return
            
        try:
            os.makedirs(args[0], exist_ok=True)
            self.write_to_terminal(f"Created directory '{args[0]}'\n")
        except PermissionError:
            self.write_to_terminal(f"Permission denied: '{args[0]}'\n")
        except Exception as e:
            self.write_to_terminal(f"Error: {str(e)}\n")
    
    def cmd_write(self, args):
        """Create/edit a file (simplified)."""
        if not args:
            self.write_to_terminal("Usage: write <filename>\n")
            return
            
        self.write_to_terminal(f"Opening {args[0]} for editing...\n")
        self.write_to_terminal("Not implemented in GUI terminal. Use a text editor like nano or vim.\n")
        
        # Launch the default editor in the terminal
        term = self.get_current_terminal()
        if term:
            editor = os.environ.get('EDITOR', 'nano')
            cmd = f"{editor} {args[0]}\n"
            term.feed_child(cmd.encode())
    
    def cmd_meminfo(self, args):
        """Display memory usage."""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        self.write_to_terminal("Memory usage:\n")
        self.write_to_terminal(f"  Total: {mem.total} bytes ({mem.total // (1024*1024)} MB)\n")
        self.write_to_terminal(f"  Used:  {mem.used} bytes ({mem.used // (1024*1024)} MB, {mem.percent}%)\n")
        self.write_to_terminal(f"  Free:  {mem.available} bytes ({mem.available // (1024*1024)} MB, {100 - mem.percent}%)\n")
        
        self.write_to_terminal("\nSwap Memory:\n")
        self.write_to_terminal(f"  Total: {swap.total} bytes ({swap.total // (1024*1024)} MB)\n")
        self.write_to_terminal(f"  Used:  {swap.used} bytes ({swap.used // (1024*1024)} MB, {swap.percent}%)\n")
    
    def cmd_ps(self, args):
        """List running processes."""
        self.write_to_terminal("PID\tCPU%\tMEM%\tNAME\n")
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                self.write_to_terminal(f"{info['pid']}\t{info['cpu_percent']:.1f}\t{info['memory_percent']:.1f}\t{info['name']}\n")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    
    def cmd_kill(self, args):
        """Terminate a process."""
        if not args:
            self.write_to_terminal("Usage: kill <pid>\n")
            return
            
        try:
            pid = int(args[0])
            if pid <= 0:
                self.write_to_terminal("Invalid PID\n")
                return
                
            process = psutil.Process(pid)
            process.terminate()
            self.write_to_terminal(f"Process {pid} terminated\n")
        except ValueError:
            self.write_to_terminal("Invalid PID format\n")
        except psutil.NoSuchProcess:
            self.write_to_terminal(f"No process with PID {pid}\n")
        except psutil.AccessDenied:
            self.write_to_terminal(f"Permission denied to kill PID {pid}\n")
        except Exception as e:
            self.write_to_terminal(f"Error: {str(e)}\n")
    
    def cmd_sleep(self, args):
        """Sleep for milliseconds."""
        if not args:
            self.write_to_terminal("Usage: sleep <milliseconds>\n")
            return
            
        try:
            ms = int(args[0])
            self.write_to_terminal(f"Sleeping for {ms} ms...\n")
            
            # Use GLib timeout for non-blocking sleep
            def wake_up():
                self.write_to_terminal("Done sleeping\n")
                return False
                
            GLib.timeout_add(ms, wake_up)
        except ValueError:
            self.write_to_terminal("Invalid time format\n")
    
    def cmd_diag(self, args):
        """Run system diagnostics."""
        self.write_to_terminal("Running system diagnostics...\n")
        
        # System information
        self.write_to_terminal("\n=== System Information ===\n")
        self.write_to_terminal(f"System: {platform.system()} {platform.release()}\n")
        self.write_to_terminal(f"Version: {platform.version()}\n")
        self.write_to_terminal(f"Machine: {platform.machine()}\n")
        self.write_to_terminal(f"Processor: {platform.processor()}\n")
        
        # Memory information
        self.write_to_terminal("\n=== Memory Information ===\n")
        mem = psutil.virtual_memory()
        self.write_to_terminal(f"Memory: {mem.total // (1024*1024)} MB total, "
                              f"{mem.used // (1024*1024)} MB used, "
                              f"{mem.available // (1024*1024)} MB free\n")
        
        # Disk information
        self.write_to_terminal("\n=== Disk Information ===\n")
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                self.write_to_terminal(f"Partition: {part.device} mounted at {part.mountpoint}\n")
                self.write_to_terminal(f"  Type: {part.fstype}\n")
                self.write_to_terminal(f"  Total: {usage.total // (1024*1024)} MB\n")
                self.write_to_terminal(f"  Used: {usage.used // (1024*1024)} MB ({usage.percent}%)\n")
                self.write_to_terminal(f"  Free: {usage.free // (1024*1024)} MB\n")
            except PermissionError:
                self.write_to_terminal(f"Partition: {part.device} mounted at {part.mountpoint} (Permission denied)\n")
        
        # Network information
        self.write_to_terminal("\n=== Network Information ===\n")
        try:
            for name, stats in psutil.net_io_counters(pernic=True).items():
                self.write_to_terminal(f"Interface: {name}\n")
                self.write_to_terminal(f"  Bytes sent: {stats.bytes_sent}\n")
                self.write_to_terminal(f"  Bytes received: {stats.bytes_recv}\n")
        except Exception as e:
            self.write_to_terminal(f"Error retrieving network info: {str(e)}\n")
        
        self.write_to_terminal("\nDiagnostics completed.\n")