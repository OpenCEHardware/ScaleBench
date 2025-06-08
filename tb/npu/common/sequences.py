import pyuvm
import cocotb
from pyuvm import *
from cocotb.queue import Queue
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

    def __str__(self):
        if self.access == access_e.UVM_WRITE:
            data_str = ", ".join(f"{beat:08x}" for beat in self.wdata)
            strb_str = ", ".join(f"{beat:04b}" for beat in self.wstrb)
            string = f"{self.get_name()} : WRITE id={self.id:02x}, addr={self.addr:08x}, wdata=[{wdata_str}], wstrb=[{wstrb_str}], prot={self.prot}, size={self.size}, burst={self.burst}"

            if self.resp != None:
                string += f", resp={self.resp}"
        else:
            string = f"{self.get_name()} : READ  id={self.id:02x}, addr={self.addr:08x}, prot={self.prot}, size={self.size}, burst={self.burst}"
            if self.resp != None:
                string += f", resp={self.resp}"
            if self.rdata != None:
                data_str = ", ".join(f"{beat:08x}" for beat in self.rdata)
                string += f", rdata=[{data_str}]"

        return string


class AXI4BurstReady(uvm_sequence_item):
    def __init__(self, name='AXI4BurstReady', *, ar_delays=[], aw_delays=[], w_delays=[]):
        super().__init__(name)

        self.ar_delays = ar_delays
        self.aw_delays = aw_delays
        self.w_delays = w_delays

    def do_copy(self, other):
        self.ar_delays = other.ar_delays
        self.aw_delays = other.aw_delays
        self.w_delays = other.w_delays


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
        data_str = ", ".join(f"{beat:08x}" for beat in self.data)
        strb_str = ", ".join(f"{beat:04b}" for beat in self.strb)
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
        data_str = ", ".join(f"{beat:08x}" for beat in self.data)
        return f"{self.get_name()} : id={self.id:02x}, data=[{data_str}], resp={self.resp}"


class AXI4BurstBItem(uvm_sequence_item):
    def __init__(self, *, id, resp, name='AXI4BurstBItem'):
        super().__init__(name)
        self.id = int(id)
        self.resp = [AXI4Result(beat) for beat in resp] if isinstance(resp, list) else AXI4Result(resp)

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


class MemorySequence(uvm_sequence):
    def __init__(self, name="MemorySequence", *, mem, ar_fifo, aw_fifo, w_fifo, max_pending=3):
        super().__init__(name)
        self.mem = mem
        self.ar_fifo = ar_fifo
        self.aw_fifo = aw_fifo
        self.w_fifo = w_fifo
        self.queue = Queue()
        self.max_pending = max_pending

    async def body(self):
        cocotb.start_soon(self.do_reads())
        cocotb.start_soon(self.do_writes())

        item = AXI4BurstReady(ar_delays=([0] * self.max_pending), aw_delays=([0] * self.max_pending), w_delays=([0] * self.max_pending))
        await self.queue.put(item)

        while True:
            item = await self.queue.get()
            await self.start_item(item)
            await self.finish_item(item)

    async def do_reads(self):
        while True:
            ar_item = await self.ar_fifo.get()

            resp = AXI4BurstRequest()
            resp.access = access_e.UVM_READ
            resp.id = ar_item.id
            resp.addr = ar_item.addr
            resp.prot = ar_item.prot
            resp.size = ar_item.size
            resp.burst = ar_item.burst
            resp.resp_delays = [0] * ar_item.length #TODO

            result = self.mem.read_beats(ar_item.addr, ar_item.length, ar_item.size, ar_item.burst)
            resp.rdata = [beat[0] for beat in result]
            resp.resp = [beat[1] for beat in result]

            await self.queue.put(AXI4BurstReady(ar_delays=[0]))
            await self.queue.put(resp)

    async def do_writes(self):
        while True:
            aw_item = await self.aw_fifo.get()
            if aw_item.length - self.max_pending:
                await self.queue.put(AXI4BurstReady(w_delays=([0] * (aw_item.length - self.max_pending))))

            w_item = await self.w_fifo.get()
            assert aw_item.length == len(w_item.data)

            resp = AXI4BurstRequest()
            resp.access = access_e.UVM_WRITE
            resp.id = aw_item.id
            resp.addr = aw_item.addr
            resp.prot = aw_item.prot
            resp.size = aw_item.size
            resp.burst = aw_item.burst
            resp.wdata = w_item.data
            resp.wstrb = w_item.strb
            resp.resp = self.mem.write_beats(aw_item.addr, w_item.data, w_item.strb, aw_item.size, aw_item.burst)
            resp.resp_delays = [0] #TODO

            await self.queue.put(AXI4BurstReady(aw_delays=[0], w_delays=([0] * min(aw_item.length, self.max_pending))))
            await self.queue.put(resp)
