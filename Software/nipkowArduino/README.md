# Arduino Stepper Motor & Camera Control System

Sistema integrado para control de motor stepper mediante Arduino con driver A4988 y captura de imágenes con cámara USB, controlado desde Python via comunicación serial.

## 📋 Componentes Necesarios

### Hardware Stepper
- Arduino (Uno, Nano, Mega, etc.)
- Driver TB6560 (o TB6600)
- Motor stepper (NEMA 17, NEMA 23, etc.)
- Fuente de alimentación (12-36V DC para el motor)
- Cables de conexión

### Hardware Cámara
- Cámara USB compatible con Windows
- Puerto USB disponible

## 🔌 Conexiones Hardware

### TB6560 a Arduino
```
TB6560 PUL+ (CLK+)  -> Arduino Pin 3
TB6560 DIR+ (CW+)   -> Arduino Pin 4
TB6560 ENA+         -> Arduino Pin 5 (opcional)
TB6560 PUL-         -> Arduino GND
TB6560 DIR-         -> Arduino GND
TB6560 ENA-         -> Arduino GND
```

### TB6560 a Motor y Alimentación
```
TB6560 VCC   -> Fuente de alimentación + (12-36V DC)
TB6560 GND   -> Fuente de alimentación -
TB6560 A+, A- -> Bobina A del motor
TB6560 B+, B- -> Bobina B del motor
```

### Configuración del TB6560
⚠️ **IMPORTANTE**: 
- **Ajustar corriente**: Usar los DIP switches según las especificaciones de tu motor
- **Microstepping**: Configurar según necesites (1, 2, 4, 8, 16 pasos)
- **Voltaje**: Verificar que la fuente esté dentro del rango 12-36V DC

## 🚀 Instalación

### 1. Clonar o descargar el proyecto
```bash
cd nipkowArduino
```

### 2. Instalar dependencias Python
```bash
pip install -r requirements.txt
```

### 3. Cargar código al Arduino
1. Abre `arduino_stepper/arduino_stepper.ino` en Arduino IDE
2. Conecta tu Arduino por USB
3. Selecciona el puerto COM correcto en Herramientas > Puerto
4. Haz clic en "Cargar" (Upload)

## 💻 Uso

### Ejecutar la Aplicación Principal

El sistema se controla mediante comandos de texto:

```bash
python main.py
```

### Interfaz de Comandos

```
>>> help

CONNECTION:
  connect <PORT>              - Connect to Arduino
  cam                         - Connect to camera (auto-detect)
  cam <INDEX>                 - Connect to specific camera
  disconnect                  - Disconnect all devices

STEPPER MOTOR:
  speed <RPM>                 - Set motor speed
  stop                        - Stop motor immediately
  status                      - Show motor status

CAMERA:
  capture <N> <EXP> avg       - Capture N images, exposure EXP ms, average
  capture <N> <EXP> sum       - Capture N images, exposure EXP ms, sum
  live                        - Show live video feed
  list-cam                    - List available cameras

SYSTEM:
  info                        - Show system status
  help                        - Show this help
  exit                        - Exit program
```

### Flujo de Trabajo Típico

#### 1. Conectar Dispositivos
```
>>> connect COM3
Connecting to COM3...
Connected to stepper on COM3

>>> cam
Connecting to camera...
Camera connected: Index 0, 1920x1080
```

#### 2. Controlar Motor Stepper
```
>>> speed 150
Arduino: Speed set to 150 RPM

>>> status
Motor Status:
   Speed: 150 RPM
   State: CW
   Running: Yes

>>> stop
Stopping motor...
Arduino: Speed set to 0 RPM
```

#### 3. Capturar y Procesar Imágenes
```
>>> capture 10 100 avg
Starting capture: 10 images @ 100ms...

Capturing 10 images with timing measurement...
============================================================
  Image 1/10 | Capture: 45.23ms | Interval: N/A (first)
  Image 2/10 | Capture: 43.87ms | Interval: 545.12ms
  ...
============================================================
CAPTURE STATISTICS
============================================================
Images captured: 10/10
Total burst time: 5.432s (5432.15ms)

INDIVIDUAL CAPTURE TIMES:
  Average: 44.28ms
  Min: 43.87ms
  Max: 45.67ms

INTER-CAPTURE INTERVALS:
  Average: 544.33ms
  Min: 543.98ms
  Max: 545.12ms

Effective FPS: 1.84
============================================================

Averaging 10 images...
Successfully averaged 10 images -> output_averaged_20251126_143052.jpg

Save timing statistics to file? (y/n): y
Statistics saved to: capture_stats_20251126_143052.txt
```

#### 4. Vista en Vivo
```
>>> live
Starting live video...
Controls:
  'q' or ESC - Exit live view
  's' - Save snapshot

[Ventana de OpenCV se abre]
[Presionar 's' para guardar snapshot]
Snapshot saved: snapshot_20251126_143215_1.jpg
[Presionar 'q' para salir]
```

#### 5. Ver Estado del Sistema
```
>>> info
==================================================
SYSTEM STATUS
==================================================
[OK] Stepper: Connected
  Speed: 0 RPM
  State: STOPPED
[OK] Camera: Connected (Index 0)
  Resolution: 1920x1080
==================================================
```

### Uso Avanzado - Módulos Independientes

#### Solo Control de Stepper
```bash
python stepper_control.py
```

#### Solo Control de Cámara
```bash
python camera_controller.py
```

## 🎯 Casos de Uso

### Fotografía de Larga Exposición
```
>>> cam
>>> capture 10 200 avg
```
1. Conectar cámara
2. Capturar 10 imágenes con exposición de 200ms
3. Promediar para reducir ruido
4. Resultado guardado automáticamente

### Astrofotografía
```
>>> cam
>>> capture 30 500 sum
```
1. Capturar 30 frames con exposición de 500ms
2. Sumar imágenes para aumentar señal
3. Resultado normalizado automáticamente

### Time-Lapse con Motor
```
>>> connect COM3
>>> cam
>>> speed 10
>>> capture 100 100 avg
>>> stop
```
1. Configurar stepper para rotación lenta (10 RPM)
2. Capturar 100 imágenes promediadas
3. Detener motor al finalizar

### Escaneo Panorámico
```
>>> connect COM3
>>> cam
>>> live              # Verificar encuadre primero
>>> speed 20
>>> capture 50 200 avg
>>> stop
```

## ⚙️ Configuración

### Parámetros de Cámara

#### Exposición Manual
- Rango típico: 1-1000 ms
- Para fotografía nocturna: 100-500 ms
- Para objetos en movimiento: 1-50 ms

#### Número de Imágenes
- Promediado (reducir ruido): 5-20 imágenes
- Suma (astrofotografía): 10-50 imágenes
- Más imágenes = mejor calidad pero más tiempo

### Cambiar Pasos por Revolución
Si tu motor tiene diferente número de pasos (por ejemplo, 400 pasos):

En `arduino_stepper.ino` línea 19:
```cpp
const int STEPS_PER_REVOLUTION = 200;  // Cambiar según tu motor
```

### Cambiar Pines
Modifica las definiciones en `arduino_stepper.ino` líneas 15-17:
```cpp
const int STEP_PIN = 3;   // PUL+ on TB6560
const int DIR_PIN = 4;    // DIR+ on TB6560
const int ENABLE_PIN = 5; // ENA+ on TB6560
```

### Cambiar Dirección de Rotación
En `arduino_stepper.ino` línea 26:
```cpp
digitalWrite(DIR_PIN, HIGH);  // HIGH = horario, LOW = antihorario
```


## 🔧 Resolución de Problemas

### Cámara

#### No se detecta la cámara
- Verifica que esté conectada al USB
- Prueba con otro puerto USB
- Cierra otras aplicaciones que puedan estar usando la cámara
- Verifica que los drivers estén instalados

#### Las imágenes salen muy oscuras/claras
- Ajusta el tiempo de exposición
- Valores más altos = más luz capturada
- Prueba con diferentes tiempos

#### Error al guardar imágenes
- Verifica permisos de escritura en el directorio
- Asegúrate de tener espacio en disco

### Motor Stepper
- Verifica las conexiones
- Comprueba que la alimentación del motor esté conectada
- Ajusta la corriente del A4988
- Verifica que ENABLE esté en LOW (motor habilitado)

#### El motor no gira
- Verifica las conexiones (PUL+, DIR+, ENA+ a Arduino y todos los - a GND)
- Comprueba que la alimentación del motor esté conectada (12-36V DC)
- Ajusta la corriente mediante DIP switches del TB6560
- Verifica que ENABLE esté en LOW (motor habilitado)
- Asegúrate de conectar correctamente PUL-, DIR-, ENA- a GND del Arduino

#### El motor vibra pero no gira
- La velocidad puede ser demasiado alta
- Reduce el RPM
- Ajusta la corriente mediante DIP switches del TB6560
- Verifica la configuración de microstepping
- Asegúrate de que las conexiones A+/A- y B+/B- sean correctas

#### Error al conectar por serial
- Verifica el puerto COM correcto
- Cierra otras aplicaciones que puedan estar usando el puerto (Arduino IDE Serial Monitor)
- Asegúrate de que los drivers del Arduino estén instalados

#### El motor pierde pasos
- Reduce la velocidad
- Ajusta la corriente del TB6560 (aumentar ligeramente)
- Verifica que la carga mecánica no sea excesiva
- Reduce el microstepping o aumenta el voltaje de alimentación

## 📝 Estructura del Proyecto

```
nipkowArduino/
├── main.py                     # Aplicación principal unificada
├── stepper_control.py          # Módulo control stepper
├── camera_controller.py        # Módulo control cámara
├── arduino_stepper/
│   └── arduino_stepper.ino     # Código Arduino
├── requirements.txt            # Dependencias Python
├── .gitignore
├── README.md
└── .github/
    └── copilot-instructions.md
```

## 📋 Referencia de Comandos

### Comandos de Conexión

| Comando | Descripción | Ejemplo |
|---------|-------------|----------|
| `connect <PORT>` | Conectar Arduino en puerto especificado | `connect COM3` |
| `cam` | Conectar cámara (auto-detecta) | `cam` |
| `cam <INDEX>` | Conectar cámara específica | `cam 0` |
| `disconnect` | Desconectar todos los dispositivos | `disconnect` |

### Comandos de Motor

| Comando | Descripción | Ejemplo |
|---------|-------------|----------|
| `speed <RPM>` | Establecer velocidad (0-300 RPM) | `speed 100` |
| `stop` | Parada de emergencia | `stop` |
| `status` | Ver estado del motor | `status` |

### Comandos de Cámara

| Comando | Descripción | Ejemplo |
|---------|-------------|----------|
| `capture <N> <EXP> avg` | Capturar N imágenes, promediar | `capture 10 100 avg` |
| `capture <N> <EXP> sum` | Capturar N imágenes, sumar | `capture 20 50 sum` |
| `live` | Vista en vivo | `live` |
| `list-cam` | Listar cámaras disponibles | `list-cam` |

### Comandos de Sistema

| Comando | Descripción | Ejemplo |
|---------|-------------|----------|
| `info` | Estado completo del sistema | `info` |
| `help` o `?` | Mostrar ayuda | `help` |
| `exit` o `quit` | Salir del programa | `exit` |

### Archivos Generados

| Archivo | Descripción |
|---------|-------------|
| `output_averaged_YYYYMMDD_HHMMSS.jpg` | Imágenes promediadas |
| `output_summed_YYYYMMDD_HHMMSS.jpg` | Imágenes sumadas |
| `snapshot_YYYYMMDD_HHMMSS_N.jpg` | Snapshots desde live view |
| `capture_stats_YYYYMMDD_HHMMSS.txt` | Estadísticas de timing |

### Medición de Tiempos

Cada captura registra:
- **Tiempo individual** de cada imagen (ms)
- **Intervalo exacto** entre capturas consecutivas (ms)
- **Tiempo total** de la ráfaga (ms/s)
- **Estadísticas**: promedio, mínimo, máximo
- **FPS efectivo** de la captura

Ejemplo de estadísticas guardadas:
```
CAPTURE BURST STATISTICS
============================================================

Date/Time: 2025-11-26 14:30:52
Images captured: 10/10
Total burst time: 5.432156s (5432.156ms)

INDIVIDUAL CAPTURE TIMES (ms):
  Image 1: 45.234ms
  Image 2: 43.871ms
  Image 3: 44.012ms
  ...

AVERAGE: 44.283ms
MIN: 43.871ms
MAX: 45.671ms

INTER-CAPTURE INTERVALS (ms):
  Interval 1-2: 545.123ms
  Interval 2-3: 543.987ms
  ...

AVERAGE: 544.332ms
MIN: 543.987ms
MAX: 546.012ms

EFFECTIVE FPS: 1.841
```

## 🎓 Funcionalidades Principales

### Control de Stepper
- ✅ Comunicación serial bidireccional con Arduino
- ✅ Control de velocidad en RPM (0-300)
- ✅ Lectura de confirmaciones del Arduino
- ✅ Parada de emergencia
- ✅ Monitoreo de estado en tiempo real
- ✅ Interfaz por comandos de texto

### Control de Cámara
- ✅ Detección automática de cámaras USB
- ✅ Control de exposición manual
- ✅ Captura múltiple de imágenes
- ✅ Promediado de imágenes (reducir ruido)
- ✅ Suma de imágenes (aumentar señal)
- ✅ Vista en vivo con OpenCV
- ✅ Captura de snapshots durante live view
- ✅ Guardado automático con timestamp
- ✅ Normalización automática
- ✅ **Medición precisa de tiempos de captura**
- ✅ **Estadísticas detalladas de intervalos**
- ✅ **Exportación de estadísticas a archivo**

## 📚 Recursos Adicionales

- [Datasheet TB6560](https://www.epitran.it/ebayDrive/TB6560.pdf)
- [TB6600 Manual](https://www.dfrobot.com/wiki/index.php/TB6600_Stepper_Motor_Driver_SKU:_DRI0043)
- [PySerial Documentation](https://pyserial.readthedocs.io/)
- [OpenCV Python Tutorials](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)
- [Arduino Serial Reference](https://www.arduino.cc/reference/en/language/functions/communication/serial/)
- [NumPy Documentation](https://numpy.org/doc/)

## 🔬 Aplicaciones

- **Astrofotografía**: Captura y suma de múltiples exposiciones
- **Fotografía de larga exposición**: Reducción de ruido mediante promediado
- **Time-lapse**: Sincronización de motor y captura de imágenes
- **Escaneo panorámico**: Control preciso de rotación con captura
- **Microscopía**: Control de iluminación y captura automática

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.
