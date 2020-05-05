import board
import busio
import pulseio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo
import time

i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)
pca.frequency = 50

joint_1 = servo.ContinuousServo(pca.channels[0], min_pulse= 1350, max_pulse= 1765)
joint_2 = servo.ContinuousServo(pca.channels[1], min_pulse= 1350, max_pulse= 1770)

def get_feedback(pin):
    global pulses
    unitsFC = 360
    dutyScale = 1000
    tc = 0
    dcMin = 29
    dcMax = 971
    q2min = unitsFC/4
    q3max = q2min * 3
    turns = 0
    pulses = pulseio.PulseIn(pin)
    thetaP = 0


    while True:
        while len(pulses) < 2:
            if pulses.paused == True:
                pulses.resume()
            continue
        pulses.pause()
        pulse_list = [pulses[0], pulses[1]]

        if sum(pulse_list) > 1000 and sum(pulse_list) < 1200:
            high = pulses[0]
            low = pulses[1]
            tc = sum(pulse_list)
            dc = (dutyScale * high) / tc
            theta = (unitsFC - 1) - ((dc - dcMin) * unitsFC) / (dcMax - dcMin + 1)
            if theta < 0:
                theta = 0
            elif (theta > (unitsFC - 1)):
                theta = unitsFC - 1
            if (theta < q2min) and (thetaP > q3max):
                turns = turns + 1
            elif (thetaP < q2min) and (theta > q3max):
                turns = turns - 1
            if (turns >= 0):
                angle = (turns * unitsFC) + theta;
            elif (turns <  0):
                angle = ((turns + 1) * unitsFC) - (unitsFC - theta)
            yield angle, turns, theta
            pulses.clear()
            thetaP = theta
            continue
        else:
            pulses.clear()
            continue

def set_theta360(feedback_pin, joint, throttle, new_theta):

    g = get_feedback(feedback_pin)

    while True:
        feedback = list(next(g))
        if abs(new_theta - feedback[2]) < 2:
            break
        else:
            while abs(new_theta - feedback[2]) > .5:
                feedback = list(next(g))
                joint.throttle = throttle
                print(feedback)
            joint.throttle = 0
            print(feedback[2])
            pulses.deinit()
            break

while True:
    set_theta360(board.D7, joint_1, .15, 0)
    time.sleep(1)
    set_theta360(board.D7, joint_1, .15, 186)
    time.sleep(1)
    set_theta360(board.D7, joint_1, -.15, 8)
    time.sleep(1)
    set_theta360(board.D7, joint_1, -.15, 186)
    time.sleep(1)