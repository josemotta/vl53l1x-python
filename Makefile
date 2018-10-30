BUILD_DIR = ./build/
DEFINES = -D VL53L1_DEBUG=1 -D PAL_EXTENDED=1
WARNINGS = -Wno-implicit-function-declaration
CFLAGS = -ggdb
INCLUDES = -Iapi/core -Iapi/platform
OBJECTS = api/core/*c api/platform/*c python_lib/vl53l1x_python.c
SO = python/vl53l1x_python.so

COMPILE_LOG = compile.log
TEST_LOG = compile.tst


all: compile link test

test:
	objdump -t $(SO) | grep initialise | tee $(TEST_LOG)
	python test.py | tee -a $(TEST_LOG)

link:
	#echo TODO

compile:
	echo "" | tee $(COMPILE_LOG)
	[ -d $(BUILD_DIR) ] || mkdir $(BUILD_DIR) 2>&1 | tee $(COMPILE_LOG)
	gcc $(DEFINES) $(WARNINGS) $(CFLAGS) $(INCLUDES) $(OBJECTS) -shared -o $(SO) 2>&1 | tee -a $(COMPILE_LOG)

tail:
	multitail -f -cS attila_log $(COMPILE_LOG) $(TEST_LOG)
