from cocotb_coverage.coverage import *


@CoverPoint("io.irq",
            bins=[True],
            bins_labels=['done'])
def irq(irq):
    pass


@CoverPoint("shape.input_rows",
            bins=[0, 2, 4, 6, 8, 'other'],
            bins_labels=['0', '2', '4', '6', '8', '> 8'],
            xf=lambda input_rows, input_cols, weight_rows, weight_cols:
                input_rows if input_rows <= 8 else 'other')
@CoverPoint("shape.input_cols",
            bins=[0, 2, 4, 6, 8, 'other'],
            bins_labels=['0', '2', '4', '6', '8', '> 8'],
            xf=lambda input_rows, input_cols, weight_rows, weight_cols:
                input_cols if input_cols <= 8 else 'other')
@CoverPoint("shape.weight_rows",
            bins=[0, 2, 4, 6, 8, 'other'],
            bins_labels=['0', '2', '4', '6', '8', '> 8'],
            xf=lambda input_rows, input_cols, weight_rows, weight_cols:
                weight_rows if weight_rows <= 8 else 'other')
@CoverPoint("shape.weight_cols",
            bins=[0, 2, 4, 6, 8, 'other'],
            bins_labels=['0', '2', '4', '6', '8', '> 8'],
            xf=lambda input_rows, input_cols, weight_rows, weight_cols:
                weight_cols if weight_cols <= 8 else 'other')
def shape(input_rows, input_cols, weight_rows, weight_cols):
    pass


@CoverPoint("features.shiftamt",
            bins=[0, 32, 'other'],
            bins_labels=['0', '32', '> 0 && < 32'],
            xf=lambda shiftamt, saveout, usebias, usesumm, reinputs, reweights, actfn:
                shiftamt if shiftamt in (0, 32) else 'other')
@CoverPoint("features.saveout",
            bins=[True, False],
            bins_labels=['Save', 'NoSave'],
            xf=lambda shiftamt, saveout, usebias, usesumm, reinputs, reweights, actfn:
                bool(saveout))
@CoverPoint("features.usebias",
            bins=[True, False],
            bins_labels=['UseBias', 'NoBias'],
            xf=lambda shiftamt, saveout, usebias, usesumm, reinputs, reweights, actfn:
                bool(usebias))
@CoverPoint("features.usesumm",
            bins=[True, False],
            bins_labels=['UseSumm', 'NoSumm'],
            xf=lambda shiftamt, saveout, usebias, usesumm, reinputs, reweights, actfn:
                bool(usesumm))
@CoverPoint("features.reinputs",
            bins=[True, False],
            bins_labels=['ReuseInputs', 'NewInputs'],
            xf=lambda shiftamt, saveout, usebias, usesumm, reinputs, reweights, actfn:
                bool(reinputs))
@CoverPoint("features.reweights",
            bins=[True, False],
            bins_labels=['ReuseWeights', 'NewWeights'],
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
