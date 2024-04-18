import math, time, os
from tkinter import *
import paho.mqtt.client as mqtt

## Eoin Brennan Kinematics Visualiser for Sisyphus System

# Graphical Interface that displays the current behaviour of the physical system.

## User Variables

armLength = [57.5, 57.5]
drawArea = 115

## System Variables

lineThickness = 4

arms = []       # List for arms to be stored in
drawPath = []   # List for the drawn path to be stored in
colArray = []
dataPoints = [] # List for storing the coordinate data to be drawn

buffSize = 5    # Size of buffer for number of arms drawn

startColour = [136,64,66]   # "#05743C" in RGB Decimal Values
endColour = [29,36,66]   # "#3BE490" in RGB Decimal Values
drawIndex = 0

drawTime = 0.001

pointHide = False
armHide = False

## tkinter setup

visualiserArea = 800
border = 25

## Classes

class armStructure:
    def __init__(self, endx, endy, midx, midy, colourIndex):
        self.endx = endx; self.endy = endy
        self.midx = midx; self.midy = midy
        self.col = colourIndex

        self.armJoint = []; self.armBase = []; self.centre = []
        if armHide == False:
            self.draw()
            
        
    def draw(self):
        if self.armJoint == []:
            self.armJoint = canvas.create_line(self.endx, self.endy, self.midx, self.midy, width =lineThickness-1, fill = colArray[self.col])
        if self.armBase == []:
            self.armBase = canvas.create_line(self.midx, self.midy, visualiserArea/2, visualiserArea/2, width =lineThickness-1, fill = colArray[self.col])
        if self.centre == []:
            self.centre = DrawPoint(self.midx, self.midy, 0.5)

    def hideArms(self):
        if self.armJoint != []:
            canvas.delete(self.armJoint)
        if self.armBase != []:
            canvas.delete(self.armBase)
        if self.centre != []:
            canvas.delete(self.centre)

    def recolour(self, colourIndex):
        if armHide == False:
            canvas.itemconfigure(self.armJoint, fill = colArray[colourIndex])
            canvas.itemconfigure(self.armBase, fill = colArray[colourIndex])
            canvas.itemconfigure(self.centre, fill = colArray[colourIndex])

    def __del__(self):
        if self.centre != 0:
            canvas.delete(self.centre)
        if self.armBase != 0:
            canvas.delete(self.armBase)
        if self.armJoint != 0:
            canvas.delete(self.armJoint)


class lineSegment:
    def __init__(self, x, y, index):
        self.x = x; self.y = y
        try:
            pastx = drawPath[index-1].x
            pasty = drawPath[index -1].y
        except:
            pastx = self.x; pasty = self.y

        self.line = canvas.create_line(self.x, self.y, pastx, pasty, width=lineThickness-1, fill='green')
        
        if pointHide == False:
            self.oval = DrawPoint(self.x, self.y,0.8)
        else: self.oval = []

    def __del__(self):
        if self.oval != 0:
            canvas.delete(self.oval)
        if self.line != 0:
            canvas.delete(self.line)
    def hidePoint(self):
        if self.oval != 0:
            canvas.delete(self.oval)
            self.oval = []
    def drawPoint(self):
        if self.oval == []:
            self.oval = DrawPoint(self.x, self.y,0.8)

class PointDataStore:
    def __init__(self, endx, endy, midx, midy):
        self.endx = endx; self.endy = endy
        self.midx = midx; self.midy = midy
 
        

## MQTT Connection

# Publishers
mqtt_broker = "localhost"
picomms_topic = "PathPublisher"
visualiser_topic = "RTVisualiser"


## Callback Functions

def RTVisualiser_Callback(client,userdata,message):
    global drawIndex
    segment = lineSegment(dataPoints[drawIndex].endx, dataPoints[drawIndex].endy, drawIndex)
    drawPath.append(segment)
    UpdateArms(dataPoints[drawIndex].endx, dataPoints[drawIndex].endy, dataPoints[drawIndex].midx, dataPoints[drawIndex].midy)
    drawIndex += 1
    dataPoints.pop(0)


def PathPublisher_Callback(client,userdata,message):
    global drawIndex
    msg = str(message.payload.decode("utf-8"))
    msgSplit = msg.split(",")

    match msgSplit[0]:
        case "S": # Start of a sequence
            pass        

        case "F": # End of a sequence
            pass    

        case "P": # Point Data
            # Add points to the stored list
            endx, endy = CartToScreen(float(msgSplit[1]), float(msgSplit[2]))
            midx, midy = CartToScreen(float(msgSplit[3]), float(msgSplit[4]))
            struc = PointDataStore(endx, endy, midx, midy)
            dataPoints.append(struc)
            print("Appended Data")

        case "Delete":
            ResetDisplay()
            dataPoints.clear()
            

## Functions

# Function to convert the cartesian coordinates to screen relative dimensions
def CartToScreen(x,y):
    global drawArea
    xout = ( ( (visualiserArea/2 - 2*border) ) * (x/drawArea) ) + visualiserArea/2
    yout = ( ( (visualiserArea/2 - 2*border) ) * (y/drawArea) ) + visualiserArea/2

    return xout, yout

# Function to convert rgb values into hex format for arm colour
def RGBToHex(r,g,b):
    r = round(r); g = round(g); b = round(b)
    return "#{:02x}{:02x}{:02x}".format(int(r),int(g),int(b))
  

    
def UpdateArms(endx, endy, midx, midy):
    global arms, colArray
    
    try:
        if len(arms) != buffSize:
            arms.clear(); colArray.clear()  # Clear the arms and colour array
            colInc = [0,1,2]; colRGB = [0,1,2]  # Prepare the colour incrementing arrays
            for i in colInc: colInc[i] = (endColour[i] - startColour[i]) / (buffSize-1) # Populate colourInc with the RGB increments

            for i in range(buffSize):
                for j in range(len(colInc)): colRGB[j] = startColour[j] + (i * colInc[j])
                colHex = RGBToHex(colRGB[0], colRGB[1], colRGB[2])
                colArray.append(colHex)

                struc = armStructure(endx, endy, midx, midy, i)
                arms.append(struc)

        else:
            for i in range(len(arms) - 2): # Shift the arms through the buffer and update their colours
                arms[i+1].recolour(i)

            arms.pop(0)
            struc = armStructure(endx, endy, midx, midy, buffSize-1)
            arms.append(struc)

    except: arms.clear()



def DrawPoint(xscreen,yscreen, sizeMultiplier):
    r = visualiserArea/500 * sizeMultiplier
    return canvas.create_oval( xscreen- r,  yscreen -r, xscreen + r, yscreen + r, outline = 'white', fill='white')

## Interface Functions

class button:
    def __init__(self, text, callback, relx, rely, widthScale, heightScale):
        # Convert Relative positions to exact control area
        sizex = visualiserArea / widthScale
        sizey = visualiserArea / heightScale
        x , y = RelToPixel(relx, rely)
        self.x = x - sizex/2 ; self.y = y - sizey/2

        self.widget = Button(root, text = text, command = callback)
        self.widget.place(x=self.x, y=self.y, width = sizex, height= sizey)

    def callback(self, val):    # Update the value of the slider and its text display
        self.title.config(text='You have selected: ' + val)
        self.value = float(val)
        # Set value as desired
    

    
# Convert relative x and y coordinates to their relative values in the control area
def RelToPixel(x, y):
    conx = (x * visualiserArea)
    cony = (y * visualiserArea)
    return conx, cony

def ResetDisplay(): # Reset the display by deleting the path and arms
    global drawPath, arms, drawIndex
    print("Reset Display")

    drawPath.clear()
    arms.clear()
    drawIndex = 0

def HidePoints():   # Toggles the visibility of the points on the display
    global pointHide
    pointHide = not pointHide
    if pointHide == True:
        for i in range(len(drawPath)):
            drawPath[i].hidePoint()
    else:
        for i in range(len(drawPath)):
            drawPath[i].drawPoint()

def HideArms():
    global armHide
    armHide = not armHide
    if armHide == True:
        for i in range(len(arms)):
            arms[i].hideArms()
    else:
        for i in range(len(arms)):
            arms[i].draw()
        

## Main Start

# Create base UI
root = Tk()
root.title("Real Time Sisyphus Visualiser")

canvas = Canvas(root, bg="#08141a", width = visualiserArea, height = visualiserArea)
canvas.pack()

# Create draw area and centre point
canvas.create_oval(border, border, visualiserArea-border, visualiserArea-border, width=lineThickness, outline='white')
DrawPoint( visualiserArea/2, visualiserArea/2, 3)

# Create User Buttons
btnReset = button('Reset Display', ResetDisplay, 9/10, 3/100, 5, 20)
btnHidePoints = button('HidePoints', HidePoints, 6/100, 3/100, 10, 20)
btnHideArms = button('HideArms', HideArms, 16/100, 3/100, 10, 20)

# Connecting to MQTT
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = PathPublisher_Callback # Setting callback function

client_RTVis = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client_RTVis.on_message = RTVisualiser_Callback # Setting callback function

client.connect(mqtt_broker) # Connect to the broker
client_RTVis.connect(mqtt_broker) # Connect to the broker

client.subscribe(picomms_topic)
client_RTVis.subscribe(visualiser_topic)

client.loop_start()
client_RTVis.loop_start()


root.mainloop()

