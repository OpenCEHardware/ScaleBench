# test_hello.py
import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def hello_test(dut):
    cocotb.log.info("¡Hola desde cocotb!")
    await Timer(1, units='ns')
