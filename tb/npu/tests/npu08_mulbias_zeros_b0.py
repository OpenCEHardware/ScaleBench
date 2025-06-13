import cocotb
import pyuvm
import logging
import random
from pyuvm import *
from common.env import *
from common.sequences import *


@pyuvm.test()
class NPU08_MULBIAS_Zeros_B0(BaseTest):
    """Verify that bias = 0 has no effect"""

    def end_of_elaboration_phase(self):
        self.csr_item = csr_item = CSRSeqItem("NPU08_csr_item")
        self.mem_item = MemSeqItem("NPU08_mem_item")
        self.query = BasicQuerySeq("NPU08_seq", self.mem_item, self.csr_item)

    async def run_phase(self):
        self.raise_objection()

        self.csr_item.features_setup(
            reinputs=False,
            saveout=True, 
            # The DUT does not support disabling of BIAS and SUMM at the same time.
            usebias=True,
            usesumm=False,
            shift_amount=0,
            activation_function=False,
            reweights=False
        )

        inputs_rows = inputs_cols = weights_rows = weights_cols = 8

        # Using default value of systolic array size
        self.csr_item.matrix_setup(
            inputs_rows, 
            inputs_cols,
            weights_rows, 
            weights_cols, 
            base_addr=0x0, 
            result_addr=1024
        )

        self.mem_item.inputs = [0] * inputs_cols * inputs_rows
        self.mem_item.weights = [0] * weights_cols * weights_rows
        self.mem_item.bias = [0] * inputs_cols

        self.logger.info(self.csr_item)
        self.logger.info(self.mem_item)

        await self.query.start()

        self.drop_objection()

