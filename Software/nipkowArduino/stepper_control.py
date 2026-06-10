"""
Arduino Stepper Motor Speed Control
Controls a stepper motor connected to an A4988 driver via Arduino.
Send speed commands from Python via serial communication.
"""

import serial
import time
import sys

class StepperController:
    def __init__(self, port='COM3', baudrate=9600, timeout=1):
        """
        Initialize serial connection to Arduino.
        
        Args:
            port (str): Serial port (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux)
            baudrate (int): Communication speed (must match Arduino)
            timeout (float): Read timeout in seconds
        """
        self.current_speed = 0
        self.is_running = False
        
        try:
            self.ser = serial.Serial(port, baudrate, timeout=timeout)
            time.sleep(2)  # Wait for Arduino to reset
            print(f"✓ Connected to Arduino on {port}")
            
            # Read initial response from Arduino
            response = self.read_response()
            if response:
                print(f"Arduino: {response}")
                
        except serial.SerialException as e:
            raise Exception(f"Failed to connect to {port}: {e}")
    
    def set_speed(self, rpm):
        """
        Set motor speed in RPM (revolutions per minute).
        
        Args:
            rpm (int): Speed in RPM (0-300 range)
            
        Returns:
            bool: True if successful
        """
        if not 0 <= rpm <= 300:
            print("⚠ Warning: RPM should be between 0 and 300")
            rpm = max(0, min(300, rpm))  # Clamp value
        
        command = f"SPEED:{rpm}\n"
        self.ser.write(command.encode())
        self.ser.flush()
        
        # Wait for Arduino confirmation
        response = self.read_response()
        if response:
            print(f"Arduino: {response}")
            self.current_speed = rpm
            self.is_running = (rpm > 0)
            return True
        else:
            print("⚠ No response from Arduino")
            return False
    
    def read_response(self, timeout=1):
        """
        Read response from Arduino.
        
        Args:
            timeout (float): Maximum time to wait for response
            
        Returns:
            str: Response from Arduino or None
        """
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            if self.ser.in_waiting > 0:
                try:
                    response = self.ser.readline().decode('utf-8').strip()
                    if response:
                        return response
                except UnicodeDecodeError:
                    continue
            time.sleep(0.01)
        
        return None
    
    def emergency_stop(self):
        """Emergency stop - immediately set speed to 0."""
        print("\n🛑 EMERGENCY STOP")
        return self.set_speed(0)
    
    def stop(self):
        """Stop the motor."""
        return self.set_speed(0)
    
    def get_status(self):
        """
        Get current motor status.
        
        Returns:
            dict: Motor status information
        """
        return {
            'speed': self.current_speed,
            'running': self.is_running,
            'direction': 'CW' if self.current_speed > 0 else 'STOPPED'
        }
    
    def close(self):
        """Close serial connection."""
        if hasattr(self, 'ser') and self.ser.is_open:
            self.stop()
            time.sleep(0.5)
            self.ser.close()
            print("✓ Stepper disconnected")

def main():
    # Create controller instance
    # Change 'COM3' to your Arduino port
    controller = StepperController(port='COM3', baudrate=9600)
    
    try:
        print("\nStepper Motor Control")
        print("=" * 40)
        print("Commands:")
        print("  - Enter RPM value (0-200)")
        print("  - Type 'quit' or 'exit' to stop")
        print("=" * 40)
        
        while True:
            user_input = input("\nEnter speed (RPM): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Stopping motor...")
                break
            
            try:
                rpm = int(user_input)
                controller.set_speed(rpm)
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    finally:
        controller.close()

if __name__ == "__main__":
    main()
