import time, serial
import paho.mqtt.client as mqtt

## Eoin Brennan Motor Communicator for Sisyphus System

# Intermediary point between raspberry pi and arduino that communicates motor behaviour.
# Handles updates on the moment by moment behaviour of the physical system through serial communication.

## System Variables

commandList = []
pathIndex = []
pause = False
firstPoint = True

# Classes

class pointConstruct:
    def __init__(self, endx, endy, midx, midy, twistBase, twistJoint):
        self.endx = endx; self.ebdy = endy
        self.midx = midx; self.midy = midy
        self.twistBase = twistBase
        self.twistJoint = twistJoint

    def pubUSB(self):
        msg = "P," + str(self.twistBase) + "," + str(self.twistJoint)
        port.write(msg)
        # Send to the arduino

    def pubVisualiserComms(self):   # Send to MQTT comms for the real time visualiser
        msg = "P," + str(self.endx) + "," + str(self.endy) + "," + str(self.midx) + "," + str(self.midy)
        client.publish(visualiser_topic, msg)
        
        
        
## MQTT Connection

# Broker and Topics
mqtt_broker = "localhost"
picomms_topic = "PathPublisher"
visualiser_topic = "RTVisualiser"


## Callback Functions

def PiCommsCallback(client,userdata,message):
    global firstPoint, pause 
    msg = str(message.payload.decode("utf-8"))

    msgSplit = msg.split(",")
       
    print("Message recieved: ", msg)
    match msgSplit[0]:
        case "S": # Starting sending a path
            # If no current path then send the first point
            if len(commandList) == 0:
                firstPoint = True
            print("Path Starting")
            pass
        case "F": # Finished sending a path
            if firstPoint == True:
                firstPoint = False
                # Call USB Comm for first 2 points
                commandList[0].pubUSB()
                commandList[1].pubUSB()          

        case "P":   # Incoming Point for the Arduino
            # Split message and append to the list
            print("Added to Command List")
            struc = pointConstruct(float(msgSplit[1]), float(msgSplit[2]), float(msgSplit[3]), float(msgSplit[4]), float(msgSplit[5]), float(msgSplit[6]))
            commandList.append(struc)
            pass

        case "Pause": # Pause movement of the arduino temporarily
            # Toggle pause variable that holds arduino commands
            pause = not pause

        case "Delete":  # Clear the current command list for the arduino
            global CommandList
            CommandList.clear()



## Other Functions

def USBRead():
    while (1):
        input = port.read() # Read next character
        if input == "C":    # Check if a confirmation message
            ArdConfirm()
            input = ""


def ArdConfirm():
    global commandList
    if len(commandList > 2):
        # Send next point if one is available and not on pause
        while pause == False:
            commandList[2].PubUSB()

    if commandList[0] != []:
        # Send coords to visualiser
        commandList[0].pubVisualiserComms()
        # Delete the completed task
        commandList[0].pop


## Main Start

# Connecting to Serial
port = serial.Serial("/dev/ttyUSB0", baudrate = 7200, timeout = 2)

# Connecting to MQTT
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = PiCommsCallback # Setting callback function

client.connect(mqtt_broker) # Connect to the broker

print("Subscribing to topic: ", picomms_topic)
client.subscribe(picomms_topic)

client.loop_start()



# Test Message for Rose Generation
#client.publish(user_topic, "P,Rose,2,1")

while(1):
    USBRead(port)
    time.sleep(1)