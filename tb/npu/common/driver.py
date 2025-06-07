import pyuvm
import cocotb
from cocotb.queue import Queue
from cocotb.triggers import ClockCycles, RisingEdge
from pyuvm import *
from common.constants import *


class AXI4LiteDriver(uvm_driver):
    def __init__(self, name="AXI4LiteDriver", parent=None):
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
