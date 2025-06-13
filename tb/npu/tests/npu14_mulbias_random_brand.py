import cocotb
import pyuvm
import random
from pyuvm import *
from common.env import *
from common.sequences import *


@pyuvm.test()
class NPU14_MULBIAS_Random_B0(BaseTest):
    """Confirm bias acccuracy with random data"""

    def end_of_elaboration_phase(self):
        self.csr_item = csr_item = CSRSeqItem("NPU14_csr_item")
        self.mem_item = MemSeqItem("NPU14_mem_item")
        self.query = BasicQuerySeq("NPU14_seq", self.mem_item, self.csr_item)

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

        self.mem_item.randomize_inputs(inputs_rows, inputs_cols)
        self.mem_item.randomize_weights(weights_rows, weights_cols)
        self.mem_item.bias = [random.randint(-0x7FFFFFFF, 0x7FFFFFFF) for _ in range(inputs_cols)]

        await self.query.start()

        self.drop_objection()