import math, time
import paho.mqtt.client as mqtt
from fractions import Fraction

## TEMP VARIABLES
increment = 0.05     # The resolution of increments in time (t)
simTime = 4*math.pi      # Time length for system to draw
## TEMP VARIABLES

##~~~~~~~~~~~~~Eoin Brennan Kinematics Visualiser for Sisyphus System ~~~~~~~~~~~~~~~~~~~##

# Script that calculates joint values and arm positions for user control visualiser.
# Pushes joint control lists to motor controller when user desired.

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

## User Variables

armLength = [55, 55]
drawArea = 115 

## System Variables

currPath = []
pathIndex = []

# Classes

class pathConstruct:
    def __init__(self, end_X, end_Y, mid_X, mid_Y, jointTwist1, jointTwist2):
        self.endCoords = [end_X, end_Y] # Access end effector coordinates
        self.midCoords = [mid_X, mid_Y] # Access end effector coordinates
        self.JointTwists = [jointTwist1, jointTwist2]   # Access joint rotations

    def pubCoords(self,identifier, topic):
        msg = identifier + str(self.endCoords[0]) + "," + str(self.endCoords[1]) + "," + str(self.midCoords[0]) + "," + str(self.midCoords[1])
        client.publish(topic, msg)

    def pubAll(self, identifier, topic):
        msg = identifier+str(self.endCoords[0])+","+str(self.endCoords[1])+","+str(self.midCoords[0])+","+str(self.midCoords[1])+","+str(self.JointTwists[0])+","+str(self.JointTwists[1])
        client.publish(topic, msg)
        
        
## MQTT Connection

# Publishers
mqtt_broker = "localhost"
user_topic = "UserControlDisplay"
picomms_topic = "PathPublisher"


## Callback Functions

def UserDisplay_Callback(client,userdata,message):
    msg = str(message.payload.decode("utf-8"))

    msgSplit = msg.split(",")

    if msgSplit[0] == "P":  # Checking if message is intended for the Pi
        # Handle response based on job type
        print("Message recieved: ", msg)
        match msgSplit[1]:
            case "Rose":   # Case to create a roses
                if msgSplit[3].isnumeric() and msgSplit[4].isnumeric(): 
                    GenerateRose(round(float(msgSplit[2]), 3), int(msgSplit[3]), int(msgSplit[4]))
                    PublishPath(user_topic)
                else: print("Error values entered")


            case "Liss":     # Generate Lissajous path
               
                GenerateLissajous(round(float(msgSplit[2]), 3), round(float(msgSplit[3]), 2), round(float(msgSplit[4]), 2), float(msgSplit[5]))
                PublishPath(user_topic)
                print("Lissajous test case")

            case "Para":     # Generate Parametric path
                print("Parametric test case")
                GenerateParametric()
                PublishPath(user_topic)

            case "ResSel":  # Reset Select, reset the system path and add current path
                client.publish(picomms_topic, "Delete")
                SendToSystem()

            case "Sel":      # Select, add cuurent path through to system
                SendToSystem()

            case "Pause":    # Pause the current behaviour of the system
                client.publish(picomms_topic, "Pause")
                print("Stop test case")

            case "Resend":   # Resends the current stored path to the visualiser
                PublishWholePath(user_topic)

            case "Reset":
                global currPath
                print("Reset Stored Path")
                currPath=[]


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
def PolarToJoint( angle, magnitude, prevJointBase):
    angleDiff = math.acos(magnitude / 2 / armLength[0])
    prevChange = [abs( prevJointBase - ((angle - angleDiff) % (2*math.pi)) ) , abs( prevJointBase - ((angle + angleDiff) % (2*math.pi)) ) ]
    
    for i in range(2):
        if prevChange[i] > math.pi: prevChange[i] = 2*math.pi - prevChange[i]

    if prevChange[0] < prevChange[1]:
        jointBase = angle - angleDiff
    else: 
        jointBase = angle + angleDiff


    jointArm = 2 * angleDiff

    return jointBase, jointArm


## Path Generation Functions

# Lissajous Curve Generation
def GenerateLissajous(res, a, b, delta):
    global currPath, pathIndex
    pathIndex = len(currPath)
    
    print("a and b are:" , a , "," , b)
    print("LCM is: " , math.lcm(int(a*100), int(b*100)))
    a_calc = int(a * 100)
    b_calc = int(b * 100)

    period = 2*math.pi * math.lcm(int(a_calc),int(b_calc)) / (a * b)
    period = period/100
    delta = delta * math.pi

    increment = 0.025 * res
    theta = -increment
    jointBase = 0
    while theta < period:
        theta = theta + increment
        if theta> period: theta = period

        x_end = (drawArea) / 1.5 * math.sin((theta * a) + delta)
        y_end = (drawArea) / 1.5 * math.cos(theta*b)

        # Convert to polar
        angle, magnitude = CartToPolar(x_end,y_end)

        # Calculate the inverse kinematics to get joint rotations
        jointBase, jointArm = PolarToJoint(angle, magnitude, jointBase)

        # Calculate the arm midpoint from the angle and arm length
        x_mid = math.sin(jointBase) * armLength[0]
        y_mid = math.cos(jointBase) * armLength[0]

        #Format the calculations into path structure
        pathPoint = pathConstruct(x_end, y_end, x_mid, y_mid, jointBase, jointArm)
        currPath.append(pathPoint)

    print("Finished generating lissajous")
    print("Length of currPath is: ", len(currPath))
    print("Period is: ", period/math.pi)

    pass


# Rose Path Generation
def GenerateRose(res, n, d):
    print("Begin Rose generation")
    global currPath, pathIndex
    pathIndex = len(currPath)
    k = Fraction(n, d)
    n = k.numerator; d = k.denominator
    # Define the period
    if k % 1 != 0:  # Non-integer values of k
        if ((n%2 != 0) and (d%2 != 0)) or ((n%2 == 0) and (d%2 == 0)): period = d *math.pi
        else: period = 2*d*math.pi
        
    else:           # Integer values of k
        if k%2 != 0: period = math.pi
        else: period = math.pi * 2
    
    increment = 0.025 * res
    theta = -increment
    jointBase=0
    while theta < period:
        # Generate x and y coordinates
        theta = theta + increment
        if theta > period: theta = period
        
        roseCoeff = (drawArea - 5) * math.cos((n/d) * theta)
        x_end = roseCoeff*math.cos(theta)
        y_end = roseCoeff*math.sin(theta)

        # Convert to polar
        angle, magnitude = CartToPolar(x_end,y_end)

        # Calculate the inverse kinematics to get joint rotations
        print("Angle/Magtnitude input is: " , angle , "," , magnitude)

        jointBase, jointArm = PolarToJoint(angle, magnitude, jointBase)

        print("Joint Base Ouput: ", jointBase)
        # Calculate the arm midpoint from the angle and arm length
        x_mid = math.sin(jointBase) * armLength[0]
        y_mid = math.cos(jointBase) * armLength[0]
        

        #Format the calculations into path structure
        pathPoint = pathConstruct(x_end, y_end, x_mid, y_mid, jointBase, jointArm)
        currPath.append(pathPoint)

    print("Finished generating rose path")
    print("Length of currPath is: ", len(currPath))
    print("Period is: ", period/math.pi)
    print(k)

def GenerateParametric():
    print("Begin Parametric Generation")
    global currPath, armLength, increment

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

    for i in range((len(currPath)) - pathIndex):  # For each point, publish the coordinates using class function
        i += pathIndex
        currPath[i].pubCoords("U,P,",topic)

    client.publish(topic, "U,F")    #Confirm end of path


# Publish Current Path
def PublishWholePath(topic):
    client.publish(topic, "U,S")    #Confirm start of path

    for i in range(len(currPath)):  # For each point, publish the coordinates using class function
        currPath[i].pubCoords("U,P,",topic)

    client.publish(topic, "U,F")    #Confirm end of path

def SendToSystem():
    client.publish(picomms_topic, "S")  # Notify that the sequence is starting
    for i in range(len(currPath)):
        currPath[i].pubAll("P,", picomms_topic)
    client.publish(picomms_topic, "F")  # Notify that the sequence is finished


## Main Start

# Connecting to MQTT
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = UserDisplay_Callback # Setting callback function

client.connect(mqtt_broker) # Connect to the broker

print("Subscribing to topic: ", user_topic)
client.subscribe(user_topic)

client.loop_start()

client.publish(user_topic, 'BootedUp')

# Test Message for Rose Generation
#client.publish(user_topic, "P,Rose,2,1")

while(1):
    time.sleep(1)