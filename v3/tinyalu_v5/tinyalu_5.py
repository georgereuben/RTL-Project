from cocotb.triggers import FallingEdge 
import cocotb
import random
from pathlib import Path
parent_path = Path("..").resolve()
import sys
sys.path.insert(0, str(parent_path))
import logging
from tinyalu_utils import Ops, alu_prediction, logger, get_int, TinyAluBfm
import pyuvm
from pyuvm import *


class BaseTester(uvm_component):                         #base class for forgiveness dynamic typing

    def start_of_simulation_phase(self):
        TinyAluBfm().start_tasks()

    async def run_phase(self):
        self.raise_objection()
        self.bfm = TinyAluBfm()
        ops = list(Ops)
        for op in ops:
            aa, bb = self.get_operands()
            await self.bfm.send_op(aa, bb, op)
        #send two dummy operations to allow last real operation to complete
        await self.bfm.send_op(0,0,1)
        await self.bfm.send_op(0,0,1)
        self.drop_objection()

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

class ScoreBoard(uvm_component):
    
    async def get_cmd(self):
        while True:
            cmd = await self.bfm.get_cmd()
            self.cmds.append(cmd)
    
    async def get_result(self):
        while True:
            result = await self.bfm.get_result()
            self.results.append(result)
        
    def start_of_simulation_phase(self):
        self.bfm = TinyAluBfm()
        self.cmds = []
        self.results = []
        self.cvg = set()
        cocotb.start_soon(self.get_cmd())
        cocotb.start_soon(self.get_result())
    
    def check_phase(self):
        passed = True
        for cmd in self.cmds:
            aa, bb, op_int = cmd
            op = Ops(op_int)
            self.cvg.add(op)
            actual = self.results.pop(0)
            prediction = alu_prediction(aa, bb, op)
            if actual == prediction:
                self.logger.debug(f"PASS: {aa} {op} {bb} = {prediction}")
            else:
                self.logger.error(f"FAIL: {aa} {op} {bb} = {prediction} (got {actual})")
                passed = False
        if len(set(Ops) - self.cvg) > 0:
            self.logger.error(f"FUNCTIONAL COVERAGE FAILED: {set(Ops) - self.cvg} were not tested")
            passed = False
        else:
            self.logger.debug(f"FUNCTIONAL COVERAGE PASSED: All ops were tested")
        assert passed

class BaseEnv(uvm_env):
    
    def build_phase(self):
        self.scoreboard = ScoreBoard("scoreboard", self)

class RandomEnv(BaseEnv):
    """Generate random operands"""
    def build_phase(self):
        super().build_phase()
        self.tester = RandomTester("tester", self)
    
class MaxEnv(BaseEnv):
    """Generate max operands"""
    def build_phase(self):
        super().build_phase()
        self.tester = MaxTester("tester", self)

@pyuvm.test()
class RandomTest(uvm_test):
    """Run with random operations"""
    def build_phase(self):
        self.env = RandomEnv("env", self)

@pyuvm.test()
class MaxTest(uvm_test):
    """Run with max operations"""
    def build_phase(self):
        self.env = MaxEnv("env", self)

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
      