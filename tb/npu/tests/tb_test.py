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
class SimpleTest(uvm_test):
    """Simple NPU test"""

    def build_phase(self):
        self.env = NPUEnv('env', self)

    def end_of_elaboration_phase(self):
        self.custom_query = CustomQuerySeq.create("custom_query") 

    async def run_phase(self):
        self.raise_objection()

        csr_item = CSRSeqItem("csr_item")

        csr_item.matrix_setup(8, 8, 8, 8, 0x0, 0x100)

        csr_item.features_setup()

        weigths = [39, 12, 14, 6, 41, 9, 43, 33, 4, 24, 17, 42, 27, 32, 5, 15, 11, 49, 34, 27, 13, 9, 7, 20, 37, 28, 40, 20, 18, 19, 17, 20, 29, 4, 45, 19, 4, 16, 5, 23, 36, 8, 13, 38, 13, 47, 25, 27, 26, 34, 6, 47, 16, 33, 2, 13, 12, 8, 1, 24, 28, 4, 47, 50]

        inputs = [49, 44, 39, 44, 50, 35, 3, 43, 42, 8, 12, 46, 8, 40, 43, 12, 20, 29, 26, 2, 7, 18, 38, 0, 32, 21, 50, 23, 3, 48, 28, 34, 20, 20, 27, 24, 45, 19, 32, 4, 14, 3, 27, 13, 2, 31, 15, 36, 5, 35, 45, 19, 23, 2, 2, 18, 48, 2, 48, 41, 34, 37, 8, 16]

        bias = [5] * 8

        summ = [5] * 8

        mem_item = MemSeqItem("mem_item", weights=weigths, inputs=inputs, bias=bias, summ=summ)

        self.custom_query.csr_item = csr_item
        self.custom_query.mem_item = mem_item

        await self.custom_query.start()

        self.drop_objection()



