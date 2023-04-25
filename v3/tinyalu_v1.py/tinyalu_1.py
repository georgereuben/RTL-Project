from cocotb.triggers import FallingEdge 
import cocotb
import random
from pathlib import Path
parent_path = Path("..").resolve()
import sys
sys.path.insert(0, str(parent_path))
import logging
from tinyalu_utils import Ops, alu_prediction, logger, get_int

import enum
class Ops (enum. IntEnum):
    """Legal ops for the TinyALU"""
    ADD = 1
    AND = 2
    XOR = 3
    MUL = 4

def alu_prediction(A, B, op):
    """Python Model of the TinyALU"""
    assert isinstance(op, Ops), "The tinyalu's op should be of type Ops"
    if op == Ops.ADD:
        return A + B
    elif op == Ops.AND:
        return A & B
    elif op == Ops.XOR:
        return A ^ B
    elif op == Ops.MUL:
        return A * B
    
@cocotb.test()
async def alu_test(dut):
    """Test the TinyALU"""
    logger.info("INITIALIZING TEST")

    passed = True
    cvg = set()
    logger.info("RESETTING DUT")
    await FallingEdge(dut.clk)
    dut.reset.value = 0
    dut.start.value = 0
    await FallingEdge(dut.clk)
    dut.reset.value = 1
    #dut resetted above

    result = 0
    logger.info("STARTING TEST")
    cmd_count = 1
    op_list = list(Ops)
    num_ops = len(op_list)
    logger.info(f"num_ops = {num_ops}")
    while(cmd_count <= num_ops):
        await FallingEdge(dut.clk)
        st = get_int(dut.start)
        dn = get_int(dut.done)

        #got the start and done signals of the dut at the falling edge of the clock, so we pass commands
        if(st == 0 and dn == 0):
            #if start and done are both 0, then we can start a new command and generate stimulus here
            aa = random.randint(0, 255)
            bb = random.randint(0, 255)
            op = op_list.pop(0)
            cvg.add(op)
            #set the inputs of the dut
            dut.A.value = aa
            dut.B.value = bb
            dut.op.value = op
            #set the start signal to 1
            dut.start.value = 1

        #logger.info("DUT: start = %d, done = %d", st, dn)

        if(st == 0 and dn == 1):
            raise AssertionError("DUT ERROR: done set to 1 without start being set to 1")
        
        if(st == 1 and dn == 0):    # dut is in an operation
            continue

        if(st == 1 and dn == 1):
            dut.start.value = 0
            cmd_count += 1
            result = get_int(dut.result)

            logger.info(f"CMD {cmd_count}: {aa:2x} {op.name} {bb:2x} = {result:04x}")
            
            pr = alu_prediction(aa, bb, op)
            #logger.info(f"PREDICTED VALUE: {aa:2x} {op.name} {bb:2x} = {pr:04x} , ACTUAL VALUE: {aa:2x} {op.name} {bb:2x} = {result:04x}")
                        
            if(result == pr):
                logger.debug(f"PASSED: {aa:2x} {op.name} {bb:2x} = {result:04x}")
                passed = True
            else:
                logger.error(f"FAILED: {aa:2x} {op.name} {bb:2x} = {result:04x} (expected {pr:04x})")
                passed = False
    
    if(len(set(Ops) - cvg) > 0):
        logger.error(f"FUNCTIONAL COVERAGE ERROR. Missed: {set(Ops) - cvg}")
        passed = False
    else:
        logger.debug("FUNCTIONAL COVERAGE PASSED")
    
    assert passed
    