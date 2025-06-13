import pyuvm
import cocotb
import random
from pyuvm import *
from cocotb.queue import Queue
from common.constants import *
import common.coverage as coverage


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


class CSRSeqItem(uvm_sequence_item):
    def __init__(self, name):
        super().__init__(name)
        self._matrix_ops = []
        self._feature_ops = []
        self._custom_ops = []
        self.reg_block = ConfigDB().get(None, "", "reg_block")

    def add_operation(self, register, mode, value=0x0):
        assert isinstance(register, uvm_reg)
        assert isinstance(mode, CSRMode)
        assert isinstance(value, int)

        from common.regs import NPUReg_INIT
        assert not isinstance(register, NPUReg_INIT)

        self._custom_ops.append((register, mode, value))

    @property
    def operations(self):
        return self._matrix_ops + self._feature_ops + self._custom_ops

    def __eq__(self, other):
        return isinstance(other, CSRSeqItem) and self.operations == other.operations

    def __str__(self):
        return f"{self.get_name()}:\n" + "\n".join(
            f"REG:{reg.get_name()}, MODE:{mode}, VALUE:{value}" 
            for reg, mode, value in self.operations
        )

    def matrix_setup(self, inputs_rows, inputs_cols, weights_rows, weights_cols, base_addr, result_addr):
        assert all(isinstance(x, int) for x in [inputs_rows, inputs_cols, weights_rows, weights_cols, base_addr, result_addr]), \
            "All parameters must be integers"

        self._matrix_ops = [
            (self.reg_block.INROWS, CSRMode.WRITE, inputs_rows),
            (self.reg_block.INCOLS, CSRMode.WRITE, inputs_cols),
            (self.reg_block.WGHTROWS, CSRMode.WRITE, weights_rows),
            (self.reg_block.WGHTCOLS, CSRMode.WRITE, weights_cols),
            (self.reg_block.BASE, CSRMode.WRITE, base_addr),
            (self.reg_block.RESULT, CSRMode.WRITE, result_addr)
        ]

        coverage.shape(inputs_rows, inputs_cols, weights_rows, weights_cols)

    def features_setup(self, reinputs=False, saveout=True, usebias=True, usesumm=True, shift_amount=0, activation_function=False, reweights=False):
        self._feature_ops = [
            (self.reg_block.REINPUTS, CSRMode.WRITE, int(reinputs)),
            (self.reg_block.SAVEOUT, CSRMode.WRITE, int(saveout)),
            (self.reg_block.USEBIAS, CSRMode.WRITE, int(usebias)),
            (self.reg_block.USESUMM, CSRMode.WRITE, int(usesumm)),
            (self.reg_block.SHIFTAMT, CSRMode.WRITE, shift_amount),
            (self.reg_block.ACTFN, CSRMode.WRITE, int(activation_function)),
            (self.reg_block.REWEIGHTS, CSRMode.WRITE, int(reweights))
        ]

        coverage.features(shift_amount,
                          saveout,
                          usebias,
                          usesumm,
                          reinputs,
                          reweights,
                          activation_function)


class MemSeqItem(uvm_sequence_item):
    def __init__(self, name, weights=[], inputs=[], bias=[], summ=[]):
        super().__init__(name)
        self.weights = weights
        self.inputs = inputs
        self.bias = bias
        self.summ = summ

    def __str__(self):
        return "\n".join([
            self.get_name(),
            f"Weights: {self.weights}",
            f"Inputs: {self.inputs}",
            f"Bias: {self.bias}",
            f"Sum: {self.summ}"
        ])
    
    def __eq__(self, other):
        return isinstance(other, MemSeqItem) and (
            self.weights == other.weights and
            self.inputs == other.inputs and
            self.bias == other.bias and
            self.summ == other.summ
        )

    def randomize_weights(self, rows, cols, min_number=0, max_number=255):
        total = rows * cols
        self.weights = [random.randint(min_number, max_number) for _ in range(total)]

    def randomize_inputs(self, rows, cols, min_number=0, max_number=255):
        total = rows * cols
        self.inputs = [random.randint(min_number, max_number) for _ in range(total)]

    def randomize_bias(self, length, min_number=0, max_number=255):
        self.bias = [random.randint(min_number, max_number) for _ in range(length)]

    def randomize_summs(self, length, min_number=0, max_number=255):
        self.summ = [random.randint(min_number, max_number) for _ in range(length)]
