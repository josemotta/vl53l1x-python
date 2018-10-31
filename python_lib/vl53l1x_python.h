
#ifndef _VL53L1_PYTHON
#define _VL53L1_PYTHON

// External functions, accessible from outside the compilation unit
extern VL53L1_Dev_t* copy_dev(VL53L1_Dev_t*);
extern void init_dev(VL53L1_Dev_t*, uint8_t);
extern uint8_t get_address(VL53L1_Dev_t*);
extern VL53L1_Error setDeviceAddress(VL53L1_Dev_t*, uint8_t);
extern VL53L1_Dev_t* initialise(void);
extern VL53L1_Error setDeviceAddress(VL53L1_Dev_t*, uint8_t);
extern VL53L1_Error startRanging(VL53L1_Dev_t*, int);
extern int32_t getDistance(VL53L1_Dev_t*);

// Internal functions, only accessible in the compilation unit
static void try_command(VL53L1_Error (*) ( VL53L1_Dev_t *), VL53L1_Dev_t*, char*);
static void print_device_info(VL53L1_Dev_t*);
static VL53L1_Dev_t* allocate_VL53L1_Dev_t(void);

#endif
