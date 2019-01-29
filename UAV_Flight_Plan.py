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
import argparse

def set_up():
    parser = argparse.ArgumentParser(description='Commands vehicle using vehicle.simple_goto.')
    parser.add_argument('--connect', 
                       help="Vehicle connection target string. If not specified, SITL automatically started and used.")
    args = parser.parse_args()

    connection_string = args.connect
    sitl = None


    ################################################################################################
    #Start SITL if no connection string specified
    ################################################################################################
    if not connection_string:
        import dronekit_sitl
        #sitl = dronekit_sitl.start_default()
        #connection_string = sitl.connection_string()
        ardupath ="/home/uav/git/ardupilot"
        home = "41.714801,-86.241871,221,0"
        sitl_defaults = os.path.join(ardupath, 'Tools', 'autotest', 'default_params', 'copter.parm')
        sitl_args = ['-I{}'.format(0), '--home', home, '--model', '+', '--defaults', sitl_defaults]
        sitl = dronekit_sitl.SITL(path=os.path.join(ardupath, 'build', 'sitl', 'bin', 'arducopter'))
        sitl.launch(sitl_args, await_ready=True)

        tcp, ip, port = sitl.connection_string().split(':')
        port = str(int(port) + 0 * 10)
        connection_string = ':'.join([tcp, ip, port])

        #vehicle = dronekit.connect(conn_string)
        #vehicle.wait_ready(timeout=120)



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


def gotoFEA(vehicle,points,airspeed):
    fly_to(vehicle,points,airspeed)

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
    dropCount = 0;
    while dropcount<2:
        lat = vehicle.location.global_relative_frame.lat
        lon = vehicle.location.global_relative_frame.lon
        if checkIfCentered:
            new_alt = vehicle.location.global_relative_frame.alt/2 #Check to see exactly what global relative frame does and edit me
            dropCount++;
            
        else:
            new_alt = vehicle.location.global_relative_frame.alt*2 #Check to see exactly what global relative frame does and edit me
            #add code here to recenter on the spot
           # -
           # -
           # -
       
            dropcount--
        
        target_location = LocationGlobalRelative(lat,lon,new_alt)
        vehicle.simple_goto(target_location)
     target_location = LocationGlobalRelative(lat,lon,2) # drop drone to 2 meters  
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
    return [p1,p2,p3,p4]
    
def chooseFEA():
    points = createFEAs()
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
    ################################################################################################
    # Connect to the Vehicle
    ################################################################################################
    print 'Connecting to vehicle on: %s' % connection_string
    vehicle = connect(connection_string, wait_ready=False)
    vehicle.wait_ready(True,timeout=300)       
    set_up()
           
    altitude = 10 #randomly choosen
    airspeed = 10 
    arm_and_takeoff(altitude)
    
    gotoFEA(vehicle,chooseFEA(),airspeed)
    
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
