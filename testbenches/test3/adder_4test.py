import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer

@cocotb.test()
async def adder4_test(dut):
    clock = Clock(dut.clock, 10, units="ns")
    cocotb.fork(clock.start())

    for i in range(2):
        dut.a <= 1
        dut.b <= 1
        dut.cin <= 0
        await RisingEdge(dut.clock)
        assert dut.sum == 2
        assert dut.cout == 0

        dut.a <= 3
        dut.b <= 4
        dut.cin <= 1
        await RisingEdge(dut.clock)
        assert dut.sum == 8
        assert dut.cout == 1