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

def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print "Basic pre-arm checks"
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print " Waiting for vehicle to initialise..."
        time.sleep(1)

    print "home: " + str(vehicle.location.global_relative_frame.lat)
    
    print "Arming motors"
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True    
    print "Mode" + str(vehicle.mode)

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:      
        print " Waiting for arming..."
        time.sleep(1)

    print "Taking off!"
    vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command 
    #  after Vehicle.simple_takeoff will execute immediately).
    while True:
        print " Altitude: ", vehicle.location.global_relative_frame.alt 
        #Break and return from function just below target altitude.        
        if vehicle.location.global_relative_frame.alt>=aTargetAltitude*.95: 
            print "Reached target altitude"
            break
        time.sleep(1)
arm_and_takeoff(10)#hard coded takeoff height relative to take off


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
    arm_and_takeoff(Altitude)
    
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
