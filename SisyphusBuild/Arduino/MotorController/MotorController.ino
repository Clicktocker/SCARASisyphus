/*
Eoin Brennan Sisyphus Masters Project Motor Controller
Arduino Motor Control system taking inputs from raspberry pi through USB serial

*/
#include <Stepper.h>
#define DEG_PER_STEP 1.8
#define STEP_PER_REVOLUTION (360/DEG_PER_STEP)
// Setting hall effect sensor pins
const int baseSensor = A0;
const int endSensor = A1;

// Setting motor control Variables
int currSteps[2] = {0,0};
int targetSteps[4] = {-1,-1,-1,-1};
bool moveStatus = false;

// Setting USB Comms Variables
static char message[50];
static unsigned int pos = 0;

// Defining the Stepper Motors
const int stepsPerRevolution=50;
Stepper stepperBase(STEP_PER_REVOLUTION, 8,9,10,11);
Stepper stepperJoint(STEP_PER_REVOLUTION, 4,5,6,7);


void setup() {
  // Setting Hall Effect Sensors
  pinMode(baseSensor, INPUT);
  pinMode(endSensor, INPUT);
  stepperBase.setSpeed(10);
  Serial.begin(9600);
  //stepperBase.step(100);
  stepperJoint.step(20);
  //HomeRoutine();
}

void loop() {
  // Check for data in serial buffer
  while (Serial.available() > 0){
    Serial.write("Reading\n");
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
  delay(50);
  if ((moveStatus == true) && (targetSteps[0] != -1)){
    StepsControl(targetSteps[0], targetSteps[1], 1500);
  }
}

void MessageHandler(char msg[50]){
  char charHold[50];
  // Respond to Message type
  switch (msg[0]) {
    case 'T':{ // Target
      // Add target point into buffer slot and act on the first point
      strtok(msg, ":");
      char *targetBase = strtok(NULL, ",");
      char *targetArm = strtok(NULL, ",");
      float angBase = atof(targetBase);
      float angArm = atof(targetArm);
      // Convert to step equivalent and store
      targetSteps[2] = (angBase / 0.9) + 0.5;
      targetSteps[3] = (angArm / 0.9) + 0.5;
      moveStatus = true;
      break;
    }

    case 'I':{ // Incoming
      // Add point into target positions and check again for next point
      strtok(msg, ":");
      char *targetBase = strtok(NULL, ",");
      char *targetArm = strtok(NULL, ",");
      float angBase = atof(targetBase);
      float angArm = atof(targetArm);
      
      // Convert to step equivalent and store
      targetSteps[0] = (angBase / 0.9) + 0.5;
      targetSteps[1] = (angArm / 0.9) + 0.5;
      moveStatus = false;
      break;
    }
    case 'D':{ // Delete
      // Remove the currently stored targets
      break;
    }
    case 'P':{ // Pause
      // Enter waiting function until getting a resume command
      moveStatus = !moveStatus;
      break;
    }
    default:{ // Back up response
      // Clear message and move on
      Serial.println("Default Response");
      break;
    }
  }
  Serial.println("Exiting System");
  
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
    delay(800);
    sensorReading = analogRead(baseSensor);
    
    if (sensorReading > largestReading){
      // Store the reading and position
      largestReading = sensorReading;
      largestPosition = inc;
    }
    Serial.println(String("Position and value:" ) + inc + ":" + sensorReading);
  }
  // Move to the largest position
  stepperBase.step(largestPosition);
  Serial.println(largestPosition);

  //Reset variables and perform second sweep
  largestReading = 512;
  largestPosition = 0;
  for (inc = 1; inc <=50; inc++){
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
      stepperBase.step(stepsBase);
    }
    else if (stepsBase == 0) // Rotate joint only
    {
      stepperJoint.step(stepsJoint);
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
