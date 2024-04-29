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


buffSize = 5    # Size of buffer for number of arms drawn

startColour = [29,36,66]  # "#3BE490" in RGB Decimal Values 
endColour =  [136,64,66]  # "#05743C" in RGB Decimal Values
drawIndex = 0
dataIndex = 0
showFuture = False

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
    def __init__(self, endx, endy, midx, midy, index):
        self.endx = endx; self.endy = endy
        self.midx = midx; self.midy = midy
        try:
            self.pastx = drawPath[index -1].endx
            self.pasty = drawPath[index -1].endy
        except:
            self.pastx = self.endx; self.pasty = self.endy
        self.oval = []

    def drawLine(self, colour):
        self.line = canvas.create_line(self.endx, self.endy, self.pastx, self.pasty, width=lineThickness-1, fill= colour)
        
        if pointHide == False:
            self.oval = DrawPoint(self.endx, self.endy,0.8)
        else: self.oval = []

    def deleteLine(self):
        try: canvas.delete(self.line)
        except: pass


    def __del__(self):
        try: canvas.delete(self.oval)
        except: pass

        try: canvas.delete(self.line)
        except: pass

    def hidePoint(self):
        try: canvas.delete(self.oval); self.oval = []
        except: pass

    def drawPoint(self):
        if self.oval == []:
            self.oval = DrawPoint(self.endx, self.endy,0.8)
 
        

## MQTT Connection

# Publishers
mqtt_broker = "localhost"
picomms_topic = "PathPublisher"
visualiser_topic = "RTVisualiser"


## Callback Functions

def RTVisualiser_Callback(client,userdata,message):
    global drawIndex
    try:
        drawPath[drawIndex].deleteLine()
        drawPath[drawIndex].drawLine('green')
        UpdateArms(drawPath[drawIndex].endx, drawPath[drawIndex].endy, drawPath[drawIndex].midx, drawPath[drawIndex].midy)
        drawIndex += 1
    except: pass


def PathPublisher_Callback(client,userdata,message):
    global dataIndex
    msg = str(message.payload.decode("utf-8"))
    msgSplit = msg.split(",")

    match msgSplit[0]:
        case "S": #Starting line
            print("Starting points Points, current size of path is: " , len(drawPath))

        case "F": #Finished line
            print("Finish Points, current size of path is: " , len(drawPath))
        case "P": # Point Data
            # Add points to the stored list
            endx, endy = CartToScreen(float(msgSplit[1]), float(msgSplit[2]))
            midx, midy = CartToScreen(float(msgSplit[3]), float(msgSplit[4]))
            struc = lineSegment(endx, endy, midx, midy, dataIndex)
            drawPath.append(struc)
            dataIndex += 1

        case "Delete":
            ResetDisplay()
            drawPath.clear()
            dataIndex = 0
            

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

    for i in range(drawIndex):
        drawPath.pop(0)
    arms.clear()
    drawIndex = 0

def HidePoints():   # Toggles the visibility of the points on the display
    global pointHide
    pointHide = not pointHide
    if showFuture == True: target = len(drawPath)
    else: target = (drawIndex)

    if pointHide == True:
        for i in range(target):
            drawPath[i].hidePoint()
    else:
        for i in range(target):
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

def ToggleFuture():
    global showFuture, drawIndex
    print("Current Draw Index: ", drawIndex)
    print("Current length of drawpath: ", len(drawPath))
    showFuture = not showFuture
    if showFuture == True:
        for i in range(len(drawPath) - drawIndex):
            drawPath[i + drawIndex].drawLine('red')
    else:
        for i in range(len(drawPath) - drawIndex):
            drawPath[i + drawIndex].deleteLine()
            drawPath[i + drawIndex].hidePoint()

        
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
btnToggleFuture = button('Toggle Future', ToggleFuture, 6/100, 8/100, 10, 20)


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

