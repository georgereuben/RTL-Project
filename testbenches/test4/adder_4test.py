import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer
import pyuvm
from pyuvm import *



@pyuvm.test()
class test(uvm_test):
    
    async def run_phase(self):
        self.raise_objection()
        await Timer(1000, units='ns')
        print("Hello World!")
        await Timer(1000, units='ns')
        self.logger.info("Hi all! Welcome to the python Version")
        await Timer(1000, units='ns')

uvm_root().run_test("test")    