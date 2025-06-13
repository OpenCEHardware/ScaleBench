import cocotb
import pyuvm
import logging
import random
from pyuvm import *
from common.env import *
from common.sequences import *


@pyuvm.test()
class NPU03_MUL_Special(BaseTest):
    """Evaluate behavior on constant patterns"""

    def end_of_elaboration_phase(self):
        self.csr_item = csr_item = CSRSeqItem("NPU03_csr_item")
        self.mem_item = MemSeqItem("NPU03_mem_item")
        self.query = BasicQuerySeq("NPU03_seq", self.mem_item, self.csr_item)

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

        pattern_alternating = [
            0 if (i + j) % 2 == 0 else random.randint(0, 255)
            for i in range(inputs_rows) for j in range(inputs_cols)
        ]

        pattern_ramp = [
            i * 8 + j + 1
            for i in range(weights_rows) for j in range(weights_cols)
        ]


        self.mem_item.inputs = pattern_alternating

        self.mem_item.weights = pattern_ramp

        await self.query.start()

        self.drop_objection()
