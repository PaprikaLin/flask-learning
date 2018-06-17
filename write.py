import xlrd
import cols
from xlutils.copy import copy
import test

wbn = copy(test.workbook)
ws = wbn.get_sheet(0)

# 这里选择尺码组的位置
for i, j in enumerate(cols.cols):
    print(cols.code[j])
    ws.write(i + 1, 8, cols.code[j])
wbn.save(test.path)



