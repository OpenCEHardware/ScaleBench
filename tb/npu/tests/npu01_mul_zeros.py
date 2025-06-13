import cocotb
import pyuvm
import logging
import random
from pyuvm import *
from common.env import *
from common.sequences import *


@pyuvm.test()
class NPU01_MUL_Zeros(BaseTest):
    """Verify zero output with null inputs"""

    def end_of_elaboration_phase(self):
        self.csr_item = csr_item = CSRSeqItem("NPU01_csr_item")
        # Using an empty item to test case of complete clean memory
        self.mem_item = MemSeqItem("NPU01_mem_item", 0, 0)
        self.query = BasicQuerySeq("NPU01_seq", self.mem_item, self.csr_item)

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

        # Using default value of systolic array size
        self.csr_item.matrix_setup(
            inputs_rows=8, 
            inputs_cols=8, 
            weights_rows=8, 
            weights_cols=8, 
            base_addr=0x0, 
            result_addr=0x200
        )

        await self.query.start()

        self.drop_objection()
