import cocotb
import pyuvm
import random
from pyuvm import *
from common.env import *
from common.sequences import *


@pyuvm.test()
class NPU32_MUL_Outbound(BaseTest):
    """Try to make multiplication with a size bigger than systolic array"""

    def end_of_elaboration_phase(self):
        self.csr_item = csr_item = CSRSeqItem("NPU32_csr_item")
        self.mem_item = MemSeqItem("NPU32_mem_item")
        self.query = BasicQuerySeq("NPU32_seq", self.mem_item, self.csr_item)

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

        inputs_rows = inputs_cols = weights_rows = weights_cols = 12

        # Using default value of systolic array size
        self.csr_item.matrix_setup(
            inputs_rows,
            inputs_cols,
            weights_rows, 
            weights_cols,
            base_addr=0x0,
            result_addr=1024
        )

        self.mem_item.randomize_inputs(inputs_rows, inputs_cols)
        self.mem_item.randomize_weights(weights_rows, weights_cols)

        self.logger.info(self.csr_item)

        await self.query.start()

        self.drop_objection()