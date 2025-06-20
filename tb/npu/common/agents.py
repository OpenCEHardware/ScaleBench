import pyuvm
import cocotb
from pyuvm import *
from common.constants import *
from common.monitors import *
from common.driver import *
from common.regs import *


class CSRAgent(uvm_agent):
    def __init__(self, name="CSRAgent", parent=None):
        super().__init__(name, parent)

    def build_phase(self):
        self.seqr = uvm_sequencer("seqr", self)

        self.drvr = AXI4LiteMasterDriver("drvr", self)

        self.mon_csr_ar = AXI4LiteARMonitor("mon_csr_ar", self)
        self.mon_csr_aw = AXI4LiteAWMonitor("mon_csr_aw", self)
        self.mon_csr_w = AXI4LiteWMonitor("mon_csr_w", self)
        self.mon_csr_r = AXI4LiteRMonitor("mon_csr_r", self)
        self.mon_csr_b = AXI4LiteBMonitor("mon_csr_b", self)

        self.reg_block = NPURegBlock("reg_block")
        self.reg_adapter = AXI4LiteBusAdapter("reg_adapter")

        ConfigDB().set(self, "*", "vif_name", "csr")
        ConfigDB().set(None, "", "reg_block", self.reg_block)

    def connect_phase(self):
        self.drvr.seq_item_port.connect(self.seqr.seq_item_export)

        self.reg_block.def_map.set_sequencer(self.seqr)
        self.reg_block.def_map.set_adapter(self.reg_adapter)


class MemoryAgent(uvm_agent):
    def __init__(self, name="MemoryAgent", parent=None):
        super().__init__(name, parent)

    def build_phase(self):
        self.seqr = uvm_sequencer("seqr", self)

        self.drvr = AXI4BurstSlaveDriver("drvr", self)

        self.mon_mem_ar = AXI4BurstARMonitor("mon_mem_ar", self)
        self.mon_mem_aw = AXI4BurstAWMonitor("mon_mem_aw", self)
        self.mon_mem_w = AXI4BurstWMonitor("mon_mem_w", self)
        self.mon_mem_r = AXI4BurstRMonitor("mon_mem_r", self)
        self.mon_mem_b = AXI4BurstBMonitor("mon_mem_b", self)

        ConfigDB().set(self, "*", "vif_name", "mem")

    def connect_phase(self):
        self.drvr.seq_item_port.connect(self.seqr.seq_item_export)
