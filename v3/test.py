from logging import Logger
from threading import Timer
import cocotb
from cocotb.queue import Queue, QueueFull, QueueEmpty

async def Producer(queue, nn, delay=None):
    """Produce numbers from 1 to nn and send them"""
    for datum in range(1, nn+1):
        if delay is not None:
            await Timer(delay, units="ns")
        await queue.put(datum)
        Logger.info(f"Producer sent: {datum}")

async def Consumer(queue):
    """Consume numbers from the queue and print them to the log"""
    while True:
        datum = await queue.get()
        Logger.info(f"Consumer got: {datum}")

@cocotb.test()
async def infinite_queue(_):
    """Test an infinite queue"""
    queue = Queue()
    cocotb.start_soon(Consumer(queue))
    cocotb.start_soon(Producer(queue, 10))
    await Timer(100, units="ns")

def main():
    """Run the test"""
    cocotb.regression.TestFactory(infinite_queue).generate_tests()
    