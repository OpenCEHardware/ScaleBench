import cocotb
import pyuvm
import random
from pyuvm import *
from common.env import *
from common.sequences import *


@pyuvm.test()
class NPU29_All_Ramdon_Brand_Srand_Arand(BaseTest):
    """Randomize with all enabled"""

    def end_of_elaboration_phase(self):
        self.csr_item = csr_item = CSRSeqItem("NPU29_csr_item")
        self.mem_item = MemSeqItem("NPU29_mem_item")
        self.query = BasicQuerySeq("NPU29_seq", self.mem_item, self.csr_item)

    async def run_phase(self):
        self.raise_objection()

        for idx in range(20):

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

            base_addr = random.randint(0, 824)
            result_addr = random.randint(1024, 1984)

            # Using default value of systolic array size
            self.csr_item.matrix_setup(
                inputs_rows,
                inputs_cols,
                weights_rows, 
                weights_cols,
                base_addr=base_addr & ~3,
                result_addr=result_addr & ~3
            )

            self.mem_item.randomize_inputs(inputs_rows, inputs_cols, -255, 255)

            self.mem_item.randomize_weights(weights_rows, weights_cols, -255, 255)

            self.mem_item.randomize_bias(inputs_cols, -2**31, 2**31 - 1)
            self.mem_item.randomize_summs(inputs_cols, -2**31, 2**31 - 1)
            
            self.logger.info(self.csr_item)
            self.logger.info(self.mem_item)

            await self.query.start()

        self.drop_objection()