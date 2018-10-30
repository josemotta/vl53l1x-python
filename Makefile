.PHONY: test tail

DEFINES = -D VL53L1_DEBUG=0 -D PAL_EXTENDED=1
WARNINGS = -Wno-implicit-function-declaration
CFLAGS = -ggdb
INCLUDES = -Iapi/core -Iapi/platform
OBJECTS = api/core/*c api/platform/*c python_lib/vl53l1x_python.c
SO = python/vl53l1x_python.so

COMPILE_LOG = compile.log
TEST_LOG = test.log

all: $(SO) test

test:
	objdump -t $(SO) | grep initialise | tee $(TEST_LOG)
	python test/turn_off_gpio.py 2>&1 | tee -a $(TEST_LOG)
	python test/change_address.py 41 16 2>&1 | tee -a $(TEST_LOG)
	# python test/change_address.py 41 20 2>&1 | tee -a $(TEST_LOG)
	# parallel python test/change_address.py ::: 40 39 :::+ 20 16  2>&1 | tee -a $(TEST_LOG)
	echo Done | tee -a $(TEST_LOG)

$(SO): $(OBJECTS)
	echo "" | tee $(COMPILE_LOG)
	gcc $(DEFINES) $(WARNINGS) $(CFLAGS) $(INCLUDES) $(OBJECTS) -shared -o $(SO) 2>&1 | tee -a $(COMPILE_LOG)
	echo Done | tee -a $(COMPILE_LOG)

tail:
	multitail -F .multitailrc -CS vl53l1 $(COMPILE_LOG) $(TEST_LOG)

