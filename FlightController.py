#!/usr/bin/env python
# -*- coding: utf-8 -*-


import dronekit
import numpy as np
import time
from math import sin, cos, sqrt, atan2, radians, sqrt
import logging
import os

def arm_and_takeoff(vehicle,aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """
    print("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print " Waiting for vehicle to initialise..."
        time.sleep(1)

    print "Arming motors"
    # Copter should arm in GUIDED mode
    vehicle.mode = dronekit.VehicleMode("GUIDED")
    vehicle.armed = True

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
        if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95:
            print "Reached target altitude"
            break
        time.sleep(1)

def main():
    ################################################################################################
    # Connect to the Vehicle
    ################################################################################################
    try:
        vehicle = dronekit.connect('/dev/serial0',baud=57600)
        vehicle.wait_ready(True,timeout=300)
    except Exception as e:
        print(str(e))
           
    altitude = 3 # Meters
    airspeed = 1 # Meters/second
    arm_and_takeoff(vehicle,altitude)
    ''' Return to start location and land
    if (vehicle.mode.name=="Guided"):
        print "Returning to Launch"
        vehicle.mode = dronekit.VehicleMode("RTL") '''
    print("Setting LAND mode...") # This allows you to land in place, even if you have moved
    vehicle.mode = dronekit.VehicleMode("LAND")

    #Close vehicle object before exiting script
    print "Close vehicle object"
    vehicle.close()
    
    
if __name__ == "__main__":
    main()


################################################################################################
# function:    Get distance in meters
# parameters:  Two global relative locations
# returns:     Distance in meters
################################################################################################
def get_distance_meters(locationA, locationB):
    # approximate radius of earth in km
    R = 6373.0

    lat1 = radians(locationA.lat)
    lon1 = radians(locationA.lon)
    lat2 = radians(locationB.lat)
    lon2 = radians(locationB.lon)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = (R * c) * 1000

    print("Distance (meters):", distance)
    return distance
