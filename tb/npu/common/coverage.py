from cocotb_coverage.coverage import *


@CoverPoint("io.irq",
            bins=[True])
def irq(irq):
    pass


@CoverPoint("shape.input_rows",
            bins=[0, 2, 4, 6, 8, 'other'],
            bins_labels=['0', '2', '4', '6', '8', '> 8'],
            xf=lambda input_rows, input_cols, weight_rows, weight_cols: input_rows)
@CoverPoint("shape.input_cols",
            bins=[0, 2, 4, 6, 8, 'other'],
            bins_labels=['0', '2', '4', '6', '8', '> 8'],
            xf=lambda input_rows, input_cols, weight_rows, weight_cols: input_cols)
@CoverPoint("shape.weight_rows",
            bins=[0, 2, 4, 6, 8, 'other'],
            bins_labels=['0', '2', '4', '6', '8', '> 8'],
            xf=lambda input_rows, input_cols, weight_rows, weight_cols: weight_rows)
@CoverPoint("shape.weight_cols",
            bins=[0, 2, 4, 6, 8, 'other'],
            bins_labels=['0', '2', '4', '6', '8', '> 8'],
            xf=lambda input_rows, input_cols, weight_rows, weight_cols: weight_cols)
@CoverCross("shape.input_weight_rows_cols",
            items=["shape.input_rows",
                   "shape.input_cols",
                   "shape.weight_rows",
                   "shape.weight_cols"])
def shape(input_rows, input_cols, weight_rows, weight_cols):
    pass


@CoverPoint("features.shiftamt",
            bins=[0, 32, 'other'],
            bins_labels=['0', '32', '> 0 && < 32'],
            xf=lambda shiftamt, saveout, usebias, usesumm, reinputs, reweights, actfn:
                shiftamt if shiftamt in (0, 32) else 'other')
@CoverPoint("features.saveout",
            bins=[True, False],
            xf=lambda shiftamt, saveout, usebias, usesumm, reinputs, reweights, actfn:
                bool(saveout))
@CoverPoint("features.usebias",
            bins=[True, False],
            xf=lambda shiftamt, saveout, usebias, usesumm, reinputs, reweights, actfn:
                bool(usebias))
@CoverPoint("features.usesumm",
            bins=[True, False],
            xf=lambda shiftamt, saveout, usebias, usesumm, reinputs, reweights, actfn:
                bool(usesumm))
@CoverPoint("features.reinputs",
            bins=[True, False],
            xf=lambda shiftamt, saveout, usebias, usesumm, reinputs, reweights, actfn:
                bool(reinputs))
@CoverPoint("features.reweights",
            bins=[True, False],
            xf=lambda shiftamt, saveout, usebias, usesumm, reinputs, reweights, actfn:
                bool(reweights))
@CoverPoint("features.actfn",
            bins=[0, 1],
            bins_labels=['Off', 'ReLU'],
            xf=lambda shiftamt, saveout, usebias, usesumm, reinputs, reweights, actfn:
                int(actfn))
@CoverCross("features.all",
            items=["features.shiftamt",
                   "features.saveout",
                   "features.usebias",
                   "features.usesumm",
                   "features.reinputs",
                   "features.reweights",
                   "features.actfn"])
def features(shiftamt, saveout, usebias, usesumm, reinputs, reweights, actfn):
    pass
