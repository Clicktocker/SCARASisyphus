/*
Eoin Brennan Sisyphus Masters Project Motor Controller
Arduino Motor Control system taking inputs from raspberry pi through USB serial

*/
#include "Stepper.h"
const int stepsPerRevolution = 200;

#define basePwmA 3
#define basePwmB 11
#define baseBrakeA 9
#define baseBrakeB 8
#define baseDirA 12
#define baseDirB 13

#define jointPwmA 2
#define jointPwmB 14
#define jointBrakeA 7
#define jointBrakeB 6
#define jointDirA 15
#define jointDirB 16


Stepper baseStepper = Stepper(stepsPerRevolution, baseDirA, baseDirB);
Stepper jointStepper = Stepper(stepsPerRevolution, jointDirA, jointDirB);

float twistBase = 0;
float twistJoint = 0;
float currBase = 0;
float currJoint = 0;

void setup() {
  // Setup Base Stepper Pins
  pinMode(basePwmA, OUTPUT);
  pinMode(basePwmB, OUTPUT);
  pinMode(baseBrakeA, OUTPUT);
  pinMode(baseBrakeB, OUTPUT);

  digitalWrite(basePwmA, HIGH);
  digitalWrite(basePwmB, HIGH);
  digitalWrite(baseBrakeA, LOW);
  digitalWrite(baseBrakeB, LOW);

  // Setup Joint Stepper Pins
  pinMode(jointPwmA, OUTPUT);
  pinMode(jointPwmB, OUTPUT);
  pinMode(jointBrakeA, OUTPUT);
  pinMode(jointBrakeB, OUTPUT);

  digitalWrite(jointPwmA, HIGH);
  digitalWrite(jointPwmB, HIGH);
  digitalWrite(jointBrakeA, LOW);
  digitalWrite(jointBrakeB, LOW);

  // Set the motor speeds (RPMs):
  baseStepper.setSpeed(60);
  jointStepper.setSpeed(60);
  
  // Connect to the serial
  
  // Run the homing sequence and initialise motor positions
  
}


void loop() {  
  // Complete revolution in positive direction
  baseStepper.step(stepsPerRevolution);

  delay(2000);

  // Complete revolution in negative direction
  baseStepper.step(-stepsPerRevolution);

  delay(2000);
    
  // Checking the USB serial for a task to start

  // Start motor movement task with input twists (a, b)
  
}


void motorControl(float twistBase, float twistJoint) {
  // Compare a and b to the current known position
  
  // Move to the target motor position in shortest distance 
  
}
