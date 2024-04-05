import math, time
import paho.mqtt.client as mqtt

## TEMP VARIABLES
increment = 0.05     # The resolution of increments in time (t)
simTime = 4*math.pi      # Time length for system to draw
## TEMP VARIABLES

##~~~~~~~~~~~~~Eoin Brennan Kinematics Visualiser for Sisyphus System ~~~~~~~~~~~~~~~~~~~##

# Script that calculates joint values and arm positions for user control visualiser.
# Pushes joint control lists to motor controller when user desired.

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

## User Variables

armLength = [57.5, 57.5]
drawArea = 115 

## System Variables

currPath = []

# Classes

class pathConstruct:
    def __init__(self, end_X, end_Y, mid_X, mid_Y, jointTwist1, jointTwist2):
        self.endCoords = [end_X, end_Y] # Access end effector coordinates
        self.midCoords = [mid_X, mid_Y] # Access end effector coordinates
        self.JointTwists = [jointTwist1, jointTwist2]   # Access joint rotations

    def pubCoords(self, topic):
        msg = "U,P," + str(self.endCoords[0]) + "," + str(self.endCoords[1]) + "," + str(self.midCoords[0]) + "," + str(self.midCoords[1])
        client.publish(topic, msg)
        
        
## MQTT Connection

# Publishers
mqtt_broker = "localhost"
user_topic = "UserControlDisplay"
picomms_topic = "PiLocalCommunication"


## Callback Functions

def UserDisplay_Callback(client,userdata,message):
    msg = str(message.payload.decode("utf-8"))
    print("Message recieved: ", msg)


    msgSplit = msg.split(",")

    if msgSplit[0] == "P":  # Checking if message is intended for the Pi
        # Handle response based on job type

        match msgSplit[1]:
            case "Rose":   # Case to create a roses
                print("Rose test case")
                GenerateRose(int(msgSplit[2]), int(msgSplit[3]))
                PublishPath(user_topic)


            case "Liss":   # Generate Lissajous path
                print("Lissajous test case")

            case "Para":   # Generate Parametric path
                print("Parametric test case")
                GenerateParametric()
                PublishPath(user_topic)

            case "Sel":   # Select, push cuurent path through to system
                print("Confirm test case")

            case "Pause":    # Pause the current behaviour of the system
                print("Stop test case")


## Math functions

# Function converting cartesian coordinates to polar equivalent
def CartToPolar(x, y):
    magnitude = (x ** 2 + y ** 2) ** (1/2)  # length of distance from pythagoras

    # Using a tan to find the angle in range 0 to 2 pi
    angle = math.atan2(x,y)

    if x < 0:   # Checking for negative x quadrants and counteracting to set 0 degrees as north moving round 2 pi clockwise
        angle = angle + 2*math.pi

    return angle, magnitude


# Function to calculate the joint rotations from the polar coordinates
def PolarToJoint( angle, magnitude):
    angleDiff = math.acos( (0.5 * magnitude) / armLength[0])
    jointBase = angle - angleDiff
    jointArm = 2 * angleDiff

    return jointBase, jointArm


## Path Generation Functions


# Rose Path Generation
def GenerateRose(n, d):
    print("Begin Rose generation")
    global currPath, armLength, increment
    currPath = []

    for i in range(int(4*math.pi/increment)+2):
        # Generate x and y coordinates
        if i == int(simTime/increment)+1: i = 4*math.pi
        else: i = i*increment
        
        roseCoeff = (drawArea - 5) * math.cos((n/d) * i)
        x_end = roseCoeff*math.cos(i)
        y_end = roseCoeff*math.sin(i)

        # Convert to polar
        angle, magnitude = CartToPolar(x_end,y_end)

        # Calculate the inverse kinematics to get joint rotations
        jointBase, jointArm = PolarToJoint(angle, magnitude)

        # Calculate the arm midpoint from the angle and arm length
        x_mid = math.sin(angle) * armLength[0]
        y_mid = math.sin(angle) * armLength[0]

        #Format the calculations into path structure
        pathPoint = pathConstruct(x_end, y_end, x_mid, y_mid, jointBase, jointArm)
        currPath.append(pathPoint)

    print("Finished generating rose path")
    print("Length of currPath is: ", len(currPath))

def GenerateParametric():
    print("Begin Parametric Generation")
    global currPath, armLength, increment
    currPath = []

    for i in range(int(simTime/increment)):
        # Generate x and y coordinates
        j = i*increment
        x_end = drawArea*0.6*math.cos(i)
        y_end = drawArea*0.4*math.sin(i)

        # Convert to polar
        angle, magnitude = CartToPolar(x_end,y_end)

        # Calculate the inverse kinematics to get joint rotations
        jointBase, jointArm = PolarToJoint(angle, magnitude)

        # Calculate the arm midpoint from the angle and arm length
        x_mid = math.sin(angle) * armLength[0]
        y_mid = math.sin(angle) * armLength[0]

        #Format the calculations into path structure
        pathPoint = pathConstruct(x_end, y_end, x_mid, y_mid, jointBase, jointArm)
        currPath.append(pathPoint)

    print("Finished generating rose path")
    print("Length of currPath is: ", len(currPath))


## Other Functions

# Publish Current Path
def PublishPath(topic):
    client.publish(topic, "U,S")    #Confirm start of path

    for i in range(len(currPath)):  # For each point, publish the coordinates using class function
        currPath[i].pubCoords(topic)

    client.publish(topic, "U,F")    #Confirm end of path


## Main Start

# Connecting to MQTT
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = UserDisplay_Callback # Setting callback function

client.connect(mqtt_broker) # Connect to the broker

print("Subscribing to topic: ", user_topic)
client.subscribe(user_topic)

client.loop_start()

# Test Message for Rose Generation
#client.publish(user_topic, "P,Rose,2,1")

while(1):
    time.sleep(1)