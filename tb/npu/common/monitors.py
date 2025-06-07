
import cocotb
from cocotb.triggers import ClockCycles, RisingEdge
from pyuvm import *
from common.constants import *
from common.sequences import *


class ReadyValidMonitor(uvm_monitor):
    def __init__(self, name='ReadyValidMonitor', parent=None, *, channel_name=''):
        super().__init__(name, parent)
        self.channel_name = channel_name

    def build_phase(self):
        self.ap = uvm_analysis_port("ap", self)

        self.clk = ConfigDB().get(self, "", "clk")
        self.rst_n = ConfigDB().get(self, "", "rst_n")

        self.vif = ConfigDB().get(self, "", "vif")
        self.vif_name = ConfigDB().get(self, "", "vif_name")

        self.ready = self.get_vif_signal('ready')
        self.valid = self.get_vif_signal('valid')

    async def run_phase(self):
        while True:
            await RisingEdge(self.clk)

            if self.rst_n.value and self.ready.value and self.valid.value:
                self.ap.write(self.sample())

    def get_vif_signal(self, signal_name):
        return getattr(self.vif, f'{self.vif_name}_{self.channel_name}{signal_name}')

    def sample(self):
        raise NotImplementedError()


class AXI4LiteARMonitor(ReadyValidMonitor):
    def __init__(self, name='AXI4LiteARMonitor', parent=None):
        super().__init__(name, parent, channel_name='ar')

    def build_phase(self):
        super().build_phase()

        self.addr = self.get_vif_signal('addr')
        self.prot = self.get_vif_signal('prot')

    def sample(self):
        return AXI4LiteARItem(addr=self.addr.value, prot=self.prot.value)


class AXI4LiteAWMonitor(ReadyValidMonitor):
    def __init__(self, name='AXI4LiteAWMonitor', parent=None):
        super().__init__(name, parent, channel_name='aw')

    def build_phase(self):
        super().build_phase()

        self.addr = self.get_vif_signal('addr')
        self.prot = self.get_vif_signal('prot')

    def sample(self):
        return AXI4LiteAWItem(addr=self.addr.value, prot=self.prot.value)


class AXI4LiteAWMonitor(ReadyValidMonitor):
    def __init__(self, name='AXI4LiteAWMonitor', parent=None):
        super().__init__(name, parent, channel_name='aw')

    def build_phase(self):
        super().build_phase()

        self.addr = self.get_vif_signal('addr')
        self.prot = self.get_vif_signal('prot')

    def sample(self):
        return AXI4LiteAWItem(addr=self.addr.value, prot=self.prot.value)


class AXI4LiteWMonitor(ReadyValidMonitor):
    def __init__(self, name='AXI4LiteWMonitor', parent=None):
        super().__init__(name, parent, channel_name='w')

    def build_phase(self):
        super().build_phase()

        self.data = self.get_vif_signal('data')
        self.strb = self.get_vif_signal('strb')

    def sample(self):
        return AXI4LiteWItem(data=self.data.value, strb=self.strb.value)


class AXI4LiteRMonitor(ReadyValidMonitor):
    def __init__(self, name='AXI4LiteRMonitor', parent=None):
        super().__init__(name, parent, channel_name='r')

    def build_phase(self):
        super().build_phase()

        self.data = self.get_vif_signal('data')
        self.resp = self.get_vif_signal('resp')

    def sample(self):
        return AXI4LiteRItem(data=self.data.value, resp=self.resp.value)


class AXI4LiteBMonitor(ReadyValidMonitor):
    def __init__(self, name='AXI4LiteBMonitor', parent=None):
        super().__init__(name, parent, channel_name='b')

    def build_phase(self):
        super().build_phase()

        self.resp = self.get_vif_signal('resp')

    def sample(self):
        return AXI4LiteBItem(resp=self.resp.value)
