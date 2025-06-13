from mk import *

hs_npu = find_package('hs_npu')

tb_test = CocotbTestPackage('tb_test')

tb_test.requires       (hs_npu)
tb_test.top            ('hs_npu_top_flat')
tb_test.cocotb_paths   (['.'])
tb_test.cocotb_modules (['tests'])
