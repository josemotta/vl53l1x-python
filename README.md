# vl53l1x-python

Revised Python library for the VL53L1X Laser Ranger.

# Installing

```
sudo pip3 install smbus2
sudo pip3 install VL53L1X2
```

# Usage

'''See tests/use_sensor_pypi.py for details.'''

import VL53L1X2

...

# I2C addresses for each sensor
ADDRESS_1 = 0x29

# GPIO pins connected to the sensors SHUTX pins
SHUTX_PIN_1 = 16

# Arbitrary sensor id-s, should be unique for each sensor
sensor_id_1 = 1111

GPIO.setwarnings(False)

# Setup GPIO for shutdown pins on
GPIO.setmode(GPIO.BCM)
GPIO.setup(SHUTX_PIN_1, GPIO.OUT)

# Reset sensor
GPIO.output(SHUTX_PIN_1, GPIO.LOW)
time.sleep(0.01)
GPIO.output(SHUTX_PIN_1, GPIO.HIGH)
time.sleep(0.01)

# Init VL53L1X sensor
tof = VL53L1X2.VL53L1X()
tof.open()
tof.add_sensor(sensor_id_1, ADDRESS_1)

tof.start_ranging(sensor_id_1, 1)

for _ in range(0,20):
    distance_mm_1 = tof.get_distance(sensor_id_1)
    print("Time: {}\tSensor 1: {} mm".format(datetime.utcnow().strftime("%S.%f"), distance_mm_1))
    time.sleep(0.001)
tof.stop_ranging(sensor_id_1)

# Clean-up
tof.close()

GPIO.output(SHUTX_PIN_1, GPIO.LOW)
