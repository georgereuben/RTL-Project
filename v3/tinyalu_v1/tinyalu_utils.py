import cocotb
from cocotb.triggers import FallingEdge
from cocotb.queue import QueueEmpty, Queue
import enum
import logging

from pyuvm import utility_classes

logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class GreenFormatter(logging.Formatter):
    GREEN = "\033[32m"
    RESET = "\033[0m"
    YELLOW = "\033[33m"
    ORANGE = "\033[38;5;208m"

    def format(self, record):
        if record.levelno == logging.DEBUG:
            record.msg = f"{self.GREEN}{record.msg}{self.RESET}"
        if record.levelno == logging.WARNING:
            record.msg = f"{self.YELLOW}{record.msg}{self.RESET}"
        return super().format(record)

handler = logging.StreamHandler()
formatter = GreenFormatter(fmt="%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)
logger.addHandler(handler)

@enum.unique
class Ops(enum.IntEnum):
    """Legal ops for the TinyALU"""
    ADD = 1
    AND = 2
    XOR = 3
    MUL = 4


def alu_prediction(A, B, op, error=False):
    """Python model of the TinyALU"""
    assert isinstance(op, Ops), "The tinyalu op must be of type Ops"
    if op == Ops.ADD:
        result = A + B
    elif op == Ops.AND:
        result = A & B
    elif op == Ops.XOR:
        result = A ^ B
    elif op == Ops.MUL:
        result = A * B
    if error:
        result = result + 1
    return result


def get_int(signal):
    try:
        sig = int(signal.value)
    except ValueError:
        sig = 0
    return sig


class TinyAluBfm(metaclass=utility_classes.Singleton):
    def __init__(self):
        self.dut = cocotb.top
        self.driver_queue = Queue(maxsize=1)
        self.cmd_mon_queue = Queue(maxsize=0)           #maxsize zero means infinitely large
        self.result_mon_queue = Queue(maxsize=0)

    async def send_op(self, aa, bb, op):
        command_tuple = (aa, bb, op)
        await self.driver_queue.put(command_tuple)

    async def get_cmd(self):
        cmd = await self.cmd_mon_queue.get()
        return cmd

    async def get_result(self):
        result = await self.result_mon_queue.get()
        return result

    async def reset(self):
        await FallingEdge(self.dut.clk)
        self.dut.reset.value = 0
        self.dut.A.value = 0
        self.dut.B.value = 0
        self.dut.op.value = 0
        await FallingEdge(self.dut.clk)
        self.dut.reset.value = 1
        await FallingEdge(self.dut.clk)

    async def cmd_driver(self):
        self.dut.start.value = 0
        self.dut.A.value = 0
        self.dut.B.value = 0
        self.dut.op.value = 0
        while True:
            await FallingEdge(self.dut.clk)
            start = get_int(self.dut.start)
            done = get_int(self.dut.done)
            if start == 0 and done == 0:
                try:
                    (aa, bb, op) = self.driver_queue.get_nowait()
                    self.dut.A.value = aa
                    self.dut.B.value = bb
                    self.dut.op.value = op
                    self.dut.start.value = 1
                except QueueEmpty:
                    pass
            elif start == 1:
                if done == 1:
                    self.dut.start.value = 0

    async def cmd_mon(self):
        prev_start = 0
        while True:
            await FallingEdge(self.dut.clk)
            start = get_int(self.dut.start)
            if start == 1 and prev_start == 0:
                cmd_tuple = (get_int(self.dut.A),
                             get_int(self.dut.B),
                             get_int(self.dut.op))
                self.cmd_mon_queue.put_nowait(cmd_tuple)
            prev_start = start

    async def result_mon(self):
        prev_done = 0
        while True:
            await FallingEdge(self.dut.clk)
            done = get_int(self.dut.done)
            if prev_done == 0 and done == 1:
                result = get_int(self.dut.result)
                self.result_mon_queue.put_nowait(result)
            prev_done = done

    def start_tasks(self):
        cocotb.start_soon(self.cmd_driver())
        cocotb.start_soon(self.cmd_mon())
        cocotb.start_soon(self.result_mon())
