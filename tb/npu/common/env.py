import os
import cocotb
import pyuvm
import logging
from pyuvm import *
from cocotb.clock import Clock
from cocotb_coverage.coverage import coverage_db
from common.agents import *
from common.scoreboard import *
from common.models import *

class NPUEnv(uvm_env):
    def __init__(self, name="NPUEnv", parent=None, mem_size=2048):
        self.mem_size = mem_size
        super().__init__(name, parent)

    def build_phase(self):
        self.csr_agent = CSRAgent('csr_agent', self)

        self.mon_irq = IRQMonitor('mon_irq', self)

        self.mem = Memory(self.mem_size)
        self.mem_agent = MemoryAgent('mem_agent', self)
        self.mem_ar_fifo = uvm_tlm_analysis_fifo("mem_ar_fifo", self)
        self.mem_aw_fifo = uvm_tlm_analysis_fifo("mem_aw_fifo", self)
        self.mem_w_fifo = uvm_tlm_analysis_fifo("mem_w_fifo", self)

        self.scoreboard = NPUScoreboard('scoreboard', self)

        self.mem_seq = MemorySequence(mem=self.mem, ar_fifo=self.mem_ar_fifo, aw_fifo=self.mem_aw_fifo, w_fifo=self.mem_w_fifo)

        self.dut = cocotb.top

        ConfigDB().set(None, "*", "dut", self.dut)
        ConfigDB().set(self, "*", "clk", self.dut.clk_npu)
        ConfigDB().set(self, "*", "rst_n", self.dut.rst_n)
        ConfigDB().set(self, "*", "vif", self.dut)
        ConfigDB().set(self.mon_irq, "", "irq", self.dut.irq)
        ConfigDB().set(None, "*", "mem", self.mem)


    def connect_phase(self):
        self.csr_agent.mon_csr_ar.ap.connect(self.scoreboard.csr_ar_fifo.analysis_export)
        self.csr_agent.mon_csr_aw.ap.connect(self.scoreboard.csr_aw_fifo.analysis_export)
        self.csr_agent.mon_csr_w.ap.connect(self.scoreboard.csr_w_fifo.analysis_export)
        self.csr_agent.mon_csr_r.ap.connect(self.scoreboard.csr_r_fifo.analysis_export)
        self.csr_agent.mon_csr_b.ap.connect(self.scoreboard.csr_b_fifo.analysis_export)

        self.mem_agent.mon_mem_ar.ap.connect(self.scoreboard.mem_ar_fifo.analysis_export)
        self.mem_agent.mon_mem_aw.ap.connect(self.scoreboard.mem_aw_fifo.analysis_export)
        self.mem_agent.mon_mem_w.ap.connect(self.scoreboard.mem_w_fifo.analysis_export)
        self.mem_agent.mon_mem_r.ap.connect(self.scoreboard.mem_r_fifo.analysis_export)
        self.mem_agent.mon_mem_b.ap.connect(self.scoreboard.mem_b_fifo.analysis_export)

        self.mem_agent.mon_mem_ar.ap.connect(self.mem_ar_fifo.analysis_export)
        self.mem_agent.mon_mem_aw.ap.connect(self.mem_aw_fifo.analysis_export)
        self.mem_agent.mon_mem_w.ap.connect(self.mem_w_fifo.analysis_export)

        self.mon_irq.ap.connect(self.scoreboard.irq_fifo.analysis_export)

    async def run_phase(self):
        cocotb.start_soon(Clock(cocotb.top.clk_npu, NPUArch.CLK_PERIOD).start())
        cocotb.start_soon(self.mem_seq.start(self.mem_agent.seqr))

        self.dut.rst_n.value = 0
        await ClockCycles(self.dut.clk_npu, 5)
        self.dut.rst_n.value = 1


class BaseTest(uvm_test):
    def build_phase(self):
        self.env = NPUEnv('env', self)
        ConfigDB().set(None, "", "error", False)

    def final_phase(self):
        seed = os.environ.get('RANDOM_SEED', '')
        if seed:
            seed = f".{seed}";

        coverage_db.report_coverage(self.logger.info, bins=True)
        coverage_db.export_to_xml(filename=f"coverage{seed}.xml")
        coverage_db.export_to_yaml(filename=f"coverage{seed}.yaml")

        if ConfigDB().get(None, "", "error"):
            raise UVMError(f"{type(self).__name__} failed, check errors")
