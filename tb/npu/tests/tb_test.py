import cocotb
import pyuvm
import logging
import random
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

        data = await self.reg_read(reg_block.ARCHID)

        base = 0x0000_0000
        input_cols = 8
        input_rows = 8
        weight_cols = 8
        weight_rows = 8

        def generate_random_weights_matrix(rows, cols, min_val=0, max_val=255):
            for i in range(rows):
                for j in range(cols):
                    data = random.randint(min_val, max_val)
                    self.logger.info(f"WEIGTHS[{i}][{j}]: {data}")
                    self.env.mem.write_weight(base, i, j, data, weight_rows, weight_cols)
        

        def generate_random_input_matrix(rows, cols, min_val=0, max_val=255):
            for i in range(rows):
                for j in range(cols):
                    data = random.randint(min_val, max_val)
                    self.logger.info(f"INPUTS[{i}][{j}]: {data}")
                    self.env.mem.write_input(base, i, j, data, weight_rows, weight_cols, input_cols)

        generate_random_weights_matrix(8, 8, max_val=69)
        generate_random_input_matrix(8, 8, max_val=69)



        await self.reg_write(reg_block.INROWS, input_rows)
        await self.reg_write(reg_block.INCOLS, input_cols)
        await self.reg_write(reg_block.WGHTROWS, weight_rows)
        await self.reg_write(reg_block.WGHTCOLS, weight_cols)
        await self.reg_write(reg_block.REINPUTS, 0)
        await self.reg_write(reg_block.REWEIGHTS, 0)
        await self.reg_write(reg_block.SAVEOUT, 1)
        await self.reg_write(reg_block.USEBIAS, 1)
        await self.reg_write(reg_block.USESUMM, 1)
        await self.reg_write(reg_block.SHIFTAMT, 0)
        await self.reg_write(reg_block.ACTFN, 1)

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
