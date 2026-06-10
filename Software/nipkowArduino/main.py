"""
Main Application - Stepper Motor and Camera Control System
Unified interface for controlling stepper motor and USB camera.
Command-line interface with short descriptive commands.
"""

import sys
import os
from datetime import datetime
import serial
import platform
from stepper_control import StepperController
from camera_controller import CameraController

# For listing available ports
try:
    import serial.tools.list_ports
except ImportError:
    serial = None

class MainController:
    def __init__(self):
        """Initialize main controller."""
        self.stepper = None
        self.camera = None
        self.running = True
        
    def setup_stepper(self, port='COM3', baudrate=9600):
        """Initialize stepper motor controller."""
        try:
            self.stepper = StepperController(port=port, baudrate=baudrate)
            return True
        except Exception as e:
            print(f"[ERROR] Error initializing stepper: {e}")
            return False
    
    def setup_camera(self, camera_index=None):
        """Initialize camera controller."""
        self.camera = CameraController()
        return self.camera.connect_camera(camera_index)
    
    def parse_command(self, cmd_line):
        """Parse command line into command and arguments."""
        parts = cmd_line.strip().split()
        if not parts:
            return None, []
        return parts[0].lower(), parts[1:]
    
    def show_help(self):
        """Display help information."""
        print("\n" + "="*60)
        print("  AVAILABLE COMMANDS")
        print("="*60)
        print("\nCONNECTION:")
        print("  connect <PORT>              - Connect to Arduino (e.g., connect COM3)")
        print("  list-ports                  - List active serial ports (COM/ttyUSB)")
        print("  cam                         - Connect to camera (auto-detect)")
        print("  cam <INDEX>                 - Connect to specific camera")
        print("  disconnect                  - Disconnect all devices")
        
        print("\nSTEPPER MOTOR:")
        print("  speed <RPM>                 - Set motor speed (e.g., speed 100)")
        print("  stop                        - Stop motor immediately")
        print("  status                      - Show motor status")
        
        print("\nCAMERA:")
        print("  capture <N> <EXP> avg       - Capture N images, exposure EXP ms, average")
        print("  capture <N> <EXP> sum       - Capture N images, exposure EXP ms, sum")
        print("  live                        - Show live video feed")
        print("  list-cam                    - List available cameras")
        
        print("\nSYSTEM:")
        print("  info                        - Show system status")
        print("  help                        - Show this help")
        print("  exit                        - Exit program")
        print("="*60)
        
        print("\nEXAMPLES:")
        print("  connect COM3                - Connect to Arduino on COM3")
        print("  list-ports                  - Show all available COM ports")
        print("  speed 150                   - Set motor to 150 RPM")
        print("  live                        - Show live camera feed")
        print("  capture 10 100 avg          - Capture 10 images, 100ms exposure, average them")
        print("  capture 20 50 sum           - Capture 20 images, 50ms exposure, sum them")
        print("="*60 + "\n")
    
    def cmd_list_ports(self, args):
        """Handle list-ports command - list available serial ports."""
        print("\nScanning for active serial ports...\n")
        
        try:
            from serial.tools.list_ports import comports
            
            ports = comports()
            
            if not ports:
                print("No serial ports detected.")
                print("\nOn Linux, look for:")
                print("  - /dev/ttyUSB0, /dev/ttyUSB1, etc. (USB devices)")
                print("  - /dev/ttyACM0, /dev/ttyACM1, etc. (Arduino)")
                print("\nOn Windows, look for COM3, COM4, etc.")
                return
            
            print(f"Found {len(ports)} serial port(s):\n")
            
            for i, port in enumerate(ports, 1):
                print(f"  [{i}] {port.device}")
                if port.description:
                    print(f"      Description: {port.description}")
                if port.manufacturer:
                    print(f"      Manufacturer: {port.manufacturer}")
                if port.product:
                    print(f"      Product: {port.product}")
                print()
            
            print("Usage: connect <PORT>")
            print("  Example: connect /dev/ttyACM0")
            print("  Example: connect COM3")
            print()
            
        except Exception as e:
            print(f"[ERROR] Failed to list ports: {e}")
            print("\nTrying fallback method...")
            self._list_ports_fallback()
    
    def _list_ports_fallback(self):
        """Fallback method to list ports."""
        import os
        import glob
        
        os_name = platform.system()
        
        if os_name == "Linux":
            print("\nLinux ports detected:")
            usb_ports = glob.glob('/dev/ttyUSB*')
            acm_ports = glob.glob('/dev/ttyACM*')
            
            all_ports = sorted(usb_ports + acm_ports)
            
            if all_ports:
                for port in all_ports:
                    print(f"  - {port}")
            else:
                print("  No USB or ACM ports found")
                
        elif os_name == "Windows":
            print("\nWindows COM ports detected:")
            for i in range(256):
                port = f"COM{i}"
                try:
                    s = serial.Serial(port)
                    print(f"  - {port}")
                    s.close()
                except:
                    pass
        
        elif os_name == "Darwin":  # macOS
            print("\nmacOS ports detected:")
            usb_ports = glob.glob('/dev/tty.usbserial*')
            usbmodem_ports = glob.glob('/dev/tty.usbmodem*')
            
            all_ports = sorted(usb_ports + usbmodem_ports)
            
            if all_ports:
                for port in all_ports:
                    print(f"  - {port}")
            else:
                print("  No USB ports found")
        
        print()
    
    def cmd_connect(self, args):
        """Handle connect command."""
        if not args:
            print("[ERROR] Usage: connect <PORT>")
            print("   Example: connect COM3")
            return
        
        port = args[0]
        print(f"Connecting to {port}...")
        if self.setup_stepper(port=port):
            print(f"Connected to stepper on {port}")
    
    def cmd_cam(self, args):
        """Handle cam command."""
        camera_index = None
        if args:
            try:
                camera_index = int(args[0])
            except ValueError:
                print("[ERROR] Invalid camera index")
                return
        
        print("Connecting to camera...")
        if self.setup_camera(camera_index):
            info = self.camera.get_camera_info()
            print(f"Camera connected: Index {info.get('index')}, {info.get('width')}x{info.get('height')}")
    
    def cmd_disconnect(self, args):
        """Handle disconnect command."""
        print("Disconnecting devices...")
        if self.stepper:
            self.stepper.close()
            self.stepper = None
        if self.camera:
            self.camera.close()
            self.camera = None
        print("Disconnected")
    
    def cmd_speed(self, args):
        """Handle speed command."""
        if not self.stepper:
            print("[ERROR] Stepper not connected. Use: connect <PORT>")
            return
        
        if not args:
            print("[ERROR] Usage: speed <RPM>")
            print("   Example: speed 100")
            return
        
        try:
            rpm = int(args[0])
            self.stepper.set_speed(rpm)
        except ValueError:
            print("[ERROR] Invalid RPM value")
    
    def cmd_stop(self, args):
        """Handle stop command."""
        if not self.stepper:
            print("[ERROR] Stepper not connected")
            return
        
        print("Stopping motor...")
        self.stepper.stop()
    
    def cmd_status(self, args):
        """Handle status command."""
        if not self.stepper:
            print("[ERROR] Stepper not connected")
            return
        
        status = self.stepper.get_status()
        print("\nMotor Status:")
        print(f"   Speed: {status['speed']} RPM")
        print(f"   State: {status['direction']}")
        print(f"   Running: {'Yes' if status['running'] else 'No'}\n")
    
    def cmd_capture(self, args):
        """Handle capture command."""
        if not self.camera:
            print("[ERROR] Camera not connected. Use: cam")
            return
        
        if len(args) < 3:
            print("[ERROR] Usage: capture <N> <EXPOSURE_MS> <avg|sum>")
            print("   Example: capture 10 100 avg")
            return
        
        try:
            num_images = int(args[0])
            exposure_time = float(args[1])
            mode = args[2].lower()
            
            if mode not in ['avg', 'average', 'sum']:
                print("[ERROR] Mode must be 'avg' or 'sum'")
                return
            
            print(f"Starting capture: {num_images} images @ {exposure_time}ms...")
            images, stats = self.camera.capture_multiple(num_images, exposure_time)
            
            if not images:
                print("[ERROR] No images captured")
                return
            
            # Process images
            if mode in ['avg', 'average']:
                result = self.camera.average_images(images)
                operation = "averaged"
            else:
                result = self.camera.sum_images(images, normalize=True)
                operation = "summed"
            
            if result is not None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"output_{operation}_{timestamp}.jpg"
                self.camera.save_image(result, filename)
                print(f"Successfully {operation} {num_images} images -> {filename}")
                
                # Ask if user wants to save stats
                save_stats = input("\nSave timing statistics to file? (y/n): ").strip().lower()
                if save_stats == 'y':
                    self.camera.save_capture_stats()
                print()
                
        except ValueError:
            print("[ERROR] Invalid parameters")
    
    def cmd_live(self, args):
        """Handle live video command."""
        if not self.camera:
            print("[ERROR] Camera not connected. Use: cam")
            return
        
        self.camera.show_live_video()
    
    def cmd_list_cam(self, args):
        """Handle list-cam command."""
        print("\nDetecting cameras...")
        temp_cam = CameraController()
        cameras = temp_cam.detect_cameras()
        
        if cameras:
            print(f"Found {len(cameras)} camera(s):")
            for idx in cameras:
                print(f"  - Camera index: {idx}")
        else:
            print("No cameras detected")
        print()
    
    def cmd_info(self, args):
        """Handle info command."""
        print("\n" + "="*50)
        print("SYSTEM STATUS")
        print("="*50)
        
        # Stepper status
        if self.stepper is not None:
            status = self.stepper.get_status()
            print(f"[OK] Stepper: Connected")
            print(f"  Speed: {status['speed']} RPM")
            print(f"  State: {status['direction']}")
        else:
            print("[--] Stepper: Not connected")
        
        # Camera status
        if self.camera is not None and self.camera.camera is not None:
            info = self.camera.get_camera_info()
            print(f"[OK] Camera: Connected (Index {info.get('index', 'N/A')})")
            print(f"  Resolution: {info.get('width', 0)}x{info.get('height', 0)}")
        else:
            print("[--] Camera: Not connected")
        print("="*50 + "\n")
    
    def cmd_exit(self, args):
        """Handle exit command."""
        print("\nShutting down...")
        self.running = False
    
    def process_command(self, cmd_line):
        """Process a command line."""
        cmd, args = self.parse_command(cmd_line)
        
        if cmd is None:
            return
        
        # Command dispatch
        commands = {
            'connect': self.cmd_connect,
            'list-ports': self.cmd_list_ports,
            'cam': self.cmd_cam,
            'disconnect': self.cmd_disconnect,
            'speed': self.cmd_speed,
            'stop': self.cmd_stop,
            'status': self.cmd_status,
            'capture': self.cmd_capture,
            'live': self.cmd_live,
            'list-cam': self.cmd_list_cam,
            'info': self.cmd_info,
            'help': lambda args: self.show_help(),
            'exit': self.cmd_exit,
            'quit': self.cmd_exit,
            '?': lambda args: self.show_help(),
        }
        
        if cmd in commands:
            commands[cmd](args)
        else:
            print(f"[ERROR] Unknown command: {cmd}")
            print("Type 'help' for available commands")
    
    def run(self):
        """Run main application loop."""
        print("\n" + "="*60)
        print("  ARDUINO STEPPER & CAMERA CONTROL SYSTEM")
        print("="*60)
        print("  Type 'help' for available commands")
        print("="*60 + "\n")
        
        try:
            while self.running:
                try:
                    cmd_line = input(">>> ").strip()
                    if cmd_line:
                        self.process_command(cmd_line)
                except EOFError:
                    break
        
        except KeyboardInterrupt:
            print("\n\n[INTERRUPT] Interrupted by user")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        print("\nCleaning up...")
        
        if self.stepper is not None:
            self.stepper.close()
        
        if self.camera is not None:
            self.camera.close()
        
        print("Goodbye!\n")

def main():
    """Entry point."""
    controller = MainController()
    controller.run()

if __name__ == "__main__":
    main()
