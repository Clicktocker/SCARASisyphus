import math, time, os
from tkinter import *
import paho.mqtt.client as mqtt


##~~~~~~~~~~~~~~~~ Eoin Brennan Path Controller for Sisyphus System ~~~~~~~~~~~~~~~~~~~~~##

# Interfce system that allows control of the physical system and example behaviours of paths.
# Visualises paths generated by the pi and allows for controls of point density etc.

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

## User Variables

armLength = [57.5, 57.5]
drawArea = 115

## System Variables

lineThickness = 4

arms = []       # List for arms to be stored in
drawPath = []   # List for the drawn path to be stored in
colArray = []

buffSize = 5    # Size of buffer for number of arms drawn

startColour = [136,64,66]   # "#05743C" in RGB Decimal Values
endColour = [29,36,66]   # "#3BE490" in RGB Decimal Values

drawTime = 0.001

pointHide = False

## tkinter setup

visualiserArea = 800
controlArea = visualiserArea / 4
canvasSize = visualiserArea * 1.25
border = 25

## Classes

class armStructure:
    def __init__(self, endx, endy, midx, midy, colourIndex):
        self.endx = endx; self.endy = endy
        self.midx = midx; self.midy = midy

        self.armJoint = canvas.create_line(endx, endy, midx, midy, width =lineThickness-1, fill = colArray[colourIndex])
        self.armBase = canvas.create_line(midx, midy, visualiserArea/2, visualiserArea/2, width =lineThickness-1, fill = colArray[colourIndex])
        self.centre = DrawPoint(midx, midy, 0.5)
        
    def undraw(self):
        canvas.delete(self.armBase)
        canvas.delete(self.armJoint)
        canvas.delete(self.centre)

    def recolour(self, colourIndex):
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


class lineSegments:
    def __init__(self, xscreen, yscreen, pathIndex):
        self.x = xscreen
        self.y = yscreen
        if pathIndex == 0:
            pastx = xscreen; pasty = yscreen
        else:
            pastx = drawPath[pathIndex-1].x
            pasty = drawPath[pathIndex-1].y

        self.line = canvas.create_line(xscreen, yscreen, pastx, pasty, width=lineThickness-1, fill='green')
        
        if pointHide == False:
            self.oval = DrawPoint(xscreen, yscreen,0.8)
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
 
        
        
## MQTT Connection

# Publishers
mqtt_broker = "localhost"
user_topic = "UserControlDisplay"


## Callback Functions

def UserDisplay_Callback(client,userdata,message):
    global startIndex, drawPath
    msg = str(message.payload.decode("utf-8"))
    #print("Message recieved: ", msg)

    msgSplit = msg.split(",")

    if msgSplit[0] == "U":  # Checking if message is intended for the User Device
        # Handle response based on job type

        match msgSplit[1]:
            case "S":   # Case for a path starting
                print("Starting path read")
                startIndex = len(drawPath)
                if startIndex != 0:
                    startIndex = startIndex - 1
                #Mark the start of the path position in drawPath

            case "P":   # Case for path coords being sent
                #print("Receiving path")
                #AddDrawPoint(msgSplit)
                #canvas.after(1, 
                AddDrawPoint(msgSplit)
                UpdateArms(msgSplit)
                delay = 0.001 + 0.005 * (drawRateSlider.value)
                
                time.sleep( delay)

            case "F":   # Case for path finish being transmitted
                print("Path received, start drawing")

                

## Functions

# Function to convert the cartesian coordinates to screen relative dimensions
def CartToScreen(x,y):
    global drawArea, canvasSize
    xout = ( ( (visualiserArea/2 - 2*border) ) * (x/drawArea) ) + visualiserArea/2
    yout = ( ( (visualiserArea/2 - 2*border) ) * (y/drawArea) ) + visualiserArea/2

    return xout, yout

# Function to convert rgb values into hex format for arm colour
def RGBToHex(r,g,b):
    r = round(r); g = round(g); b = round(b)
    return "#{:02x}{:02x}{:02x}".format(int(r),int(g),int(b))

# Function to add new path data to be drawn
def AddDrawPoint(msg):
    x, y = CartToScreen(float(msg[2]) , float(msg[3]))

    
        
    i = len(drawPath)
    segment = lineSegments(x, y, i)
    drawPath.append(segment)

    

def UpdateArms(msg):
    global arms, colArray
    #print("Arm updating")
    endx, endy = CartToScreen(float(msg[2]) , float(msg[3]))
    midx, midy = CartToScreen(float(msg[4]) , float(msg[5]))
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
    r = canvasSize/500 * sizeMultiplier
    return canvas.create_oval( xscreen- r,  yscreen -r, xscreen + r, yscreen + r, outline = 'white', fill='white')

## Interface Functions

def CreateButton(text, callback, relx, rely, widthScale, heightScale):
    # Convert Relative positions to exact control area
    sizex = controlArea / widthScale ; sizey = visualiserArea / heightScale
    x , y = RelToControl(relx, rely)
    x = x - sizex/2 ; y = y - sizey/2

    btn = Button(root, text = text, command = callback)
    btn.place(x=x, y=y, width = sizex, height= sizey)

    return btn

def CreateEntry(label ,relx , rely , widthScale, heightScale):
    sizex = controlArea / widthScale ; sizey = visualiserArea / heightScale
    x , y = RelToControl(relx, rely)
    x = x - sizex/2 ; y = y - sizey/2

    entry = Entry(root, textvariable = StringVar, justify= CENTER)
    entry.place(x=x, y=y, width = sizex, height= sizey)
    Title = Label(root, text=label)
    Title.place(x = x, y = y - sizey/2, width = sizex, height= sizey/2)

    return entry, Title

class slider:
    def __init__(self, label, relx, rely, widthScale, heightScale, min, max):
        sizex = controlArea / widthScale; sizey = visualiserArea / heightScale
        self.max = max; self.min = min
        x, y = RelToControl(relx, rely)
        self.posx = x - sizex/2
        self.posy = y - sizey/2
        self.value = min

        self.widget = Scale(root, label=label, from_=min, to=max, length=sizex, showvalue=0, tickinterval=2, orient='horizontal', resolution=0.01, command= self.callback)
        self.widget.place(x = self.posx, y = self.posy, width = sizex, height= sizey/2)
        self.Title = Label(root, text="")
        self.Title.place(x = self.posx, y = self.posy + sizey/2, width = sizex, height= sizey/4)
        print("Finished creating slider")

    def callback(self, val):    # Update the value of the slider and its text display
        self.Title.config(text='You have selected: ' + val)
        self.value = float(val)
        # Set value as desired
    

    
# Convert relative x and y coordinates to their relative values in the control area
def RelToControl(x, y):
    conx = (( 0.8 + (x * 0.2) ) * canvasSize)
    cony = (y * visualiserArea)
    return conx, cony
    
def SendRose(): # Send the values to generate a rose curve to the pi
    print("Sending Rose Variables")
    d = entryRosed.get()
    n = entryRosen.get()
    res = str(resolutionSlider.value)

    msg = str("P,Rose," + res + "," + n + "," + d)
    client.publish(user_topic, msg)

def ResetDisplay(): # Reset the display by deleting the path and arms
    global drawPath, arms
    print("Reset Display")

    drawPath.clear()
    arms.clear()

def ResendPattern(): # Request the pi to resend the last path
    client.publish(user_topic, "P,Resend")

def HidePoints():   # Toggles the visibility of the points on the display
    global pointHide
    pointHide = not pointHide
    if pointHide == True:
        for i in range(len(drawPath)):
            drawPath[i].hidePoint()
    else:
        for i in range(len(drawPath)):
            drawPath[i].drawPoint()
        

## Main Start

# Create base UI
root = Tk()
root.title("User Control Display")

canvas = Canvas(root, bg="#08141a", width = canvasSize, height = visualiserArea)
canvas.pack()

# Create draw area and centre point
canvas.create_oval(border, border, visualiserArea-border, visualiserArea-border, width=lineThickness, outline='white')
DrawPoint( visualiserArea/2, visualiserArea/2, 3)

# Create user control area
canvas.create_rectangle(visualiserArea, 0, canvasSize*1.1, visualiserArea*1.1, fill = "#CCE1DF")
canvas.create_line(visualiserArea, 0, visualiserArea, visualiserArea * 1.1, width = lineThickness, fill='#8CB1BA')

# Create User Buttons

btnReset = CreateButton('Reset Display', ResetDisplay, 1/4, 26/100, 2.5, 20)
btnResend = CreateButton('ResendPattern', ResendPattern, 3/4, 26/100, 2.5, 20)
btnHidePoints = CreateButton('HidePoints', HidePoints, 3/4, 32/100, 2.5, 20)

# Create rose n and d entry boxes
entryRosen, titleRosen  = CreateEntry( "n", 1/12, 1/2, 7, 20)
entryRosed, titleRosed = CreateEntry( "d", 3/12, 1/2, 7, 20)
btnRoseSend = CreateButton('Send Rose', SendRose, 3/4, 1/2, 2.5, 20)



# Creating Sliders
drawRateSlider = slider("Draw Speed", 1/2, 1/10, 1.05, 10, 0, 10)
resolutionSlider = slider("Point Resolution (1x to 20x)", 1/2, 2/10, 1.05, 10, 1, 20)


# Connecting to MQTT
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = UserDisplay_Callback # Setting callback function

client.connect(mqtt_broker) # Connect to the broker

print("Subscribing to topic: ", user_topic)
client.subscribe(user_topic)

client.loop_start()


root.mainloop()