import cocotb
import pyuvm
import logging
import random
from pyuvm import *
from common.env import *
from common.sequences import *


@pyuvm.test()
class NPU02_MUL_Max(BaseTest):
    """Check potential overflow without bias"""

    def end_of_elaboration_phase(self):
        self.csr_item = csr_item = CSRSeqItem("NPU02_csr_item")
        self.mem_item = MemSeqItem("NPU02_mem_item", 0, 0)
        self.query = BasicQuerySeq("NPU02_seq", self.mem_item, self.csr_item)

    async def run_phase(self):
        self.raise_objection()

        self.csr_item.features_setup(
            reinputs=False,
            saveout=True, 
            # The DUT does not support disabling of BIAS and SUMM at the same time.
            usebias=True,
            usesumm=True,
            shift_amount=0,
            activation_function=False,
            reweights=False
        )

        inputs_rows = 8
        inputs_cols = 8
        weights_rows = 8
        weights_cols = 8

        # Using default value of systolic array size
        self.csr_item.matrix_setup(
            inputs_rows, 
            inputs_cols, 
            weights_rows, 
            weights_cols, 
            base_addr=0x0, 
            result_addr=1024
        )

        self.mem_item.inputs = [254] * inputs_cols * inputs_rows

        self.mem_item.weights = [254] * inputs_cols * inputs_rows

        await self.query.start()

        self.drop_objection()
