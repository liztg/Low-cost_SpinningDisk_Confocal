
SOFTWARE

The system integrates the control of a stepper motor (with a TB6560 driver through Arduino) and the acquisition of images with a USB camera from a unique Python interface.
It allows connecting and disconnecting devices, adjusting the motor velocity (between 0 and 300 RPM), showing live video, acquiring a series of images with manual exposure, and
to carry out different operations like average or sum to improve the signal, always saving the results with time stamps.

The software uses PySerial for the serial communication between the motor and Arduino. In controlling the camera, it uses opencv-python (OpenCV) for the detection, capture, and
visualization of images, and Numpy for the processing. It also uses standard utilities of Python, like Datetime for the names of the files and for time management.
