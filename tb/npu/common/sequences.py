import pyuvm
import cocotb
from cocotb.queue import Queue
from cocotb.triggers import RisingEdge, with_timeout, ClockCycles
from pyuvm import *
from common.constants import *
from common.seq_items import *


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


class NPUBaseSequence(uvm_sequence, uvm_report_object):

    def __init__(self, name="NPUBaseSequence"):
        super().__init__(name)
        self.reg_block = ConfigDB().get(None, "", "reg_block")
        self.dut = ConfigDB().get(None, "", "dut")
    
    async def body(self):
        raise UVMNotImplemented

    async def execute_query(self, mem_item, csr_item):

        # await RisingEdge(self.dut.rst_n)

        self.logger.info("STARTING OPERATION")

        await self.load_csr(csr_item)

        await self.load_mem(mem_item)

        await self.reg_write(self.reg_block.INIT, 1)

        await self.wait_irq()

        exit_code = await self.reg_read(self.reg_block.EXITCODE)

        self.logger.info(f"EXIT_CODE: {exit_code}")

        await self.reg_write(self.reg_block.IRQ, 1)

    async def load_csr(self, item):

        # self.logger.info(item)

        for reg, mode, value in item.operations:

            if mode == CSRMode.READ:
                await self.reg_read(reg)

            elif mode == CSRMode.WRITE:
                await self.reg_write(reg, value)

    async def load_mem(self, item):
        mem = ConfigDB().get(None, "", "mem")

        base_addr = await self.reg_read(self.reg_block.BASE)
        input_rows = await self.reg_read(self.reg_block.INROWS)
        input_cols = await self.reg_read(self.reg_block.INCOLS)
        weight_rows = await self.reg_read(self.reg_block.WGHTROWS)
        weight_cols = await self.reg_read(self.reg_block.WGHTCOLS)

        # self.logger.info(item)

        for index, data in enumerate(item.weights):
            i = index // weight_cols
            j = index % weight_cols
            mem.write_weight(base_addr, i, j, data, weight_rows, weight_cols)

        for index, data in enumerate(item.inputs):
            i = index // input_cols
            j = index % input_cols
            mem.write_input(base_addr, i, j, data, weight_rows, weight_cols, input_cols)

        for index, data in enumerate(item.bias):
            mem.write_bias(base_addr, index, data, weight_rows, weight_cols, input_cols, input_rows)

        for index, data in enumerate(item.summ):
            mem.write_summ(base_addr, index, data, weight_rows, weight_cols, input_cols, input_rows)

    async def reg_write(self, reg, value):
        resp = await reg.write(value, self.reg_block.def_map, path_t.FRONTDOOR, check_t.NO_CHECK)
        assert resp == status_t.IS_OK
    
    async def reg_read(self, reg):
        resp, data = await reg.read(self.reg_block.def_map, path_t.FRONTDOOR, check_t.NO_CHECK)
        assert resp == status_t.IS_OK
        return data

    async def wait_irq(self, cycles=10000):
        try:
            await with_timeout(RisingEdge(self.dut.irq), timeout_time=cycles * NPUArch.CLK_PERIOD)
            self.logger.info("OPERATION FINISHED")
        except cocotb.result.SimTimeoutError:
            self.logger.error(f"IRQ TIMEOUT AFTER: {cycles} cycles")
            ConfigDB().set(None, "", "error", True)
    
    async def reset(self):
        self.logger.info("RESETTING NPU")
        self.dut.rst_n.value = 0
        await ClockCycles(self.dut.clk_npu, 5)
        self.dut.rst_n.value = 1


class BasicQuerySeq(NPUBaseSequence):

    def __init__(self, name, mem_item, csr_item):
        super().__init__(name)
        self.mem_item = mem_item
        self.csr_item = csr_item

    async def body(self):
        await self.execute_query(self.mem_item, self.csr_item)
