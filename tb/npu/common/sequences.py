import pyuvm
from pyuvm import *
from common.constants import *


class AXI4LiteRequest(uvm_sequence_item):
    def __init__(self, name='AXI4LiteRequest'):
        super().__init__(name)

        self.addr = None
        self.access = None
        self.rdata = None
        self.wdata = None
        self.wstrb = None
        self.resp = None

    def do_copy(self, other):
        self.addr = other.addr
        self.access = other.access
        self.rdata = other.rdata
        self.wdata = other.wdata
        self.wstrb = other.wstrb


class CSRSequence(uvm_sequence):
    def __init__(self, name, addr, mode=CSRMode.READ, data=None):
        super().__init__(name)
        self.addr = addr
        self.data = data
        self.mode = mode

    async def body(self):
        seq_item = CSRTransaction("seq_item", self.addr, self.mode, self.data)
        await self.start_item(seq_item)
        await self.finish_item(seq_item)
        self.result = seq_item.result


class AXI4LiteARItem(uvm_sequence_item):
    def __init__(self, *, addr, prot, name='AXI4LiteARItem'):
        super().__init__(name)
        self.addr = int(addr)
        self.prot = AXI4Prot(prot)

    def __eq__(self, other):
        same = self.addr == other.addr and self.prot == other.prot
        return same

    def __str__(self):
        return f"{self.get_name()} : addr={self.addr:08x}, prot={self.prot}"


class AXI4LiteAWItem(uvm_sequence_item):
    def __init__(self, *, addr, prot, name='AXI4LiteAWItem'):
        super().__init__(name)
        self.addr = int(addr)
        self.prot = AXI4Prot(prot)

    def __eq__(self, other):
        same = self.addr == other.addr and self.prot == other.prot
        return same

    def __str__(self):
        return f"{self.get_name()} : addr={self.addr:08x}, prot={self.prot}"


class AXI4LiteWItem(uvm_sequence_item):
    def __init__(self, *, data, strb, name='AXI4LiteWItem'):
        super().__init__(name)
        self.data = int(data)
        self.strb = int(strb)

    def __eq__(self, other):
        same = self.data == other.data and self.strb == other.strb
        return same

    def __str__(self):
        return f"{self.get_name()} : data={self.data:08x}, strb={self.strb:04b}"


class AXI4LiteRItem(uvm_sequence_item):
    def __init__(self, *, data, resp, name='AXI4LiteRItem'):
        super().__init__(name)
        self.data = int(data)
        self.resp = AXI4Result(resp)

    def __eq__(self, other):
        same = self.data == other.data and self.resp == other.resp
        return same

    def __str__(self):
        return f"{self.get_name()} : data={self.data:08x}, resp={self.resp}"


class AXI4LiteBItem(uvm_sequence_item):
    def __init__(self, *, resp, name='AXI4LiteBItem'):
        super().__init__(name)
        self.resp = AXI4Result(resp)

    def __eq__(self, other):
        same = self.resp == other.resp
        return same

    def __str__(self):
        return f"{self.get_name()} : resp={self.resp}"


class IRQItem(uvm_sequence_item):
    def __init__(self, *, name='IRQItem'):
        super().__init__(name)

    def __eq__(self, other):
        same = True
        return same

    def __str__(self):
        return f"{self.get_name()}"
