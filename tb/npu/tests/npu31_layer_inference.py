import cocotb
import pyuvm
import random
from pyuvm import *
from common.env import *
from common.sequences import *


@pyuvm.test()
class NPU31_Layer_Inference(BaseTest):
    """Inference using layers"""

    def end_of_elaboration_phase(self):
        self.csr_item = csr_item = CSRSeqItem("NPU31_csr_item")
        self.mem_item = MemSeqItem("NPU31_mem_item")
        self.query = BasicQuerySeq("NPU31_seq", self.mem_item, self.csr_item)

    async def run_phase(self):
        self.raise_objection()

        # Layer 1

        inputs_rows = 4
        inputs_cols = weights_rows = 8
        weights_cols = 4

        self.mem_item.randomize_inputs(inputs_rows, inputs_cols, 0, 50)

        self.mem_item.randomize_weights(weights_rows, weights_cols, 0, 50)

        self.mem_item.bias = [-128, -12, 127, 0, 0, 0, 0, 0]

        self.csr_item.matrix_setup(
            inputs_rows,
            inputs_cols,
            weights_rows, 
            weights_cols,
            base_addr=0x0,
            result_addr=88
        )

        self.csr_item.features_setup(
            reinputs=False,
            saveout=False, 
            # The DUT does not support disabling of BIAS and SUMM at the same time.
            usebias=True,
            usesumm=False,
            shift_amount=7,
            activation_function=True,
            reweights=False
        )
        
        self.logger.info(self.csr_item)
        self.logger.info(self.mem_item)

        await self.query.start()

        # Layer 2

        inputs_rows = 4
        inputs_cols = weights_rows = 8
        weights_cols = 8

        self.mem_item.inputs = []

        self.mem_item.randomize_weights(weights_rows, weights_cols, 0, 50)

        self.mem_item.bias = [-128, 41, 18, -23, 127, 86, 119, 15]

        self.csr_item.matrix_setup(
            inputs_rows,
            inputs_cols,
            weights_rows, 
            weights_cols,
            base_addr=120,
            result_addr=200
        )

        self.csr_item.features_setup(
            reinputs=True,
            saveout=False, 
            # The DUT does not support disabling of BIAS and SUMM at the same time.
            usebias=True,
            usesumm=False,
            shift_amount=7,
            activation_function=True,
            reweights=False
        )

        self.logger.info(self.csr_item)
        self.logger.info(self.mem_item)

        await self.query.start()

        # Layer 3

        inputs_rows = 4
        inputs_cols = weights_rows = 8
        weights_cols = 8

        self.mem_item.inputs = []

        self.mem_item.randomize_weights(weights_rows, weights_cols, 0, 50)

        self.mem_item.bias = [-128, -12, 127, 0, 0, 0, 0, 0]

        self.csr_item.matrix_setup(
            inputs_rows,
            inputs_cols,
            weights_rows, 
            weights_cols,
            base_addr=264,
            result_addr=1024
        )

        self.csr_item.features_setup(
            reinputs=True,
            saveout=True, 
            # The DUT does not support disabling of BIAS and SUMM at the same time.
            usebias=True,
            usesumm=False,
            shift_amount=0,
            activation_function=False,
            reweights=False
        )

        self.logger.info(self.csr_item)
        self.logger.info(self.mem_item)

        await self.query.start()

        self.drop_objection()