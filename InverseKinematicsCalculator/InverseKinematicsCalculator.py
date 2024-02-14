import math
import sys

# Eoin Brennan Inverse Kinematics Calculator for Sisyphus System
print("Running Inverse Kinematics Calucator")

# System Parameters

Length1 = 7.5
Length2 = 7.5

# Target End Effector Position in Cartesian Coordinates

Effector = [0,0]
Effector[0] = 0
Effector[1] = 10

print("Target End Pos is:" , Effector)

# Convert cartesian to polar

Magnitude = (Effector[0] ** 2 + Effector[1] ** 2) ** (1/2)
print("Magnitude is: ", "%.2f" % Magnitude)

if Effector[0] == 0:

    if Effector[1] > 0:
        Angle = 0
    else:
        Angle = math.pi

elif Effector[1] == 0:

    if EEffector[0] > 0:
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


        

print("\nInverse Kinematics Joint Values")
print("Joint1 is: ", "%.2f" % Joint1)
print("Joint2 is: ", "%.2f" % Joint2)
print("\nInDegrees")
print("Joint1 is: ", "%.2f" % (Joint1 / math.pi * 180))
print("Joint2 is: ", "%.2f" % (Joint2 / math.pi * 180))