"""
MECH 305/6 DATA ANALYSIS
----------------------------------------
WRITTEN BY: THOMAS BEMENT
DATE: 3/07/2021

CAPSTONE EXPERIMENT
"""

"""
IMPORTS
"""
import serial
from serial import Serial
from drawnow import *
import sys
import numpy as np
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import tkinter as tk

"""
PLOTTING AND DATA COLLECTION
"""
Calibration=0.9897807654 # You need to find the exact calibration number
filName = 'SiftedWhiteFlour'
style.use('fivethirtyeight')

# Define figure and title
fig = plt.figure()
fig.suptitle('Time series plot:')
# Define subplots
ax1 = fig.add_subplot(2,1,1)
ax2 = fig.add_subplot(2,1,2)
#ax3 = fig.add_subplot(3,1,3)

#     [[time],[pressure], [0.3um], [0.5um], [1um], [2.5um], [5um], [10um]]
#     [  0   ,    1     ,    2   ,    3   ,   4  ,  5     ,   6  ,    7  ]

dat = [[],[],[],[],[],[],[],[],[]]
ArduinoData=serial.Serial('COM5', baudrate=9600)

def moistCal(val):
    return ((1/(880 - 1023))*(val-1023))

def animate(i):
    ArduinoString = ArduinoData.readline().decode('ASCII').replace('\n', '')
    FloatList = [float(elem) for elem in ArduinoString.split(' ') if elem != '']
    if len(FloatList)==8:
        dat[0].append(0.001*FloatList[0])
        dat[1].append(FloatList[1])
        dat[2].append(FloatList[2])
        dat[3].append(FloatList[3])
        dat[4].append(FloatList[4])
        dat[5].append(FloatList[5])
        dat[6].append(FloatList[6])
        dat[7].append(FloatList[7])

    
    ax1.clear()
    ax2.clear()
    ax1.plot(dat[0], dat[1])
    ax2.plot(dat[0], dat[2])

wet = 880
dry = 1023
ani = animation.FuncAnimation(fig, animate, interval=1)
plt.show()
ArduinoData.close()
plt.close()
f = open("%s.csv" %filName,"w+")
f.write('Time,Pressure,0.3um,0.5um,1um,2.5um,5um,10um\n')
for i in range(len(dat[0])-1):
    f.write('%f,%f,%f,%f,%f,%f,%f,%f\n' %(dat[0][i],dat[1][i],dat[2][i],dat[3][i],dat[4][i],dat[5][i],dat[6][i],dat[7][i]))
f.close()
