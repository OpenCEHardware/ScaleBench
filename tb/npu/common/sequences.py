import pyuvm
from pyuvm import *
from constants import *

class CSRTransaction(uvm_sequence_item):
    def __init__(self, name, addr, mode=CSRMode.READ, data=None):
        super().__init__(name)
        self.addr = addr
        self.mode = mode
        self.data = data

    def __eq__(self, other):
        same = self.addr == other.addr and self.data == other.data and self.mode == other.mode
        return same

    def __str__(self):
        return f"{self.get_name()} : addr={hex(self.addr)}, data={self.data}, mode={self.mode.name}"


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
