import cocotb
import pyuvm
import logging
from pyuvm import *
from cocotb.clock import Clock
from interfaces import *
from cocotb.triggers import ClockCycles, FallingEdge, RisingEdge, ReadOnly, NextTimeStep
from cocotb_bus.drivers.amba import AXI4LiteMaster

@pyuvm.test()
class Test(uvm_test):
    """Simple test for ScaleNPU"""

    async def run_phase(self):
        self.raise_objection()

        clock = Clock(cocotb.top.clk_npu, 10, units="ns")
        cocotb.start_soon(clock.start())

        cocotb.top.rst_n.value = 0
        await ClockCycles(cocotb.top.clk_npu, 5)
        cocotb.top.rst_n.value = 1

        self.if_csr = AXI4LiteController()

        data = await self.if_csr.read_data(4)

        print(data)

        self.drop_objection()

