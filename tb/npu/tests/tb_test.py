import cocotb
import pyuvm
import logging
from pyuvm import *
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from common.env import *
from common.sequences import *


def generate_random_matrix(rows, cols, min_val=0, max_val=255):
    matrix = []
    for _ in range(rows):
        row = [random.randint(min_val, max_val) for _ in range(cols)]
        matrix.extend(row)
    return matrix


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

        data = await self.reg_read(reg_block.ARCHID)

        self.env.mem.write_mem(0x0000_0000, 2)
        self.env.mem.write_mem(0x0000_0002, 2)
        self.env.mem.write_mem(0x0000_0004, 2)
        self.env.mem.write_mem(0x0000_0006, 2)

        self.env.mem.write_mem(0x0000_0008, 2)
        self.env.mem.write_mem(0x0000_0010, 2)
        self.env.mem.write_mem(0x0000_0012, 2)
        self.env.mem.write_mem(0x0000_0014, 2)

        await self.reg_write(reg_block.INROWS, 2)
        await self.reg_write(reg_block.INCOLS, 2)
        await self.reg_write(reg_block.WGHTROWS, 2)
        await self.reg_write(reg_block.WGHTCOLS, 2)
        await self.reg_write(reg_block.REINPUTS, 0)
        await self.reg_write(reg_block.REWEIGHTS, 0)
        await self.reg_write(reg_block.SAVEOUT, 1)
        await self.reg_write(reg_block.USEBIAS, 1)
        await self.reg_write(reg_block.USESUMM, 0)
        await self.reg_write(reg_block.SHIFTAMT, 0)
        await self.reg_write(reg_block.ACTFN, 0)

        await self.reg_write(reg_block.BASE,   0x0000_0000)
        await self.reg_write(reg_block.RESULT, 0x0000_0100)

        await self.reg_read(reg_block.INROWS)
        await self.reg_read(reg_block.INCOLS)
        await self.reg_read(reg_block.WGHTROWS)

        await self.reg_write(reg_block.INIT, 1)

        await ClockCycles(cocotb.top.clk_npu, 1000)

        self.drop_objection()

    async def reg_write(self, reg, value):
        resp = await reg.write(value, self.env.csr_agent.reg_block.def_map, path_t.FRONTDOOR, check_t.NO_CHECK)
        assert resp == status_t.IS_OK
    
    async def reg_read(self, reg):
        resp, data = await reg.read(self.env.csr_agent.reg_block.def_map, path_t.FRONTDOOR, check_t.NO_CHECK)

        assert resp == status_t.IS_OK

        return data
