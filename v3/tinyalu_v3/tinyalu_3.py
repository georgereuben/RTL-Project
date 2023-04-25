from cocotb.triggers import FallingEdge 
import cocotb
import random
from pathlib import Path
parent_path = Path("..").resolve()
import sys
sys.path.insert(0, str(parent_path))
import logging
from tinyalu_utils import Ops, alu_prediction, logger, get_int, TinyAluBfm

class BaseTester():                         #base class for forgiveness dynamic typing

    async def execute(self):
        self.bfm = TinyAluBfm()
        ops = list(Ops)
        for op in ops:
            aa, bb = self.get_operands()
            await self.bfm.send_op(aa, bb, op)
        await self.bfm.send_op(0,0,1)
        await self.bfm.send_op(0,0,1)

class RandomTester(BaseTester):
    
    def get_operands(self):
        aa = random.randint(0, 255)
        bb = random.randint(0, 255)
        return aa, bb
        
class MaxTester(BaseTester):
        
    def get_operands(self):
        aa = 0xff
        bb = 0xff
        return aa, bb

class ScoreBoard():
    def __init__(self):
        self.bfm = TinyAluBfm()
        self.cmds = []
        self.results = []
        self.cvg = set()

    async def get_cmd(self):
        while True:
            cmd = await self.bfm.get_cmd()
            self.cmds.append(cmd)
    
    async def get_result(self):
        while True:
            result = await self.bfm.get_result()
            self.results.append(result)
    
    def start_tasks(self):
        cocotb.start_soon(self.get_cmd())
        cocotb.start_soon(self.get_result())

    def check_results(self):
        passed = True
        for cmd in self.cmds:
            aa, bb, op_int = cmd
            op = Ops(op_int)
            self.cvg.add(op)
            actual = self.results.pop(0)
            predictions = alu_prediction(aa, bb, op)
            if actual == predictions:
                logger.debug(f"CMD {op.name} PASSED")
            else:
                logger.error(f"CMD {op.name} FAILED: {aa} {op} {bb} = {actual}, but predicted {predictions}")
                passed = False  
        if len(set(Ops) - self.cvg) > 0:
            logger.error(f"FUNCTIONAL COVERAGE FAILED: Did not test all ops, missing {set(Ops) - self.cvg}")
            passed = False
        else:
            logger.debug(f"FUNCTIONAL COVERAGE PASSED: Tested all ops")
        return passed
    
async def execute_test(tester_class):
    bfm = TinyAluBfm()
    scoreboard = ScoreBoard()
    await bfm.reset()
    bfm.start_tasks()
    scoreboard.start_tasks()
    tester = tester_class()
    await tester.execute()
    passed = scoreboard.check_results()
    return passed

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

    passed = await execute_test(RandomTester)
    assert passed, "Random test failed"