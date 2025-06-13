import cocotb
import pyuvm
import random
from pyuvm import *
from common.env import *
from common.sequences import *


@pyuvm.test()
class NPU20_MULSHFT_Zeros_Smax(BaseTest):
    """Extreme shift on zero input, no visible change"""

    def end_of_elaboration_phase(self):
        self.csr_item = csr_item = CSRSeqItem("NPU20_csr_item")
        self.mem_item = MemSeqItem("NPU20_mem_item")
        self.query = BasicQuerySeq("NPU20_seq", self.mem_item, self.csr_item)

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

        self.mem_item.randomize_inputs(inputs_rows, inputs_cols, 0, 0)
        self.mem_item.randomize_weights(weights_rows, weights_cols, 0, 0)

        self.logger.info(self.mem_item)

        await self.query.start()

        self.drop_objection()