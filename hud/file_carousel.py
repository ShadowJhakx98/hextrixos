#!/usr/bin/env python3
# 3D File Carousel for Hextrix HUD

import os
import gi
import math
import cairo
import threading
import time
import subprocess
import tempfile
from PIL import Image, ImageOps
from io import BytesIO

gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf, Pango

class FileCarousel(Gtk.Box):
    """A 3D carousel for displaying files, images, and documents"""
    
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.set_hexpand(True)
        self.set_vexpand(True)
        
        # Carousel properties
        self.files = []
        self.current_index = 0
        self.rotation_angle = 0
        self.rotation_speed = 2.0
        self.is_rotating = False
        self.radius = 300
        self.item_width = 200
        self.item_height = 150
        self.perspective = 800
        
        # Create drawing area for the carousel
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_draw_func(self.on_draw)
        self.drawing_area.set_size_request(800, 400)
        self.drawing_area.set_hexpand(True)
        self.drawing_area.set_vexpand(True)
        
        # Create controls
        self.controls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.controls_box.set_halign(Gtk.Align.CENTER)
        self.controls_box.set_spacing(10)
        self.controls_box.set_margin_top(10)
        self.controls_box.set_margin_bottom(10)
        
        # Previous button
        self.prev_button = Gtk.Button.new_from_icon_name("go-previous-symbolic")
        self.prev_button.connect("clicked", self.on_prev_clicked)
        self.controls_box.append(self.prev_button)
        
        # Play/Pause button
        self.play_button = Gtk.Button.new_from_icon_name("media-playback-start-symbolic")
        self.play_button.connect("clicked", self.on_play_clicked)
        self.controls_box.append(self.play_button)
        
        # Next button
        self.next_button = Gtk.Button.new_from_icon_name("go-next-symbolic")
        self.next_button.connect("clicked", self.on_next_clicked)
        self.controls_box.append(self.next_button)
        
        # File info label
        self.info_label = Gtk.Label()
        self.info_label.set_markup("<span font='12'>No files to display</span>")
        self.info_label.set_margin_top(10)
        self.info_label.set_margin_bottom(10)
        self.info_label.set_ellipsize(Pango.EllipsizeMode.END)
        
        # Add components to the main box
        self.append(self.drawing_area)
        self.append(self.info_label)
        self.append(self.controls_box)
        
        # Setup animation timer
        self.timeout_id = None
        
        # File preview cache
        self.preview_cache = {}
        
    def set_files(self, files):
        """Set the files to display in the carousel"""
        self.files = files
        self.current_index = 0
        self.rotation_angle = 0
        self.preview_cache = {}
        
        # Update the info label
        if len(files) > 0:
            self.update_info_label()
        else:
            self.info_label.set_markup("<span font='12'>No files to display</span>")
        
        # Queue a redraw
        self.drawing_area.queue_draw()
        
        # Start animation if we have files
        if len(files) > 0 and not self.is_rotating:
            self.start_animation()
    
    def start_animation(self):
        """Start the carousel animation"""
        if self.timeout_id is None:
            self.timeout_id = GLib.timeout_add(16, self.update_animation)
            self.is_rotating = True
            self.play_button.set_icon_name("media-playback-pause-symbolic")
    
    def stop_animation(self):
        """Stop the carousel animation"""
        if self.timeout_id is not None:
            GLib.source_remove(self.timeout_id)
            self.timeout_id = None
            self.is_rotating = False
            self.play_button.set_icon_name("media-playback-start-symbolic")
    
    def update_animation(self):
        """Update the carousel animation"""
        if len(self.files) > 0:
            self.rotation_angle += self.rotation_speed
            if self.rotation_angle >= 360:
                self.rotation_angle -= 360
            
            # Update current index based on rotation
            items_angle = 360.0 / len(self.files)
            self.current_index = int((self.rotation_angle / items_angle) % len(self.files))
            
            # Update the info label
            self.update_info_label()
            
            # Queue a redraw
            self.drawing_area.queue_draw()
        
        return True  # Continue the animation
    
    def update_info_label(self):
        """Update the info label with the current file info"""
        if 0 <= self.current_index < len(self.files):
            file_info = self.files[self.current_index]
            if isinstance(file_info, dict):
                file_path = file_info.get('path', 'Unknown')
                file_name = os.path.basename(file_path)
                self.info_label.set_markup(f"<span font='12'>{file_name}</span>")
            else:
                self.info_label.set_markup(f"<span font='12'>{file_info}</span>")
    
    def on_draw(self, area, cr, width, height):
        """Draw the carousel"""
        # Clear the background
        cr.set_source_rgb(0.1, 0.1, 0.1)
        cr.paint()
        
        if len(self.files) == 0:
            return
        
        # Calculate center of the drawing area
        center_x = width / 2
        center_y = height / 2
        
        # Draw each file in the carousel
        items_angle = 360.0 / len(self.files)
        for i, file_info in enumerate(self.files):
            # Calculate the angle for this item
            angle = math.radians((self.rotation_angle + (i * items_angle)) % 360)
            
            # Calculate 3D position
            x = center_x + self.radius * math.sin(angle)
            z = self.radius * math.cos(angle)
            
            # Apply perspective
            scale = self.perspective / (self.perspective + z)
            x = center_x + (x - center_x) * scale
            y = center_y * scale
            
            # Calculate item dimensions with perspective
            item_width = self.item_width * scale
            item_height = self.item_height * scale
            
            # Draw the item
            self.draw_file_preview(cr, file_info, x - (item_width / 2), y - (item_height / 2), 
                                  item_width, item_height, scale, z > 0)
    
    def draw_file_preview(self, cr, file_info, x, y, width, height, scale, is_visible):
        """Draw a preview of the file"""
        if not is_visible:
            return
        
        # Get file path and content
        file_path = ""
        file_content = ""
        if isinstance(file_info, dict):
            file_path = file_info.get('path', '')
            file_content = file_info.get('content', '')
        else:
            file_path = str(file_info)
        
        # Draw a rounded rectangle background
        cr.save()
        cr.set_source_rgb(0.2, 0.2, 0.2)
        self.rounded_rectangle(cr, x, y, width, height, 10 * scale)
        cr.fill()
        
        # Get file name for the header
        file_name = os.path.basename(file_path)
        
        # Draw file name header
        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        header_font_size = 14 * scale
        cr.set_font_size(header_font_size)
        
        # Truncate file name if too long
        text_width = cr.text_extents(file_name)[2]
        if text_width > width - 20:
            while text_width > width - 20 and len(file_name) > 3:
                file_name = file_name[:-1]
                text_width = cr.text_extents(file_name + "...")[2]
            file_name += "..."
        
        # Draw the header
        cr.move_to(x + 10, y + 20)
        cr.show_text(file_name)
        
        # Check if this is a photo or video file
        _, ext = os.path.splitext(file_path.lower())
        is_photo = ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
        is_video = ext in ['.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv']
        
        # For photos, show the actual image
        if is_photo and os.path.exists(file_path):
            try:
                # Try to load the image
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(file_path, int(width - 20), int(height - 50), True)
                Gdk.cairo_set_source_pixbuf(cr, pixbuf, x + 10, y + 40)
                cr.paint()
            except Exception as e:
                # If loading fails, show error message
                cr.set_source_rgb(0.9, 0.9, 0.9)
                cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                font_size = 12 * scale
                cr.set_font_size(font_size)
                cr.move_to(x + 10, y + 60)
                cr.show_text(f"Image preview failed")
                cr.move_to(x + 10, y + 80)
                cr.show_text(f"Error: {str(e)}")
        
        # For videos, try to extract a thumbnail or show an icon
        elif is_video and os.path.exists(file_path):
            # First check if we have a cached thumbnail
            if file_path in self.preview_cache:
                pixbuf = self.preview_cache[file_path]
                Gdk.cairo_set_source_pixbuf(cr, pixbuf, x + 10, y + 40)
                cr.paint()
            else:
                # Try to extract a thumbnail using ffmpeg if available
                try:
                    # Create a temporary file for the thumbnail
                    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                        temp_path = temp_file.name
                    
                    # Use ffmpeg to extract the first frame
                    cmd = [
                        'ffmpeg', '-y', '-i', file_path, 
                        '-ss', '00:00:01.000', '-vframes', '1', 
                        '-vf', f'scale={int(width-20)}:{int(height-50)}:force_original_aspect_ratio=decrease',
                        temp_path
                    ]
                    
                    # Run the command with a timeout
                    process = subprocess.run(cmd, capture_output=True, timeout=2)
                    
                    if process.returncode == 0 and os.path.exists(temp_path):
                        # Load the thumbnail
                        pixbuf = GdkPixbuf.Pixbuf.new_from_file(temp_path)
                        self.preview_cache[file_path] = pixbuf
                        Gdk.cairo_set_source_pixbuf(cr, pixbuf, x + 10, y + 40)
                        cr.paint()
                        
                        # Clean up the temporary file
                        try:
                            os.unlink(temp_path)
                        except:
                            pass
                    else:
                        # If extraction failed, fall back to an icon
                        raise Exception("Thumbnail extraction failed")
                        
                except Exception as e:
                    # If thumbnail extraction fails, show a video icon
                    icon_pixbuf = self.generate_file_icon(file_path, int(width - 20), int(height - 50))
                    if icon_pixbuf:
                        # Draw the icon centered in the card
                        icon_x = x + (width - icon_pixbuf.get_width()) / 2
                        icon_y = y + 40
                        Gdk.cairo_set_source_pixbuf(cr, icon_pixbuf, icon_x, icon_y)
                        cr.paint()
        
        # For all other files, show content preview
        else:
            cr.set_source_rgb(0.9, 0.9, 0.9)
            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            font_size = 12 * scale
            cr.set_font_size(font_size)
            
            # If we have content from the search results, use that
            if file_content:
                # Split content into lines
                lines = file_content.split('\n')
                y_pos = y + 40  # Start below the header
                
                for line in lines:
                    if y_pos > y + height - 10:
                        break
                    
                    # Truncate line if too long
                    text_width = cr.text_extents(line)[2]
                    if text_width > width - 20:
                        while text_width > width - 20 and len(line) > 3:
                            line = line[:-1]
                            text_width = cr.text_extents(line + "...")[2]
                        line += "..."
                    
                    cr.move_to(x + 10, y_pos)
                    cr.show_text(line)
                    y_pos += font_size + 4
            
            # If no content and file exists, try to read from file
            elif os.path.exists(file_path) and os.path.isfile(file_path):
                try:
                    # Try to read text content
                    try:
                        with open(file_path, 'r', errors='ignore') as f:
                            lines = [line.strip() for line in f.readlines()[:10]]
                        
                        y_pos = y + 40  # Start below the header
                        for line in lines:
                            if y_pos > y + height - 10:
                                break
                            
                            # Truncate line if too long
                            text_width = cr.text_extents(line)[2]
                            if text_width > width - 20:
                                while text_width > width - 20 and len(line) > 3:
                                    line = line[:-1]
                                    text_width = cr.text_extents(line + "...")[2]
                                line += "..."
                            
                            cr.move_to(x + 10, y_pos)
                            cr.show_text(line)
                            y_pos += font_size + 4
                    except Exception as e:
                        cr.move_to(x + 10, y + 60)
                        cr.show_text(f"Content preview not available")
                        cr.move_to(x + 10, y + 80)
                        cr.show_text(f"Error: {str(e)}")
                except Exception as e:
                    cr.move_to(x + 10, y + 60)
                    cr.show_text(f"Preview not available")
                    cr.move_to(x + 10, y + 80)
                    cr.show_text(f"Error: {str(e)}")
            else:
                # Just show the file path
                cr.move_to(x + 10, y + 60)
                cr.show_text("File not accessible")
                cr.move_to(x + 10, y + 80)
                cr.show_text(file_path)
        
        # Draw a border around the current item
        if self.files[self.current_index] == file_info:
            cr.set_source_rgb(0.0, 0.7, 1.0)
            cr.set_line_width(3 * scale)
            self.rounded_rectangle(cr, x, y, width, height, 10 * scale)
            cr.stroke()
        
        cr.restore()
    
    def generate_file_preview(self, file_path, width, height):
        """Generate a preview for the file based on its type"""
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return None
            
            # Get file extension
            _, ext = os.path.splitext(file_path.lower())
            
            # Handle image files
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                return self.generate_image_preview(file_path, width, height)
            
            # Handle PDF files
            elif ext == '.pdf':
                return self.generate_pdf_preview(file_path, width, height)
            
            # Handle text files
            elif ext in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml']:
                return self.generate_text_preview(file_path, width, height)
            
            # Default file icon
            return self.generate_file_icon(file_path, width, height)
            
        except Exception as e:
            print(f"Error generating preview for {file_path}: {e}")
            return None
    
    def generate_image_preview(self, file_path, width, height):
        """Generate a preview for an image file"""
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(file_path, width, height, True)
            return pixbuf
        except Exception as e:
            print(f"Error generating image preview: {e}")
            return None
    
    def generate_pdf_preview(self, file_path, width, height):
        """Generate a preview for a PDF file"""
        # This would require poppler or another PDF rendering library
        # For now, just return a PDF icon
        return self.generate_file_icon(file_path, width, height, "application-pdf")
    
    def generate_text_preview(self, file_path, width, height):
        """Generate a preview for a text file"""
        try:
            # Create a surface to draw on
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            cr = cairo.Context(surface)
            
            # Fill background
            cr.set_source_rgb(1, 1, 1)
            cr.paint()
            
            # Draw text content
            cr.set_source_rgb(0, 0, 0)
            cr.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            cr.set_font_size(12)
            
            # Read the first few lines of the file
            with open(file_path, 'r', errors='ignore') as f:
                lines = [line.rstrip() for line in f.readlines()[:20]]
            
            # Draw each line
            y = 20
            for line in lines:
                if y > height - 10:
                    break
                cr.move_to(10, y)
                # Truncate line if too long
                if cr.text_extents(line)[2] > width - 20:
                    while cr.text_extents(line + "...")[2] > width - 20 and len(line) > 0:
                        line = line[:-1]
                    line += "..."
                cr.show_text(line)
                y += 18
            
            # Convert to pixbuf
            surface.flush()
            data = surface.get_data()
            
            # Create pixbuf from data
            pixbuf = GdkPixbuf.Pixbuf.new_from_data(
                data, GdkPixbuf.Colorspace.RGB, True, 8,
                width, height, surface.get_stride()
            )
            
            return pixbuf
        except Exception as e:
            print(f"Error generating text preview: {e}")
            return self.generate_file_icon(file_path, width, height, "text-x-generic")
    
    def generate_file_icon(self, file_path, width, height, icon_name=None):
        """Generate a generic file icon"""
        try:
            # Create a surface to draw on
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            cr = cairo.Context(surface)
            
            # Fill background with a color based on file type
            _, ext = os.path.splitext(file_path.lower())
            
            # Choose color based on file type
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                cr.set_source_rgb(0.2, 0.6, 0.2)  # Green for images
            elif ext == '.pdf':
                cr.set_source_rgb(0.8, 0.2, 0.2)  # Red for PDFs
            elif ext in ['.doc', '.docx', '.txt', '.md']:
                cr.set_source_rgb(0.2, 0.2, 0.8)  # Blue for documents
            elif ext in ['.py', '.js', '.html', '.css', '.json', '.xml']:
                cr.set_source_rgb(0.8, 0.6, 0.2)  # Orange for code
            elif ext in ['.mp3', '.wav', '.ogg', '.flac']:
                cr.set_source_rgb(0.6, 0.2, 0.6)  # Purple for audio
            elif ext in ['.mp4', '.mkv', '.avi', '.mov', '.webm']:
                cr.set_source_rgb(0.2, 0.6, 0.6)  # Teal for video
            else:
                cr.set_source_rgb(0.5, 0.5, 0.5)  # Gray for others
            
            # Draw a rounded rectangle
            self.rounded_rectangle(cr, 0, 0, width, height, 10)
            cr.fill()
            
            # Draw file extension text
            cr.set_source_rgb(1, 1, 1)
            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            font_size = width / 5
            cr.set_font_size(font_size)
            
            # Use the file extension as the text
            ext_text = ext[1:].upper() if ext else "FILE"
            
            # Center the text
            text_extents = cr.text_extents(ext_text)
            text_x = (width - text_extents[2]) / 2
            text_y = (height + text_extents[3]) / 2
            
            cr.move_to(text_x, text_y)
            cr.show_text(ext_text)
            
            # Convert to pixbuf
            surface.flush()
            data = surface.get_data()
            
            # Create pixbuf from data
            pixbuf = GdkPixbuf.Pixbuf.new_from_data(
                data, GdkPixbuf.Colorspace.RGB, True, 8,
                width, height, surface.get_stride()
            )
            
            return pixbuf
        except Exception as e:
            print(f"Error generating file icon: {e}")
            return None
    
    def rounded_rectangle(self, cr, x, y, width, height, radius):
        """Draw a rounded rectangle"""
        degrees = math.pi / 180.0
        
        cr.new_sub_path()
        cr.arc(x + width - radius, y + radius, radius, -90 * degrees, 0 * degrees)
        cr.arc(x + width - radius, y + height - radius, radius, 0 * degrees, 90 * degrees)
        cr.arc(x + radius, y + height - radius, radius, 90 * degrees, 180 * degrees)
        cr.arc(x + radius, y + radius, radius, 180 * degrees, 270 * degrees)
        cr.close_path()
    
    def on_prev_clicked(self, button):
        """Handle previous button click"""
        if len(self.files) > 0:
            # Calculate the target angle for the previous item
            items_angle = 360.0 / len(self.files)
            target_index = (self.current_index - 1) % len(self.files)
            target_angle = target_index * items_angle
            
            # Adjust rotation angle
            self.rotation_angle = target_angle
            self.current_index = target_index
            
            # Update the info label
            self.update_info_label()
            
            # Queue a redraw
            self.drawing_area.queue_draw()
    
    def on_next_clicked(self, button):
        """Handle next button click"""
        if len(self.files) > 0:
            # Calculate the target angle for the next item
            items_angle = 360.0 / len(self.files)
            target_index = (self.current_index + 1) % len(self.files)
            target_angle = target_index * items_angle
            
            # Adjust rotation angle
            self.rotation_angle = target_angle
            self.current_index = target_index
            
            # Update the info label
            self.update_info_label()
            
            # Queue a redraw
            self.drawing_area.queue_draw()
    
    def on_play_clicked(self, button):
        """Handle play/pause button click"""
        if self.is_rotating:
            self.stop_animation()
        else:
            self.start_animation()
    
    def get_current_file(self):
        """Get the currently selected file"""
        if len(self.files) > 0 and 0 <= self.current_index < len(self.files):
            return self.files[self.current_index]
        return None
    
    def open_current_file(self):
        """Open the currently selected file"""
        current_file = self.get_current_file()
        if current_file:
            file_path = current_file.get('path', '') if isinstance(current_file, dict) else str(current_file)
            if os.path.exists(file_path):
                # Use xdg-open to open the file with the default application
                subprocess.Popen(['xdg-open', file_path]) 