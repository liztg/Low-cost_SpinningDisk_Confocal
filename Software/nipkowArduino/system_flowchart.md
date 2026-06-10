# Diagrama de Flujo del Sistema de Control

## Arquitectura General del Sistema

```mermaid
graph TB
    subgraph "Usuario"
        USER[Usuario]
    end
    
    subgraph "Aplicación Python - main.py"
        CLI[Interfaz de Comandos CLI]
        PARSER[Parser de Comandos]
        MAIN[MainController]
    end
    
    subgraph "Módulos de Control"
        STEPPER[StepperController]
        CAMERA[CameraController]
    end
    
    subgraph "Hardware"
        ARDUINO[Arduino + TB6560]
        MOTOR[Motor Stepper]
        CAM[Cámara USB]
    end
    
    subgraph "Salidas"
        IMG[Imágenes Procesadas]
        STATS[Estadísticas de Timing]
        SNAP[Snapshots]
    end
    
    USER -->|Comandos de texto| CLI
    CLI --> PARSER
    PARSER --> MAIN
    
    MAIN -->|Comandos de motor| STEPPER
    MAIN -->|Comandos de cámara| CAMERA
    
    STEPPER <-->|Serial 9600 baud| ARDUINO
    ARDUINO -->|Pulsos STEP/DIR| MOTOR
    
    CAMERA <-->|USB / OpenCV| CAM
    
    CAMERA --> IMG
    CAMERA --> STATS
    CAMERA --> SNAP
```

## Flujo de Inicio del Sistema

```mermaid
flowchart TD
    START([Ejecutar python main.py]) --> INIT[Inicializar MainController]
    INIT --> WELCOME[Mostrar mensaje de bienvenida]
    WELCOME --> PROMPT[Mostrar prompt: >>>]
    PROMPT --> WAIT{Esperar entrada<br/>de usuario}
    
    WAIT -->|Comando recibido| PARSE[Parsear comando]
    PARSE --> VALIDATE{¿Comando<br/>válido?}
    
    VALIDATE -->|No| ERROR[Mostrar error]
    ERROR --> PROMPT
    
    VALIDATE -->|Sí| DISPATCH[Despachar a handler]
    DISPATCH --> EXEC[Ejecutar comando]
    EXEC --> RESULT[Mostrar resultado]
    RESULT --> PROMPT
    
    WAIT -->|Ctrl+C o EOF| CLEANUP[Cleanup: cerrar dispositivos]
    CLEANUP --> END([Salir])
```

## Flujo de Conexión de Dispositivos

```mermaid
flowchart TD
    subgraph "Conexión Arduino"
        CONN_START[Comando: connect COM3] --> OPEN_SERIAL[Abrir puerto serial]
        OPEN_SERIAL --> WAIT_RESET[Esperar 2s para reset]
        WAIT_RESET --> READ_INIT[Leer mensaje inicial]
        READ_INIT --> CONN_OK[Stepper conectado]
    end
    
    subgraph "Conexión Cámara"
        CAM_START[Comando: cam] --> DETECT[Detectar cámaras USB]
        DETECT --> CHECK{¿Cámaras<br/>encontradas?}
        CHECK -->|No| CAM_ERROR[Error: sin cámaras]
        CHECK -->|Sí| SELECT[Seleccionar cámara]
        SELECT --> OPEN_CAM[Abrir VideoCapture]
        OPEN_CAM --> GET_INFO[Obtener resolución/info]
        GET_INFO --> CAM_OK[Cámara conectada]
    end
```

## Flujo de Control de Motor Stepper

```mermaid
flowchart TD
    SPEED_CMD[Comando: speed 150] --> CHECK_CONN{¿Stepper<br/>conectado?}
    CHECK_CONN -->|No| ERR1[Error: no conectado]
    
    CHECK_CONN -->|Sí| VALIDATE_RPM{¿RPM válido<br/>0-300?}
    VALIDATE_RPM -->|No| ERR2[Advertencia: valor fuera de rango]
    ERR2 --> CLAMP[Ajustar a rango válido]
    
    VALIDATE_RPM -->|Sí| CLAMP
    CLAMP --> BUILD_CMD[Construir comando: SPEED:150]
    BUILD_CMD --> SEND[Enviar por serial]
    SEND --> FLUSH[Flush buffer]
    FLUSH --> WAIT_RESP[Esperar respuesta Arduino]
    
    WAIT_RESP --> READ{¿Respuesta<br/>recibida?}
    READ -->|No| TIMEOUT[Advertencia: sin respuesta]
    READ -->|Sí| PARSE_RESP[Parsear respuesta]
    PARSE_RESP --> UPDATE[Actualizar estado interno]
    UPDATE --> SHOW[Mostrar confirmación]
    
    subgraph "Arduino"
        ARD_RECV[Recibir comando serial] --> ARD_PARSE[Parsear SPEED:XXX]
        ARD_PARSE --> ARD_CALC[Calcular delay entre pasos]
        ARD_CALC --> ARD_SET[Configurar stepDelay]
        ARD_SET --> ARD_SEND[Enviar confirmación]
        ARD_SEND --> ARD_LOOP[Loop: generar pulsos STEP]
    end
```

## Flujo de Captura de Imágenes

```mermaid
flowchart TD
    CAPTURE_CMD[Comando: capture 10 100 avg] --> PARSE_ARGS[Parsear argumentos]
    PARSE_ARGS --> EXTRACT[Extraer: N=10, EXP=100ms, MODE=avg]
    
    EXTRACT --> CHECK_CAM{¿Cámara<br/>conectada?}
    CHECK_CAM -->|No| ERR_CAM[Error: cámara no conectada]
    
    CHECK_CAM -->|Sí| SET_EXP[Configurar exposición manual]
    SET_EXP --> WAIT_CAM[Esperar ajuste de cámara 0.5s]
    WAIT_CAM --> INIT_STATS[Inicializar arrays de estadísticas]
    
    INIT_STATS --> START_TIMER[Iniciar timer de ráfaga]
    START_TIMER --> LOOP_START{i < N?}
    
    LOOP_START -->|No| LOOP_END[Fin de captura]
    LOOP_START -->|Sí| TIMER1[Timestamp inicial]
    
    TIMER1 --> CAP[Capturar imagen]
    CAP --> TIMER2[Timestamp final]
    TIMER2 --> CALC_TIME[Calcular tiempo de captura]
    CALC_TIME --> STORE_IMG[Guardar imagen en array]
    STORE_IMG --> STORE_TIME[Guardar tiempo en array]
    
    STORE_TIME --> CALC_INT{¿i > 0?}
    CALC_INT -->|Sí| CALC_INTERVAL[Calcular intervalo desde anterior]
    CALC_INTERVAL --> STORE_INT[Guardar intervalo]
    CALC_INT -->|No| SKIP_INT[Intervalo = N/A]
    
    STORE_INT --> PRINT[Imprimir estadísticas de imagen]
    SKIP_INT --> PRINT
    PRINT --> DELAY[Delay entre capturas]
    DELAY --> INCREMENT[i++]
    INCREMENT --> LOOP_START
    
    LOOP_END --> END_TIMER[Finalizar timer total]
    END_TIMER --> CALC_STATS[Calcular estadísticas]
    CALC_STATS --> PRINT_STATS[Imprimir estadísticas completas]
    
    PRINT_STATS --> PROCESS{Modo de<br/>procesamiento}
    PROCESS -->|avg| AVG[Promediar imágenes]
    PROCESS -->|sum| SUM[Sumar imágenes]
    
    AVG --> SAVE_IMG[Guardar imagen procesada]
    SUM --> SAVE_IMG
    
    SAVE_IMG --> ASK{¿Guardar<br/>estadísticas?}
    ASK -->|Sí| SAVE_STATS[Guardar archivo .txt]
    ASK -->|No| DONE[Finalizado]
    SAVE_STATS --> DONE
```

## Flujo de Vista en Vivo (Live View)

```mermaid
flowchart TD
    LIVE_CMD[Comando: live] --> CHECK_CAM{¿Cámara<br/>conectada?}
    CHECK_CAM -->|No| ERR[Error: cámara no conectada]
    
    CHECK_CAM -->|Sí| SHOW_INST[Mostrar instrucciones]
    SHOW_INST --> WAIT_USER[Esperar usuario presione tecla]
    WAIT_USER --> INIT_WIN[Crear ventana OpenCV]
    
    INIT_WIN --> LOOP{Loop infinito}
    LOOP --> READ_FRAME[Leer frame de cámara]
    READ_FRAME --> CHECK_FRAME{¿Frame<br/>válido?}
    
    CHECK_FRAME -->|No| ERR_FRAME[Error: frame inválido]
    ERR_FRAME --> EXIT
    
    CHECK_FRAME -->|Sí| OVERLAY[Agregar info overlay]
    OVERLAY --> DISPLAY[Mostrar en ventana]
    DISPLAY --> KEY[Leer tecla con waitKey(1)]
    
    KEY --> CHECK_KEY{¿Qué tecla?}
    CHECK_KEY -->|'q' o ESC| EXIT[Salir de live view]
    CHECK_KEY -->|'s'| SNAP[Guardar snapshot]
    CHECK_KEY -->|Otra| LOOP
    
    SNAP --> GEN_NAME[Generar nombre con timestamp]
    GEN_NAME --> SAVE_SNAP[Guardar snapshot]
    SAVE_SNAP --> PRINT_SNAP[Imprimir confirmación]
    PRINT_SNAP --> LOOP
    
    EXIT --> DESTROY[Destruir ventanas OpenCV]
    DESTROY --> CLEAR[Limpiar buffers]
    CLEAR --> DONE[Retornar a prompt]
```

## Flujo de Procesamiento de Imágenes

```mermaid
flowchart TD
    START[Array de imágenes capturadas] --> CHECK{¿Modo de<br/>procesamiento?}
    
    subgraph "Promediado (avg)"
        AVG_START[Modo: average] --> CONVERT_F[Convertir a float]
        CONVERT_F --> MEAN[np.mean(images, axis=0)]
        MEAN --> CONVERT_U8[Convertir a uint8]
        CONVERT_U8 --> AVG_RESULT[Imagen promediada]
    end
    
    subgraph "Suma (sum)"
        SUM_START[Modo: sum] --> SUM_F[Sumar como float64]
        SUM_F --> NORMALIZE{¿Normalizar?}
        NORMALIZE -->|Sí| NORM[Normalizar 0-255]
        NORMALIZE -->|No| CLIP[Clip 0-255]
        NORM --> SUM_RESULT[Imagen sumada]
        CLIP --> SUM_RESULT
    end
    
    CHECK -->|avg| AVG_START
    CHECK -->|sum| SUM_START
    
    AVG_RESULT --> SAVE
    SUM_RESULT --> SAVE
    
    SAVE[cv2.imwrite] --> TIMESTAMP[Generar nombre con timestamp]
    TIMESTAMP --> FILE[Guardar archivo JPG]
```

## Estados del Sistema

```mermaid
stateDiagram-v2
    [*] --> Desconectado
    
    Desconectado --> StepperConectado: connect COM3
    Desconectado --> CamaraConectada: cam
    
    StepperConectado --> Ambos: cam
    CamaraConectada --> Ambos: connect COM3
    
    StepperConectado --> MotorActivo: speed > 0
    MotorActivo --> StepperConectado: speed 0 / stop
    
    CamaraConectada --> Capturando: capture
    Capturando --> CamaraConectada: fin de captura
    
    CamaraConectada --> VistaEnVivo: live
    VistaEnVivo --> CamaraConectada: 'q' / ESC
    
    Ambos --> MotorYCaptura: speed > 0 && capture
    MotorYCaptura --> Ambos: fin
    
    StepperConectado --> Desconectado: disconnect
    CamaraConectada --> Desconectado: disconnect
    Ambos --> Desconectado: disconnect
    MotorActivo --> Desconectado: disconnect (auto-stop)
    
    Desconectado --> [*]: exit
    StepperConectado --> [*]: exit
    CamaraConectada --> [*]: exit
    Ambos --> [*]: exit
```

## Diagrama de Secuencia - Captura Completa

```mermaid
sequenceDiagram
    actor Usuario
    participant CLI as CLI/Main
    participant Camera as CameraController
    participant USB as Cámara USB
    participant File as Sistema de Archivos
    
    Usuario->>CLI: capture 10 100 avg
    CLI->>Camera: capture_multiple(10, 100)
    Camera->>USB: set_exposure(100)
    USB-->>Camera: OK
    
    Note over Camera: Espera 0.5s
    
    loop Para cada imagen (i=1..10)
        Camera->>Camera: timestamp_start
        Camera->>USB: read()
        USB-->>Camera: frame
        Camera->>Camera: timestamp_end
        Camera->>Camera: calcular tiempo
        Camera->>Camera: guardar en array
        Camera->>CLI: Image i/10 | 45ms | 544ms
        Note over Camera: Delay 0.5s
    end
    
    Camera->>Camera: calcular estadísticas
    Camera->>CLI: CAPTURE STATISTICS
    CLI->>Usuario: Mostrar stats
    
    Camera->>Camera: average_images(array)
    Camera->>File: save_image(result)
    File-->>Camera: OK
    
    Camera->>CLI: Resultado guardado
    CLI->>Usuario: ¿Guardar estadísticas? (y/n)
    Usuario->>CLI: y
    CLI->>Camera: save_capture_stats()
    Camera->>File: write stats.txt
    File-->>Camera: OK
    Camera->>CLI: Stats guardadas
```

## Diagrama de Componentes

```mermaid
graph TB
    subgraph "Capa de Presentación"
        CLI[CLI Interface]
        HELP[Help System]
    end
    
    subgraph "Capa de Lógica"
        MAIN[MainController]
        PARSER[Command Parser]
        DISPATCH[Command Dispatcher]
    end
    
    subgraph "Capa de Control de Hardware"
        STEPPER[StepperController]
        CAMERA[CameraController]
    end
    
    subgraph "Capa de Comunicación"
        SERIAL[PySerial]
        OPENCV[OpenCV]
    end
    
    subgraph "Capa de Procesamiento"
        IMG_PROC[Image Processing]
        STATS[Statistics Calculator]
        TIMING[Timing Measurement]
    end
    
    subgraph "Capa de Persistencia"
        FILE_IO[File I/O]
        IMG_SAVE[Image Saver]
        STATS_SAVE[Stats Saver]
    end
    
    CLI --> MAIN
    HELP --> CLI
    MAIN --> PARSER
    PARSER --> DISPATCH
    
    DISPATCH --> STEPPER
    DISPATCH --> CAMERA
    
    STEPPER --> SERIAL
    CAMERA --> OPENCV
    
    CAMERA --> IMG_PROC
    CAMERA --> STATS
    CAMERA --> TIMING
    
    IMG_PROC --> IMG_SAVE
    STATS --> STATS_SAVE
    
    IMG_SAVE --> FILE_IO
    STATS_SAVE --> FILE_IO
```

## Leyenda de Símbolos

- **Rectángulos**: Procesos o acciones
- **Rombos**: Decisiones o condiciones
- **Círculos**: Puntos de inicio/fin
- **Flechas sólidas**: Flujo de control
- **Flechas punteadas**: Flujo de datos
- **Subgraphs**: Agrupación de componentes relacionados
