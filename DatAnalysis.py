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

def partSize(szStr):
    if (szStr == '0.3um'):
        return 2
    elif (szStr == '0.5um'):
        return 3
    elif (szStr == '1um'):
        return 4
    elif (szStr == '2.5um'):
        return 5
    elif (szStr == '5um'):
        return 6
    elif (szStr == '10um'):
        return 7

def getRange(dat, key, index):
    if (index==7):
        return dat[key][index]
    else:
        diff = []
        for i in range(len(dat[key][index])):
            diff.append(dat[key][index][i] - dat[key][index+1][i])
        return diff
"""
READ DATA
"""
#     [[time],[pressure], [0.3um], [0.5um], [1um], [2.5um], [5um], [10um], [PM1.0 SP], [PM2.5 SP], [PM10.0 SP], [PM1.0 AM], [PM2.5 AM], [PM10.0 AM]]
#     [  0   ,    1     ,    2   ,    3   ,   4  ,  5     ,   6  ,    7  ,      8    ,     9     ,      10    ,     11    ,     12    ,     13     ]

def readDat(pathlist):
    column_number = 14
    ans = {}
    for path in pathlist:
        for filename in glob.glob(os.path.join(path, '*.csv')):
            key = filename.split('\\')[-1].replace('.csv', '')
            ans[key] = ([],[],[],[],[],[],[],[],[],[],[],[],[],[])
            with open(os.path.join(os.getcwd(), filename), 'r') as f: # open in readonly mode
                for j, row in enumerate(csv.reader(f, delimiter=',')):
                    if j != 0:
                        if len(row) == column_number:
                            for i in range(column_number):
                                ans[key][i].append(float(row[i]))
    return ans
"""
DATA ANALYSIS
"""
def stats(dat):
    numpyDat, mean, std = [], [], []
    for i in range(len(dat)):
        numpyDat.append(np.array(dat[i]))
    mean = np.mean(numpyDat)
    std = np.std(numpyDat)  
    return mean, std, numpyDat
"""
PLOT FUNCTIONS
"""
Headers = ['Time','Pressure','0.3um','0.5um','1um','2.5um','5um','10um','PM1.0_SP','PM2.5_SP','PM10.0_SP','PM1.0_AM','PM2.5_AM','PM10.0_AM']

def get_cmap1(n, name='plasma'):
    return plt.cm.get_cmap(name, n)

def get_cmap2(n, name='magma'):
    return plt.cm.get_cmap(name, n)

def timeSerries(dat, key):
    cmap = get_cmap1(len(dat[key]))
    fig, axs = plt.subplots(2)
    fig.suptitle('Time serries plot for: %s' %key)
    fig.tight_layout(pad=3.0)
    # Pressure vs. time
    axs[0].plot(dat[key][0], dat[key][1], color=cmap(1))
    axs[0].set_title('Pressure vs. Time:')
    axs[0].set(xlabel='Time (s)', ylabel='Pressure Difference (Pa)')
    legendlis = []
    # Particle count vs. time
    for i in range(2,7):
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
    cmap1 = get_cmap1(len(dat[key1])+2)
    cmap2 = get_cmap2(len(dat[key2])+2)
    legendlis = []
    count = 0
    plt.title('Particle count data for %s and %s' %(key1, key2))
    plt.xlabel('Time (s)')
    plt.ylabel('# Particles/0.1 L')
    for i in range(2,7):
        plt.plot(dat[key1][0], dat[key1][i], color=cmap1(i), alpha=0.6)
        legendlis.append('%s: %s' %(key1, Headers[i]))
    for i in range(2,7):
        plt.plot(dat[key2][0], dat[key2][i], color=cmap2(i), alpha=0.6)
        legendlis.append('%s: %s' %(key2, Headers[i]))
    plt.legend(legendlis, bbox_to_anchor=(1.04, 0.5), loc="center left")
    # Save Plots
    plt.savefig('PythonFigures/TS/%s_%s_OVERLAY.png' %(key1, key2), format='png', bbox_inches='tight', orientation='landscape')
    plt.show()
    plt.close()
    return

def filterEff(dat, particleSize):
    lowIndex = partSize(particleSize)
    cmap = get_cmap1(len(dat)+2)
    legendlis = []
    count = 0
    plt.title('# Particles/0.1 L vs. Pressure Drop:')
    plt.xlabel('Pressure Drop (Pa)')
    plt.ylabel('# Particles/0.1 L')
    allMean, allSTD = [], [] 
    allMeanPress, allSTDPress = [], [] 
    names = []
    for key in dat:
        diffLis = getRange(dat, key, lowIndex)
        mean, std, _ = stats(diffLis)
        meanPress, stdPress, _ = stats(dat[key][1])
        allMean.append(mean)
        allSTD.append(std)
        allMeanPress.append(meanPress)
        allSTDPress.append(stdPress)
        names.append(key)
    for i in range(len(dat)):
        plt.errorbar(allMeanPress[i], allMean[i], xerr=allSTDPress[i], yerr=allSTD[i], color=cmap(i))
        legendlis.append(names[i])
    plt.legend(legendlis, bbox_to_anchor=(1.04, 0.5), loc="center left")
    # Save Plots
    plt.savefig('PythonFigures/Efficency/Efficency_%s.png' %particleSize, format='png', bbox_inches='tight', orientation='landscape')
    plt.show()
    plt.close()
    return

"""
RUN ANALYSIS
"""
allDat = readDat(['.\Data\CSV'])
timeSerries(allDat, 'Ambient_Day1')
#particleOverlay(allDat, 'IncenceMask001', 'IncenceMask002')
#filterEff(allDat, '0.5um')
