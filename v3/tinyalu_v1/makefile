CWD=$(shell pwd)

SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(CWD)/tinyalu.sv

TOPLEVEL = tinyalu
COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ns
MODULE = tinyalu_1

include $(shell cocotb-config --makefiles)/Makefile.sim