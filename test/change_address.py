#!/usr/bin/env python

from compiled_lib import VL53L1X
import time
from datetime import datetime
import sys

import RPi.GPIO as GPIO

SHUTX_PIN = int(sys.argv[1])
sensor_id = 123

GPIO.setwarnings(False)

# Setup GPIO for shutdown pins on
GPIO.setmode(GPIO.BCM)
GPIO.setup(SHUTX_PIN, GPIO.OUT)

# Reset sensor
GPIO.output(SHUTX_PIN, GPIO.LOW)
time.sleep(0.1)
GPIO.output(SHUTX_PIN, GPIO.HIGH)

# Init VL53L1X sensor
tof = VL53L1X.VL53L1X()
tof.open()
address = 0x25
tof.add_sensor(sensor_id, address)

tof.start_ranging(sensor_id, 1)
for _ in range(0,3):
    distance_mm = tof.get_distance(sensor_id)
    print("Address: {} Distance: {}mm".format(address, distance_mm))
    time.sleep(0.001)
tof.stop_ranging(sensor_id)

# Change address again
address = 0x26
tof.change_address(sensor_id, address)
tof.start_ranging(sensor_id, 1)
for _ in range(0,3):
    distance_mm = tof.get_distance(sensor_id)
    print("Time: {} Distance: {}mm".format(datetime.utcnow().strftime("%S.%f"), distance_mm))
    time.sleep(0.001)
tof.stop_ranging(sensor_id)
time.sleep(0.1)

# Change address back to default
address = 0x26
tof.change_address(sensor_id, address)
tof.start_ranging(sensor_id, 1)
for _ in range(0,3):
    distance_mm = tof.get_distance(sensor_id)
    print("Time: {} Distance: {}mm".format(datetime.utcnow().strftime("%S.%f"), distance_mm))
    time.sleep(0.001)
tof.stop_ranging(sensor_id)
time.sleep(0.1)

GPIO.output(SHUTX_PIN, GPIO.LOW)

print("### Done: %s\n" % __file__)
