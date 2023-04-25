CWD=$(shell pwd)

SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(CWD)/4_bit_adder.sv

TOPLEVEL = adder_four_bit
COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ns
MODULE = adder_4test

include $(shell cocotb-config --makefiles)/Makefile.sim
