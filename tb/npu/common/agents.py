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
        self.ap_csr_ar = uvm_analysis_port("ap_csr_ar", self)
        self.ap_csr_aw = uvm_analysis_port("ap_csr_aw", self)
        self.ap_csr_w = uvm_analysis_port("ap_csr_w", self)
        self.ap_csr_r = uvm_analysis_port("ap_csr_r", self)
        self.ap_csr_b = uvm_analysis_port("ap_csr_b", self)

        self.seqr = uvm_sequencer("seqr", self)

        self.drvr = AXI4LiteDriver("drvr", self)

        self.mon_csr_ar = AXI4LiteARMonitor("mon_csr_ar", self)
        self.mon_csr_aw = AXI4LiteAWMonitor("mon_csr_aw", self)
        self.mon_csr_w = AXI4LiteWMonitor("mon_csr_w", self)
        self.mon_csr_r = AXI4LiteRMonitor("mon_csr_r", self)
        self.mon_csr_b = AXI4LiteBMonitor("mon_csr_b", self)

        self.reg_block = NPURegBlock("reg_block")
        self.reg_adapter = AXI4LiteBusAdapter("reg_adapter")

        ConfigDB().set(self, "*", "vif_name", "csr")

    def connect_phase(self):
        self.drvr.seq_item_port.connect(self.seqr.seq_item_export)

        self.reg_block.def_map.set_sequencer(self.seqr)
        self.reg_block.def_map.set_adapter(self.reg_adapter)

        self.mon_csr_ar.ap.connect(self.ap_csr_ar)
        self.mon_csr_aw.ap.connect(self.ap_csr_aw)
        self.mon_csr_w.ap.connect(self.ap_csr_w)
        self.mon_csr_r.ap.connect(self.ap_csr_r)
        self.mon_csr_b.ap.connect(self.ap_csr_b)
