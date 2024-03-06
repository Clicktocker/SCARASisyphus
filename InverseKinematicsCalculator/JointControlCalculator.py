import tkinter
import math
import time
import sys
import numpy as np

# Eoin Brennan Joint Control Kinematics Calculator for Sisyphus System
# Defining system behaviour with descritions of joint arms
print("Running Inverse Kinematics Calucator")

# Generating parametric paths to follow
def func_j1(t):
    #return 5 * math.sin(1 * t)
    return 0.5 * t
    return 11 * math.sin(0.94432 * t)

def func_j2(t):
    #return 5 * math.cos(2 * t)
    return math.pi * t
    return 10 * math.cos(0.8776 * t)


# Breaking parametric function into equally distant pieces

increment = 0.05     # The resolution of increments in time (t)
simTime = 150      # Time length for system to draw

startColour = "#05743C" # Colours for the arm gradients
endColour = "#3BE490"

buffsize = 5       # Size of buffer for displaying joint forms
elements = [0] * ( (buffsize*2) + 2 ) # Elements for display which are redrawn each frame
buffsel = 0         # Starting point in buffer, leave as zero
delay = 0.01        # Delay for how long each frame should take in seconds


# Convert R,G,B into a hex string 
def rgb2hex(r,g,b):
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

# Initial states setup
joint1Vals = np.array([func_j1(0)])
joint2Vals = np.array([func_j2(0)])
drawTime = increment

while drawTime < simTime:
    joint1Vals = np.concatenate(((joint1Vals) , np.array([func_j1(drawTime)])))
    joint2Vals = np.concatenate(((joint2Vals) , np.array([func_j2(drawTime)])))

    drawTime = drawTime + increment


print("TEST SHOWCASE")
print(joint1Vals)
# System Parameters
Length1 = 7.5
Length2 = 7.5

Effector = [0,0]

i = 0


# Graphics drawing of movement
    
canvas_size = 800
canvas = tkinter.Canvas(bg="#08141a", width=canvas_size, height=canvas_size)
canvas.pack()

def calcCoord(xin, yin):
    xout = ( (4 * canvas_size/10) *  (xin / 15) ) + canvas_size/2
    yout = ( (4 * canvas_size/10) *  (yin / 15) ) + canvas_size/2

    return xout, yout


canvas.create_oval(canvas_size / 10, canvas_size / 10, 9* canvas_size/10, 9* canvas_size/10, outline='white')

# Colour calculation for arm gradient
    
colourCals = ["0x"+startColour[1:3], "0x"+startColour[3:5], "0x"+startColour[5:7], "0x"+endColour[1:3], "0x"+endColour[3:5], "0x"+endColour[5:7]]
print(colourCals)
i = 0
for x in colourCals:
    colourCals[i] = int(x, 0)
    i = i+1
colourInc = [ (colourCals[3] - colourCals[0]) / (buffsize - 1), (colourCals[4] - colourCals[1]) / (buffsize - 1), (colourCals[5] - colourCals[2]) / (buffsize - 1) ]

colourSel = [startColour]
i = 1
while i < (buffsize):
    colourStore = [int(colourCals[0] + (colourInc[0] * i) ), int(colourCals[1] + (colourInc[1] * i) ), int(colourCals[2] + (colourInc[2] * i))]
    print(colourStore)
    colourSel.append( rgb2hex(colourStore[0], colourStore[1], colourStore[2]) )
    i = i+1
print(colourSel)



# Drawing Function for animated components
def draw(elements):
    for element in elements:
        canvas.delete(element)
    
    global buffsel
     
    if buffsel == buffsize:
        buffsel = 0


    buffer[buffsel, 0] = Length1 * math.sin(joint1Vals[i])
    buffer[buffsel, 1] = Length1 * math.cos(joint1Vals[i])
    buffer[buffsel, 2] = Length1 * math.sin(joint1Vals[i]) + Length2 *(math.sin(joint1Vals[i] + joint2Vals[i]))
    buffer[buffsel, 3] = Length1 * math.cos(joint1Vals[i]) + Length2 *(math.cos(joint1Vals[i] + joint2Vals[i]))

    for x in range(buffsize):
        if buffsel == -1:
            buffsel = buffsize

        # Arm1
        x1, y1 = calcCoord(buffer[buffsel, 0], buffer[buffsel, 1])
        elements[(x*2)] = canvas.create_line(canvas_size/2, canvas_size/2, x1, y1, width = 4, fill = colourSel[x])

        # Arm2
        x2, y2 = calcCoord(buffer[buffsel, 2], buffer[buffsel, 3])
        elements[(x*2) + 1] = canvas.create_line(x1, y1, x2, y2, width = 4, fill = colourSel[x])
        

        buffsel = buffsel - 1

    # Small circle in center
    elements[(buffsize*2) + 1] = canvas.create_oval(canvas_size / 2 - 10, canvas_size / 2 - 10,
                                    canvas_size / 2 + 10, canvas_size / 2 + 10, fill="#405b80",
                                    width=0)

    
    return elements


# Drawing Loop
initial = np.array([[Length1 * math.sin(func_j1(0)),  
            Length1 * math.cos(func_j1(0)),  
            Length1 * math.sin(func_j1(0)) + Length2 *(math.sin(func_j1(0) + func_j2(0))),
            Length1 * math.cos(func_j1(0)) + Length2 *(math.cos(func_j1(0) + func_j2(0)))]])

buffer = initial
for i in range(buffsize):
    buffer = np.concatenate( (buffer, initial), axis = 0)


lineUpdate = np.array([ [0,0] ,
                [Length1 * math.sin(func_j1(0)) + Length2 *(math.sin(func_j1(0) + func_j2(0))),
                Length1 * math.cos(func_j1(0)) + Length2 *(math.cos(func_j1(0) + func_j2(0))) ] ])
lineUpdate[1,0], lineUpdate[1,1] = calcCoord(lineUpdate[1, 0], lineUpdate[1,1])
i = 0
print(lineUpdate)

while True:
    timeloop = time.time()
    elements = draw(elements)
    print(lineUpdate[1, 1])
    # Draw new section of line
    lineUpdate[(i%2), 0] = Length1 * math.sin(joint1Vals[i]) + Length2 *(math.sin(joint1Vals[i] + joint2Vals[i]))
    lineUpdate[(i%2), 1] = Length1 * math.cos(joint1Vals[i]) + Length2 *(math.cos(joint1Vals[i] + joint2Vals[i]))
    lineUpdate[i%2,0], lineUpdate[i%2,1] = calcCoord(lineUpdate[i%2, 0], lineUpdate[i%2,1])

    canvas.create_line(lineUpdate[0,0], lineUpdate[0,1], lineUpdate[1,0], lineUpdate[1,1], width = 1, fill = "#AA0000")

    canvas.update()
    print("Updated display")
    
    while time.time() < (timeloop + delay):
        time.sleep(0.05)
    #buffsel = buffsel + 1
    i = i+1