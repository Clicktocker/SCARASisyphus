import math

# Eoin Brennan Inverse Kinematics Calculator for Sisyphus System
print("Running Inverse Kinematics Calucator")

# System Parameters

Length1 = 7.5
Length2 = 7.5

# Forward Kinematics Calculation for testing

Angle1 = 3/2 * math.pi
Angle2 = math.pi/2

Effector = [0,0]
Effector[0] = Length1 * math.sin(Angle1) + Length2 *(math.sin(Angle1 + Angle2))
Effector[1] = Length1 * math.cos(Angle1) + Length2 *(math.cos(Angle1 + Angle2))


print("Caluclated EndPos")
print("%.2f" % Effector[0])
print("%.2f" % Effector[1])

# Convert to Rho and Phi

Magnitude = (Effector[0] ** 2 + Effector[1] ** 2) ** (1/2)

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

    print("Debug Angle", Angle)

    if Effector[1] > 0 and Angle < 0:
        Angle = Angle + (2*math.pi)

    elif Effector[1] < 0:
        Angle = math.pi + Angle
        

print("\nConverting to magnitude and phase")
print("Magnitude is: ", "%.2f" % Magnitude)
print("Angle is: ", "%.2f" % Angle)
print("Angle in degrees", Angle / math.pi * 180)