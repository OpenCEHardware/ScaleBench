import cocotb
import pyuvm
import logging
import random
from pyuvm import *
from common.env import *
from common.sequences import *


@pyuvm.test()
class NPU06_MUL_ZeroSize(BaseTest):
    """Edge case test with empty matrices"""

    def end_of_elaboration_phase(self):
        self.csr_item = csr_item = CSRSeqItem("NPU06_csr_item")
        self.mem_item = MemSeqItem("NPU06_mem_item")
        self.query = BasicQuerySeq("NPU06_seq", self.mem_item, self.csr_item)

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

        inputs_rows = 0
        inputs_cols = 0
        weights_rows = 0
        weights_cols = 0

        # Using default value of systolic array size
        self.csr_item.matrix_setup(
            inputs_rows, 
            inputs_cols, 
            weights_rows, 
            weights_cols, 
            base_addr=0x0, 
            result_addr=1024
        )

        await self.query.start()

        self.drop_objection()

