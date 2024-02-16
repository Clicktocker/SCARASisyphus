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
#Joints = np.array([[0, 0]])

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
        Joints = np.array([[Joint1, Joint2]])

    else:
        test = np.array([[Joint1, Joint2]])
        Joints = np.concatenate( ( Joints, test ), axis = 0)
        

    

    #print("\nInverse Kinematics Joint Values")
    print("Joint1 is: ", "%.2f" % Joint1)
    print("Joint2 is: ", "%.2f" % Joint2)
    print("Current size: ", np.shape(Joints))
    #print("\nInDegrees")
    #print("Joint1 is: ", "%.2f" % (Joint1 / math.pi * 180))
    #print("Joint2 is: ", "%.2f" % (Joint2 / math.pi * 180))

    i = i+1


