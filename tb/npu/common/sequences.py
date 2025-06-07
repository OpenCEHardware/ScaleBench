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
        self.prot = None

    def do_copy(self, other):
        self.addr = other.addr
        self.access = other.access
        self.rdata = other.rdata
        self.wdata = other.wdata
        self.wstrb = other.wstrb
        self.resp = other.resp
        self.prot = other.prot


class AXI4BurstRequest(uvm_sequence_item):
    def __init__(self, name='AXI4BurstRequest'):
        super().__init__(name)

        self.id = None
        self.addr = None
        self.access = None
        self.rdata = None
        self.wdata = None
        self.wstrb = None
        self.resp = None
        self.prot = None
        self.size = None
        self.burst = None
        self.resp_delays = None

    def do_copy(self, other):
        self.id = other.id
        self.addr = other.addr
        self.access = other.access
        self.rdata = other.rdata
        self.wdata = other.wdata
        self.wstrb = other.wstrb
        self.resp = other.resp
        self.prot = other.prot
        self.size = other.size
        self.burst = other.burst
        self.resp_delays = other.resp_delays


class AXI4BurstReady(uvm_sequence_item):
    def __init__(self, name='AXI4BurstReady'):
        super().__init__(name)

        self.ar_delays = None
        self.aw_delays = None
        self.w_delays = None

    def do_copy(self, other):
        self.ar_delays = other.ar_delays
        self.aw_delays = other.aw_delays
        self.w_delays = other.w_delays


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


class AXI4BurstARItem(uvm_sequence_item):
    def __init__(self, *, id, addr, prot, length, size, burst, name='AXI4BurstARItem'):
        super().__init__(name)

        assert 1 <= length <= 256

        self.id = int(id)
        self.addr = int(addr)
        self.prot = AXI4Prot(prot)
        self.size = AXI4Size(size)
        self.burst = AXI4BurstMode(burst)
        self.length = length

        assert self.size.value <= 4

    def __eq__(self, other):
        same = self.id == other.id and self.addr == other.addr and self.prot == other.prot and self.length == other.length and self.size == other.size and self.burst == other.burst
        return same

    def __str__(self):
        return f"{self.get_name()} : id={self.id:02x}, addr={self.addr:08x}, len={self.length}, prot={self.prot}, burst={self.burst}, size={self.size}"


class AXI4BurstAWItem(uvm_sequence_item):
    def __init__(self, *, id, addr, prot, length, size, burst, name='AXI4BurstAWItem'):
        super().__init__(name)

        assert 1 <= length <= 256

        self.id = int(id)
        self.addr = int(addr)
        self.prot = AXI4Prot(prot)
        self.size = AXI4Size(size)
        self.burst = AXI4BurstMode(burst)
        self.length = length

        assert self.size.value <= 4

    def __eq__(self, other):
        same = self.id == other.id and self.addr == other.addr and self.prot == other.prot and self.length == other.length and self.size == other.size and self.burst == other.burst
        return same

    def __str__(self):
        return f"{self.get_name()} : id={self.id:02x}, addr={self.addr:08x}, len={self.length}, prot={self.prot}, burst={self.burst}, size={self.size}"


class AXI4BurstWItem(uvm_sequence_item):
    def __init__(self, *, data, strb, name='AXI4BurstWItem'):
        super().__init__(name)

        assert type(data) is list and type(strb) is list
        assert len(data) > 0 and len(data) == len(strb)

        self.data = [int(beat) for beat in data]
        self.strb = [int(beat) for beat in strb]

    def __eq__(self, other):
        same = self.data == other.data and self.strb == other.strb
        return same

    def __str__(self):
        data_str = ", ".join("{beat:08x}" for beat in self.data)
        strb_str = ", ".join("{beat:04b}" for beat in self.strb)
        return f"{self.get_name()} : data=[{data_str}], strb=[{strb_str}]"


class AXI4BurstRItem(uvm_sequence_item):
    def __init__(self, *, id, data, resp, name='AXI4BurstRItem'):
        super().__init__(name)

        assert type(data) is list and type(resp) is list
        assert len(data) > 0 and len(data) == len(resp)

        self.id = int(id)
        self.data = [int(d) for d in data]

        self.resp = AXI4Result.OK
        for beat in resp:
            beat = AXI4Result(beat)
            if beat != AXI4Result.OK:
                self.resp = beat

    def __eq__(self, other):
        same = self.id == other.id and self.data == other.data and self.resp == other.resp
        return same

    def __str__(self):
        data_str = ", ".join("{beat:08x}" for beat in self.data)
        return f"{self.get_name()} : id={self.id:02x}, data=[{data_str}], resp={self.resp}"


class AXI4BurstBItem(uvm_sequence_item):
    def __init__(self, *, id, resp, name='AXI4BurstBItem'):
        super().__init__(name)
        self.id = int(id)
        self.resp = AXI4Result(resp)

    def __eq__(self, other):
        same = self.id == other.id and self.resp == other.resp
        return same

    def __str__(self):
        return f"{self.get_name()} : id={self.id:02x}, resp={self.resp}"


class IRQItem(uvm_sequence_item):
    def __init__(self, *, name='IRQItem'):
        super().__init__(name)

    def __eq__(self, other):
        same = True
        return same

    def __str__(self):
        return f"{self.get_name()}"
