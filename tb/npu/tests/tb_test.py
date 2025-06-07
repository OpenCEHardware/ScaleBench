import cocotb
import pyuvm
import logging
from pyuvm import *
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from common.env import *


@pyuvm.test()
class Test(uvm_test):
    """Simple test for ScaleNPU"""

    def build_phase(self):
        self.env = NPUEnv('env', self)
        self.dut = cocotb.top

        ConfigDB().set(self.env, "", "dut", self.dut)

    async def run_phase(self):
        self.raise_objection()

        await RisingEdge(self.dut.rst_n)

        reg_block = self.env.csr_agent.reg_block
        resp, data = await reg_block.ARCHID.read(reg_block.def_map, path_t.FRONTDOOR, check_t.NO_CHECK)
        assert (resp, data) == (status_t.IS_OK, 0xb00b)

        await ClockCycles(cocotb.top.clk_npu, 10)

        self.drop_objection()
