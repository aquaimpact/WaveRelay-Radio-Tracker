import numpy as np

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
from matplotlib import style
import pandas as pd

def plotHistorical(csvName):
    data = pd.read_csv(csvName)
    xdf = data['x-Coords']
    ydf = data['y-Coords']
    zdf = data['z-Coords']
    
    fig = plt.figure()
    ax = plt.subplot(111, projection='3d')
    ax.set_xlabel("X-Axis")
    ax.set_ylabel("Y-Axis")
    ax.set_zlabel("Z-Axis")
    ax.set_zlim(0, 50)
    ax.set_ylim(0, 50)
    ax.set_xlim(0, 50)
       
    x = xdf.tolist()
    x = list(map(float, x))
    y = ydf.tolist()
    y = list(map(float, y))
    z = zdf.tolist()
    z = list(map(float, z))
    ax.plot(x,y,z, "--g")
    
plotHistorical('coords2.csv')