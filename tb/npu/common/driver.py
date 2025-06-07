import pyuvm
import cocotb
from cocotb.queue import Queue
from cocotb.triggers import ClockCycles, RisingEdge, ReadWrite
from pyuvm import *
from common.constants import *
from common.sequences import *


class AXI4LiteMasterDriver(uvm_driver):
    def __init__(self, name="AXI4LiteMasterDriver", parent=None):
        super().__init__(name, parent)

        self.aw = Queue()
        self.ar = Queue()
        self.w = Queue()
        self.r = Queue()
        self.b = Queue()

    def build_phase(self):
        self.clk = ConfigDB().get(self, "", "clk")
        self.rst_n = ConfigDB().get(self, "", "rst_n")

        self.vif = ConfigDB().get(self, "", "vif")
        self.vif_name = ConfigDB().get(self, "", "vif_name")

        self.arready = self.get_axi_signal('arready')
        self.arvalid = self.get_axi_signal('arvalid')
        self.araddr = self.get_axi_signal('araddr')
        self.arprot = self.get_axi_signal('arprot')

        self.awready = self.get_axi_signal('awready')
        self.awvalid = self.get_axi_signal('awvalid')
        self.awaddr = self.get_axi_signal('awaddr')
        self.awprot = self.get_axi_signal('awprot')

        self.wready = self.get_axi_signal('wready')
        self.wvalid = self.get_axi_signal('wvalid')
        self.wdata = self.get_axi_signal('wdata')
        self.wstrb = self.get_axi_signal('wstrb')

        self.rready = self.get_axi_signal('rready')
        self.rvalid = self.get_axi_signal('rvalid')
        self.rdata = self.get_axi_signal('rdata')
        self.rresp = self.get_axi_signal('rresp')

        self.bready = self.get_axi_signal('bready')
        self.bvalid = self.get_axi_signal('bvalid')
        self.bresp = self.get_axi_signal('bresp')

    async def run_phase(self):
        self.arvalid.value = 0
        self.awvalid.value = 0
        self.wvalid.value = 0
        self.bready.value = 0
        self.rready.value = 0

        cocotb.start_soon(self.req_main(self.ar, self.r, self.arready, self.arvalid, self.araddr, self.arprot, access_e.UVM_READ))
        cocotb.start_soon(self.req_main(self.aw, self.b, self.awready, self.awvalid, self.awaddr, self.awprot, access_e.UVM_WRITE))
        cocotb.start_soon(self.w_main())
        cocotb.start_soon(self.resp_main(self.r, self.rready, self.rvalid, self.rdata, self.rresp, access_e.UVM_READ))
        cocotb.start_soon(self.resp_main(self.b, self.bready, self.bvalid, None,       self.bresp, access_e.UVM_WRITE))

        while True:
            req = await self.seq_item_port.get_next_item()
            self.seq_item_port.item_done()

            if req.access == access_e.UVM_WRITE:
                await self.aw.put(req)
                await self.w.put(req)
            else:
                await self.ar.put(req)

    async def req_main(self, req_channel, resp_channel, ready, valid, addr, prot, access):
        while True:
            req = await req_channel.get()
            assert req.access == access

            addr.value = req.addr
            prot.value = req.prot.value
            valid.value = 1

            while True:
                await RisingEdge(self.clk)
                if self.rst_n.value and ready.value:
                    break

            valid.value = 0

            resp = req.clone()
            resp.set_id_info(req)

            await resp_channel.put(resp)

    async def w_main(self):
        while True:
            req = await self.w.get()
            assert req.access == access_e.UVM_WRITE

            self.wdata.value = req.wdata
            self.wstrb.value = req.wstrb
            self.wvalid.value = 1

            while True:
                await RisingEdge(self.clk)
                if self.rst_n.value and self.wready.value:
                    break

            self.wvalid.value = 0

    async def resp_main(self, queue, ready, valid, data, resp, access):
        while True:
            req = await queue.get()
            assert req.access == access

            ready.value = 1
            while True:
                await RisingEdge(self.clk)
                if self.rst_n.value and valid.value:
                    break

            req.resp = AXI4Result(resp.value)
            if data is not None:
                req.rdata = data.value

            self.seq_item_port.put_response(req)

            ready.value = 0

    def get_axi_signal(self, name):
        return getattr(self.vif, f"{self.vif_name}_{name}")


class AXI4BurstSlaveDriver(uvm_driver):
    def __init__(self, name="AXI4BurstSlaveDriver", parent=None):
        super().__init__(name, parent)

        self.aw = Queue()
        self.ar = Queue()
        self.w = Queue()
        self.r = Queue()
        self.b = Queue()

    def build_phase(self):
        self.clk = ConfigDB().get(self, "", "clk")
        self.rst_n = ConfigDB().get(self, "", "rst_n")

        self.vif = ConfigDB().get(self, "", "vif")
        self.vif_name = ConfigDB().get(self, "", "vif_name")

        self.arready = self.get_axi_signal('arready')
        self.arvalid = self.get_axi_signal('arvalid')
        self.araddr = self.get_axi_signal('araddr')
        self.arprot = self.get_axi_signal('arprot')
        self.arid = self.get_axi_signal('arid')
        self.arlen = self.get_axi_signal('arlen')
        self.arsize = self.get_axi_signal('arsize')
        self.arburst = self.get_axi_signal('arburst')

        self.awready = self.get_axi_signal('awready')
        self.awvalid = self.get_axi_signal('awvalid')
        self.awaddr = self.get_axi_signal('awaddr')
        self.awprot = self.get_axi_signal('awprot')
        self.awid = self.get_axi_signal('awid')
        self.awlen = self.get_axi_signal('awlen')
        self.awsize = self.get_axi_signal('awsize')
        self.awburst = self.get_axi_signal('awburst')

        self.wready = self.get_axi_signal('wready')
        self.wvalid = self.get_axi_signal('wvalid')
        self.wdata = self.get_axi_signal('wdata')
        self.wstrb = self.get_axi_signal('wstrb')
        self.wlast = self.get_axi_signal('wlast')

        self.rready = self.get_axi_signal('rready')
        self.rvalid = self.get_axi_signal('rvalid')
        self.rdata = self.get_axi_signal('rdata')
        self.rresp = self.get_axi_signal('rresp')
        self.rid = self.get_axi_signal('rid')
        self.rlast = self.get_axi_signal('rlast')

        self.bready = self.get_axi_signal('bready')
        self.bvalid = self.get_axi_signal('bvalid')
        self.bresp = self.get_axi_signal('bresp')
        self.bid = self.get_axi_signal('bid')

    async def run_phase(self):
        self.arready.value = 0
        self.awready.value = 0
        self.wready.value = 0
        self.bvalid.value = 0
        self.rvalid.value = 0

        cocotb.start_soon(self.ready_main(self.ar, self.arready, self.arvalid, lambda resp: resp.ar_delays))
        cocotb.start_soon(self.ready_main(self.aw, self.awready, self.awvalid, lambda resp: resp.aw_delays))
        cocotb.start_soon(self.ready_main(self.w,  self.awready, self.awvalid, lambda resp: resp.w_delays))
        cocotb.start_soon(self.r_main())
        cocotb.start_soon(self.b_main())

        while True:
            resp = await self.seq_item_port.get_next_item()
            self.seq_item_port.item_done()

            if isinstance(resp, AXI4BurstReady):
                await self.ar.put(resp)
                await self.aw.put(resp)
                await self.w.put(resp)
            elif resp.access == access_e.UVM_WRITE:
                await self.b.put(resp)
            else:
                await self.r.put(resp)

    async def ready_main(self, ready_channel, ready, valid, get_channel_delays):
        while True:
            resp = await ready_channel.get()

            for delay in get_channel_delays(resp):
                while True:
                    await ReadWrite()

                    if self.rst_n.value and valid.value:
                        break

                    await RisingEdge(self.clk)

                await ClockCycles(self.clk, delay)

                ready.value = 1
                await RisingEdge(self.clk)
                ready.value = 0

    async def r_main(self):
        while True:
            resp = await self.r.get()
            assert resp.access == access_e.UVM_READ

            assert len(resp.rdata) >= 0
            assert len(resp.rdata) > 0 and len(resp.resp_delays) == len(resp.rdata)

            for i, data in enumerate(resp.rdata):
                await ClockCycles(self.clk, resp.resp_delays[i])

                self.rid.value = resp.id
                self.rdata.value = data
                self.rlast.value = i == len(resp.rdata) - 1
                self.rvalid.value = 1

                while True:
                    await RisingEdge(self.clk)
                    if self.rst_n.value and self.rready.value:
                        break

                self.rvalid.value = 0

    async def b_main(self):
        while True:
            resp = await self.b.get()
            assert resp.access == access_e.UVM_WRITE
            assert len(resp.resp_delays) == 1

            await ClockCycles(self.dut, resp.resp_delays[0])

            self.bid.value = resp.id
            self.bvalid.value = 1

            while True:
                await RisingEdge(self.clk)
                if self.rst_n.value and self.bready.value:
                    break

            self.bvalid.value = 0

    def get_axi_signal(self, name):
        return getattr(self.vif, f"{self.vif_name}_{name}")
