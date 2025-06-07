from enum import Enum


class CSRMode(Enum):
    READ  = 0
    WRITE = 1


class AXI4Result(Enum):
    OK     = 0
    EXOK   = 1
    SLVERR = 2
    DECERR = 3


class AXI4Prot(Enum):
    DATA_SECURE_UNPRIV    = 0b000
    DATA_SECURE_PRIV      = 0b001
    DATA_NONSECURE_UNPRIV = 0b010
    DATA_NONSECURE_PRIV   = 0b011
    CODE_SECURE_UNPRIV    = 0b100
    CODE_SECURE_PRIV      = 0b101
    CODE_NONSECURE_UNPRIV = 0b110
    CODE_NONSECURE_PRIV   = 0b111


class AXI4Size(Enum):
    BYTES_1   = 0
    BYTES_2   = 1
    BYTES_4   = 2
    BYTES_8   = 3
    BYTES_16  = 4
    BYTES_32  = 5
    BYTES_64  = 6
    BYTES_128 = 7


class AXI4BurstMode(Enum):
    FIXED = 0
    INCR  = 1
    WRAP  = 2
