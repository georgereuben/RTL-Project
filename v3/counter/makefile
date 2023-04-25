CWD=$(shell pwd)

SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(CWD)/counter.sv

TOPLEVEL = counter
COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ns
MODULE = counter_test

include $(shell cocotb-config --makefiles)/Makefile.sim
