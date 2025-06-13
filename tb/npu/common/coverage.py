from cocotb_coverage.coverage import *


@CoverPoint("io.irq",
            bins=[True])
def irq(irq):
    pass


@CoverPoint("shape.weight_rows",
            bins=[0, 2, 4, 6, 8, 'other'],
            bins_labels=['0', '2', '4', '6', '8', '> 8'],
            xf=lambda n: n if 0 <= n <= 8 else 'other')
def weight_rows(n):
    pass


@CoverPoint("shape.weight_cols",
            bins=[0, 2, 4, 6, 8, 'other'],
            bins_labels=['0', '2', '4', '6', '8', '> 8'],
            xf=lambda n: n if 0 <= n <= 8 else 'other')
def weight_cols(n):
    pass


@CoverPoint("shape.input_rows",
            bins=[0, 2, 4, 6, 8, 'other'],
            bins_labels=['0', '2', '4', '6', '8', '> 8'],
            xf=lambda n: n if 0 <= n <= 8 else 'other')
def input_rows(n):
    pass


@CoverPoint("shape.input_cols",
            bins=[0, 2, 4, 6, 8, 'other'],
            bins_labels=['0', '2', '4', '6', '8', '> 8'],
            xf=lambda n: n if 0 <= n <= 8 else 'other')
def input_cols(n):
    pass


@CoverPoint("csr.shiftamt",
            bins=[0, 32, 'other'],
            bins_labels=['0', '32', '> 0 && < 32'],
            xf=lambda n: n if n in (0, 32) else 'other')
def shiftamt(n):
    pass


@CoverPoint("csr.saveout",
            bins=[True, False],
            xf=lambda x: bool(x))
def saveout(saveout):
    pass


@CoverPoint("csr.usebias",
            bins=[True, False],
            xf=lambda x: bool(x))
def usebias(usebias):
    pass


@CoverPoint("csr.usesumm",
            bins=[True, False],
            xf=lambda x: bool(x))
def usesumm(usesumm):
    pass


@CoverPoint("csr.reinputs",
            bins=[True, False],
            xf=lambda x: bool(x))
def reinputs(reinputs):
    pass


@CoverPoint("csr.reweights",
            bins=[True, False],
            xf=lambda x: bool(x))
def reweights(reweights):
    pass


@CoverPoint("csr.actfn",
            bins=[0, 1],
            bins_labels=['Off', 'ReLU'],
            xf=lambda x: int(x))
def actfn(actfn):
    pass
