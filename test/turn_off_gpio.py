#!/usr/bin/env python

import RPi.GPIO as GPIO

SHUTX_PIN_1 = 20
SHUTX_PIN_2 = 16
SHUTX_PIN_3 = 21

GPIO.setwarnings(False)

# Setup GPIO for shutdown pins on
GPIO.setmode(GPIO.BCM)
GPIO.setup(SHUTX_PIN_1, GPIO.OUT)
GPIO.setup(SHUTX_PIN_2, GPIO.OUT)
GPIO.setup(SHUTX_PIN_3, GPIO.OUT)

# Reset sensor
GPIO.output(SHUTX_PIN_1, GPIO.LOW)
GPIO.output(SHUTX_PIN_2, GPIO.LOW)
GPIO.output(SHUTX_PIN_3, GPIO.LOW)
