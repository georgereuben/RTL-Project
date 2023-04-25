from cocotb.triggers import FallingEdge 
import cocotb
import random
from pathlib import Path
parent_path = Path("..").resolve()
import sys
sys.path.insert(0, str(parent_path))
import logging
from tinyalu_utils import Ops, alu_prediction, logger, get_int

@cocotb.test()
async def adder_test(dut):
    """Test the 4-bit adder"""
    logger.info("INITIALIZING TEST")
    passed = 0
    
    for i in range(10):
        aa = random.randint(0, 15)
        bb = random.randint(0, 15)
        dut.A.value = aa
        dut.B.value = bb
        await FallingEdge(dut.clk)
        result = get_int(dut.result)
        pr = aa + bb
        if result == pr:
            logger.debug(f"TEST {i} PASSED")
            passed+=1
        else:
            logger.error(f"TEST {i} FAILED")
            logger.warning(f"result = {result}, predicted = {pr}")
    
    logger.info(f"TEST PASSED {passed} TIMES")
    assert passed >= 5
    

