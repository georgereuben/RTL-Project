from cocotb.triggers import FallingEdge 
import cocotb
import random
from pathlib import Path
parent_path = Path("..").resolve()
import sys
sys.path.insert(0, str(parent_path))
import logging
from tinyalu_utils import Ops, alu_prediction, logger, get_int, TinyAluBfm

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
async def alu_test(_):
    """Test the TinyALU"""
    logger.info("INITIALIZING TEST")

    passed = True
    bfm = TinyAluBfm()
    logger.info("RESETTING DUT")
    await bfm.reset()
    cvg = set()

    ops = list(Ops)
    for op in ops:
        aa = random.randint(0, 255)
        bb = random.randint(0, 255)
        await bfm.send_op(aa, bb, op)

        seen_cmd = await bfm.get_cmd()
        seen_op = await bfm.get_op()
        cvg.add(seen_op)

        result = await bfm.get_result()
        pr = alu_prediction(aa, bb, op)

        if result == pr:
            logger.debug(f"CMD {op.name} PASSED")
            passed = True
        else:
            logger.error(f"CMD {op.name} FAILED")
            passed = False
        
    assert passed, "Test Failed"
    
    