import pyuvm
import cocotb
from cocotb_bus.drivers.amba import AXI4LiteMaster
from cocotb.triggers import ClockCycles
from pyuvm import *
from constants import *


class AXI4LiteDriver(uvm_driver):
    def build_phase(self):
        self.ap = uvm_analysis_port("ap", self)
        self.dut = cocotb.top

    def start_of_simulation_phase(self):
        self.csr_interface = AXI4LiteMaster(self.dut, "csr", self.dut.clk_npu, case_insensitive=True)

    async def reset(self):
        self.dut.rst_n.value = 0
        await ClockCycles(self.dut.clk_npu, 5)
        self.dut.rst_n.value = 1

    async def run_phase(self):
        await self.reset()
        while True:
            csr_tx = await self.seq_item_port.get_next_item()

            result = AXI4LiteWriteResult.DECERR

            if csr_tx.mode == CSRMode.READ:
                data = self.csr_interface.read(csr_tx.addr)
                result = AXI4LiteWriteResult.OK
            self.seq_item_port.item_done()