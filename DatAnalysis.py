"""
MECH 305/6 DATA ANALYSIS
----------------------------------------
WRITTEN BY: THOMAS BEMENT
DATE: 3/07/2021

CAPSTONE EXPERIMENT
"""
import csv
import os
import glob
import matplotlib.pyplot as plt
import numpy as np
import math
import time
from scipy.signal import savgol_filter
from scipy.signal import decimate

"""
DEFINE CONSTANTS
"""

"""
DEFINE GLOBAL FUNCTIONS
"""
# Get flow rate from given parameters, only applies for our orfice setup
def flowRate(CD, Rho, orfD, pipeD, dP):
    return ((CD/(math.sqrt(1-((orfD/pipeD)**4))))*((math.pi*(orfD**2))/4)*(math.sqrt(2*dP*Rho)))/Rho

"""
READ ANALYSIS
"""
# Headers: X_Value, Intake Pressure, Cylinder Pressure, Encoder, TDC, Spark
# datStruct  0    ,        1       ,         2        ,   3    ,  4 ,   5

def readDat(pathlist):
    column_number = 8
    ans = {}
    for path in pathlist:
        for filename in glob.glob(os.path.join(path, '*.csv')):
            key = filename.split('\\')[-1].replace('.csv', '')
            ans[key] = ([],[],[],[],[],[],[],[])
            with open(os.path.join(os.getcwd(), filename), 'r') as f: # open in readonly mode
                for j, row in enumerate(csv.reader(f, delimiter=',')):
                    if j != 0:
                        if len(row) == column_number:
                            for i in range(column_number):
                                ans[key][i].append(float(row[i]))
    return ans

"""
PLOT FUNCTIONS
"""
Headers = ['Time','Pressure','0.3um','0.5um','1um','2.5um','5um','10um']

def get_cmap(n, name='plasma'):
    return plt.cm.get_cmap(name, n)

def timeSerries(dat, key):
    cmap = get_cmap(len(dat[key]))
    fig, axs = plt.subplots(2)
    fig.suptitle('Time serries plot for: %s' %key)
    fig.tight_layout(pad=3.0)
    # Pressure vs. time
    axs[0].plot(dat[key][0], dat[key][1], color=cmap(1))
    axs[0].set_title('Pressure vs. Time:')
    axs[0].set(xlabel='Time (s)', ylabel='Pressure Difference (Pa)')
    legendlis = []
    # Particle count vs. time
    for i in range(2,len(dat[key])):
        axs[1].plot(dat[key][0], dat[key][i], color=cmap(i))
        legendlis.append(Headers[i])
    axs[1].set_title('Particle Count vs. Time:')
    axs[1].set(xlabel='Time (s)', ylabel='# Particles/0.1 L')
    axs[1].legend(legendlis, bbox_to_anchor=(1.04, 0.5), loc="center left")
    # Save Plots
    plt.savefig('PythonFigures/TS/%s_TS.png' %key, format='png', bbox_inches='tight', orientation='landscape')
    plt.show()
    plt.close()
    return 

def particleOverlay(dat, key1, key2):
    cmap = get_cmap(12)
    legendlis = []
    count = 0
    plt.title('Particle count data for %s and %s' %(key1, key2))
    plt.xlabel('Time (s)')
    plt.ylabel('# Particles/0.1 L')
    for i in range(2,len(dat[key1])):
        plt.plot(dat[key1][0], dat[key1][i], color=cmap(i), alpha=0.6)
        legendlis.append('%s: %s' %(key1, Headers[i]))
        count = i+1
    for i in range(2,len(dat[key2])):
        plt.plot(dat[key2][0], dat[key2][i], color=cmap(count), alpha=0.6)
        legendlis.append('%s: %s' %(key2, Headers[i]))
        count += 1
    plt.legend(legendlis, bbox_to_anchor=(1.04, 0.5), loc="center left")
    # Save Plots
    plt.savefig('PythonFigures/TS/%s_%s_OVERLAY.png' %(key1, key2), format='png', bbox_inches='tight', orientation='landscape')
    plt.show()
    plt.close()
    return

"""
RUN ANALYSIS
"""
allDat = readDat(['.\Data\CSV'])
timeSerries(allDat, 'SiftedWhiteFlour')
particleOverlay(allDat, 'BakingSodaBlended', 'SiftedWhiteFlour')