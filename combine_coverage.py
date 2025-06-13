import logging
import glob
from cocotb_coverage.coverage import *

merge_coverage(logging.info, 'coverage.combined.xml', *glob.glob('coverage.*.xml'))
