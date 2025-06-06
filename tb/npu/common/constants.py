from enum import Enum

class CSRMode(Enum):
    READ  = 0
    WRITE = 1

class AXI4LiteWriteResult(Enum):
    OK     = bin(0)
    EXOK   = bin(1)
    SLVERR = bin(2)
    DECERR = bin(3)