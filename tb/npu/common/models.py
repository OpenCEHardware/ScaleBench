import pyuvm
import cocotb
from math import log2
from pyuvm import *
from common.sequences import *


class NPUModel:

    registers = {
        0x00: 0xB00B,  # ARCHID_REG_ADDR
        0x04: 0x100,  # IMPID_REG_ADDR
        0x08: "",  # NUM_ROWS_INPUT_REG_ADDR
        0x0C: "",  # NUM_COLS_INPUT_REG_ADDR
        0x10: "",  # NUM_ROWS_WEIGHT_REG_ADDR
        0x14: "",  # NUM_COLS_WEIGHT_REG_ADDR
        0x18: "",  # REINPUT_REG_ADDR
        0x1C: "",  # REWEIGHT_REG_ADDR
        0x20: "",  # SAVEOUT_REG_ADDR
        0x24: "",  # USE_BIAS_REG_ADDR
        0x28: "",  # USE_SUMM_REG_ADDR
        0x2C: "",  # SHIFT_AMT_REG_ADDR
        0x30: "",  # ACT_FN_REG_ADDR
        0x34: "",  # BASE_MEMADDR_REG_ADDR
        0x38: "",  # RESULT_MEMADDR_REG_ADDR
        0x3C: "",  # MAINCTRL_INIT_REG_ADDR
        0x40: "",  # EXIT_CODE_REG_ADDR
    }

    def __init__(self, mem):
        self.mem = mem

    def csr_read(self, req):
        data = self.registers.get(req.addr)

        if data is None:
            return AXI4LiteRItem(data=0x00000000, resp=AXI4Result.SLVERR)
        
        return AXI4LiteRItem(data=data, resp=AXI4Result.OK)

    def csr_write(self, req, data):
        self.registers[req.addr] = data.data
        return AXI4LiteBItem(resp=AXI4Result.OK)

    def mem_read(self, req):
        return AXI4BurstRItem(id=0x69, data=([0xffffffff] * req.length), resp=([AXI4Result.SLVERR] * req.length))

    def mem_write(self, req, data):
        #TODO
        return AXI4BurstBItem(id=0x69, resp=([AXI4Result.SLVERR] * req.length))


class Memory:
    def __init__(self, size):
        self.mem = bytearray(size)

    def read_beats(self, address, length, size=AXI4Size.BYTES_4, burst=AXI4BurstMode.INCR):
        result = []
        beat_bytes = 1 << size.value

        for i in range(length):
            data = self.mem[address:address + beat_bytes][::-1]
            resp = AXI4Result.OK

            if len(data) != beat_bytes:
                data = data.zfill(beat_bytes)
                resp = AXI4Result.SLVERR

            result.append((int.from_bytes(data), resp))

            match burst:
                case AXI4BurstMode.FIXED:
                    pass
                case AXI4BurstMode.INCR:
                    address += beat_bytes
                case AXI4BURSTMode.WRAP:
                    address = (address + beat_bytes) % len(self.mem)

        return result

    def write_beats(self, address, beats, strobes, size=AXI4Size.BYTES_4, burst=AXI4BurstMode.INCR):
        result = []
        beat_bytes = 1 << size.value

        assert len(beats) == len(strobes)

        for i, data in enumerate(beats):
            if isinstance(data, int):
                data = data.to_bytes(beat_bytes)

            strobe = strobes[i]

            assert isinstance(data, (bytearray, bytes))
            assert isinstance(strobe, int) and not (strobe & ~((1 << beat_bytes) - 1))

            old = self.mem[address:address + beat_bytes][::-1].zfill(beat_bytes)
            data = data.zfill(beat_bytes)
            data = bytes(data[i] if strobe & (1 << i) else old[i] for i in range(beat_bytes))

            resp = AXI4Result.OK
            try:
                self.mem[address:address + beat_bytes] = data[::-1]
            except ValueError:
                resp = AXI4Result.SLVERR

            result.append(resp)

            match burst:
                case AXI4BurstMode.FIXED:
                    pass
                case AXI4BurstMode.INCR:
                    address += beat_bytes
                case AXI4BURSTMode.WRAP:
                    address = (address + beat_bytes) % len(self.mem)

        return result
    
    # Default data width is set to 16 bits, according to the current DUT configuration for INPUT_DATA_WIDTH.
    # Modify data_width here if the DUT configuration is updated.
    # Reference: https://opencehardware.github.io/ScaleNPU/block/configuration/#parameters
    def write_mem(self, addr, data, data_width=16):
        assert not (addr & ((data_width // 8) - 1))
        if isinstance(data, int):
            data = (data,)
        self.mem[addr:addr + (data_width // 8) * len(data)] = b''.join(val.to_bytes((data_width // 8), 'little') for val in data)

    def read_mem(self, addr, length=1, data_width=16):
        assert not (addr & ((data_width // 8) - 1))
        return [int.from_bytes(self.mem[addr + (data_width // 8) * i:addr + (data_width // 8) * (i + 1)], 'little') for i in range(length)]
