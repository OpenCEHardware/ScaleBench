import cocotb
import pyuvm
import logging
import random
from pyuvm import *
from common.env import *
from common.sequences import *


@pyuvm.test()
class NPU04_MUL_Identity(BaseTest):
    """Should reproduce the original matrix"""

    def end_of_elaboration_phase(self):
        self.csr_item = csr_item = CSRSeqItem("NPU04_csr_item")
        self.mem_item = MemSeqItem("NPU04_mem_item")
        self.query = BasicQuerySeq("NPU04_seq", self.mem_item, self.csr_item)

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

        weights_matrix = [
            1 if i == j else 0 for j in range(weights_cols)
            for i in range(weights_rows)
        ]


        self.mem_item.randomize_inputs(inputs_rows, inputs_cols)

        self.mem_item.weights = weights_matrix

        await self.query.start()

        self.drop_objection()

