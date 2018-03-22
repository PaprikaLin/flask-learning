import xlrd
import cols
from xlutils.copy import copy
import test

# path = u'C:\\Users\\49931\Desktop\\test.xls'
# workbook = xlrd.open_workbook(path)
# sheet_names = workbook.sheet_names()
# sheetname = workbook.sheet_by_name(sheet_names[0])
wbn = copy(test.workbook)
ws = wbn.get_sheet(0)

# 这里选择尺码组的位置
for i, j in enumerate(cols.cols):
    print(cols.d[j])
    ws.write(i + 2, 6, cols.d[j])
wbn.save(test.path)



