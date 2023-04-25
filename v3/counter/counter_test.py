import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles
from pathlib import Path    
import sys
import logging

parent_path = Path("..").resolve()
sys.path.insert(0, str(parent_path))
from tinyalu_utils import get_int, logger

def get_int(signal):
    try:
        int_val = int(signal.value)
    except ValueError:
        int_val = 0
    return int_val

logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

@cocotb.test()
async def no_count(dut):
    """Test no count if reset is 0"""
    cocotb.start_soon(Clock(dut.clk, 2, units="ns").start())
    dut.reset_n.value = 0

    await ClockCycles(dut.clk, 5)
    count = get_int(dut.count)
    logger.info(f"After 5 clock cycles, count is {count}")
    assert count == 0
