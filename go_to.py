#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modified from 3DR simple_goto.py
"""

from dronekit import connect, VehicleMode, LocationGlobalRelative
import time
from math import sin, cos, sqrt, atan2, radians, sqrt
import logging
import time
import os
import time



################################################################################################
#Set up option parsing to get connection string
################################################################################################
import argparse  
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

################################################################################################
# Connect to the Vehicle
################################################################################################
print 'Connecting to vehicle on: %s' % connection_string
vehicle = connect(connection_string, wait_ready=False)
vehicle.wait_ready(True,timeout=300)


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


################################################################################################
# LOGGING FUNCTIONALITY
# Field 0: reserved by logging function
# Field 1: latitude
# Field 2: longitude
# Field 3: altitude
# Field 4: speed in meters  (replace with vehicle.velocity if velocity vector is needed)
# Field 5: timestamp in milliseconds
# Field 6: command tag (e.g., GOTO-1-START, continue)
# Field 7: optional text field
################################################################################################

# Setup filename
logging.basicConfig(filename='Test7Physical.log',level=logging.DEBUG)

# function:    log message
# parameters:  Vehicle, command issued, optional text
# returns:     n/a
def logmesssage(vehicle,command,extra):
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()  
    xv = vehicle.velocity[0]
    xy = vehicle.velocity[1]
    xz = vehicle.velocity[2]
    speed = sqrt((xv*xv)+(xy*xy)+(xz*xz))
    #print "X velocity " + str(xv)
    logging.debug("," + str(vehicle.location.global_relative_frame.lat) + "," + str(vehicle.location.global_relative_frame.lon) + "," + str(vehicle.location.global_relative_frame.alt) + "," + str(speed) + "," + str(time.time()) + "," + command + "," + extra + ",")

################################################################################################
# ARM and TAKEOFF
################################################################################################

# function:   	arm and takeoff
# parameters: 	target altitude (e.g., 10, 20)
# returns:	n/a

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

################################################################################################
# Fly to
################################################################################################
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
       

################################################################################################
# Experiment Code
################################################################################################

#print "Enter latitude: "
#latitude = input()
#print "Enter longitude: "
#longitude = input()
#point = LocationGlobalRelative(latitude,longitude,10)
#fly_to(vehicle,point,3,"GOTO-1-START","GOTO_1_END")
#time.sleep(100)
p1 = LocationGlobalRelative(41.714473,-86.24252,10)#make sure this matches with takeoff height
p2 = LocationGlobalRelative(41.714999,-86.24252,10)
p3 = LocationGlobalRelative(41.714799,-86.240,10)
p4 = LocationGlobalRelative(41.714799,-86.2418,10)

points = [p1,p2,p3,p4]

print "Set default/target airspeed to 3"
vehicle.airspeed = 10

#print "Going towards first point for 30 seconds ..."
#point1 = LocationGlobalRelative(41.714693,-86.242520,10)
#vehicle.simple_goto(point1)

#print "Fly to waypoint 1"
#point1 = LocationGlobalRelative(41.714693,-86.242520,10)
# sleep so we can see the change in map
#time.sleep(20)

close = 100000000

#get closest point
for point in points:
	if(close > get_distance_meters(vehicle.location.global_relative_frame,point)):
		close =  get_distance_meters(vehicle.location.global_relative_frame,point)
		closePoint = point

#print out coordiantes of points

#fly to closest point
fly_to(vehicle,closePoint,10)#speed should be between 7 and 10. Test



############################################
#do target detection stuff
#land

#if (vehicle.mode.name=="Guided"):
#    print "Fly to waypoint 2"
#    fly_to(vehicle,LocationGlobalRelative(41.714701,-86.240239,20),20,"GOTO-1-START","GOTO_1_END")

if (vehicle.mode.name=="Guided"):
    print "Returning to Launch"
    vehicle.mode = VehicleMode("RTL")

#Close vehicle object before exiting script
print "Close vehicle object"
vehicle.close()

# Shut down simulator if it was started.
if sitl is not None:
    sitl.stop()
