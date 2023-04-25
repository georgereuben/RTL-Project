import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, Timer

import uvm

class Adder4Testbench(uvm.Testbench):
    def build_phase(self, phase):
        self.add_config(self, uvm.ConfigDb().get(None, "", "add_config"))

    def connect_phase(self, phase):
        self.dut = uvm_port_proxy("dut", self)
        self.agent = self.env.agent

class Adder4Driver(uvm.Driver):
    async def run_phase(self, phase):
        for i in range(2):
            await self.send_packet({'a': 1, 'b': 1, 'cin': 0})
            await self.send_packet({'a': 3, 'b': 4, 'cin': 1})

class Adder4Monitor(uvm.UVMMonitor):
    async def run_phase(self, phase):
        while True:
            await RisingEdge(self.dut.clock)
            a = self.dut.a.value.integer
            b = self.dut.b.value.integer
            cin = self.dut.cin.value.integer
            sum = self.dut.sum.value.integer
            cout = self.dut.cout.value.integer
            uvm_info("Adder4Monitor", f"a={a}, b={b}, cin={cin}, sum={sum}, cout={cout}", UVM_LOW)

class Adder4Scoreboard(uvm.UVMScoreboard):
    async def compare_phase(self, phase):
        pass

class Adder4Agent(uvm.UVMAgent):
    def build_phase(self, phase):
        self.config = self.get_config()
        self.driver = Adder4Driver("driver", self)
        self.monitor = Adder4Monitor("monitor", self)
        self.scoreboard = Adder4Scoreboard("scoreboard", self)
        self.add_subscriber(self.monitor)

    def connect_phase(self, phase):
        self.driver.item_port.connect(self.config.analysis_export)
        self.config.analysis_export.connect(self.scoreboard.analysis_export)

    def get_config(self):
        config = uvm.UVMConfigDb.get(self, "", "add_config")
        if config is None:
            config = uvm.UVMConfigDb()
            config.set(None, "", "add_config", uvm.uvm_object_wrapper(None))
        return config

class Adder4Test(uvm.UVMTest):
    def build_phase(self, phase):
        self.agent = Adder4Agent("adder_agent", self)
        self.testbench = Adder4Testbench("adder_testbench", self)

    def connect_phase(self, phase):
        self.agent.item_collector_port.connect
        self.testbench.dut.a.connect(self.agent.driver.export_fifo.analysis_export)
        self.testbench.dut.b.connect(self.agent.driver.export_fifo.analysis_export)
        self.testbench.dut.cin.connect(self.agent.driver.export_fifo.analysis_export)
        self.agent.scoreboard.expected_export.connect(self.testbench.dut.sum)
        self.agent.scoreboard.expected_cout_export.connect(self.testbench.dut.cout)
   
class Adder4Env(uvm.UVMEnv):
    def build_phase(self, phase):
        self.add_config(self, uvm.ConfigDb().get(None, "", "add_config"))
        self.agent = self.create_agent("Adder4Agent", None)
   
@cocotb.test()
async def adder4_test(dut):
    env = Adder4Env("Adder4Env", None)
    test = Adder4Test("Adder4Test", None)
    test.set_starting_phase(env.build_phase)
    await run_test()      