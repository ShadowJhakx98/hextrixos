# kinect_processor.py
import cv2
import numpy as np
from simple_point_cloud import PointCloud

class KinectProcessor:
    def __init__(self):
        """Initialize the Kinect processor."""
        self.color_capture = None
        self.depth_capture = None
        
        # Camera parameters (these will need calibration for accurate results)
        self.fx = 525.0  # focal length x
        self.fy = 525.0  # focal length y
        self.cx = 319.5  # optical center x
        self.cy = 239.5  # optical center y
        
    def initialize_cameras(self, color_index=0, depth_index=1, max_attempts=3):
        """Initialize color and depth cameras with retry logic."""
        try:
            # Try to release any previously initialized cameras
            self.release()
            
            # Add retry mechanism
            for attempt in range(max_attempts):
                try:
                    self.color_capture = cv2.VideoCapture(color_index)
                    self.depth_capture = cv2.VideoCapture(depth_index)
                    
                    # Try to set high resolution
                    self.color_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                    self.color_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                    
                    # Read a test frame to verify camera works
                    ret_color, _ = self.color_capture.read()
                    ret_depth, _ = self.depth_capture.read()
                    
                    if not ret_color or not ret_depth:
                        print(f"Failed to read test frames from cameras (attempt {attempt+1}/{max_attempts})")
                        self.release()
                        if attempt < max_attempts - 1:
                            print(f"Retrying in 2 seconds...")
                            time.sleep(2)  # Wait before retrying
                            continue
                        else:
                            return False
                    
                    print(f"Successfully initialized cameras on attempt {attempt+1}")
                    return True
                    
                except Exception as e:
                    print(f"Error initializing cameras on attempt {attempt+1}: {e}")
                    self.release()
                    if attempt < max_attempts - 1:
                        print(f"Retrying in 2 seconds...")
                        time.sleep(2)  # Wait before retrying
                    
            return False
        except Exception as e:
            print(f"Error initializing cameras: {e}")
            self.release()
            return False
    
    def capture_frames(self):
        """Capture color and depth frames with error handling."""
        if not self.color_capture or not self.depth_capture:
            return None, None
        
        try:
            # Capture color frame
            ret_color, color_frame = self.color_capture.read()
            if not ret_color:
                return None, None
                
            # Capture depth frame
            ret_depth, depth_frame = self.depth_capture.read()
            if not ret_depth:
                return color_frame, None
                
            return color_frame, depth_frame
        except Exception as e:
            print(f"Error capturing frames: {e}")
            return None, None
    
    def convert_depth_to_point_cloud(self, depth_image, color_image=None, depth_scale=1000.0, max_depth=3.0):
        """Convert depth image to point cloud."""
        if depth_image is None:
            return None
            
        # Get image dimensions
        height, width = depth_image.shape[:2]
        
        # Create arrays for 3D points and colors
        points = []
        colors = []

        # Create meshgrid for pixel coordinates
        pixel_x, pixel_y = np.meshgrid(np.arange(width), np.arange(height))
        pixel_x = pixel_x.flatten()
        pixel_y = pixel_y.flatten()
        
        # Get depth values
        z = depth_image.flatten() / depth_scale  # Convert to meters
        
        # Filter out invalid depth values
        valid_indices = np.where((z > 0) & (z < max_depth))[0]
        
        # Safety check for empty valid_indices
        if len(valid_indices) == 0:
            return PointCloud()  # Return empty point cloud
            
        # Calculate 3D coordinates
        x = (pixel_x[valid_indices] - self.cx) * z[valid_indices] / self.fx
        y = (pixel_y[valid_indices] - self.cy) * z[valid_indices] / self.fy
        z = z[valid_indices]
        
        # Combine XYZ coordinates
        points = np.vstack([x, y, z]).T
        
        # Get colors if color image is available
        if color_image is not None:
            # Make sure color_image is the right shape for flattening
            if len(color_image.shape) == 3 and color_image.shape[0] == height and color_image.shape[1] == width:
                colors = color_image.reshape(-1, 3)[valid_indices]
            else:
                # Log a warning but continue without colors
                print(f"Warning: Color image shape {color_image.shape} doesn't match depth shape {depth_image.shape}")
        
        # Create point cloud
        point_cloud = PointCloud(points=points, colors=colors if len(colors) > 0 else None)
        
        return point_cloud
    
    def release(self):
        """Release camera resources."""
        if self.color_capture:
            self.color_capture.release()
        if self.depth_capture:
            self.depth_capture.release()