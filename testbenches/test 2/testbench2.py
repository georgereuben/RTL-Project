import pyuvm
from pyuvm import *

# Define the interface for our adder
class adder_interface(uvm_ap_intf):
    def __init__(self, name="adder_interface"):
        super().__init__(name)

        # Define the input/output ports
        self.in1 = uvm_ap_port("in1", UVM_ALL_ON)
        self.in2 = uvm_ap_port("in2", UVM_ALL_ON)
        self.out = uvm_ap_port("out", UVM_ALL_ON)

# Define the sequence item for our adder
class adder_transaction(uvm_sequence_item):
    def __init__(self, name="adder_transaction"):
        super().__init__(name)

        # Define the fields of the transaction
        self.in1 = uvm_reg_field("in1", 4, 0)
        self.in2 = uvm_reg_field("in2", 4, 0)
        self.out = uvm_reg_field("out", 5, 0)

# Define the sequence for our adder
class adder_sequence(uvm_sequence):
    def __init__(self, name="adder_sequence"):
        super().__init__(name)
        self.item = None

    async def body(self):
        self.item = adder_transaction()
        for i in range(16):
            self.item.in1 = i // 2
            self.item.in2 = i % 2
            await self.start_item(self.item)
            await self.finish_item(self.item)

# Define the driver for our adder
class adder_driver(uvm_driver):
    def __init__(self, name="adder_driver"):
        super().__init__(name)

    async def run_phase(self, phase):
        item = None
        while True:
            item = await self.get_next_item()
            if item is None:
                break
            # Drive the input signals
            await self.ap.write(item.in1, 0)
            await self.ap.write(item.in2, 1)
            # Wait for some time to simulate signal propagation delay
            await Timer(1, 'NS')
            # Read the output signal
            out_val = await self.ap.read(item.out)
            # Compare the expected and actual output values
            expected_out = item.in1 + item.in2
            if out_val != expected_out:
                self.uvm_report_error(self.get_name(), f"Output mismatch: expected {expected_out}, got {out_val}")
            # Finish the item
            await self.item_done()

# Define the monitor for our adder
class adder_monitor(uvm_monitor):
    def __init__(self, name="adder_monitor"):
        super().__init__(name)

    async def run_phase(self, phase):
        item = adder_transaction()
        while True:
            # Wait for the input signals to change
            await self.ap.wait_for_change((item.in1, item.in2))
            # Sample the input signals
            item.in1 = await self.ap.read(item.in1)
            item.in2 = await self.ap.read(item.in2)
            # Sample the output signal
            item.out = await