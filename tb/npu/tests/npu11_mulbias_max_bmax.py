import cocotb
import pyuvm
import random
from pyuvm import *
from common.env import *
from common.sequences import *


@pyuvm.test()
class NPU11_MULBIAS_Max_Bmax(BaseTest):
    """Check saturation due to large sum"""

    def end_of_elaboration_phase(self):
        self.csr_item = csr_item = CSRSeqItem("NPU10_csr_item")
        self.mem_item = MemSeqItem("NPU10_mem_item")
        self.query = BasicQuerySeq("NPU10_seq", self.mem_item, self.csr_item)

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

        self.mem_item.inputs = [63] * inputs_cols * inputs_rows
        self.mem_item.weights = [63] * weights_cols * weights_rows
        self.mem_item.bias = [1000] * inputs_cols

        await self.query.start()

        self.drop_objection()