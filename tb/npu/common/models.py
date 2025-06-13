import pyuvm
import cocotb
from pyuvm import *
from common.sequences import *
from common.constants import *


class NPUModel:

    registers = {
        0x00: 0xB00B,  # ARCHID_REG_ADDR
        0x04: 0x100,  # IMPID_REG_ADDR
        0x08: 0x0,  # NUM_ROWS_INPUT_REG_ADDR
        0x0C: 0x0,  # NUM_COLS_INPUT_REG_ADDR
        0x10: 0x0,  # NUM_ROWS_WEIGHT_REG_ADDR
        0x14: 0x0,  # NUM_COLS_WEIGHT_REG_ADDR
        0x18: 0x0,  # REINPUT_REG_ADDR
        0x1C: 0x0,  # REWEIGHT_REG_ADDR
        0x20: 0x0,  # SAVEOUT_REG_ADDR
        0x24: 0x0,  # USE_BIAS_REG_ADDR
        0x28: 0x0,  # USE_SUMM_REG_ADDR
        0x2C: 0x0,  # SHIFT_AMT_REG_ADDR
        0x30: 0x0,  # ACT_FN_REG_ADDR
        0x34: 0x0,  # BASE_MEMADDR_REG_ADDR
        0x38: 0x0,  # RESULT_MEMADDR_REG_ADDR
        0x3C: 0x0,  # INIT_REG_ADDR
        0x40: 0x0,  # IRQ_REG_ADDR
        0x44: 0x0,  # EXIT_CODE_REG_ADDR
    }

    def __init__(self, mem):
        self.mem = mem
        self.last_result = None

    def csr_read(self, req):
        data = self.registers.get(req.addr)

        if data is None:
            return AXI4LiteRItem(data=0x00000000, resp=AXI4Result.SLVERR)
        
        return AXI4LiteRItem(data=data, resp=AXI4Result.OK)

    def csr_write(self, req, data):

        if req.addr == 0x40 and (data.data & 1):
            self.registers[req.addr] = 0
        else:
            self.registers[req.addr] = data.data

        # init
        if req.addr == 0x3C and (data.data & 1):
            self.shift = int(self.registers[0x2c])
            self.input_rows = int(self.registers[0x08])
            self.input_cols = int(self.registers[0x0c])
            self.weight_rows = int(self.registers[0x10])
            self.weight_cols = int(self.registers[0x14])
            self.reinputs = int(self.registers[0x18])

            addr = int(self.registers[0x34])

            self.weights = self.mem.read_mem(addr, length=(self.weight_rows * self.weight_cols), data_width=NPUArch.WEIGHT_DATA_WIDTH, signed=True)
            addr += self.weight_rows * self.weight_cols * 1

            self.weights = [self.weights[(self.weight_rows - i - 1) * self.weight_cols + j] for i in range(self.weight_rows) for j in range(self.weight_cols)]

            if self.reinputs:
                self.inputs = self.last_result
            else:
                self.inputs = self.mem.read_mem(addr, length=(self.input_rows * self.input_cols), data_width=NPUArch.INPUT_DATA_WIDTH, signed=True)
                addr += self.input_rows * self.input_cols * 1

            self.last_result = None

            if int(self.registers[0x24]) & 1: #USEBIAS
                self.bias = self.mem.read_mem(addr, length=self.input_cols, data_width=NPUArch.OUTPUT_DATA_WIDTH, signed=True)
                addr += self.input_cols * 4
            else:
                self.bias = [0] * self.input_cols

            if int(self.registers[0x28]) & 1: #USESUMM
                self.summ = self.mem.read_mem(addr, length=self.input_cols, data_width=NPUArch.OUTPUT_DATA_WIDTH, signed=True)
            else:
                self.summ = [0] * self.input_cols

        return AXI4LiteBItem(resp=AXI4Result.OK)

    def get_result_address(self):
        return int(self.registers[0x38])

    def get_result_length(self):
        return int(self.weight_rows * self.input_cols)

    def interrupt(self):
        assert self.input_cols == self.weight_rows

        if not self.registers[0x20]:
            return [0] * (self.input_rows * self.weight_cols)

        matrix = []
        for row in range(self.input_rows):
            for col in range(self.weight_cols):
                product = 0

                for i in range(self.weight_rows):
                    product += self.inputs[row * self.input_cols + i] * self.weights[i * self.weight_cols + col]

                if col < len(self.bias):
                    product += self.bias[col] + self.summ[col]

                if self.registers[0x30]:
                    if product < 0:
                        product = 0

                product >>= self.shift

                # Pasa de 16 bits con signo a 32
                product = product & 0xffff
                if product & 0x8000:
                    product -= 0x10000

                matrix.append(product)

        self.last_result = matrix

    def predict_result(self):
        assert isinstance(self.last_result, list)
        return self.last_result.copy()


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
    
    def write_mem(self, addr, data, data_width=NPUArch.INPUT_DATA_WIDTH):
        assert not (addr & ((data_width // 8) - 1))
        if isinstance(data, int):
            data = (data,)
        self.mem[addr:addr + (data_width // 8) * len(data)] = b''.join(val.to_bytes((data_width // 8), 'little') for val in data)

    def read_mem(self, addr, length=1, data_width=NPUArch.INPUT_DATA_WIDTH, signed=False):
        assert not (addr & ((data_width // 8) - 1))

        data = []
        for i in range(length):
            read = int.from_bytes(self.mem[addr + (data_width // 8) * i:addr + (data_width // 8) * (i + 1)], 'little')
            if signed and (read & (1 << (data_width - 1))):
                read -= 1 << data_width

            data.append(read)

        return data

    def write_weight(self, base, i, j, data, weight_rows, weight_cols):
        self.write_mem(base + (weight_rows - i - 1) * weight_cols + j, data, data_width=NPUArch.WEIGHT_DATA_WIDTH)

    def write_input(self, base, i, j, data, weight_rows, weight_cols, input_cols):
        self.write_mem(base + weight_rows * weight_cols + i * input_cols + j, data, data_width=NPUArch.INPUT_DATA_WIDTH)

    def write_bias(self, base, i, data, weight_rows, weight_cols, input_cols, input_rows):
        self.write_mem(base + weight_rows * weight_cols + input_rows * input_cols + i * 4, data, data_width=NPUArch.OUTPUT_DATA_WIDTH)

    def write_summ(self, base, i, data, weight_rows, weight_cols, input_cols, input_rows):
        self.write_mem(base + weight_rows * weight_cols + input_cols * (input_rows + 1) + i * 4, data, data_width=NPUArch.OUTPUT_DATA_WIDTH)
