/*
MIT License

Copyright (c) 2017 John Bryan Moore

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

#include <pthread.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <ctype.h>
#include <time.h>
#include "vl53l1_api.h"
#include "vl53l1_platform.h"

#include "vl53l1x_python.h"

static VL53L1_RangingMeasurementData_t RangingMeasurementData;
static VL53L1_RangingMeasurementData_t *pRangingMeasurementData = &RangingMeasurementData;

/******************************************************************************
 * @brief   Initialises the device.
 *  @param  i2c_address - I2C Address to set for this device
 *  @param  TCA9548A_Device - Device number on TCA9548A I2C multiplexer if
 *              being used. If not being used, set to 255.
 *  @param  TCA9548A_Address - Address of TCA9548A I2C multiplexer if
 *              being used. If not being used, set to 0.
 * @retval  The Dev Object to pass to other library functions.
 *****************************************************************************/
VL53L1_Dev_t* initialise()
{
    // Flush stdout and stderr to get the print instantly
    setbuf(stdout, NULL);
    setbuf(stderr, NULL);
    VL53L1_Dev_t *dev = allocate_VL53L1_Dev_t();

    // Default address
    dev->I2cDevAddr = 0x29;

    try_command( &VL53L1_software_reset, dev, "Calling software_reset...");
    try_command( &VL53L1_WaitDeviceBooted, dev, "Calling WaitDeviceBooted...");

    return dev;
}

VL53L1_Error setDeviceAddress(VL53L1_Dev_t *dev, uint8_t i2c_address)
{
    printf("Set address from 0x%x to 0x%x\n", dev->I2cDevAddr, i2c_address);
    VL53L1_Error Status = VL53L1_SetDeviceAddress(dev, i2c_address << 1);
    dev->I2cDevAddr = i2c_address;
    try_command( &VL53L1_DataInit, dev, "Calling DataInit...");
    try_command( &VL53L1_StaticInit, dev, "Calling StaticInit...");
    return Status;
}

/******************************************************************************
 * @brief   Start Ranging
 * @param   mode - ranging mode
 *              0 - Good Accuracy mode
 *              1 - Better Accuracy mode
 *              2 - Best Accuracy mode
 *              3 - Longe Range mode
 *              4 - High Speed mode
 * @note Mode Definitions
 *   Good Accuracy mode
 *       33 ms timing budget 1.2m range
 *   Better Accuracy mode
 *       66 ms timing budget 1.2m range
 *   Best Accuracy mode
 *       200 ms 1.2m range
 *   Long Range mode (indoor,darker conditions)
 *       33 ms timing budget 2m range
 *   High Speed Mode (decreased accuracy)
 *       20 ms timing budget 1.2m range
 * @retval  Error code, 0 for success.
 *****************************************************************************/
VL53L1_Error startRanging(VL53L1_Dev_t *dev, int mode)
{
    VL53L1_Error Status = VL53L1_ERROR_NONE;
    Status = VL53L1_SetDistanceMode(dev, mode);
    Status = VL53L1_SetMeasurementTimingBudgetMicroSeconds(dev, 66000);
    Status = VL53L1_SetInterMeasurementPeriodMilliSeconds(dev, 70);
    Status = VL53L1_StartMeasurement(dev);
    return Status;
}

/******************************************************************************
 * @brief   Get current distance in mm
 * @return  Current distance in mm or -1 on error
 *****************************************************************************/
int32_t getDistance(VL53L1_Dev_t *dev)
{
    VL53L1_Error Status = VL53L1_ERROR_NONE;
    int32_t current_distance = -1;
    Status = VL53L1_WaitMeasurementDataReady(dev);
    Status = VL53L1_GetRangingMeasurementData(dev, pRangingMeasurementData);
    current_distance = pRangingMeasurementData->RangeMilliMeter;
    VL53L1_ClearInterruptAndStartMeasurement(dev);
    return current_distance;
}

/******************************************************************************
 * @brief   Stop Ranging
 *****************************************************************************/
VL53L1_Error stopRanging(VL53L1_Dev_t *dev)
{
    return VL53L1_StopMeasurement(dev);
}

void try_command(VL53L1_Error (*command) ( VL53L1_Dev_t *), VL53L1_Dev_t* dev, char* print_text) {
    /* printf(print_text); */

    VL53L1_Error error_code = VL53L1_ERROR_NONE;
    while (error_code = command(dev)) {
        char error_string[100] ;
        VL53L1_get_pal_error_string(error_code, error_string);
        printf("\nError: %s", error_string);
        sleep(1);
    }
    printf("\tDone\n");
}

void print_device_info(VL53L1_Dev_t *dev)
{
    VL53L1_DeviceInfo_t DeviceInfo;
    VL53L1_Error Status = VL53L1_GetDeviceInfo(dev, &DeviceInfo);

    if(Status == VL53L1_ERROR_NONE ){
        printf("VL53L0X_GetDeviceInfo:\n");
        printf("Device Name : %s\n", DeviceInfo.Name);
        printf("Device Type : %s\n", DeviceInfo.Type);
        printf("Device ID : %s\n", DeviceInfo.ProductId);
        printf("ProductRevisionMajor : %d\n", DeviceInfo.ProductRevisionMajor);
        printf("ProductRevisionMinor : %d\n", DeviceInfo.ProductRevisionMinor);
    }
}

VL53L1_Dev_t* allocate_VL53L1_Dev_t(void) {
    VL53L1_Dev_t* dev = (VL53L1_Dev_t *) calloc(1, sizeof(VL53L1_Dev_t));
    return dev;
}

VL53L1_Dev_t* copy_dev(VL53L1_Dev_t* dev) {
    VL53L1_Dev_t* new_dev = allocate_VL53L1_Dev_t();
    memcpy(new_dev, dev, sizeof(VL53L1_Dev_t));
    return new_dev;
}

void init_dev(VL53L1_Dev_t* dev, uint8_t i2c_address) {
    setDeviceAddress( dev, i2c_address );

    // Calibration
    try_command(&VL53L1_PerformRefSpadManagement, dev, "Calling PerformRefSpadManagement");

    // Disable crosstalk compensation (bare sensor)
    VL53L1_SetXTalkCompensationEnable(dev, 0);

#ifdef VL53L1_DEBUG
    if (VL53L1_DEBUG == 1) print_device_info(dev);
#endif
}

uint8_t get_address(VL53L1_Dev_t* dev) {
    return dev->I2cDevAddr;
}
