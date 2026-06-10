/*
 * Stepper Motor Control with TB6560 Driver
 * 
 * Receives speed commands via serial and controls a stepper motor.
 * 
 * Connections:
 * - TB6560 PUL+ (or CLK+) -> Arduino Pin 3
 * - TB6560 DIR+ (or CW+)  -> Arduino Pin 4
 * - TB6560 ENA+ (optional) -> Arduino Pin 5
 * - TB6560 PUL-, DIR-, ENA- -> Arduino GND
 * - TB6560 VCC -> Power supply (12-36V DC)
 * - TB6560 GND -> Power supply GND
 * - TB6560 A+, A-, B+, B- -> Stepper motor coils
 * 
 * Note: TB6560 uses common anode (+) logic
 */

// Pin definitions
const int STEP_PIN = 3;   // PUL+ or CLK+ on TB6560
const int DIR_PIN = 4;    // DIR+ or CW+ on TB6560
const int ENABLE_PIN = 5; // ENA+ on TB6560 (optional)

// Motor parameters
const int STEPS_PER_REVOLUTION = 200;  // Change if your motor has different steps
int currentSpeed = 0;  // Current RPM
unsigned long stepDelay = 0;  // Microseconds between steps

void setup() {
  // Initialize pins
  pinMode(STEP_PIN, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);
  pinMode(ENABLE_PIN, OUTPUT);
  
  // Set direction (HIGH = clockwise, LOW = counterclockwise)
  digitalWrite(DIR_PIN, HIGH);
  
  // Enable the motor (LOW = enabled, HIGH = disabled for TB6560)
  digitalWrite(ENABLE_PIN, LOW);
  
  // Initialize serial communication
  Serial.begin(9600);
  Serial.println("Arduino Stepper Controller Ready (TB6560)");
  Serial.println("Send command: SPEED:xxx (RPM)");
}

void loop() {
  // Check for serial commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command.startsWith("SPEED:")) {
      int rpm = command.substring(6).toInt();
      setSpeed(rpm);
      Serial.print("Speed set to ");
      Serial.print(rpm);
      Serial.println(" RPM");
    }
  }
  
  // Step the motor if speed > 0
  if (currentSpeed > 0 && stepDelay > 0) {
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(stepDelay / 2);
    digitalWrite(STEP_PIN, LOW);
    delayMicroseconds(stepDelay / 2);
  }
}

void setSpeed(int rpm) {
  currentSpeed = rpm;
  
  if (rpm == 0) {
    stepDelay = 0;
    // Optionally disable motor
    // digitalWrite(ENABLE_PIN, HIGH);
  } else {
    // Calculate delay between steps
    // delay (microseconds) = 60,000,000 / (RPM * STEPS_PER_REVOLUTION)
    stepDelay = 60000000L / (rpm * STEPS_PER_REVOLUTION);
    
    // Enable motor if it was disabled
    digitalWrite(ENABLE_PIN, LOW);
  }
}
