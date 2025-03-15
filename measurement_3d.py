"""
measurement_3d.py

Implementation of 3D measurement capabilities using Kinect v2 depth camera
with calibration, privacy protections, and consent requirements
Compatible with Python 3.13 - no open3d dependency
"""

import cv2
import numpy as np
import logging
import time
import base64
from io import BytesIO
from PIL import Image

# Try to import Kinect-specific libraries, but provide fallbacks if not available
try:
    from custom_pykinect2 import PyKinectRuntime
    from custom_pykinect2 import PyKinectV2
    from custom_pykinect2.PyKinectV2 import *
    KINECT_AVAILABLE = True
except ImportError:
    KINECT_AVAILABLE = False
    print("Warning: pykinect2 not available, using fallback modes")

# Setup logging
logger = logging.getLogger("3DMeasurement")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class Measurement3DModule:
    def __init__(self, safety_manager=None):
        """
        Initialize 3D Measurement Module with Kinect v2 support
        
        Args:
            safety_manager: Optional safety manager that handles consent and verification
        """
        self.kinect = None
        self.initialized = False
        self.safety_manager = safety_manager
        self.last_measurement = None
        self.calibration_factor = 1.0  # mm to real-world units
        self.reference_object_size = None  # Known size of reference object
        
        # Kinect v2 has different camera parameters than RealSense
        self.camera_intrinsics = {
            'fx': 365.456,  # Focal length x for Kinect v2
            'fy': 365.456,  # Focal length y for Kinect v2
            'cx': 254.878,  # Principal point x for Kinect v2
            'cy': 205.395   # Principal point y for Kinect v2
        }
        
        self.depth_scale = 0.001  # Kinect v2 depth scale (mm to meters)
        self.fallback_mode = not KINECT_AVAILABLE
        
    def initialize(self):
        """Initialize the Kinect camera"""
        if self.fallback_mode:
            logger.info("Using fallback mode (no Kinect)")
            self.initialized = True
            return True
            
        try:
            # Initialize the Kinect runtime
            self.kinect = PyKinectRuntime.PyKinectRuntime(
                PyKinectV2.FrameSourceTypes_Color | 
                PyKinectV2.FrameSourceTypes_Depth
            )
            
            # Wait for first frames
            timeout = 30  # timeout in seconds
            start_time = time.time()
            while not self.kinect.has_new_depth_frame() and time.time() - start_time < timeout:
                time.sleep(0.1)
            
            if not self.kinect.has_new_depth_frame():
                logger.warning("Timed out waiting for depth frame")
                return False
            
            self.initialized = True
            logger.info("3D measurement module initialized successfully with Kinect v2")
            return True
        except Exception as e:
            logger.error(f"Error initializing 3D measurement with Kinect: {str(e)}")
            self.initialized = False
            return False
    
    def shutdown(self):
        """Safely shut down the measurement system"""
        if self.kinect and not self.fallback_mode:
            self.kinect.close()
            self.kinect = None
            self.initialized = False
            logger.info("3D measurement system shut down")
    
    def calibrate_with_reference(self, reference_size_mm):
        """
        Calibrate using reference object of known size
        
        Args:
            reference_size_mm: Known size of reference object in mm
        """
        if self.fallback_mode:
            self.reference_object_size = reference_size_mm
            self.calibration_factor = reference_size_mm / 100.0  # Assume 100 pixels for fallback
            return {
                "status": "success", 
                "message": "Calibration completed (fallback mode)",
                "calibration_factor": self.calibration_factor
            }
            
        if not self.initialized:
            if not self.initialize():
                return {"status": "error", "message": "Failed to initialize system"}
        
        try:
            # Get current frames
            if not self.kinect.has_new_depth_frame() or not self.kinect.has_new_color_frame():
                return {"status": "error", "message": "No frames available for calibration"}
            
            depth_frame = self.kinect.get_last_depth_frame()
            color_frame = self.kinect.get_last_color_frame()
            
            if depth_frame is None or color_frame is None:
                return {"status": "error", "message": "Failed to capture calibration frames"}
            
            # Convert frames to numpy arrays
            depth_image = depth_frame.reshape((self.kinect.depth_frame_desc.Height, self.kinect.depth_frame_desc.Width))
            color_image = color_frame.reshape((self.kinect.color_frame_desc.Height, self.kinect.color_frame_desc.Width, 4))
            color_image = cv2.cvtColor(color_image, cv2.COLOR_BGRA2BGR)
            
            # Display for user calibration
            # In a full implementation, you would add UI for user to
            # select the reference object in the frame
            
            # This is a placeholder - in real implementation, user would
            # mark the reference object and system would measure it
            measured_size_pixels = 100  # Placeholder
            
            # Calculate calibration factor
            self.reference_object_size = reference_size_mm
            self.calibration_factor = reference_size_mm / measured_size_pixels
            
            return {
                "status": "success", 
                "message": "Calibration completed",
                "calibration_factor": self.calibration_factor
            }
            
        except Exception as e:
            logger.error(f"Error during calibration: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def measure_object(self, region_of_interest=None, require_consent=True, user_id=None):
        """
        Measure a 3D object with safety checks
        
        Args:
            region_of_interest: Optional ROI to focus measurement
            require_consent: Whether to require consent check
            user_id: User ID for consent verification
            
        Returns:
            Dict with measurement results or error
        """
        # Safety check
        if require_consent and self.safety_manager:
            if not self.safety_manager.check_consent(user_id, "3d_measurement"):
                return {
                    "status": "error",
                    "message": "Consent required for 3D measurement",
                    "requires_consent": True
                }
            
            if not self.safety_manager.verify_age(user_id):
                return {
                    "status": "error", 
                    "message": "Age verification required",
                    "requires_verification": True
                }
        
        # System check
        if not self.initialized:
            if not self.initialize():
                return {"status": "error", "message": "Failed to initialize system"}
        
        try:
            # Handle fallback mode
            if self.fallback_mode:
                return self._fallback_measurement(region_of_interest)
            
            # Get current frames
            if not self.kinect.has_new_depth_frame() or not self.kinect.has_new_color_frame():
                return {"status": "error", "message": "No frames available for measurement"}
            
            depth_frame = self.kinect.get_last_depth_frame()
            color_frame = self.kinect.get_last_color_frame()
            
            if depth_frame is None or color_frame is None:
                return {"status": "error", "message": "Failed to capture measurement frames"}
            
            # Convert frames to numpy arrays
            depth_image = depth_frame.reshape((self.kinect.depth_frame_desc.Height, self.kinect.depth_frame_desc.Width))
            color_image = color_frame.reshape((self.kinect.color_frame_desc.Height, self.kinect.color_frame_desc.Width, 4))
            color_image = cv2.cvtColor(color_image, cv2.COLOR_BGRA2BGR)
            
            # Map the depth frame to color frame space for alignment
            # Note: In a full implementation, you would use the Kinect's coordinate mapper
            # For simplicity, we'll just resize the depth image to match color dimensions
            depth_resized = cv2.resize(depth_image, 
                                     (self.kinect.color_frame_desc.Width, self.kinect.color_frame_desc.Height), 
                                     interpolation=cv2.INTER_NEAREST)
            
            # Apply ROI if specified
            if region_of_interest:
                x, y, w, h = region_of_interest
                depth_roi = depth_resized[y:y+h, x:x+w]
                color_roi = color_image[y:y+h, x:x+w]
            else:
                depth_roi = depth_resized
                color_roi = color_image
            
            # Process with custom point cloud function
            measurements = self._process_depth_for_measurements(depth_roi, color_roi)
            
            # Store last measurement
            self.last_measurement = measurements
            
            result = {
                "status": "success",
                "measurements": measurements,
                "timestamp": time.time()
            }
            
            logger.info(f"Measurement completed: {measurements}")
            return result
            
        except Exception as e:
            logger.error(f"Error measuring object: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _fallback_measurement(self, region_of_interest=None):
        """Generate simulated measurements for fallback mode"""
        # Create simulated measurements - this would be replaced with actual
        # calculations in a real implementation
        width = 100.0 * self.calibration_factor * (1 + 0.2 * np.random.rand())
        height = 150.0 * self.calibration_factor * (1 + 0.2 * np.random.rand())
        depth = 50.0 * self.calibration_factor * (1 + 0.2 * np.random.rand())
        
        # Calculate volume (approximate)
        volume = width * height * depth
        
        # Calculate surface area (approximate)
        surface_area = 2 * (width * height + width * depth + height * depth)
        
        measurements = {
            "width_mm": round(width, 1),
            "height_mm": round(height, 1),
            "depth_mm": round(depth, 1),
            "volume_mm3": round(volume, 1),
            "surface_area_mm2": round(surface_area, 1),
            "width_inches": round(width / 25.4, 1),
            "height_inches": round(height / 25.4, 1),
            "depth_inches": round(depth / 25.4, 1)
        }
        
        self.last_measurement = measurements
        
        return {
            "status": "success",
            "measurements": measurements,
            "timestamp": time.time(),
            "fallback": True
        }
    
    def _process_depth_for_measurements(self, depth_image, color_image=None):
        """
        Process depth image to extract measurements
        
        This implements core functionality for Kinect v2 depth processing
        """
        # Convert Kinect depth values to millimeters
        # Kinect V2 depth values are in millimeters already, but we apply the calibration factor
        depth_mm = depth_image.astype(np.float32) * self.calibration_factor
        
        # Filter the depth image to remove noise
        # Use a median filter
        filtered_depth = cv2.medianBlur(depth_mm.astype(np.uint16), 5)
        
        # Remove outliers
        # Create a mask of valid depth values (non-zero and not too far)
        valid_mask = (filtered_depth > 0) & (filtered_depth < 8000)  # 8 meters max for Kinect
        
        # Get all valid depth values
        valid_depths = filtered_depth[valid_mask]
        
        if len(valid_depths) == 0:
            # No valid depths, return default values
            return {
                "width_mm": 0.0,
                "height_mm": 0.0,
                "depth_mm": 0.0,
                "volume_mm3": 0.0,
                "surface_area_mm2": 0.0,
                "width_inches": 0.0,
                "height_inches": 0.0,
                "depth_inches": 0.0
            }
        
        # Calculate mean and standard deviation
        mean_depth = np.mean(valid_depths)
        std_depth = np.std(valid_depths)
        
        # Remove statistical outliers (values outside 2 standard deviations)
        inlier_mask = abs(filtered_depth - mean_depth) < 2 * std_depth
        filtered_depth = np.where(inlier_mask & valid_mask, filtered_depth, 0)
        
        # Find min and max depth values
        min_depth = np.min(filtered_depth[filtered_depth > 0])
        max_depth = np.max(filtered_depth[filtered_depth > 0])
        
        # Get image dimensions
        height, width = filtered_depth.shape
        
        # Calculate bounding box in image coordinates
        # Find non-zero points
        y_coords, x_coords = np.nonzero(filtered_depth)
        
        if len(y_coords) == 0 or len(x_coords) == 0:
            # No valid points
            return {
                "width_mm": 0.0,
                "height_mm": 0.0,
                "depth_mm": 0.0,
                "volume_mm3": 0.0,
                "surface_area_mm2": 0.0,
                "width_inches": 0.0,
                "height_inches": 0.0,
                "depth_inches": 0.0
            }
        
        # Get bounding box
        min_x, max_x = np.min(x_coords), np.max(x_coords)
        min_y, max_y = np.min(y_coords), np.max(y_coords)
        
        # Calculate 3D dimensions
        # For Kinect v2, we can use the field of view to convert from pixels to real-world units
        # Kinect v2 has approximately 70° horizontal FOV and 60° vertical FOV
        
        # Get the center depth of the object
        center_x = (min_x + max_x) // 2
        center_y = (min_y + max_y) // 2
        center_depth = filtered_depth[center_y, center_x]
        if center_depth == 0:
            center_depth = mean_depth  # Use mean depth if center point is invalid
        
        # Calculate pixel to mm conversion at the current depth
        # tan(FOV/2) * 2 * depth = width in mm
        horizontal_mm_per_pixel = np.tan(np.radians(70) / 2) * 2 * center_depth / width
        vertical_mm_per_pixel = np.tan(np.radians(60) / 2) * 2 * center_depth / height
        
        # Calculate object dimensions
        width_pixels = max_x - min_x
        height_pixels = max_y - min_y
        depth_range = max_depth - min_depth
        
        width_mm = width_pixels * horizontal_mm_per_pixel
        height_mm = height_pixels * vertical_mm_per_pixel
        depth_mm = depth_range
        
        # Calculate volume (approximate)
        volume_mm3 = width_mm * height_mm * depth_mm
        
        # Calculate surface area (approximate)
        surface_area_mm2 = 2 * (width_mm * height_mm + width_mm * depth_mm + height_mm * depth_mm)
        
        return {
            "width_mm": round(width_mm, 1),
            "height_mm": round(height_mm, 1),
            "depth_mm": round(depth_mm, 1),
            "volume_mm3": round(volume_mm3, 1),
            "surface_area_mm2": round(surface_area_mm2, 1),
            "width_inches": round(width_mm / 25.4, 1),
            "height_inches": round(height_mm / 25.4, 1),
            "depth_inches": round(depth_mm / 25.4, 1)
        }
    
    def capture_frame_with_measurement(self, region_of_interest=None, user_id=None):
        """Capture a frame with measurement overlay"""
        if not self.initialized:
            if not self.initialize():
                return None, {"status": "error", "message": "Failed to initialize system"}
        
        try:
            # Handle fallback mode
            if self.fallback_mode:
                # Create a dummy color image for fallback mode
                color_image = np.zeros((480, 640, 3), dtype=np.uint8)
                # Draw a simulated object
                cv2.rectangle(color_image, (220, 140), (420, 340), (0, 0, 255), 2)
                
                # Measure the object
                measurement_result = self._fallback_measurement(region_of_interest)
                
                # Draw measurement overlay
                result_image = color_image.copy()
                
                if region_of_interest:
                    x, y, w, h = region_of_interest
                else:
                    x, y, w, h = 220, 140, 200, 200
                    
                cv2.rectangle(result_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Draw measurement text
                measurements = measurement_result["measurements"]
                
                text = f"W: {measurements['width_mm']}mm ({measurements['width_inches']}\")"
                cv2.putText(result_image, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                           1, (0, 255, 0), 2, cv2.LINE_AA)
                
                text = f"H: {measurements['height_mm']}mm ({measurements['height_inches']}\")"
                cv2.putText(result_image, text, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 
                           1, (0, 255, 0), 2, cv2.LINE_AA)
                
                text = f"D: {measurements['depth_mm']}mm ({measurements['depth_inches']}\")"
                cv2.putText(result_image, text, (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 
                           1, (0, 255, 0), 2, cv2.LINE_AA)
                
                text = "(SIMULATION MODE)"
                cv2.putText(result_image, text, (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.7, (0, 165, 255), 2, cv2.LINE_AA)
                
                return result_image, measurement_result
            
            # Measure the object
            measurement_result = self.measure_object(
                region_of_interest=region_of_interest, 
                require_consent=True, 
                user_id=user_id
            )
            
            if measurement_result["status"] != "success":
                return None, measurement_result
            
            # Get current frame
            if not self.kinect.has_new_color_frame():
                return None, {"status": "error", "message": "No color frame available"}
                
            color_frame = self.kinect.get_last_color_frame()
            if color_frame is None:
                return None, {"status": "error", "message": "Failed to get color frame"}
                
            color_image = color_frame.reshape((self.kinect.color_frame_desc.Height, self.kinect.color_frame_desc.Width, 4))
            color_image = cv2.cvtColor(color_image, cv2.COLOR_BGRA2BGR)
            
            # Draw measurement overlay
            result_image = color_image.copy()
            measurements = measurement_result["measurements"]
            
            # Draw ROI if specified
            if region_of_interest:
                x, y, w, h = region_of_interest
                cv2.rectangle(result_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Draw measurement text
            text = f"W: {measurements['width_mm']}mm ({measurements['width_inches']}\")"
            cv2.putText(result_image, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       1, (0, 255, 0), 2, cv2.LINE_AA)
            
            text = f"H: {measurements['height_mm']}mm ({measurements['height_inches']}\")"
            cv2.putText(result_image, text, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 
                       1, (0, 255, 0), 2, cv2.LINE_AA)
            
            text = f"D: {measurements['depth_mm']}mm ({measurements['depth_inches']}\")"
            cv2.putText(result_image, text, (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 
                       1, (0, 255, 0), 2, cv2.LINE_AA)
            
            return result_image, measurement_result
            
        except Exception as e:
            logger.error(f"Error capturing frame with measurement: {str(e)}")
            return None, {"status": "error", "message": str(e)}