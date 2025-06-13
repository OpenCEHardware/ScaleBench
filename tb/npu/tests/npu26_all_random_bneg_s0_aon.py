import cocotb
import pyuvm
import random
from pyuvm import *
from common.env import *
from common.sequences import *


@pyuvm.test()
class NPU26_ALL_Random_Bneg_S0_Aon(BaseTest):
    """Force positive output from null input"""

    def end_of_elaboration_phase(self):
        self.csr_item = csr_item = CSRSeqItem("NPU26_csr_item")
        self.mem_item = MemSeqItem("NPU26_mem_item")
        self.query = BasicQuerySeq("NPU26_seq", self.mem_item, self.csr_item)

    async def run_phase(self):
        self.raise_objection()

        self.csr_item.features_setup(
            reinputs=False,
            saveout=True, 
            # The DUT does not support disabling of BIAS and SUMM at the same time.
            usebias=True,
            usesumm=False,
            shift_amount=0,
            activation_function=True,
            reweights=False
        )

        inputs_rows = inputs_cols = weights_rows = weights_cols = 8

        for idx in range(10):

            self.logger.info(f"ITERATION: {idx}")

            # Using default value of systolic array size
            self.csr_item.matrix_setup(
                inputs_rows,
                inputs_cols,
                weights_rows, 
                weights_cols,
                base_addr=0x0,
                result_addr=1024
            )

            self.mem_item.randomize_inputs(inputs_rows, inputs_cols, 0, 255)
            self.mem_item.randomize_weights(weights_rows, weights_cols, 0, 255)
            self.mem_item.randomize_bias(inputs_cols, -10000, -1)

            self.logger.info(self.mem_item)

            await self.query.start()

        self.drop_objection()