import pyuvm
from pyuvm import *

from uvm.base.uvm_component import uvm_component_utils

class adder_interface(uvm_reg_block):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.a = uvm_reg('a', 4)
        self.b = uvm_reg('b', 4)
        self.sum = uvm_reg('sum', 4)

class adder_agent(uvm_agent):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.dut_if = adder_interface('dut_if', self)
        self.driver = adder_driver('driver', self)
        self.monitor = adder_monitor('monitor', self)
        self.scoreboard = adder_scoreboard('scoreboard', self)

class adder_driver(uvm_driver):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.agent = None

    def connect_phase(self, phase):
        self.agent = self.get_parent()
        self.seq_item_port.connect(self.agent.seq_item_export)

    def run_phase(self, phase):
        item = None
        while True:
            item = self.seq_item_port.get()
            if item is None:
                break
            # Drive the item to the DUT interface
            self.agent.dut_if.a.write(item.a)
            self.agent.dut_if.b.write(item.b)

class adder_monitor(uvm_monitor):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.agent = None

    def connect_phase(self, phase):
        self.agent = self.get_parent()
        self.agent.dut_if.a.add_callback(self.collect)
        self.agent.dut_if.b.add_callback(self.collect)

    def collect(self, reg):
        item = adder_transaction()
        item.a = self.agent.dut_if.a.read()
        item.b = self.agent.dut_if.b.read()
        item.sum = self.agent.dut_if.sum.read()
        self.item_collected_port.put(item)

class adder_scoreboard(uvm_scoreboard):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.agent = None

    def connect_phase(self, phase):
        self.agent = self.get_parent()
        self.driver_seq_export.connect(self.agent.driver.seq_item_export)
        self.monitor_seq_export.connect(self.agent.monitor.item_collected_port)

    def compare(self, txn1, txn2):
        if txn1.sum != (txn1.a + txn1.b):
            self.error("Sum mismatch")

class adder_sequence(uvm_sequence):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.item = adder_transaction()

    def body(self):
        for i in range(16):
            self.item.a = i % 16
            self.item.b = (i // 2) % 16
            self.start_item(self.item)
            self.finish_item(self.item)

class adder_transaction(uvm_sequence_item):
    def __init__(self):
        super().__init__()
        self.a = 0
        self.b = 0
        self.sum = 0

class adder_test(uvm_test):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.sequence = adder_sequence('sequence', self)

    def build_phase(self, phase):
        self.agent = adder_agent('agent', self)

    def connect_phase(self, phase):
        self.agent.seq_item_export.connect(self.sequence.seq_item_port)
    
    def run_phase(self, phase):
        self.start_tr(self.sequence)
        self.wait_for_sequence_state(UVM_SEQUENCE_DONE)

class adder_env(uvm_env):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.test = adder_test('test', self)

uvm_component_utils(adder_interface)
uvm_component_utils(adder_agent)
uvm_component_utils(adder_driver)
uvm_component_utils(adder_monitor)
uvm_component_utils(adder_scoreboard)
uvm_component_utils(adder_sequence)
uvm_component_utils(adder_transaction)
uvm_component_utils(adder_test)
uvm_component_utils(adder_env)



