import cocotb
import pyuvm
import random
from pyuvm import *
from common.env import *
from common.sequences import *


@pyuvm.test()
class NPU24_MULSHFT_Random_Smax(BaseTest):
    """Validate loss of precision"""

    def end_of_elaboration_phase(self):
        self.csr_item = csr_item = CSRSeqItem("NPU24_csr_item")
        self.mem_item = MemSeqItem("NPU24_mem_item")
        self.query = BasicQuerySeq("NPU24_seq", self.mem_item, self.csr_item)

    async def run_phase(self):
        self.raise_objection()

        self.csr_item.features_setup(
            reinputs=False,
            saveout=True, 
            # The DUT does not support disabling of BIAS and SUMM at the same time.
            usebias=True,
            usesumm=False,
            shift_amount=32,
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

        for idx in range(10):

            self.logger.info(f"ITERATION: {idx}")

            self.mem_item.randomize_inputs(inputs_rows, inputs_cols, -255, 255)
            self.mem_item.randomize_weights(weights_rows, weights_cols, -255, 255)

            self.logger.info(self.mem_item)

            await self.query.start()

        self.drop_objection()