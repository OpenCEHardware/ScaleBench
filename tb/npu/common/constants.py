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
    DATA_SECURE_UNPRIV    = 0
    DATA_SECURE_PRIV      = 1
    DATA_NONSECURE_UNPRIV = 2
    DATA_NONSECURE_PRIV   = 3
    CODE_SECURE_UNPRIV    = 4
    CODE_SECURE_PRIV      = 5
    CODE_NONSECURE_UNPRIV = 6
    CODE_NONSECURE_PRIV   = 7
