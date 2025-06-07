import cocotb
import pyuvm
import logging
from pyuvm import *
from cocotb.clock import Clock
from common.agents import *
from common.scoreboard import *
from common.models import *


class NPUEnv(uvm_env):
    def __init__(self, name="NPUEnv", parent=None):
        super().__init__(name, parent)

    def build_phase(self):
        self.csr_agent = CSRAgent('csr_agent', self)
        self.mem_agent = MemoryAgent('mem_agent', self)
        self.scoreboard = NPUScoreboard('scoreboard', self)
        self.mon_irq = IRQMonitor('mon_irq', self)
        self.mem = Memory(1024)

        self.dut = ConfigDB().get(self, "", "dut")

        ConfigDB().set(self, "*", "clk", self.dut.clk_npu)
        ConfigDB().set(self, "*", "rst_n", self.dut.rst_n)
        ConfigDB().set(self, "*", "vif", self.dut)
        ConfigDB().set(self.mon_irq, "", "irq", self.dut.irq)

    def connect_phase(self):
        self.csr_agent.mon_csr_ar.ap.connect(self.scoreboard.csr_ar_fifo.analysis_export)
        self.csr_agent.mon_csr_aw.ap.connect(self.scoreboard.csr_aw_fifo.analysis_export)
        self.csr_agent.mon_csr_w.ap.connect(self.scoreboard.csr_w_fifo.analysis_export)
        self.csr_agent.mon_csr_r.ap.connect(self.scoreboard.csr_r_fifo.analysis_export)
        self.csr_agent.mon_csr_b.ap.connect(self.scoreboard.csr_b_fifo.analysis_export)

        self.mon_irq.ap.connect(self.scoreboard.irq_fifo.analysis_export)

    async def run_phase(self):
        cocotb.start_soon(Clock(cocotb.top.clk_npu, 2).start())

        self.dut.rst_n.value = 0
        await ClockCycles(self.dut.clk_npu, 5)
        self.dut.rst_n.value = 1
