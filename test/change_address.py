#!/usr/bin/env python

from compiled_lib import VL53L1X
import time
from datetime import datetime
import sys

import RPi.GPIO as GPIO

address = int(sys.argv[1])
SHUTX_PIN = int(sys.argv[2])

GPIO.setwarnings(False)

# Setup GPIO for shutdown pins on
GPIO.setmode(GPIO.BCM)
GPIO.setup(SHUTX_PIN, GPIO.OUT)

# Reset sensor
GPIO.output(SHUTX_PIN, GPIO.LOW)
time.sleep(0.1)
GPIO.output(SHUTX_PIN, GPIO.HIGH)

# Init VL53L1X sensor
tof = VL53L1X.VL53L1X(i2c_address=address)
tof.open()

tof.start_ranging(1)
for _ in range(0,3):
    distance_mm = tof.get_distance()
    print("Address: {} Distance: {}mm".format(address, distance_mm))
    time.sleep(0.001)
    time.sleep(0.1)
tof.stop_ranging()

#  # Change address again
#  tof.change_address(0x28)
#  tof.start_ranging(1)
#  for _ in range(0,3):
#      distance_mm = tof.get_distance()
#      print("Time: {} Distance: {}mm".format(datetime.utcnow().strftime("%S.%f"), distance_mm))
#      time.sleep(0.001)
#  tof.stop_ranging()
#  time.sleep(0.1)
#
#  # Change address back to default
#  tof.change_address(0x29)
#  tof.start_ranging(1)
#  for _ in range(0,3):
#      distance_mm = tof.get_distance()
#      print("Time: {} Distance: {}mm".format(datetime.utcnow().strftime("%S.%f"), distance_mm))
#      time.sleep(0.001)
#  tof.stop_ranging()
#  time.sleep(0.1)
