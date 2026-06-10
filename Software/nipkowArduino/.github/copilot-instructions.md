<!-- Use this file to provide workspace-specific custom instructions to Copilot. -->

## Project: Arduino Stepper Motor & Camera Control System

Sistema integrado para control de motor stepper con TB6560 y captura de imágenes con cámara USB. Python controla ambos sistemas mediante comunicación serial (Arduino) y OpenCV (cámara).

### Components
- **main.py**: Interfaz unificada para control de todo el sistema
- **stepper_control.py**: Módulo de control del motor stepper
- **camera_controller.py**: Módulo de control de cámara USB
- **arduino_stepper.ino**: Código Arduino para TB6560
- **requirements.txt**: Dependencias (pyserial, opencv-python, numpy)

### Features
- Control de velocidad de stepper motor (0-300 RPM)
- Detección automática de cámaras USB
- Captura de imágenes con exposición manual
- Promediado de imágenes (reducción de ruido)
- Suma de imágenes (aumento de señal)
- Guardado automático con timestamp

### Progress
- [x] Created copilot-instructions.md
- [x] Project structure created
- [x] Python stepper module implemented
- [x] Arduino sketch implemented
- [x] Camera controller module implemented
- [x] Unified main interface created
- [x] README documentation complete
- [x] Dependencies installed
