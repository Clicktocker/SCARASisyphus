/*
Eoin Brennan Sisyphus Masters Project Motor Controller
Arduino Motor Control system taking inputs from raspberry pi through USB serial

*/
#include <Stepper.h>
// Setting hall effect sensor pins
const int baseSensor = A0;
const int endSensor = A1;

// Setting motor control Variables
int currBaseStep = 0;
int currJointStep = 0;
int targetSteps[4];

// Setting USB Comms Variables
static char message[50];
static unsigned int pos = 0;

// Defining the Stepper Motors
const int stepsPerRevolution=200;
Stepper stepperBase(stepsPerRevolution, 8,9,10,11);
Stepper stepperJoint(stepsPerRevolution, 4,3,5,6);


void setup() {
  // Setting Hall Effect Sensors
  pinMode(baseSensor, INPUT);
  pinMode(endSensor, INPUT);
  stepperBase.setSpeed(20);
  stepperJoint.setSpeed(20);
  Serial.begin(9600);

  HomeRoutine();
}

void loop() {
  // Check for data in serial buffer
  while (Serial.available() > 0){
    // Read next character from serial and respond
    char in = Serial.read();

    if (in != '\n') {
      // Add reading onto message list
      message[pos] = in;
      pos++;
    }
    else{
      message[pos] = '\n';
      pos = 0;

      MessageHandler(message);
    }  
  }
   
}

void MessageHandler(char msg[50]){
  // Respond to Message type
  switch (msg[1]) {
    case 'T': // Target
      // Add target point into buffer slot and act on the first point
      Serial.write("C\n");
      break;

    case 'I': // Incoming
      // Add point into target positions and check again for next point
      break;
    
    case 'D': // Delete
      // Remove the currently stored targets
      break;

    case 'P': // Pause
      // Enter waiting function until getting a resume command
      break;

    default: // Back up response
      // Clear message and move on
      break;
      
}
  
}

// Function that performs a sweep of each motor and measures the point of strongest
void HomeRoutine(){
  // Preparing variables
  int sensorReading, inc;
  int largestReading = 512;
  int largestPosition = 0;

  // First sweep test
  for (inc = 1; inc <=400; inc++){
    stepperBase.step(1);
    delay(10);
    sensorReading = analogRead(baseSensor);
    
    if (sensorReading > largestReading){
      // Store the reading and position
      largestReading = sensorReading;
      largestPosition = inc;
    }
  }
  // Move to the largest position
  stepperBase.step(inc);

  //Reset variables and perform second sweep
  largestReading = 512;
  largestPosition = 0;
  for (inc = 1; inc <=400; inc++){
    stepperJoint.step(1);
    delay(20);
    sensorReading = analogRead(endSensor);
    
    if (sensorReading > largestReading){
      // Store the reading and position
      largestReading = sensorReading;
      largestPosition = inc;
    }
  }  
  // Move to the largest position
  stepperJoint.step(inc);
  
}

// Function to opreate two motors at once
void StepsControl(int stepsBase, int stepsJoint, int timeDelay)
  {
    int stepsTotal = abs(stepsBase * stepsJoint);
    int timeDiv = timeDelay / stepsTotal;
    
    int baseDir, jointDir, i, timeStart, currTime;
    if (stepsBase > 0) { baseDir = 1; }
    else { baseDir = - 1; }

    if (stepsJoint > 0) { jointDir = 1;}
    else { jointDir = - 1; }


    if (stepsJoint == 0) // Rotate base only
    {
      stepperBase.setSpeed(10);
      stepperBase.step(stepsBase);
      stepperBase.setSpeed(20);
    }
    else if (stepsBase == 0) // Rotate joint only
    {
      stepperJoint.setSpeed(10);
      stepperJoint.step(stepsJoint);
      stepperJoint.setSpeed(20);
    }
    else {
      
      for (i = 1; i <= stepsTotal; i++) 
      {
        timeStart = millis();

        if (i % stepsJoint == 0) {
          stepperBase.step(baseDir);
        }
        if (i % stepsBase == 0) {
          stepperJoint.step(baseDir);
        }

        currTime = millis();
        while (currTime - timeStart < timeDiv) {
          currTime = millis();
        }
        
      }
    }
  }
