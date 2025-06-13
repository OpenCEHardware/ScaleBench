
import cocotb
from cocotb.triggers import ClockCycles, RisingEdge
from pyuvm import *
from common.constants import *
from common.sequences import *


class ReadyValidMonitor(uvm_monitor):
    def __init__(self, name='ReadyValidMonitor', parent=None, *, channel_name='', with_id=False, with_burst=False):
        super().__init__(name, parent)
        self.channel_name = channel_name
        self.with_id = with_id
        self.with_burst = with_burst
        self.id_bursts = {}

    def build_phase(self):
        self.ap = uvm_analysis_port("ap", self)

        self.clk = ConfigDB().get(self, "", "clk")
        self.rst_n = ConfigDB().get(self, "", "rst_n")

        self.vif = ConfigDB().get(self, "", "vif")
        self.vif_name = ConfigDB().get(self, "", "vif_name")

        self.ready = self.get_vif_signal('ready')
        self.valid = self.get_vif_signal('valid')

        if self.with_id:
            self.id = self.get_vif_signal('id')

        if self.with_burst:
            self.last = self.get_vif_signal('last')

    async def run_phase(self):
        while True:
            await RisingEdge(self.clk)

            if not self.rst_n.value or not self.ready.value or not self.valid.value:
                continue

            if self.with_id:
                id = int(self.id.value)
            else:
                id = 0

            item = self.sample(id)

            if self.with_burst:
                samples = self.id_bursts.setdefault(id, [])
                samples.append(item)

                last = self.last.value
                if last:
                    item = self.sample_burst(id, samples)
                    samples.clear()
            else:
                last = True

            if last:
                self.ap.write(item)

    def get_vif_signal(self, signal_name):
        return getattr(self.vif, f'{self.vif_name}_{self.channel_name}{signal_name}')

    def sample(self, id):
        raise NotImplementedError()

    def sample_burst(self, id, samples):
        raise NotImplementedError()


class AXI4LiteARMonitor(ReadyValidMonitor):
    def __init__(self, name='AXI4LiteARMonitor', parent=None):
        super().__init__(name, parent, channel_name='ar', with_id=False, with_burst=False)

    def build_phase(self):
        super().build_phase()

        self.addr = self.get_vif_signal('addr')
        self.prot = self.get_vif_signal('prot')

    def sample(self, id):
        addr = self.addr.value
        if addr & 3:
            self.logger.error(f"misaligned address: {addr}")
            ConfigDB().set(None, "", "error", True)

        return AXI4LiteARItem(addr=addr, prot=self.prot.value)


class AXI4LiteAWMonitor(ReadyValidMonitor):
    def __init__(self, name='AXI4LiteAWMonitor', parent=None):
        super().__init__(name, parent, channel_name='aw', with_id=False, with_burst=False)

    def build_phase(self):
        super().build_phase()

        self.addr = self.get_vif_signal('addr')
        self.prot = self.get_vif_signal('prot')

    def sample(self, id):
        addr = self.addr.value
        if addr & 3:
            self.logger.error(f"misaligned address: {addr}")
            ConfigDB().set(None, "", "error", True)

        return AXI4LiteAWItem(addr=addr, prot=self.prot.value)


class AXI4LiteWMonitor(ReadyValidMonitor):
    def __init__(self, name='AXI4LiteWMonitor', parent=None):
        super().__init__(name, parent, channel_name='w', with_id=False, with_burst=False)

    def build_phase(self):
        super().build_phase()

        self.data = self.get_vif_signal('data')
        self.strb = self.get_vif_signal('strb')

    def sample(self, id):
        return AXI4LiteWItem(data=self.data.value, strb=self.strb.value)


class AXI4LiteRMonitor(ReadyValidMonitor):
    def __init__(self, name='AXI4LiteRMonitor', parent=None):
        super().__init__(name, parent, channel_name='r', with_id=False, with_burst=False)

    def build_phase(self):
        super().build_phase()

        self.data = self.get_vif_signal('data')
        self.resp = self.get_vif_signal('resp')

    def sample(self, id):
        return AXI4LiteRItem(data=self.data.value, resp=self.resp.value)


class AXI4LiteBMonitor(ReadyValidMonitor):
    def __init__(self, name='AXI4LiteBMonitor', parent=None):
        super().__init__(name, parent, channel_name='b', with_id=False, with_burst=False)

    def build_phase(self):
        super().build_phase()

        self.resp = self.get_vif_signal('resp')

    def sample(self, id):
        return AXI4LiteBItem(resp=self.resp.value)


class AXI4BurstARMonitor(ReadyValidMonitor):
    def __init__(self, name='AXI4BurstARMonitor', parent=None):
        super().__init__(name, parent, channel_name='ar', with_id=True, with_burst=False)

    def build_phase(self):
        super().build_phase()

        self.addr = self.get_vif_signal('addr')
        self.prot = self.get_vif_signal('prot')
        self.len = self.get_vif_signal('len')
        self.size = self.get_vif_signal('size')
        self.burst = self.get_vif_signal('burst')

    def sample(self, id):
        addr = self.addr.value
        if addr & 3:
            self.logger.error(f"misaligned address: {addr}")
            ConfigDB().set(None, "", "error", True)

        return AXI4BurstARItem(id=id, addr=addr, prot=self.prot.value, length=(self.len.value + 1), size=self.size.value, burst=self.burst.value)


class AXI4BurstAWMonitor(ReadyValidMonitor):
    def __init__(self, name='AXI4BurstAWMonitor', parent=None):
        super().__init__(name, parent, channel_name='aw', with_id=True, with_burst=False)

    def build_phase(self):
        super().build_phase()

        self.addr = self.get_vif_signal('addr')
        self.prot = self.get_vif_signal('prot')
        self.len = self.get_vif_signal('len')
        self.size = self.get_vif_signal('size')
        self.burst = self.get_vif_signal('burst')

    def sample(self, id):
        addr = self.addr.value
        if addr & 3:
            self.logger.error(f"misaligned address: {addr}")
            ConfigDB().set(None, "", "error", True)

        return AXI4BurstAWItem(id=id, addr=addr, prot=self.prot.value, length=(self.len.value + 1), size=self.size.value, burst=self.burst.value)


class AXI4BurstWMonitor(ReadyValidMonitor):
    def __init__(self, name='AXI4BurstWMonitor', parent=None):
        super().__init__(name, parent, channel_name='w', with_id=False, with_burst=True)

    def build_phase(self):
        super().build_phase()

        self.data = self.get_vif_signal('data')
        self.strb = self.get_vif_signal('strb')

    def sample(self, id):
        return (self.data.value, self.strb.value)

    def sample_burst(self, id, samples):
        return AXI4BurstWItem(data=[sample[0] for sample in samples], strb=[sample[1] for sample in samples])


class AXI4BurstRMonitor(ReadyValidMonitor):
    def __init__(self, name='AXI4BurstRMonitor', parent=None):
        super().__init__(name, parent, channel_name='r', with_id=True, with_burst=True)

    def build_phase(self):
        super().build_phase()

        self.data = self.get_vif_signal('data')
        self.resp = self.get_vif_signal('resp')

    def sample(self, id):
        return (self.data.value, self.resp.value)

    def sample_burst(self, id, samples):
        return AXI4BurstRItem(id=id, data=[sample[0] for sample in samples], resp=[sample[1] for sample in samples])


class AXI4BurstBMonitor(ReadyValidMonitor):
    def __init__(self, name='AXI4BurstBMonitor', parent=None):
        super().__init__(name, parent, channel_name='b', with_id=True, with_burst=False)

    def build_phase(self):
        super().build_phase()

        self.resp = self.get_vif_signal('resp')

    def sample(self, id):
        return AXI4BurstBItem(id=id, resp=self.resp.value)


class IRQMonitor(uvm_monitor):
    def __init__(self, name='IRQMonitor', parent=None):
        super().__init__(name, parent)

    def build_phase(self):
        self.ap = uvm_analysis_port("ap", self)

        self.rst_n = ConfigDB().get(self, "", "rst_n")
        self.irq = ConfigDB().get(self, "", "irq")

    async def run_phase(self):
        while True:
            await RisingEdge(self.irq)

            if self.rst_n.value:
                self.ap.write(IRQItem())
