import pyuvm
import cocotb
from pyuvm import *
from common.constants import *
from common.models import *


class NPUScoreboard(uvm_scoreboard):
    def __init__(self, name='NPUScoreboard', parent=None):
        super().__init__(name, parent)

    def build_phase(self):
        mem = ConfigDB().get(None, "", "mem")

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

    async def run_phase(self):
        cocotb.start_soon(self.csr_read_main())
        cocotb.start_soon(self.csr_write_main())
        cocotb.start_soon(self.mem_read_main())
        cocotb.start_soon(self.mem_write_main())
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
            else:
                self.logger.info(f"CSR read executed correctly")
                self.logger.info(f"|  request:  {ar_item}")
                self.logger.info(f"|__data:   {r_item}")

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
            else:
                self.logger.info(f"CSR write executed correctly")
                self.logger.info(f"|  request:  {aw_item}")
                self.logger.info(f"|__data:     {w_item}")

    async def mem_read_main(self):
        while True:
            ar_item = await self.mem_ar_fifo.get()
            r_item = await self.mem_r_fifo.get()

            expected = self.model.mem_read(ar_item)
            if expected != r_item:
                self.logger.error(f"Mem read response mismatch")
                self.logger.error(f"|  request:  {ar_item}")
                self.logger.error(f"|  expected: {expected}")
                self.logger.error(f"|__actual:   {r_item}")
            else:
                self.logger.info(f"Mem read executed correctly")
                self.logger.info(f"|  request:  {ar_item}")
                self.logger.info(f"|__data:     {r_item}")

    async def mem_write_main(self):
        while True:
            aw_item = await self.mem_aw_fifo.get()
            w_item = await self.mem_w_fifo.get()
            b_item = await self.mem_b_fifo.get()

            expected = self.model.mem_write(aw_item, w_item)
            if expected != b_item:
                self.logger.error(f"Mem write response mismatch")
                self.logger.error(f"|  request:  {aw_item}")
                self.logger.error(f"|  data:     {w_item}")
                self.logger.error(f"|  expected: {expected}")
                self.logger.error(f"|__actual:   {b_item}")

    async def irq_main(self):
        while True:
            irq_item = await self.irq_fifo.get()
            self.logger.error(f"unexpected interrupt: {irq_item}")

    def check_phase(self):
        self.check_fifo(self.csr_ar_fifo, "csr_ar_fifo")
        self.check_fifo(self.csr_aw_fifo, "csr_aw_fifo")
        self.check_fifo(self.csr_w_fifo, "csr_w_fifo")
        self.check_fifo(self.csr_r_fifo, "csr_r_fifo")
        self.check_fifo(self.csr_b_fifo, "csr_b_fifo")

    def check_fifo(self, fifo, fifo_name):
        if not fifo.is_empty():
            self.logger.error(f"{fifo_name} not empty during check_phase")

            while True:
                success, item = fifo.try_get()
                if not success:
                    break

                self.logger.error(item)
