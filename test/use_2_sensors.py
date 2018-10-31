#!/usr/bin/env python

from compiled_lib import VL53L1X
import time
from datetime import datetime

import RPi.GPIO as GPIO

# I2C addresses for each sensor
ADDRESS_1 = 0x28
ADDRESS_2 = 0x27

# GPIO pins connected to the sensors SHUTX pins
SHUTX_PIN_1 = 20
SHUTX_PIN_2 = 21

# Arbitrary sensor id-s, should be unique for each sensor
sensor_id_1 = 1111
sensor_id_2 = 1234

GPIO.setwarnings(False)

# Setup GPIO for shutdown pins on
GPIO.setmode(GPIO.BCM)
GPIO.setup(SHUTX_PIN_1, GPIO.OUT)
GPIO.setup(SHUTX_PIN_2, GPIO.OUT)

# Reset sensor
GPIO.output(SHUTX_PIN_1, GPIO.LOW)
GPIO.output(SHUTX_PIN_2, GPIO.LOW)

time.sleep(0.01)
GPIO.output(SHUTX_PIN_1, GPIO.HIGH)
time.sleep(0.01)

# Init VL53L1X sensor
tof = VL53L1X.VL53L1X()
tof.open()
tof.add_sensor(sensor_id_1, ADDRESS_1)
GPIO.output(SHUTX_PIN_2, GPIO.HIGH)
tof.add_sensor(sensor_id_2, ADDRESS_2)

tof.start_ranging(sensor_id_1, 1)
tof.start_ranging(sensor_id_2, 1)
for _ in range(0,10):
    distance_mm_1 = tof.get_distance(sensor_id_1)
    distance_mm_2 = tof.get_distance(sensor_id_2)
    print("Time: {}\tSensor 1: {}mm\tSensor 2: {}mm".format(datetime.utcnow().strftime("%S.%f"), distance_mm_1, distance_mm_2))
    time.sleep(0.001)
tof.stop_ranging(sensor_id_1)
tof.stop_ranging(sensor_id_2)

# Clean-up
tof.close()

GPIO.output(SHUTX_PIN_1, GPIO.LOW)
GPIO.output(SHUTX_PIN_2, GPIO.LOW)

print("### Done: %s\n" % __file__)
