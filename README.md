# vl53l1x-python

Revised Python library for the VL53L1X Laser Ranger.

# Installing

```
sudo pip3 install smbus2
sudo pip3 install VL53L1X2
```

# Usage

```python
import VL53L1X

tof = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
tof.open() # Initialise the i2c bus and configure the sensor
tof.start_ranging(1) # Start ranging, 1 = Short Range, 2 = Medium Range, 3 = Long Range
distance_in_mm = tof.get_distance() # Grab the range in mm
tof.stop_ranging() # Stop ranging
```

See examples and tests for more advanced usage.

