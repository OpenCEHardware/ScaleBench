import cocotb
import pyuvm
import random
from pyuvm import *
from common.env import *
from common.sequences import *


@pyuvm.test()
class NPU30_All_Ramdon_Summs(BaseTest):
    """Randomize with all enabled"""

    def end_of_elaboration_phase(self):
        self.csr_item = csr_item = CSRSeqItem("NPU30_csr_item")
        self.mem_item = MemSeqItem("NPU30_mem_item")
        self.query = BasicQuerySeq("NPU30_seq", self.mem_item, self.csr_item)

    async def run_phase(self):
        self.raise_objection()

        for idx in range(10):

            self.logger.info(f"ITERATION: {idx}")

            self.csr_item.features_setup(
                reinputs=False,
                saveout=True, 
                # The DUT does not support disabling of BIAS and SUMM at the same time.
                usebias=True,
                usesumm=True,
                shift_amount=random.randint(-32, 32),
                activation_function=True,
                reweights=False
            )

            inputs_rows = random.randrange(2, 9, 2)
            inputs_cols = weights_rows = random.randrange(2, 9, 2)
            weights_cols = random.randrange(2, 9, 2)

            # Using default value of systolic array size
            self.csr_item.matrix_setup(
                inputs_rows,
                inputs_cols,
                weights_rows, 
                weights_cols,
                base_addr=0x0,
                result_addr=1024
            )

            self.mem_item.randomize_inputs(inputs_rows, inputs_cols, -255, 255)

            self.mem_item.randomize_weights(weights_rows, weights_cols, -255, 255)

            self.mem_item.randomize_bias(inputs_cols, -2**31, 2**31 - 1)
            self.mem_item.randomize_summs(inputs_cols, -2**31, 2**31 - 1)
            
            self.logger.info(self.csr_item)
            self.logger.info(self.mem_item)

            await self.query.start()

        self.drop_objection()