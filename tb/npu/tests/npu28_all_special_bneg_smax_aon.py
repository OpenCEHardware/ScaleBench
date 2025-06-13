import cocotb
import pyuvm
import random
from pyuvm import *
from common.env import *
from common.sequences import *


@pyuvm.test()
class NPU28_ALL_Special_Bneg_Smax_Aon(BaseTest):
    """Observe propagation of error over structure"""

    def end_of_elaboration_phase(self):
        self.csr_item = csr_item = CSRSeqItem("NPU28_csr_item")
        self.mem_item = MemSeqItem("NPU28_mem_item")
        self.query = BasicQuerySeq("NPU28_seq", self.mem_item, self.csr_item)

    async def run_phase(self):
        self.raise_objection()

        self.csr_item.features_setup(
            reinputs=False,
            saveout=True, 
            # The DUT does not support disabling of BIAS and SUMM at the same time.
            usebias=True,
            usesumm=False,
            shift_amount=32,
            activation_function=True,
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

        self.mem_item.randomize_bias(inputs_cols, -10000, -1)

        self.logger.info(self.mem_item)

        await self.query.start()

        self.drop_objection()