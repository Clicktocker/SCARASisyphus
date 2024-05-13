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
  if ((moveStatus == true) && (targetSteps[0] != -1)){
    StepsControl(targetSteps[0], targetSteps[1], 3000);
  }
  else if ((targetSteps[0] == -1) && (targetSteps[2] != -1)){
    targetSteps[0] = targetSteps[2];
    targetSteps[1] = targetSteps[3];
    targetSteps[2] = -1;
    targetSteps[3] = -1;
  }
  
}

void MessageHandler(char msg[50]){
  char charHold[50];
  // Respond to Message type
  switch (msg[0]) {
    case 'T':{ // Target
      // Add target point into buffer slot and open movement access
      strtok(msg, ":");
      char *targetBase = strtok(NULL, ",");
      char *targetArm = strtok(NULL, ",");
      float angBase = atof(targetBase);
      float angArm = atof(targetArm);
      // Convert any negative steps to positive
      if (targetSteps[2] < 0){ targetSteps[2] += 400; }
      if (targetSteps[3] < 0){ targetSteps[3] += 400; }
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
      if (targetSteps[0] < 0){ targetSteps[0] += 400; }
      targetSteps[1] = (angArm / 0.9) + 0.5;
      if (targetSteps[1] < 0){ targetSteps[1] += 400; }
      moveStatus = false;
      break;
    }
    case 'D':{ // Delete
      // Remove the currently stored targets
      break;
    }
    default:{ // Back up response
      // Clear message and move on
      break;
    }
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
    delay(60);
    sensorReading = analogRead(baseSensor);
    
    if (sensorReading > largestReading){
      // Store the reading and position
      largestReading = sensorReading;
      largestPosition = inc;
    }
    //Serial.println(String("Position and value:" ) + inc + ":" + sensorReading);
  }
  // Move to the largest position
  stepperBase.step(largestPosition);
  //Serial.println(largestPosition);

  //Reset variables and perform second sweep
  largestReading = 512;
  largestPosition = 0;
  for (inc = 1; inc <=50; inc++){
    stepperJoint.step(1);
    delay(60);
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
    int baseMove, jointMove;
    // Get the number of steps needed to reach the 
    baseMove = stepsBase - currSteps[0];
    jointMove = stepsJoint - currSteps[1];  

    // Correct for movements gerater than half the circle
    if (baseMove < -200) { baseMove += 400; }
    else if (baseMove > 200) { baseMove -= 400;  }

    if (jointMove < -200) { jointMove += 400; }
    else if (jointMove > 200) { jointMove -= 400;  }
    
    
    int stepsTotal = abs(baseMove * jointMove);
    int timeDiv;
    String msg;
    
    int baseDir, jointDir, i, timeStart, currTime;
    if (baseMove > 0) { baseDir = 1; }
    else { baseDir = - 1; }

    if (jointMove > 0) { jointDir = 1;}
    else { jointDir = - 1; }


    if (jointMove == 0) // Rotate base only
    {
      timeDiv = abs(timeDelay/baseMove);
      if (timeDiv < 1){timeDiv = 1;}
      msg = String("timeDiv in jointMove 0: ") + timeDiv;
      //Serial.println(msg);
      for (i = 1; i <= abs(baseMove); i++){
        stepperBase.step(baseDir);
        delay(timeDiv);
      }
    }
    else if (baseMove == 0) // Rotate joint only
    {
      
      timeDiv = abs(timeDelay/jointMove);
      if (timeDiv < 1){timeDiv = 1;}
      msg = String("timeDiv in baseMove 0: ") + timeDiv;
      //Serial.println(msg);
      for (i = 1; i <= abs(jointMove); i++){
        stepperJoint.step(jointDir);
        delay(timeDiv);
      }
    }
    else {
      timeDiv = timeDelay / stepsTotal;
      if (timeDiv < 1){timeDiv = 1;}
      msg = String("timeDiv in both move: ") + timeDiv;
      //Serial.println(msg);
      
      for (i = 1; i <= stepsTotal; i++) 
      {

        if (i % stepsJoint == 0) {
          stepperBase.step(baseDir);
        }
        if (i % stepsBase == 0) {
          stepperJoint.step(jointDir);
        }

        delay(timeDiv);
        
      }
    }
    // Shifting position store buffer and confirming completion
    currSteps[0] = stepsBase;
    currSteps[1] = stepsJoint;
    
    targetSteps[0] = targetSteps[2];
    targetSteps[1] = targetSteps[3];
    targetSteps[2] = -1; targetSteps[3] = -1;
    
    //delay(timeDelay);
    Serial.write("C\n");
  }
