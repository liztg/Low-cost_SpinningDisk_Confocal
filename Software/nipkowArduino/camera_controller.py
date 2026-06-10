"""
Camera Controller Module
Detects USB cameras and captures images with manual exposure control.
Supports image averaging and summing operations.
"""

import cv2
import numpy as np
import time
from datetime import datetime
from typing import List, Tuple, Optional, Dict

class CameraController:
    def __init__(self):
        """Initialize camera controller."""
        self.camera = None
        self.camera_index = None
        self.last_capture_stats = None  # Store timing statistics
        
    def detect_cameras(self) -> List[int]:
        """
        Detect all available USB cameras.
        
        Returns:
            List of camera indices that are available
        """
        available_cameras = []
        
        # Check first 10 possible camera indices
        for i in range(10):
            cap = cv2.VideoCapture(i, cv2.CAP_V4L2)  # CAP_V4L2 for Linux
            if cap.isOpened():
                available_cameras.append(i)
                cap.release()
        
        return available_cameras
    
    def connect_camera(self, camera_index: Optional[int] = None) -> bool:
        """
        Connect to a USB camera.
        
        Args:
            camera_index: Specific camera index, or None to auto-detect
            
        Returns:
            True if connection successful, False otherwise
        """
        if camera_index is None:
            cameras = self.detect_cameras()
            if not cameras:
                print("No cameras detected")
                return False
            camera_index = cameras[0]
            print(f"Auto-detected camera at index {camera_index}")
        
        self.camera = cv2.VideoCapture(camera_index, cv2.CAP_V4L2)
        
        if not self.camera.isOpened():
            print(f"Failed to open camera {camera_index}")
            return False
        
        self.camera_index = camera_index
        print(f"Connected to camera {camera_index}")
        
        # Set resolution to 1080p by default
        self.set_resolution(1280, 720)
        
        return True
    
    def set_resolution(self, width: int, height: int) -> bool:
        """
        Set camera resolution.
        
        Args:
            width: Image width in pixels
            height: Image height in pixels
            
        Returns:
            True if successful
        """
        if self.camera is None:
            print("Camera not connected")
            return False
        
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        # Verify the resolution was set
        actual_width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"Resolution set to {actual_width}x{actual_height}")
        
        if actual_width != width or actual_height != height:
            print(f"Warning: Requested {width}x{height}, but camera set to {actual_width}x{actual_height}")
            return False
        
        return True
    
    def set_exposure(self, exposure_time: float) -> bool:
        """
        Set manual exposure time.
        
        Args:
            exposure_time: Exposure time in milliseconds (negative values for manual mode)
            
        Returns:
            True if successful
        """
        if self.camera is None:
            print("Camera not connected")
            return False
        
        # Disable auto exposure
        self.camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.50)  # 0.25 = manual mode
        
        # Set exposure (OpenCV uses log scale, negative for manual)
        # Convert ms to OpenCV exposure value
        exposure_value = -int(np.log2(exposure_time / 1000.0))
        self.camera.set(cv2.CAP_PROP_EXPOSURE, exposure_value)
        
        print(f"Exposure set to {exposure_time} ms")
        return True
    
    def capture_image(self) -> Optional[np.ndarray]:
        """
        Capture a single image.
        
        Returns:
            Image as numpy array (BGR format) or None if failed
        """
        if self.camera is None:
            print("Camera not connected")
            return None
        
        ret, frame = self.camera.read()
        
        if not ret:
            print("Failed to capture image")
            return None
        
        return frame
    
    def capture_multiple(self, num_images: int, exposure_time: float, 
                        delay_between: float = 0.5) -> Tuple[List[np.ndarray], Dict]:
        """
        Capture multiple images with specified exposure and measure timing.
        
        Args:
            num_images: Number of images to capture
            exposure_time: Exposure time in milliseconds
            delay_between: Delay between captures in seconds
            
        Returns:
            Tuple of (List of captured images, timing statistics dict)
        """
        if not self.set_exposure(exposure_time):
            return [], {}
        
        # Wait for camera to adjust
        time.sleep(0.5)
        
        images = []
        capture_times = []  # Store individual capture timestamps
        interval_times = []  # Store time between consecutive captures
        
        print(f"\nCapturing {num_images} images with timing measurement...")
        print("="*60)
        
        burst_start = time.perf_counter()  # High precision timer
        last_capture_time = None
        
        for i in range(num_images):
            capture_start = time.perf_counter()
            
            img = self.capture_image()
            
            capture_end = time.perf_counter()
            capture_duration = (capture_end - capture_start) * 1000  # Convert to ms
            
            if img is not None:
                images.append(img)
                capture_times.append(capture_duration)
                
                # Calculate interval from previous capture
                if last_capture_time is not None:
                    interval = (capture_start - last_capture_time) * 1000  # ms
                    interval_times.append(interval)
                    print(f"  Image {i+1}/{num_images} | "
                          f"Capture: {capture_duration:.2f}ms | "
                          f"Interval: {interval:.2f}ms")
                else:
                    print(f"  Image {i+1}/{num_images} | "
                          f"Capture: {capture_duration:.2f}ms | "
                          f"Interval: N/A (first)")
                
                last_capture_time = capture_end
                
                if i < num_images - 1:  # Don't delay after last image
                    time.sleep(delay_between)
            else:
                print(f"  [ERROR] Failed to capture image {i+1}")
        
        burst_end = time.perf_counter()
        total_time = (burst_end - burst_start) * 1000  # Convert to ms
        
        # Calculate statistics
        stats = {
            'total_images': len(images),
            'requested_images': num_images,
            'total_time_ms': total_time,
            'total_time_s': total_time / 1000,
            'capture_times_ms': capture_times,
            'interval_times_ms': interval_times,
            'avg_capture_time_ms': np.mean(capture_times) if capture_times else 0,
            'min_capture_time_ms': np.min(capture_times) if capture_times else 0,
            'max_capture_time_ms': np.max(capture_times) if capture_times else 0,
            'avg_interval_ms': np.mean(interval_times) if interval_times else 0,
            'min_interval_ms': np.min(interval_times) if interval_times else 0,
            'max_interval_ms': np.max(interval_times) if interval_times else 0,
            'fps_effective': (len(images) / (total_time / 1000)) if total_time > 0 else 0
        }
        
        self.last_capture_stats = stats
        self._print_capture_statistics(stats)
        
        return images, stats
    
    def average_images(self, images: List[np.ndarray]) -> Optional[np.ndarray]:
        """
        Average multiple images.
        
        Args:
            images: List of images to average
            
        Returns:
            Averaged image or None if list is empty
        """
        if not images:
            print("No images to average")
            return None
        
        print(f"Averaging {len(images)} images...")
        
        # Convert to float for accurate averaging
        avg_image = np.mean(images, axis=0).astype(np.uint8)
        
        print("Averaging complete")
        return avg_image
    
    def sum_images(self, images: List[np.ndarray], normalize: bool = True) -> Optional[np.ndarray]:
        """
        Sum multiple images.
        
        Args:
            images: List of images to sum
            normalize: If True, normalize to 0-255 range
            
        Returns:
            Summed image or None if list is empty
        """
        if not images:
            print("No images to sum")
            return None
        
        print(f"Summing {len(images)} images...")
        
        # Sum as float to prevent overflow
        summed = np.sum(images, axis=0, dtype=np.float64)
        
        if normalize:
            # Normalize to 0-255 range
            summed = (summed / summed.max() * 255).astype(np.uint8)
        else:
            summed = np.clip(summed, 0, 255).astype(np.uint8)
        
        print("Summing complete")
        return summed
    
    def save_image(self, image: np.ndarray, filename: str) -> bool:
        """
        Save image to file.
        
        Args:
            image: Image to save
            filename: Output filename
            
        Returns:
            True if successful
        """
        success = cv2.imwrite("capturas/" + filename, image)
        if success:
            print(f"Image saved: {filename}")
        else:
            print(f"Failed to save image: {filename}")
        return success
    
    def get_camera_info(self) -> dict:
        """
        Get current camera properties.
        
        Returns:
            Dictionary with camera properties
        """
        if self.camera is None:
            return {}
        
        info = {
            'index': self.camera_index,
            'width': int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': self.camera.get(cv2.CAP_PROP_FPS),
            'exposure': self.camera.get(cv2.CAP_PROP_EXPOSURE),
            'auto_exposure': self.camera.get(cv2.CAP_PROP_AUTO_EXPOSURE)
        }
        
        return info
    
    def _print_capture_statistics(self, stats: Dict):
        """Print formatted capture statistics."""
        print("="*60)
        print("CAPTURE STATISTICS")
        print("="*60)
        print(f"Images captured: {stats['total_images']}/{stats['requested_images']}")
        print(f"Total burst time: {stats['total_time_s']:.3f}s ({stats['total_time_ms']:.2f}ms)")
        print(f"\nINDIVIDUAL CAPTURE TIMES:")
        print(f"  Average: {stats['avg_capture_time_ms']:.2f}ms")
        print(f"  Min: {stats['min_capture_time_ms']:.2f}ms")
        print(f"  Max: {stats['max_capture_time_ms']:.2f}ms")
        
        if stats['interval_times_ms']:
            print(f"\nINTER-CAPTURE INTERVALS:")
            print(f"  Average: {stats['avg_interval_ms']:.2f}ms")
            print(f"  Min: {stats['min_interval_ms']:.2f}ms")
            print(f"  Max: {stats['max_interval_ms']:.2f}ms")
        
        print(f"\nEffective FPS: {stats['fps_effective']:.2f}")
        print("="*60 + "\n")
    
    def get_last_capture_stats(self) -> Optional[Dict]:
        """
        Get statistics from the last capture burst.
        
        Returns:
            Dictionary with timing statistics or None
        """
        return self.last_capture_stats
    
    def save_capture_stats(self, filename: str = None) -> bool:
        """
        Save capture statistics to a text file.
        
        Args:
            filename: Output filename, auto-generated if None
            
        Returns:
            True if successful
        """
        if self.last_capture_stats is None:
            print("No capture statistics available")
            return False
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"capture_stats_{timestamp}.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write("CAPTURE BURST STATISTICS\n")
                f.write("="*60 + "\n\n")
                
                stats = self.last_capture_stats
                f.write(f"Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Images captured: {stats['total_images']}/{stats['requested_images']}\n")
                f.write(f"Total burst time: {stats['total_time_s']:.6f}s ({stats['total_time_ms']:.3f}ms)\n\n")
                
                f.write("INDIVIDUAL CAPTURE TIMES (ms):\n")
                for i, t in enumerate(stats['capture_times_ms'], 1):
                    f.write(f"  Image {i}: {t:.3f}ms\n")
                
                f.write(f"\nAVERAGE: {stats['avg_capture_time_ms']:.3f}ms\n")
                f.write(f"MIN: {stats['min_capture_time_ms']:.3f}ms\n")
                f.write(f"MAX: {stats['max_capture_time_ms']:.3f}ms\n\n")
                
                if stats['interval_times_ms']:
                    f.write("INTER-CAPTURE INTERVALS (ms):\n")
                    for i, t in enumerate(stats['interval_times_ms'], 1):
                        f.write(f"  Interval {i}-{i+1}: {t:.3f}ms\n")
                    
                    f.write(f"\nAVERAGE: {stats['avg_interval_ms']:.3f}ms\n")
                    f.write(f"MIN: {stats['min_interval_ms']:.3f}ms\n")
                    f.write(f"MAX: {stats['max_interval_ms']:.3f}ms\n\n")
                
                f.write(f"EFFECTIVE FPS: {stats['fps_effective']:.3f}\n")
            
            print(f"Statistics saved to: {filename}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to save statistics: {e}")
            return False
    
    def show_live_video(self, window_name="Live Camera"):
        """
        Show live video feed from camera.
        Press 'q' or ESC to exit.
        
        Args:
            window_name: Name of the display window
        """
        if self.camera is None:
            print("Camera not connected")
            return False
        
        print("\nStarting live video...")
        print("Controls:")
        print("  'q' or ESC - Exit live view")
        print("  's' - Save snapshot")
        print("\nPress any key to start...")
        input()
        
        snapshot_count = 0
        
        try:
            while True:
                ret, frame = self.camera.read()
                
                if not ret:
                    print("Failed to read frame")
                    break
                
                # Add info overlay
                info = self.get_camera_info()
                cv2.putText(frame, f"Camera {info.get('index', 'N/A')} - {info.get('width')}x{info.get('height')}",
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, "Press 'q' to exit, 's' to save snapshot",
                           (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                cv2.imshow(window_name, frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q') or key == 27:  # 'q' or ESC
                    print("\nExiting live view...")
                    break
                elif key == ord('s'):  # 's' for snapshot
                    snapshot_count += 1
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"snapshot_{timestamp}_{snapshot_count}.jpg"
                    self.save_image(frame, filename)
                    print(f"Snapshot saved: {filename}")
            
            cv2.destroyAllWindows()
            # Clear any remaining windows
            cv2.waitKey(1)
            return True
            
        except Exception as e:
            print(f"Error in live view: {e}")
            cv2.destroyAllWindows()
            return False
    
    def close(self):
        """Release camera resources."""
        if self.camera is not None:
            self.camera.release()
            cv2.destroyAllWindows()  # Close any open windows
            print("Camera released")
            self.camera = None
            self.camera_index = None

def main():
    """Test camera functionality."""
    controller = CameraController()
    
    # Detect cameras
    print("Detecting cameras...")
    cameras = controller.detect_cameras()
    print(f"Found {len(cameras)} camera(s): {cameras}")
    
    if not cameras:
        print("No cameras available")
        return
    
    # Connect to first camera
    if controller.connect_camera(cameras[0]):
        # Print camera info
        info = controller.get_camera_info()
        print(f"\nCamera Info: {info}")
        
        # Capture test image
        print("\nCapturing test image...")
        img = controller.capture_image()
        if img is not None:
            controller.save_image(img, "test_capture.jpg")
        
        controller.close()

if __name__ == "__main__":
    main()
