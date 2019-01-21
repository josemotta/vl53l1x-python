#!/usr/bin/python

# MIT License
#
# Copyright (c) 2017 John Bryan Moore
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from ctypes import CDLL, CFUNCTYPE, POINTER, c_int, pointer, c_ubyte, c_uint8
from smbus2 import SMBus, i2c_msg
import os
import site
import glob

class VL53L1xError(RuntimeError):
    pass

class VL53L1xDistanceMode:
    SHORT = 1
    MEDIUM = 2
    LONG = 3

# Read/write function pointer types.
_I2C_READ_FUNC = CFUNCTYPE(c_int, c_ubyte, c_ubyte, POINTER(c_ubyte), c_ubyte)
_I2C_WRITE_FUNC = CFUNCTYPE(c_int, c_ubyte, c_ubyte, POINTER(c_ubyte), c_ubyte)

# Load VL53L1X shared lib
_POSSIBLE_LIBRARY_LOCATIONS = [os.path.dirname(os.path.realpath(__file__))]

try:
    _POSSIBLE_LIBRARY_LOCATIONS += site.getsitepackages()
except AttributeError:
    pass

try:
    _POSSIBLE_LIBRARY_LOCATIONS += [site.getusersitepackages()]
except AttributeError:
    pass

for lib_location in _POSSIBLE_LIBRARY_LOCATIONS:
    files = glob.glob(lib_location + "/vl53l1x_python*.so")
    if len(files) > 0:
        lib_file = files[0]
        try:
            _TOF_LIBRARY = CDLL(lib_file)
            #print("Using: " + lib_location + "/vl51l1x_python.so")
            break
        except OSError:
            #print(lib_location + "/vl51l1x_python.so not found")
            pass
else:
    raise OSError('Could not find vl53l1x_python.so')


class VL53L1X:
    """VL53L1X ToF."""
    def __init__(self, i2c_bus=1):
        """Initialize the VL53L1X ToF Sensor from ST"""
        self._i2c_bus = i2c_bus
        self._i2c = SMBus(1)
        self._default_dev = None
        self._dev_list = None
        self._ok = True
        self._distance = 0

        # Resgiter Address
        self.ADDR_UNIT_ID_HIGH = 0x16 # Serial number high byte
        self.ADDR_UNIT_ID_LOW = 0x17 # Serial number low byte
        self.ADDR_I2C_ID_HIGH = 0x18 # Write serial number high byte for I2C address unlock
        self.ADDR_I2C_ID_LOW = 0x19 # Write serial number low byte for I2C address unlock
        self.ADDR_I2C_SEC_ADDR = 0x8a # Write new I2C address after unlock

    def open(self):
        self._i2c.open(bus=self._i2c_bus)
        self._configure_i2c_library_functions()
        self._default_dev = _TOF_LIBRARY.initialise()
        self._dev_list = dict()

    def add_sensor(self, sensor_id, address):
        self._dev_list[sensor_id] = _TOF_LIBRARY.copy_dev(self._default_dev)
        _TOF_LIBRARY.init_dev(self._dev_list[sensor_id], c_uint8(address))

    def close(self):
        self._i2c.close()
        self._default_dev = None
        self._dev_list = None

    def _configure_i2c_library_functions(self):
        # I2C bus read callback for low level library.
        def _i2c_read(address, reg, data_p, length):
            ret_val = 0

            msg_w = i2c_msg.write(address, [reg >> 8, reg & 0xff])
            msg_r = i2c_msg.read(address, length)

            # print("R: a: %x\tr:%d" % (address,reg))
            try:
                self._i2c.i2c_rdwr(msg_w, msg_r)
            except:
                print("Cannot read on 0x%x I2C bus, reg: %d" % (address,reg))

            if ret_val == 0:
                for index in range(length):
                    data_p[index] = ord(msg_r.buf[index])


            return ret_val

        # I2C bus write callback for low level library.
        def _i2c_write(address, reg, data_p, length):
            ret_val = 0
            data = []

            for index in range(length):
                data.append(data_p[index])

            msg_w = i2c_msg.write(address, [reg >> 8, reg & 0xff] + data)
            # print("W: a: %x\tr:%d" % (address,reg))

            try:
                self._i2c.i2c_rdwr(msg_w)
            except:
                print("Cannot write on 0x%x I2C bus, reg: %d" % (address, reg))

            return ret_val

        # Pass i2c read/write function pointers to VL53L1X library.
        self._i2c_read_func = _I2C_READ_FUNC(_i2c_read)
        self._i2c_write_func = _I2C_WRITE_FUNC(_i2c_write)
        _TOF_LIBRARY.VL53L1_set_i2c(self._i2c_read_func, self._i2c_write_func)

    def start_ranging(self, sensor_id, mode=VL53L1xDistanceMode.LONG):
        """Start VL53L1X ToF Sensor Ranging"""
        dev = self._dev_list[sensor_id]
        _TOF_LIBRARY.startRanging(dev, mode)

    def stop_ranging(self, sensor_id):
        """Stop VL53L1X ToF Sensor Ranging"""
        dev = self._dev_list[sensor_id]
        _TOF_LIBRARY.stopRanging(dev)

    def get_distance(self, sensor_id):
        dev = self._dev_list[sensor_id]
        return _TOF_LIBRARY.getDistance(dev)
        
    def get_address(self, sensor_id):
        dev = self._dev_list[sensor_id]
        return _TOF_LIBRARY.get_address(dev)

    def change_address(self, sensor_id, new_address):
        dev = self._dev_list[sensor_id]
        _TOF_LIBRARY.setDeviceAddress(dev, new_address)

    def update(self, sensor_id):
        """Read raw distance for homeassistant"""
        self._distance = self.get_distance(sensor_id)
    
    @property
    def sample_ok(self):
        """Return True for a valid measurement data."""
        return self._ok and self._distance >= 0

    @property
    def distance(self):
        """Distance in mm"""
        return self._distance

