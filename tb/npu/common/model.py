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
