import pyuvm
import cocotb
from pyuvm import *
from common.sequences import *


class NPUModel:
    def csr_read(self, request):
        #TODO
        return AXI4LiteRItem(data=0xffffffff, resp=AXI4Result.SLVERR)

    def csr_write(self, request, data):
        #TODO
        return AXI4LiteBItem(resp=AXI4Result.SLVERR)


class Memory:
    def __init__(self, size):
        self.mem = bytearray(size)

    def read_beats(self, address, length, size=AXI4Size.BYTES_4, burst=AXI4BurstMode.INCR):
        result = []
        beat_bytes = 1 << size.value

        for i in range(length):
            data = self.mem[address + beat_bytes - 1:address - 1:-1]
            resp = AXI4Result.OK

            if len(data) != beat_bytes:
                data = data.zfill(beat_bytes)
                resp = AXI4Result.SLVERR

            result.append((data, resp))

            match burst:
                case AXI4BurstMode.FIXED:
                    pass
                case AXI4BurstMode.INCR:
                    address += beat_bytes
                case AXI4BURSTMode.WRAP:
                    address = (address + beat_bytes) % len(self.mem)

        return result

    def write_beats(self, address, data, size=AXI4Size.BYTES_4, burst=AXI4BurstMode.INCR):
        result = []
        beat_bytes = 1 << size.value

        for data in range(resp):
            if isinstance(data, int):
                data = data.to_bytes(beat_bytes)

            assert isinstance(data, (bytearray, bytes))

            resp = AXI4Result.OK
            try:
                self.mem[address + beat_bytes - 1:address - 1:-1] = data
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
