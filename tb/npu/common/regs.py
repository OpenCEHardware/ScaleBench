import cocotb
from cocotb.triggers import ClockCycles, RisingEdge
from pyuvm import *
from common.constants import *
from common.sequences import *


class NPUReg_ARCHID(uvm_reg):
    def __init__(self, name="ARCHID"):
        super().__init__(name, 32)

        self.ID = uvm_reg_field('ID')

    def build(self):
        self.ID.configure(self, 32, 0, 'RO', 0, 0)

        self._set_lock()
        self.set_prediction(predict_t.PREDICT_DIRECT)


class NPURegBlock(uvm_reg_block):
    def __init__(self, name="NPURegBlock"):
        super().__init__(name)

        self.def_map = uvm_reg_map("map")
        self.def_map.configure(self, 0)

        self.ARCHID = NPUReg_ARCHID('ARCHID')
        self.ARCHID.configure(self, "0x0", "", False, False)

        self.def_map.add_reg(self.ARCHID, "0x0", "RO")


class AXI4LiteBusAdapter(uvm_reg_adapter):
    def __init__(self, name="AXI4LiteBusAdapter"):
        super().__init__(name)

        self.provide_response = 1
        self.byte_enable = 1

    def reg2bus(self, rw: uvm_reg_bus_op) -> AXI4LiteRequest:
        item = AXI4LiteRequest("item")

        item.addr = int(rw.addr, 16)
        item.prot = AXI4Prot.DATA_SECURE_PRIV #TODO
        item.access = rw.kind

        if rw.kind == access_e.UVM_WRITE:
            item.wdata = rw.data
            item.wstrb = rw.byte_en

        item.resp = AXI4Result.OK
        if rw.status != status_t.IS_OK:
            item.resp = AXI4Result.SLVERR

        return item

    def bus2reg(self, item: AXI4LiteRequest, rw: uvm_reg_bus_op):
        rw.addr = hex(item.addr)
        rw.kind = item.access

        if item.access == access_e.UVM_WRITE:
            rw.data = item.wdata
            rw.n_bits = pyuvm.count_bits(item.wstrb)
            rw.byte_en = item.wstrb
        else:
            rw.data = item.rdata
            rw.n_bits = 4
            rw.byte_en = 0b1111

        rw.status = status_t.IS_OK
        if item.resp != AXI4Result.OK:
            rw.status = status_t.IS_NOT_OK
