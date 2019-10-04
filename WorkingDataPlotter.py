####################
#  Libraries Used  #
####################

import sys
import time
import random
import zmq
import numpy
import json
import pandas as pd
import os

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
from matplotlib import style

##############################
#  Lists For Graph Plotting  #
##############################

xs = []
ys = []
zs = []


####################
#  Graph creation  #
####################

def add(x,y,z,fig,ax, xGround = None, yGround = None, zGround = None, xlim = None, ylim = None, zlim = None):
    
    
    ax.clear()
    
    ####################
    #  Graph settings  #
    ####################
    ax.set_xlabel("X-Axis")
    ax.set_ylabel("Y-Axis")
    ax.set_zlabel("Z-Axis")
    
    # Checks if the user has inputted any changes to the axis of the graph.
    # If there isnt any changes, the graph will be automatically set to 50 X 50 X 50    
    if xlim == None or ylim == None or zlim == None:
        ax.set_zlim(0, 50)
        ax.set_ylim(0, 50)
        ax.set_xlim(0, 50)
    else:
        
        # Requires the user to input a tuple
        if type(xlim) != tuple:
            raise TypeError("xlim is not a TUPLE! Please insert a TUPLE!")
        elif type(ylim) != tuple:
            raise TypeError("ylim is not a TUPLE! Please insert a TUPLE!")
        elif type(zlim) != tuple:
            raise TypeError("zlim is not a TUPLE! Please insert a TUPLE!")
        else:
            ax.set_zlim(zlim[0], zlim[1])
            ax.set_ylim(ylim[0], ylim[1])
            ax.set_xlim(xlim[0], xlim[1])
            
    
    
    ####################
    #  Graph Plotting  #
    ####################
    
    # This is for the live plot (Red Dotted Line)
    orix = []
    oriy = []
    oriz = []
    orix.append(x[0])
    oriy.append(y[0])
    oriz.append(z[0])
    ax.plot(orix, oriy, oriz, 'bo')
    ax.plot(x,y,z, '--r', label='Live Plot')
    
    # This is or the Ground Truth Plot (Green Solid Line)
    if xGround != None or yGround != None or zGround != None:
        ax.plot(xGround, yGround, zGround, 'g', label='Ground Truth Plot')
    
    #Uncomment this if you just want the scatter plot
#    ax.scatter(x[:-1], y[:-1], z[:-1], 'b')
#    ax.scatter(x[-1], y[-1], z[-1], 'r')
    plt.pause(0.5)
    

def groundTruth(csvName):
    data = pd.read_csv(csvName)
    xdf = data['x-Coords']
    ydf = data['y-Coords']
    zdf = data['z-Coords']
    
    x = xdf.tolist()
    x = list(map(float, x))
    y = ydf.tolist()
    y = list(map(float, y))
    z = zdf.tolist()
    z = list(map(float, z))
    
    return x,y,z
    

def connection(ipaddress, port, csvName,  topicfilter = None, groundtruthCSV = None):
    
    
    ###########################
    #  Setting up connection  #
    ###########################
    context = zmq.Context()
    print("Connecting to Publisher...")
    socket = context.socket(zmq.SUB)

    #connects to the network
    socket.connect("tcp://%s:%s" % (ipaddress, port))
    print("tcp://%s:%s" % (ipaddress, port))
    
    if topicfilter == None:
        socket.setsockopt_string(zmq.SUBSCRIBE, "")
        print("Subscribed To Everything!")
    else:
        socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)
        print("Subscribed To: " + topicfilter)
        
    counter = 0
    counter2 = 0
    
    # Checks if the csv is there, and you want to save the coords to the 
    # same CSV, you will need to confirm with a yes or no.
    if os.path.exists(csvName):
        print("There is a file with the samename. By continuing, you will rerite this current file!")
        userInput = input("[y] | n ")
        userinput = userInput.upper()
        if(userinput == 'Y'):
            os.remove(csvName)
            print("Deleting it...")
    
    # Ground truth
    if groundtruthCSV != None:
        print("Inputting ground truth into the graph...")
        xGround, yGround, zGround = groundTruth(groundtruthCSV)
    else:
        xGround = None
        yGround = None
        zGround = None
        
    #Prepariing the SubPlots
    fig = plt.figure()
    ax = plt.subplot(111, projection='3d')
    while True:
        
        # Receiving the data from the phone
        string = socket.recv(0)
        topicF, message = string.split()
        
        #Decoding the message from a binary dict or json into a dict or json format.
        newMessage = json.loads(message.decode('utf-8'))

        # x-Coords
        xCoord = float(newMessage['xCoord'])
        
        # y-Coords
        yCoord = float(newMessage['yCoord'])
        
        # z-Coords
        altitude = float(newMessage['altitude'])
        
        
        if counter % 30 == 0:
            
            # Creating a Pandas Dataframe and appending the coords to the csv for historical plotting.
            coordinates = {'x-Coords': xs, 'y-Coords': ys, 'z-Coords': zs}
            df= pd.DataFrame(coordinates)
            if counter2 == 0:
                df.to_csv(csvName, mode='a')
            else: 
                df.to_csv(csvName, mode='a', header=False)
            counter2 += 1
            
            # Print here is just to make sure that everything works.
            # If you do not see anything printing, you needa check connection!
            print(xCoord, yCoord, altitude)
        
        if counter % 200 == 0:
            
            # Clears the plotting list to prevent the graph from not responding
            xs.clear()
            ys.clear()
            zs.clear()
            print("The amount of data plotted: " + str(counter))
            print(xCoord, yCoord, altitude)
        #################################
        #  Preparing data for plotting  #
        #################################
        xs.append(float(xCoord))
        ys.append(float(yCoord))
        zs.append(float(altitude))
        
        # Plotting the graph for each point
        add(xs,ys,zs,fig,ax, xGround, yGround, zGround, )
        counter += 1

connection("198.18.2.2", "5556", "coords2.csv", "PREFIX-BFT-INSERT", "coords.csv")
