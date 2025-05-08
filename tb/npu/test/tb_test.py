import cocotb
import pyuvm
from cocotb.triggers import Timer
from pyuvm import *

from cocotbext.axi import AxiBus, AxiMaster

class ClockGen(uvm_component):
    def build_phase(self):
        # Retrieve 'clk' from config DB
        self.clk = ConfigDB().get(self, "", "clk")

    async def run_phase(self):
        self.logger.info("Clock generation started.")
        while True:
            self.clk = 0
            await Timer(5, units="ns")
            self.clk = 1
            await Timer(5, units="ns")

class ClockEnv(uvm_env):
    def build_phase(self):
        self.clock_gen = ClockGen("clock_gen", self)

        ConfigDB().set(self.clock_gen, "", "clk", 69)

@pyuvm.test()
class ClockTest(uvm_test):
    def build_phase(self):

        # Instantiate the environment
        self.env = ClockEnv("env", self)
    
    async def run_phase(self):
        self.raise_objection()
        self.logger.info("ClockTest starting run_phase.")
        await Timer(100, units="ns")
        self.logger.info("ClockTest completed run_phase.")
        self.drop_objection()
