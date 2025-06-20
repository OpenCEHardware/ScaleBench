import pyuvm
import cocotb
from pyuvm import *
from common.constants import *
from common.models import *
import common.coverage as coverage


class NPUScoreboard(uvm_scoreboard):
    def __init__(self, name='NPUScoreboard', parent=None):
        super().__init__(name, parent)

    def build_phase(self):
        mem = ConfigDB().get(None, "", "mem")

        self.mem = mem
        self.model = NPUModel(mem)

        self.csr_ar_fifo = uvm_tlm_analysis_fifo("csr_ar_fifo", self)
        self.csr_aw_fifo = uvm_tlm_analysis_fifo("csr_aw_fifo", self)
        self.csr_w_fifo = uvm_tlm_analysis_fifo("csr_w_fifo", self)
        self.csr_r_fifo = uvm_tlm_analysis_fifo("csr_r_fifo", self)
        self.csr_b_fifo = uvm_tlm_analysis_fifo("csr_b_fifo", self)

        self.mem_ar_fifo = uvm_tlm_analysis_fifo("mem_ar_fifo", self)
        self.mem_aw_fifo = uvm_tlm_analysis_fifo("mem_aw_fifo", self)
        self.mem_w_fifo = uvm_tlm_analysis_fifo("mem_w_fifo", self)
        self.mem_r_fifo = uvm_tlm_analysis_fifo("mem_r_fifo", self)
        self.mem_b_fifo = uvm_tlm_analysis_fifo("mem_b_fifo", self)

        self.irq_fifo = uvm_tlm_analysis_fifo("irq_fifo", self)

        self.error = False

    async def run_phase(self):
        cocotb.start_soon(self.csr_read_main())
        cocotb.start_soon(self.csr_write_main())
        cocotb.start_soon(self.irq_main())

    async def csr_read_main(self):
        while True:
            ar_item = await self.csr_ar_fifo.get()
            r_item = await self.csr_r_fifo.get()

            expected = self.model.csr_read(ar_item)
            if expected != r_item:
                self.logger.error(f"CSR read response mismatch")
                self.logger.error(f"|  request:  {ar_item}")
                self.logger.error(f"|  expected: {expected}")
                self.logger.error(f"|__actual:   {r_item}")
                self.error = True
            # else:
            #     self.logger.info(f"CSR read executed correctly")
            #     self.logger.info(f"|  request:  {ar_item}")
            #     self.logger.info(f"|__data:   {r_item}")

    async def csr_write_main(self):
        while True:
            aw_item = await self.csr_aw_fifo.get()
            w_item = await self.csr_w_fifo.get()
            b_item = await self.csr_b_fifo.get()

            expected = self.model.csr_write(aw_item, w_item)
            if expected != b_item:
                self.logger.error(f"CSR write response mismatch")
                self.logger.error(f"|  request:  {aw_item}")
                self.logger.error(f"|  data:     {w_item}")
                self.logger.error(f"|  expected: {expected}")
                self.logger.error(f"|__actual:   {b_item}")
                self.error = True
            # else:
            #     self.logger.info(f"CSR write executed correctly")
            #     self.logger.info(f"|  request:  {aw_item}")
            #     self.logger.info(f"|__data:     {w_item}")

    async def irq_main(self):
        while True:
            irq_item = await self.irq_fifo.get()
            self.logger.info(f"Interrupt: {irq_item}")

            coverage.irq(True)

            # Set EXITCODE in SUCCESS = 01
            self.model.registers[0x44] = 0x1

            self.model.interrupt()

            actual = self.mem.read_mem(self.model.get_result_address(), length=self.model.get_result_length(), data_width=NPUArch.OUTPUT_DATA_WIDTH, signed=True)
            expected = self.model.predict_result()

            if actual != expected:
                self.logger.error(f"Bad result")
                self.logger.error(f"|  expected: {expected}")
                self.logger.error(f"|__actual:   {actual}")
                self.error = True
            else:
                self.logger.info(f"Correct result: {actual}")

    def check_phase(self):
        self.check_fifo(self.csr_ar_fifo, "csr_ar_fifo")
        self.check_fifo(self.csr_aw_fifo, "csr_aw_fifo")
        self.check_fifo(self.csr_w_fifo, "csr_w_fifo")
        self.check_fifo(self.csr_r_fifo, "csr_r_fifo")
        self.check_fifo(self.csr_b_fifo, "csr_b_fifo")

        if self.error:
            ConfigDB().set(None, "", "error", True)

    def check_fifo(self, fifo, fifo_name):
        if not fifo.is_empty():
            self.logger.error(f"{fifo_name} not empty during check_phase")

            while True:
                success, item = fifo.try_get()
                if not success:
                    break

                self.logger.error(item)

            self.error = True
