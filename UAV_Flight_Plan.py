#!/usr/bin/env python
# -*- coding: utf-8 -*-


from dronekit import connect, VehicleMode, LocationGlobalRelative
import numpy as np
import time
from math import sin, cos, sqrt, atan2, radians, sqrt
import logging
import time
import os
import time

def takeOff():
    pass

def gotoFEA():
    pass

def locateTarget():
    def find_cm(image):
        #image is an mxn binary mask
        x = [0,0]
        y = [0,0]
        
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                if image[i,j] == 1:
                    x[0] += i
                    y[0] += j
                    x[1] += 1
                    y[1] += 1
        return([int(x[0]/x[1]),int(y[0]/y[1])])
        
    pass

def adjustPosition():
    pass

def descend():
    pass

def deployBeacon():
    pass

def safeLand():
    pass
def createFEAs():
    #REQURIES HARD CODING FOR NOW
    p1 = LocationGlobalRelative(41.714473,-86.24252,10)#make sure this matches with takeoff height
    p2 = LocationGlobalRelative(41.714999,-86.24252,10)
    p3 = LocationGlobalRelative(41.714799,-86.240,10)
    p4 = LocationGlobalRelative(41.714799,-86.2418,10)
def chooseFEA(createFEAs[]):
    close = 100000000
    #get closest point
    for point in points:
        if(close > get_distance_meters(vehicle.location.global_relative_frame,point)):
            close =  get_distance_meters(vehicle.location.global_relative_frame,point)
            closePoint = point
     return closePoint

def fly_to(vehicle, targetLocation, airspeed):
    print "Flying from: " + str(vehicle.location.global_relative_frame.lat) + "," + str(vehicle.location.global_relative_frame.lon) + " to " + str(targetLocation.lat) + "," + str(targetLocation.lon)
    vehicle.groundspeed = airspeed
    currentTargetLocation = targetLocation
    vehicle.simple_goto(targetLocation)
    while True:#while (vehicle.mode.name=="Guided"):
        remainingDistance=get_distance_meters(currentTargetLocation,vehicle.location.global_relative_frame)
        print "Distance rem: " + str(remainingDistance)
        if remainingDistance< 1:
            print "Reached target"
            break;

def main():
    takeOff()
    
    gotoFEA()
    
    centered = False
    
    while not centered:      
        locateTarget()
    
        adjustPosition()
    
    descend()
    
    deployBeacon()
    
    safeLand()
    
if (vehicle.mode.name=="Guided"):
    print "Returning to Launch"
    vehicle.mode = VehicleMode("RTL")

#Close vehicle object before exiting script
print "Close vehicle object"
vehicle.close()

# Shut down simulator if it was started.
if sitl is not None:
    sitl.stop()
