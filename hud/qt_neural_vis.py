#!/usr/bin/env python3
# Qt-based Neural Network Visualization using QtWebKit

import os
import sys
import time
import json
from urllib.parse import quote
from pathlib import Path

# Use the same GTK version as the main application (4.0)
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, GObject

# Create QApplication at module level to ensure it exists before any QWidgets
try:
    from PyQt5.QtCore import QUrl, Qt, QSize, QTimer
    from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
    from PyQt5.QtWebKitWidgets import QWebView
    from PyQt5.QtWebKit import QWebSettings
    from PyQt5.QtGui import QPixmap
    
    print("Successfully imported PyQt5 modules")
    
    # Initialize QApplication at module level
    if not QApplication.instance():
        print("Creating new QApplication instance")
        qt_app = QApplication(sys.argv)
    else:
        print("Using existing QApplication instance")
        qt_app = QApplication.instance()
        
    QTWEBKIT_AVAILABLE = True
    print("QtWebKit is available")
except ImportError as e:
    print(f"Failed to import Qt modules: {e}")
    print("QtWebKit is not available. Using fallback visualization.")
    QTWEBKIT_AVAILABLE = False
    qt_app = None

try:
    import cairo
except ImportError:
    print("Warning: Cairo not available for Qt/GTK rendering")
    cairo = None

# Import needed global imports if not already imported
if 'cairo' not in globals():
    try:
        import cairo
    except ImportError:
        print("Failed to import cairo for Qt-GTK bridge")
        cairo = None

class QtWebNeuralVisualization(QWidget):
    """Qt-based Neural Network Visualization"""
    
    def __init__(self):
        """Initialize the visualization widget"""
        print("Initializing QtWebNeuralVisualization")
        super().__init__(None, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # Set up transparency
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setStyleSheet("background: transparent;")
        
        # Create the layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Get the path to the HTML file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(script_dir)
        self.html_path = os.path.join(project_dir, "assets", "neural_vis", "index.html")
        print(f"HTML file path: {self.html_path}")
        
        # Check if the HTML file exists, create directory if needed
        html_dir = os.path.dirname(self.html_path)
        if not os.path.exists(html_dir):
            print(f"Creating HTML directory: {html_dir}")
            os.makedirs(html_dir, exist_ok=True)
        
        # Handle case when QtWebKit is not available
        if not QTWEBKIT_AVAILABLE:
            print("QtWebKit not available, creating fallback widget")
            self._create_fallback_widget()
            return
        
        # Create the WebView with optimized settings
        print("Creating WebView")
        self.webview = QWebView()
        self.webview.setStyleSheet("background: transparent;")
        
        # Make WebView transparent and non-interactive
        self.webview.setAttribute(Qt.WA_TranslucentBackground)
        self.webview.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.webview.setWindowFlags(Qt.FramelessWindowHint)
        
        # Optimize WebView performance
        print("Configuring WebView settings")
        settings = self.webview.settings()
        settings.setAttribute(QWebSettings.AcceleratedCompositingEnabled, True)
        settings.setAttribute(QWebSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebSettings.JavascriptCanOpenWindows, False)
        settings.setAttribute(QWebSettings.JavascriptCanCloseWindows, False)
        settings.setAttribute(QWebSettings.SpatialNavigationEnabled, False)
        settings.setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebSettings.WebGLEnabled, True)
        
        # Set transparency for older QtWebKit
        self.webview.page().mainFrame().setScrollBarPolicy(Qt.Horizontal, Qt.ScrollBarAlwaysOff)
        self.webview.page().mainFrame().setScrollBarPolicy(Qt.Vertical, Qt.ScrollBarAlwaysOff)
        
        # Set the transparent backgrounds
        self.webview.setStyleSheet("background: transparent; background-color: transparent;")
        
        # Add the webview to the layout
        print("Adding WebView to layout")
        self.layout.addWidget(self.webview)
        
        # Load HTML file with a short delay to ensure widget is properly set up
        print("Scheduling HTML content load")
        QTimer.singleShot(100, self._load_content)
        
        # Show the widget
        self.show()
        self.webview.show()
    
    def _load_content(self):
        """Load the visualization content with a slight delay for better stability"""
        if os.path.exists(self.html_path):
            print(f"Loading neural visualization from: {self.html_path}")
            url = QUrl.fromLocalFile(self.html_path)
            self.webview.load(url)
        else:
            # If file doesn't exist, create a basic visualization with inline HTML
            self._create_inline_visualization()
    
    def _create_fallback_widget(self):
        """Create a fallback widget when WebKit is not available"""
        label = QLabel("Neural network visualization requires QtWebKit support.")
        label.setStyleSheet("color: #00bfff; font-size: 14px;")
        label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label)
    
    def _create_inline_visualization(self):
        """Create a basic visualization using inline HTML when the file doesn't exist"""
        # Basic HTML with canvas visualization
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body, html {
                    margin: 0;
                    padding: 0;
                    width: 100%;
                    height: 100%;
                    overflow: hidden;
                    background-color: rgba(0, 0, 0, 0);
                }
                canvas {
                    display: block;
                    width: 100%;
                    height: 100%;
                }
            </style>
        </head>
        <body>
            <canvas id="canvas"></canvas>
            <script>
                const canvas = document.getElementById('canvas');
                const ctx = canvas.getContext('2d');
                
                // Set canvas dimensions
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
                
                // Animation parameters
                let animationFrame;
                let time = 0;
                
                // Draw function
                function draw() {
                    // Clear with transparent background
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    
                    // Draw neural network visualization
                    const centerX = canvas.width / 2;
                    const centerY = canvas.height / 2;
                    
                    // Draw pulsing nodes
                    for (let i = 0; i < 30; i++) {
                        const angle = (i / 30) * Math.PI * 2;
                        const radius = 100 + Math.sin(time + i * 0.2) * 20;
                        const x = centerX + Math.cos(angle) * radius;
                        const y = centerY + Math.sin(angle) * radius;
                        
                        // Pulsing effect
                        const pulse = Math.sin(time + i * 0.3) * 0.5 + 0.5;
                        
                        // Glow
                        const gradient = ctx.createRadialGradient(x, y, 0, x, y, 15);
                        gradient.addColorStop(0, `rgba(0, 191, 255, ${0.8 * pulse})`);
                        gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
                        
                        ctx.beginPath();
                        ctx.arc(x, y, 15, 0, Math.PI * 2);
                        ctx.fillStyle = gradient;
                        ctx.fill();
                        
                        // Node
                        ctx.beginPath();
                        ctx.arc(x, y, 3 + pulse * 2, 0, Math.PI * 2);
                        ctx.fillStyle = `rgba(255, 255, 255, ${0.7 + 0.3 * pulse})`;
                        ctx.fill();
                    }
                    
                    // Update time
                    time += 0.02;
                    
                    // Repeat
                    animationFrame = requestAnimationFrame(draw);
                }
                
                // Handle resize
                window.addEventListener('resize', () => {
                    canvas.width = window.innerWidth;
                    canvas.height = window.innerHeight;
                });
                
                // Start animation
                draw();
            </script>
        </body>
        </html>
        """
        self.webview.setHtml(html, QUrl("file:///"))
    
    def resizeEvent(self, event):
        """Handle resize events to update the visualization size"""
        super().resizeEvent(event)
        if hasattr(self, 'webview'):
            self.webview.resize(self.size())
    
    def generate_network(self, num_layers, nodes_per_layer, connections=None):
        """Generate a neural network with the given parameters"""
        if not hasattr(self, 'webview') or not QTWEBKIT_AVAILABLE:
            return
            
        # Create the network data structure
        network_data = {
            'layers': num_layers,
            'nodes': nodes_per_layer,
            'connections': connections or []
        }
        
        # Convert to JSON
        network_json = json.dumps(network_data)
        
        # Escape the JSON for JavaScript
        escaped_json = quote(network_json)
        
        # Call the JavaScript function
        js_code = f"if (typeof generateNetwork === 'function') {{ generateNetwork('{escaped_json}'); }}"
        self.webview.page().mainFrame().evaluateJavaScript(js_code)
    
    def update(self, values=None, connections=None):
        """Update the visualization with new values and connections"""
        if not hasattr(self, 'webview') or not QTWEBKIT_AVAILABLE:
            return
            
        # Create the update data
        update_data = {
            'values': values or [],
            'connections': connections or []
        }
        
        # Convert to JSON
        update_json = json.dumps(update_data)
        
        # Escape the JSON for JavaScript
        escaped_json = quote(update_json)
        
        # Call the JavaScript function
        js_code = f"if (typeof updateNetwork === 'function') {{ updateNetwork('{escaped_json}'); }}"
        self.webview.page().mainFrame().evaluateJavaScript(js_code)

# Create a GTK wrapper class to integrate with Hextrix OS
class QtToGtkWidget(Gtk.DrawingArea):
    """A GTK widget that wraps a Qt widget"""
    
    def __init__(self, qt_widget):
        """Initialize the widget with a Qt widget"""
        print("Initializing QtToGtkWidget")
        super().__init__()
        
        # Initialize Qt application if not already initialized at module level
        self.qapp = qt_app if qt_app else QApplication.instance()
        if not self.qapp and QTWEBKIT_AVAILABLE:
            print("Creating new QApplication in QtToGtkWidget")
            self.qapp = QApplication([])
            print("Warning: Creating QApplication inside QtToGtkWidget")
        
        # Store the Qt widget
        self.qt_widget = qt_widget
        
        # Ensure the widget is visible but doesn't steal focus
        if hasattr(self.qt_widget, 'setWindowFlags'):
            print("Setting window flags for Qt widget")
            self.qt_widget.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.ToolTip)
        
        # Connect signals
        print("Connecting GTK signals")
        self.connect("realize", self._on_realize)
        self.connect("draw", self._on_draw)
        self.connect("configure-event", self._on_configure)
        
        # Initialize size
        self.set_size_request(800, 600)
        
        # Set up a timer to process Qt events (roughly 60 FPS)
        self.last_process_time = time.time()
        print("Setting up Qt event processing timer")
        GLib.timeout_add(16, self._process_qt_events)
        
        # Set up a slower timer to check if Qt is alive
        print("Setting up Qt alive check timer")
        GLib.timeout_add(500, self._check_qt_alive)
        
        # Print diagnostic info
        if QTWEBKIT_AVAILABLE:
            print("Qt neural visualization widget initialized successfully")
    
    def _on_realize(self, widget):
        """Called when the widget is realized"""
        print("GTK widget realized")
        # Make sure the Qt widget is visible
        self.qt_widget.show()
        self.qt_widget.raise_()
        self.queue_draw()  # Force initial draw
        return True
        
    def _on_configure(self, widget, event):
        """Called when the widget is resized"""
        print(f"GTK widget configured: {event.width}x{event.height}")
        # Resize the Qt widget to match the GTK widget
        self.qt_widget.resize(event.width, event.height)
        self.queue_draw()  # Force redraw after resize
        return False
        
    def _on_draw(self, widget, context):
        """Draw the Qt widget on the GTK widget"""
        print("Drawing Qt widget on GTK context")
        # Process Qt events to make sure the widget is up to date
        self._process_qt_events()
        
        # Create a pixmap from the Qt widget
        size = self.get_allocation()
        print(f"Creating pixmap of size: {size.width}x{size.height}")
        pixmap = QPixmap(size.width, size.height)
        pixmap.fill(Qt.transparent)
        
        # Render the Qt widget to the pixmap
        print("Rendering Qt widget to pixmap")
        self.qt_widget.render(pixmap)
        
        # Convert the pixmap to a cairo surface
        if hasattr(pixmap, 'toImage'):
            qimage = pixmap.toImage()
        else:
            qimage = pixmap.convertToImage()
            
        # Create a cairo surface from the QImage
        try:
            print("Creating cairo surface from QImage")
            # Get access to the QImage data
            ptr = qimage.bits()
            if hasattr(ptr, 'setsize'):
                ptr.setsize(qimage.byteCount())
            
            # Create a cairo surface
            stride = qimage.bytesPerLine()
            format = cairo.FORMAT_ARGB32
            
            surface = cairo.ImageSurface.create_for_data(
                ptr, format, qimage.width(), qimage.height(), stride)
            
            # Draw the surface on the context
            print("Drawing surface on GTK context")
            context.set_source_surface(surface, 0, 0)
            context.paint()
        except Exception as e:
            print(f"Error rendering Qt widget to GTK: {e}")
        
        return False
    
    def _process_qt_events(self):
        """Process Qt events in the GTK main loop"""
        try:
            if QApplication.instance():
                QApplication.instance().processEvents()
                self.last_process_time = time.time()
        except Exception as e:
            print(f"Error processing Qt events: {e}")
        return True  # Continue the timer
    
    def _check_qt_alive(self):
        """Check if the Qt event processing is still working"""
        current_time = time.time()
        time_since_last_process = current_time - self.last_process_time
        
        # If it's been more than 500ms since we processed events, force an update
        if time_since_last_process > 0.5:
            print("Qt seems stuck, forcing event processing...")
            self._process_qt_events()
            self.queue_draw()  # Force a redraw
        
        return True  # Continue the timer

# Export a combined class for use in Hextrix
class WebNeuralVisualization(Gtk.Box):
    """Neural Network Visualization that can be used in GTK applications"""
    
    def __init__(self):
        """Initialize the visualization widget"""
        super(WebNeuralVisualization, self).__init__()
        
        # Create the Qt widget
        self.qt_widget = QtWebNeuralVisualization()
        
        # Create the bridge between Qt and GTK
        self.gtk_widget = QtToGtkWidget(self.qt_widget)
        
        # Add the GTK wrapper to this container
        self.add(self.gtk_widget)
        
        # Store network configuration
        self.network = None
        self.network_size = (800, 600)
        
        # Show all widgets
        self.show_all()
    
    def get_widget(self):
        """Return the GTK widget (for backwards compatibility)"""
        return self.gtk_widget
    
    def resize(self, width, height):
        """Resize the visualization widget"""
        self.network_size = (width, height)
        if hasattr(self, 'qt_widget'):
            self.qt_widget.resize(width, height)
        if hasattr(self, 'gtk_widget'):
            self.gtk_widget.set_size_request(width, height)
    
    def generate_network(self, num_layers, nodes_per_layer, connections=None):
        """Generate a neural network with the given parameters"""
        if hasattr(self, 'qt_widget'):
            self.qt_widget.generate_network(num_layers, nodes_per_layer, connections)
        self.network = {
            'layers': num_layers,
            'nodes': nodes_per_layer,
            'connections': connections
        }
    
    def update(self, values=None, connections=None):
        """Update the visualization with new values and connections"""
        if hasattr(self, 'qt_widget'):
            self.qt_widget.update(values, connections)
    
    def draw(self, cr, width, height):
        """Draw the visualization on a Cairo context - this is a no-op
        as the drawing is handled by QtToGtkWidget"""
        # This method is kept for compatibility but drawing is now 
        # handled automatically by the QtToGtkWidget
        pass
    
    def destroy(self):
        """Cleanup resources"""
        if hasattr(self, 'qt_widget'):
            self.qt_widget.close()
            self.qt_widget.deleteLater()
        super(WebNeuralVisualization, self).destroy()

# For testing the Qt widget directly
if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = QtWebNeuralVisualization()
    widget.resize(800, 600)
    widget.show()
    sys.exit(app.exec_()) 