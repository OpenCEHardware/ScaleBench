import cocotb
import pyuvm
import logging
from pyuvm import *
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from common.env import *
from common.sequences import *


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

        mem_seq = MemorySequence(mem=self.env.mem, ar_fifo=self.env.mem_ar_fifo, aw_fifo=self.env.mem_aw_fifo, w_fifo=self.env.mem_w_fifo)
        cocotb.start_soon(mem_seq.start(self.env.mem_agent.seqr))

        reg_block = self.env.csr_agent.reg_block
        resp, data = await reg_block.ARCHID.read(reg_block.def_map, path_t.FRONTDOOR, check_t.NO_CHECK)
        assert (resp, data) == (status_t.IS_OK, 0xb00b)

        await self.reg_write(reg_block.INROWS, 2)
        await self.reg_write(reg_block.INCOLS, 2)
        await self.reg_write(reg_block.WGHTROWS, 2)
        await self.reg_write(reg_block.WGHTCOLS, 2)
        await self.reg_write(reg_block.REINPUTS, 0)
        await self.reg_write(reg_block.REWEIGHTS, 0)
        await self.reg_write(reg_block.SAVEOUT, 1)
        await self.reg_write(reg_block.USEBIAS, 0)
        await self.reg_write(reg_block.USESUMM, 0)
        await self.reg_write(reg_block.SHIFTAMT, 0)
        await self.reg_write(reg_block.ACTFN, 0)

        await self.reg_write(reg_block.BASE,   0x0000_0000)
        await self.reg_write(reg_block.RESULT, 0x0000_0100)

        await self.reg_write(reg_block.INIT, 1)

        await ClockCycles(cocotb.top.clk_npu, 50000)

        self.drop_objection()

    async def reg_write(self, reg, value):
        resp = await reg.write(value, self.env.csr_agent.reg_block.def_map, path_t.FRONTDOOR, check_t.NO_CHECK)
        assert resp == status_t.IS_OK
