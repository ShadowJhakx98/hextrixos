import gi
import os
import sys
from pathlib import Path

gi.require_version('Gtk', '4.0')
try:
    gi.require_version('WebKit', '6.0')  # Adjust to the correct version
    WEBKIT_AVAILABLE = True
except (ValueError, ImportError):
    print("WebKit support not available. Using fallback visualization.")
    WEBKIT_AVAILABLE = False

from gi.repository import Gtk
if WEBKIT_AVAILABLE:
    from gi.repository import WebKit

class WebNeuralVisualization(Gtk.Box):
    """Web-based Neural Network Visualization"""
    
    def __init__(self):
        """Initialize the visualization widget"""
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        
        # Get the path to the HTML file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(script_dir)
        self.html_path = os.path.join(project_dir, "assets", "neural_vis", "index.html")
        
        # Check if the HTML file exists, create directory if needed
        html_dir = os.path.dirname(self.html_path)
        if not os.path.exists(html_dir):
            os.makedirs(html_dir, exist_ok=True)
        
        if WEBKIT_AVAILABLE:
            self.webview = WebKit.WebView()
            self.webview.set_background_color(Gdk.RGBA(0, 0, 0, 0))
            
            if os.path.exists(self.html_path):
                file_uri = "file://" + self.html_path
                self.webview.load_uri(file_uri)
            else:
                self._create_inline_visualization()
            
            self.append(self.webview)
        else:
            self._create_fallback_widget()
    
    def _create_fallback_widget(self):
        """Create a fallback widget when WebKit is not available"""
        label = Gtk.Label()
        label.set_markup("<span foreground='#00bfff'>Neural network visualization requires WebKit support.</span>")
        label.set_justify(Gtk.Justification.CENTER)
        self.append(label)
    
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
        self.webview.load_html(html, "file:///")

# Main function for testing the widget independently
def main():
    win = Gtk.Window()
    win.connect("destroy", Gtk.main_quit)
    win.set_default_size(800, 600)
    
    # Set transparency
    win.set_opacity(0.0)  # This might not be necessary if the content is transparent
    
    vis = WebNeuralVisualization()
    win.add(vis)
    
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()