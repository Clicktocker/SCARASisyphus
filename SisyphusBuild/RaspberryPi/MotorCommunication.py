import time, serial, math
import paho.mqtt.client as mqtt

## Eoin Brennan Motor Communicator for Sisyphus System

# Intermediary point between raspberry pi and arduino that communicates motor behaviour.
# Handles updates on the moment by moment behaviour of the physical system through serial communication.

## System Variables

commandList = []
pathIndex = []
pause = False
ardWork = 0

# Classes

class pointConstruct:
    def __init__(self, endx, endy, midx, midy, twistBase, twistJoint):
        self.endx = endx; self.endy = endy
        self.midx = midx; self.midy = midy
        self.twistBase = round( twistBase * 180 / (1.8 *math.pi))
        self.twistJoint = round( twistJoint * 180 / (1.8 *math.pi))

        if self.twistBase < 0: self.twistBase += 400
        elif self.twistBase > 400: self.twistBase -= 400

        if self.twistJoint < 0: self.twistBase += 400
        elif self.twistJoint > 400: self.twistBase -= 400

    def pubUSB(self, startChar):
        msg = startChar + ":" + str(self.twistBase) + "," + str(self.twistJoint) + "\n"
        port.write(msg.encode())
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
    global pause 
    msg = str(message.payload.decode("utf-8"))

    msgSplit = msg.split(",")
       
    print("Message recieved: ", msg)
    match msgSplit[0]:     

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
            commandList.clear()



## Other Functions

def USBRead():
    if port.inWaiting() > 0:
        input = str(port.readline()) # Read next character
        print("Read on Serial: ", input)
        if input == "C":    # Check if a confirmation message
            ArdConfirm()


def ArdConfirm():
    global commandList, ardWork
    
    
    # Send coords to visualiser
    commandList[0].pubVisualiserComms()
    # Delete the completed task
    commandList.pop(0)

    ardWork -= 1


## Main Start

# Connecting to Serial
port = serial.Serial("/dev/ttyUSB0", baudrate = 9600, timeout = 2)

# Connecting to MQTT
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = PiCommsCallback # Setting callback function

client.connect(mqtt_broker) # Connect to the broker

print("Subscribing to topic: ", picomms_topic)
client.subscribe(picomms_topic)
client.publish(visualiser_topic, "Test!")

client.loop_start()



# Test Message for Rose Generation
#client.publish(user_topic, "P,Rose,2,1")
time.sleep(20)
while(1):
    USBRead()
    if len(commandList) > ardWork and pause != True:

        if ardWork == 0 and len(commandList) > 1:
            print("Sending 1 of 2 points")
            commandList[0].pubUSB("I")
            ardWork += 1
        elif ardWork == 1 and len(commandList) > 1:
            print("Sending second point")
            commandList[1].pubUSB("T")
            ardWork += 1





    

    