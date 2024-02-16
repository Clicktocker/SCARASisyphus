import tkinter
import math
import time
import sys
import numpy as np

# Eoin Brennan Inverse Kinematics Calculator for Sisyphus System
print("Running Inverse Kinematics Calucator")

# Generating parametric paths to follow
def func_x(t):
    return 11 * math.sin(t)

def func_y(t):
    return 10 * math.cos(0.821 * t)


# Breaking parametric function into equally distant pieces

Increment = 0.05     # The resolution of increments in t
Radius = 0.5        # The target distance between points
LineLength = 2      # The length of the parametric line, multiplied by 2*pi

buffsize = 5        # Size of buffer for displaying joint forms
elements = [0] * ( (buffsize*2) + 2 ) # Elements for display which are redrawn each frame
buffsel = 0         # Starting point in buffer, leave as zero

# Initial states setup
x_rec = np.array([func_x(0)])
y_rec = np.array([func_y(0)])
t_current = t_answer = 0

while t_answer < LineLength * 2 * math.pi:
    CoordCompare = np.array([func_x(t_answer), func_y(t_answer)])
    CoordPrev = np.concatenate( (CoordCompare, np.array([t_answer])) )
    t_current = t_answer

    done = False
    while done == False:
        t_current = t_current + Increment
        CoordCurrent = np.array([func_x(t_current), func_y(t_current), t_current])

        if t_current > 2*LineLength * math.pi:
            t_answer = t_current
            done = True

        elif ( (CoordCompare[0] - CoordCurrent[0])**2 + (CoordCompare[1] - CoordCurrent[1])**2 )**0.5 > Radius:
            # Case for new point being beyond the target length
            Overshoot = - Radius + ((CoordCompare[0] - CoordCurrent[0])**2 + (CoordCompare[1] - CoordCurrent[1])**2)**0.5
            Undershoot = Radius -  ((CoordCompare[0] - CoordPrev[0]   )**2 + (CoordCompare[1] - CoordPrev[1])**2   )**0.5

            Ratio = Undershoot / (Overshoot + Undershoot)

            t_answer = (t_current - Increment) + (Ratio * Increment)
            x_rec = np.concatenate(((x_rec) , np.array([func_x(t_answer)])))
            y_rec = np.concatenate(((y_rec) , np.array([func_y(t_answer)])))

            done = True

        else:
            CoordPrev = CoordCurrent

# System Parameters

Length1 = 7.5
Length2 = 7.5

Effector = [0,0]


i = 0
for x in x_rec:
    # Target End Effector Position in Cartesian Coordinates

    
    Effector[0] = x_rec[i]
    Effector[1] = y_rec[i]

    print("\nTarget End Pos for position ", i, " is: " , Effector)

    # Convert cartesian to polar

    Magnitude = (Effector[0] ** 2 + Effector[1] ** 2) ** (1/2)
    #print("Magnitude is: ", "%.2f" % Magnitude)

    if Effector[0] == 0:

        if Effector[1] > 0:
            Angle = 0
        else:
            Angle = math.pi

    elif Effector[1] == 0:

        if Effector[0] > 0:
            Angle = math.pi/2
        else:
            Angle = (3/2) * math.pi

    else:
        Angle = math.atan(Effector[1] / Effector[0])

        if Effector[1] > 0 and Angle < 0:
            Angle = Angle + (2*math.pi)

        elif Effector[1] < 0:
            Angle = math.pi + Angle


    # Check for being out of coordinate space
    if Magnitude > 15:
        print("Error with coordinates outside workspace")
        sys.exit


    # Inverse Kinematics Calculation
    AngleComp = math.acos( (0.5 * Magnitude) / Length1)
    Joint1 = Angle - AngleComp
    Joint2 = 2 * AngleComp

    if i == 0:
        Calcs = np.array([[Joint1, Joint2, Effector[0], Effector[1]]])

    else:
        test = np.array([[Joint1, Joint2, Effector[0], Effector[1]]])
        Calcs = np.concatenate( ( Calcs, test), axis = 0)
        

    

    #print("\nInverse Kinematics Joint Values")
    print("Joint1 is: ", "%.2f" % Joint1)
    print("Joint2 is: ", "%.2f" % Joint2)
    print("Current size: ", np.shape(Calcs))
    #print("\nInDegrees")
    #print("Joint1 is: ", "%.2f" % (Joint1 / math.pi * 180))
    #print("Joint2 is: ", "%.2f" % (Joint2 / math.pi * 180))

    i = i+1


# Graphics drawing of movement
    
canvas_size = 1000
canvas = tkinter.Canvas(bg="#08141a", width=canvas_size, height=canvas_size)
canvas.pack()

def calcCoord(xin, yin):
    xout = ( (4 * canvas_size/10) /  (15 / xin) ) + canvas_size/2
    yout = ( (4 * canvas_size/10) /  (15 / yin) ) + canvas_size/2

    return xout, yout


canvas.create_oval(canvas_size / 10, canvas_size / 10, 9* canvas_size/10, 9* canvas_size/10, outline='white')

# 
def draw(elements):
    for element in elements:
        canvas.delete(element)
    
    global buffsel
     
    if buffsel == buffsize:
        buffsel = 0


    buffer[buffsel, 0] = Length1*math.sin(Calcs[i,0])
    buffer[buffsel, 1] = Length1*math.cos(Calcs[i,0])
    buffer[buffsel, 2] = Length1 * math.sin(Calcs[i,0]) + Length2 *(math.sin(Calcs[i,0] + Calcs[i,1]))
    buffer[buffsel, 3] = Length1 * math.cos(Calcs[i,0]) + Length2 *(math.cos(Calcs[i,0] + Calcs[i,1]))

    for x in range(5):
        if buffsel == -1:
            buffsel = buffsize

        # Arm1
        x1, y1 = calcCoord(buffer[buffsel, 0], buffer[buffsel, 1])
        elements[(x*2)] = canvas.create_line(canvas_size/2, canvas_size/2, x1, y1, width = 4, fill = "#2a638c")

        # Arm2
        x2, y2 = calcCoord(buffer[buffsel, 2], buffer[buffsel, 3])
        elements[(x*2) + 1] = canvas.create_line(x1, y1, x2, y2, width = 4, fill =  "#2a638c")
        

        buffsel = buffsel - 1

    # Small circle in center
    elements[(buffsize*2) + 1] = canvas.create_oval(canvas_size / 2 - 10, canvas_size / 2 - 10,
                                    canvas_size / 2 + 10, canvas_size / 2 + 10, fill="#405b80",
                                    width=0)

    
    return elements


# Drawing Loop
initial = np.array([[7.5 * math.sin(Calcs[0,0]), 7.5 * math.cos(Calcs[0,0]), Calcs[0,2], Calcs[0,3]]])
buffer = initial
for i in range(buffsize):
    buffer = np.concatenate( (buffer, initial), axis = 0)

i = 0
while True:
    elements = draw(elements)



    
    canvas.update()
    print("Updated display")
    time.sleep(0.05)
    i = i+1