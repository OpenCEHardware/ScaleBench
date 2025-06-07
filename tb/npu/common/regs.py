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


class NPUReg_IMPID(uvm_reg):
    def __init__(self, name="IMPID"):
        super().__init__(name, 32)

        self.ID = uvm_reg_field('ID')

    def build(self):
        self.ID.configure(self, 32, 0, 'RO', 0, 0)

        self._set_lock()
        self.set_prediction(predict_t.PREDICT_DIRECT)


class NPUReg_INROWS(uvm_reg):
    def __init__(self, name="INROWS"):
        super().__init__(name, 32)

        self.ROWS = uvm_reg_field('ROWS')

    def build(self):
        self.ROWS.configure(self, 8, 0, 'RW', 0, 0)

        self._set_lock()
        self.set_prediction(predict_t.PREDICT_DIRECT)


class NPUReg_INCOLS(uvm_reg):
    def __init__(self, name="INCOLS"):
        super().__init__(name, 32)

        self.COLS = uvm_reg_field('COLS')

    def build(self):
        self.COLS.configure(self, 8, 0, 'RW', 0, 0)

        self._set_lock()
        self.set_prediction(predict_t.PREDICT_DIRECT)


class NPUReg_WGHTROWS(uvm_reg):
    def __init__(self, name="WGHTROWS"):
        super().__init__(name, 32)

        self.ROWS = uvm_reg_field('ROWS')

    def build(self):
        self.ROWS.configure(self, 8, 0, 'RW', 0, 0)

        self._set_lock()
        self.set_prediction(predict_t.PREDICT_DIRECT)


class NPUReg_WGHTCOLS(uvm_reg):
    def __init__(self, name="WGHTCOLS"):
        super().__init__(name, 32)

        self.COLS = uvm_reg_field('COLS')

    def build(self):
        self.COLS.configure(self, 8, 0, 'RW', 0, 0)

        self._set_lock()
        self.set_prediction(predict_t.PREDICT_DIRECT)


class NPUReg_REINPUTS(uvm_reg):
    def __init__(self, name="REINPUTS"):
        super().__init__(name, 32)

        self.REUSE = uvm_reg_field('REUSE')

    def build(self):
        self.REUSE.configure(self, 1, 0, 'RW', 0, 0)

        self._set_lock()
        self.set_prediction(predict_t.PREDICT_DIRECT)


class NPUReg_REWEIGHTS(uvm_reg):
    def __init__(self, name="REWEIGHTS"):
        super().__init__(name, 32)

        self.REUSE = uvm_reg_field('REUSE')

    def build(self):
        self.REUSE.configure(self, 1, 0, 'RW', 0, 0)

        self._set_lock()
        self.set_prediction(predict_t.PREDICT_DIRECT)


class NPUReg_SAVEOUT(uvm_reg):
    def __init__(self, name="SAVEOUT"):
        super().__init__(name, 32)

        self.SAVE = uvm_reg_field('SAVE')

    def build(self):
        self.SAVE.configure(self, 1, 0, 'RW', 0, 0)

        self._set_lock()
        self.set_prediction(predict_t.PREDICT_DIRECT)


class NPUReg_USEBIAS(uvm_reg):
    def __init__(self, name="USEBIAS"):
        super().__init__(name, 32)

        self.USE = uvm_reg_field('USE')

    def build(self):
        self.USE.configure(self, 1, 0, 'RW', 0, 0)

        self._set_lock()
        self.set_prediction(predict_t.PREDICT_DIRECT)


class NPUReg_USESUMM(uvm_reg):
    def __init__(self, name="USESUMM"):
        super().__init__(name, 32)

        self.USE = uvm_reg_field('USE')

    def build(self):
        self.USE.configure(self, 1, 0, 'RW', 0, 0)

        self._set_lock()
        self.set_prediction(predict_t.PREDICT_DIRECT)


class NPUReg_SHIFTAMT(uvm_reg):
    def __init__(self, name="SHIFTAMT"):
        super().__init__(name, 32)

        self.AMOUNT = uvm_reg_field('AMOUNT')

    def build(self):
        self.AMOUNT.configure(self, 8, 0, 'RW', 0, 0)

        self._set_lock()
        self.set_prediction(predict_t.PREDICT_DIRECT)


class NPUReg_ACTFN(uvm_reg):
    def __init__(self, name="ACTFN"):
        super().__init__(name, 32)

        self.SELECT = uvm_reg_field('AMOUNT')

    def build(self):
        self.SELECT.configure(self, 1, 0, 'RW', 0, 0)

        self._set_lock()
        self.set_prediction(predict_t.PREDICT_DIRECT)


class NPUReg_BASE(uvm_reg):
    def __init__(self, name="BASE"):
        super().__init__(name, 32)

        self.ADDR = uvm_reg_field('ADDR')

    def build(self):
        self.ADDR.configure(self, 32, 0, 'RW', 0, 0)

        self._set_lock()
        self.set_prediction(predict_t.PREDICT_DIRECT)


class NPUReg_RESULT(uvm_reg):
    def __init__(self, name="RESULT"):
        super().__init__(name, 32)

        self.ADDR = uvm_reg_field('ADDR')

    def build(self):
        self.ADDR.configure(self, 32, 0, 'RW', 0, 0)

        self._set_lock()
        self.set_prediction(predict_t.PREDICT_DIRECT)


class NPUReg_INIT(uvm_reg):
    def __init__(self, name="INIT"):
        super().__init__(name, 32)

        self.VALUE = uvm_reg_field('VALUE')

    def build(self):
        self.VALUE.configure(self, 1, 0, 'W1S', 0, 0)

        self._set_lock()
        self.set_prediction(predict_t.PREDICT_DIRECT)


class NPUReg_IRQ(uvm_reg):
    def __init__(self, name="IRQ"):
        super().__init__(name, 32)

        self.FINISHED = uvm_reg_field('FINISHED')

    def build(self):
        self.FINISHED.configure(self, 1, 0, 'W1C', 0, 0)

        self._set_lock()
        self.set_prediction(predict_t.PREDICT_DIRECT)


class NPUReg_EXITCODE(uvm_reg):
    def __init__(self, name="EXITCODE"):
        super().__init__(name, 32)

        self.CODE = uvm_reg_field('CODE')

    def build(self):
        self.CODE.configure(self, 2, 0, 'RO', 0, 0)

        self._set_lock()
        self.set_prediction(predict_t.PREDICT_DIRECT)


class NPURegBlock(uvm_reg_block):
    def __init__(self, name="NPURegBlock"):
        super().__init__(name)

        self.def_map = uvm_reg_map("map")
        self.def_map.configure(self, 0)

        self.ARCHID = NPUReg_ARCHID()
        self.IMPID = NPUReg_IMPID()
        self.INROWS = NPUReg_INROWS()
        self.INCOLS = NPUReg_INCOLS()
        self.WGHTROWS = NPUReg_WGHTROWS()
        self.WGHTCOLS = NPUReg_WGHTCOLS()
        self.REINPUTS = NPUReg_REINPUTS()
        self.REWEIGHTS = NPUReg_REWEIGHTS()
        self.SAVEOUT = NPUReg_SAVEOUT()
        self.USEBIAS = NPUReg_USEBIAS()
        self.USESUMM = NPUReg_USESUMM()
        self.SHIFTAMT = NPUReg_SHIFTAMT()
        self.ACTFN = NPUReg_ACTFN()
        self.BASE = NPUReg_BASE()
        self.RESULT = NPUReg_RESULT()
        self.INIT = NPUReg_INIT()
        self.IRQ = NPUReg_IRQ()
        self.EXITCODE = NPUReg_EXITCODE()

        self.ARCHID.configure(self,    "0x0", "", False, False)
        self.IMPID.configure(self,     "0x4", "", False, False)
        self.INROWS.configure(self,    "0x8", "", False, False)
        self.INCOLS.configure(self,    "0xc", "", False, False)
        self.WGHTROWS.configure(self,  "0x10", "", False, False)
        self.WGHTCOLS.configure(self,  "0x14", "", False, False)
        self.REINPUTS.configure(self,  "0x18", "", False, False)
        self.REWEIGHTS.configure(self, "0x1c", "", False, False)
        self.SAVEOUT.configure(self,   "0x20", "", False, False)
        self.USEBIAS.configure(self,   "0x24", "", False, False)
        self.USESUMM.configure(self,   "0x28", "", False, False)
        self.SHIFTAMT.configure(self,  "0x2c", "", False, False)
        self.ACTFN.configure(self,     "0x30", "", False, False)
        self.BASE.configure(self,      "0x34", "", False, False)
        self.RESULT.configure(self,    "0x38", "", False, False)
        self.INIT.configure(self,      "0x3c", "", False, False)
        self.IRQ.configure(self,       "0x40", "", False, False)
        self.EXITCODE.configure(self,  "0x44", "", False, False)

        self.def_map.add_reg(self.ARCHID, "0x0", "RO")
        self.def_map.add_reg(self.IMPID, "0x0", "RO")
        self.def_map.add_reg(self.INROWS, "0x0", "RW")
        self.def_map.add_reg(self.INCOLS, "0x0", "RW")
        self.def_map.add_reg(self.WGHTROWS, "0x0", "RW")
        self.def_map.add_reg(self.WGHTCOLS, "0x0", "RW")
        self.def_map.add_reg(self.REINPUTS, "0x0", "RW")
        self.def_map.add_reg(self.REWEIGHTS, "0x0", "RW")
        self.def_map.add_reg(self.SAVEOUT, "0x0", "RW")
        self.def_map.add_reg(self.USEBIAS, "0x0", "RW")
        self.def_map.add_reg(self.USESUMM, "0x0", "RW")
        self.def_map.add_reg(self.SHIFTAMT, "0x0", "RW")
        self.def_map.add_reg(self.ACTFN, "0x0", "RW")
        self.def_map.add_reg(self.BASE, "0x0", "RW")
        self.def_map.add_reg(self.RESULT, "0x0", "RW")
        self.def_map.add_reg(self.INIT, "0x0", "RW")
        self.def_map.add_reg(self.IRQ, "0x0", "RW")
        self.def_map.add_reg(self.EXITCODE, "0x0", "RO")


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
            item.wstrb = 0b1111 # rw.byte_en

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
