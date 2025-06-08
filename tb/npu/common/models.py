import pyuvm
import cocotb
from pyuvm import *
from common.sequences import *


class NPUModel:
    def csr_read(self, req):
        #TODO
        return AXI4LiteRItem(data=0xffffffff, resp=AXI4Result.SLVERR)

    def csr_write(self, req, data):
        #TODO
        return AXI4LiteBItem(resp=AXI4Result.SLVERR)

    def mem_read(self, req):
        #TODO
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
