import cocotb
import pyuvm
import logging
import random
from pyuvm import *
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from common.env import *
from common.sequences import *


class BaseTest(uvm_test):
    def build_phase(self):
        self.env = NPUEnv('env', self)

@pyuvm.test()
class NPU00_MUL_Basic(BaseTest):
    """Test the incapacity of the DUT to perform operations with BIAS and SUMM disabled"""

    def end_of_elaboration_phase(self):
        self.csr_item = csr_item = CSRSeqItem("NPU00_csr_item")
        # Using an empty item to test case of complete clean memory
        self.mem_item = MemSeqItem("NPU00_mem_item", 0, 0)
        self.query = BasicQuerySeq("NPU00_seq", self.mem_item, self.csr_item)

    async def run_phase(self):
        self.raise_objection()

        self.csr_item.features_setup(
            reinputs=False,
            saveout=True, 
            # The DUT does not support disabling of BIAS and SUMM at the same time.
            usebias=False,
            usesumm=False,
            shift_amount=0,
            activation_function=False,
            reweights=False
        )

        # Using default value of systolic array size
        self.csr_item.matrix_setup(
            inputs_rows=8, 
            inputs_cols=8, 
            weights_rows=8, 
            weights_cols=8, 
            base_addr=0x0, 
            result_addr=0x200
        )

        await self.query.start()

        self.drop_objection()


@pyuvm.test()
class NPU01_MUL_Zeros(BaseTest):
    """Verify zero output with null inputs"""

    def end_of_elaboration_phase(self):
        self.csr_item = csr_item = CSRSeqItem("NPU01_csr_item")
        # Using an empty item to test case of complete clean memory
        self.mem_item = MemSeqItem("NPU01_mem_item", 0, 0)
        self.query = BasicQuerySeq("NPU01_seq", self.mem_item, self.csr_item)

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

        # Using default value of systolic array size
        self.csr_item.matrix_setup(
            inputs_rows=8, 
            inputs_cols=8, 
            weights_rows=8, 
            weights_cols=8, 
            base_addr=0x0, 
            result_addr=0x200
        )

        await self.query.start()

        self.drop_objection()


@pyuvm.test()
class NPU02_MUL_Max(BaseTest):
    """Check potential overflow without bias"""

    def end_of_elaboration_phase(self):
        self.csr_item = csr_item = CSRSeqItem("NPU02_csr_item")
        self.mem_item = MemSeqItem("NPU02_mem_item", 0, 0)
        self.query = BasicQuerySeq("NPU02_seq", self.mem_item, self.csr_item)

    async def run_phase(self):
        self.raise_objection()

        self.csr_item.features_setup(
            reinputs=False,
            saveout=True, 
            # The DUT does not support disabling of BIAS and SUMM at the same time.
            usebias=True,
            usesumm=True,
            shift_amount=0,
            activation_function=False,
            reweights=False
        )

        inputs_rows = 8
        inputs_cols = 8
        weights_rows = 8
        weights_cols = 8

        # Using default value of systolic array size
        self.csr_item.matrix_setup(
            inputs_rows, 
            inputs_cols, 
            weights_rows, 
            weights_cols, 
            base_addr=0x0, 
            result_addr=1024
        )

        self.mem_item.inputs = [254] * inputs_cols * inputs_rows

        self.mem_item.weights = [254] * inputs_cols * inputs_rows

        await self.query.start()

        self.drop_objection()


@pyuvm.test()
class NPU03_MUL_Special(BaseTest):
    """Evaluate behavior on constant patterns"""

    def end_of_elaboration_phase(self):
        self.csr_item = csr_item = CSRSeqItem("NPU03_csr_item")
        self.mem_item = MemSeqItem("NPU03_mem_item", 0, 0)
        self.query = BasicQuerySeq("NPU03_seq", self.mem_item, self.csr_item)

    async def run_phase(self):
        self.raise_objection()

        self.csr_item.features_setup(
            reinputs=False,
            saveout=True, 
            # The DUT does not support disabling of BIAS and SUMM at the same time.
            usebias=True,
            usesumm=True,
            shift_amount=0,
            activation_function=False,
            reweights=False
        )

        inputs_rows = 8
        inputs_cols = 8
        weights_rows = 8
        weights_cols = 8

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
            0 if (i + j) % 2 == 0 else 127
            for i in range(inputs_rows) for j in range(inputs_cols)
        ]

        pattern_ramp = [
            i * 8 + j + 1
            for i in range(weights_rows) for j in range(weights_cols)
        ]


        self.mem_item.inputs = pattern_alternating

        self.mem_item.weights = pattern_ramp

        await self.query.start()

        self.drop_objection()


@pyuvm.test()
class NPU04_MUL_Identity(BaseTest):
    """Should reproduce the original matrix"""

    def end_of_elaboration_phase(self):
        self.csr_item = csr_item = CSRSeqItem("NPU04_csr_item")
        self.mem_item = MemSeqItem("NPU04_mem_item", 0, 0)
        self.query = BasicQuerySeq("NPU04_seq", self.mem_item, self.csr_item)

    async def run_phase(self):
        self.raise_objection()

        self.csr_item.features_setup(
            reinputs=False,
            saveout=True, 
            # The DUT does not support disabling of BIAS and SUMM at the same time.
            usebias=True,
            usesumm=True,
            shift_amount=0,
            activation_function=False,
            reweights=False
        )

        inputs_rows = 8
        inputs_cols = 8
        weights_rows = 8
        weights_cols = 8

        # Using default value of systolic array size
        self.csr_item.matrix_setup(
            inputs_rows, 
            inputs_cols, 
            weights_rows, 
            weights_cols, 
            base_addr=0x0, 
            result_addr=1024
        )

        inputs_matrix = [
            random.randint(1, 127) for _ in range(inputs_cols)
            for _ in range(inputs_rows)
        ]

        weights_matrix = [
            1 if i == j else 0 for j in range(weights_cols)
            for i in range(weights_rows)
        ]

        print(inputs_matrix)
        print(weights_matrix)


        self.mem_item.inputs = inputs_matrix

        self.mem_item.weights = weights_matrix

        await self.query.start()

        self.drop_objection()

