import test
from xlutils.copy import copy

# 获取款式编号,选择款式编号所在的行
cols = test.sheetname.col_values(3)
cols = cols[1:]

code = {}
for m in cols:
    if m not in code:
        code[m] = []

# 添加尺码到字典的值，这里选尺码的位置
for i, j in enumerate(cols):
    temp = str(test.sheetname.cell(i + 1, 7))
    temp = temp[temp.index("'") + 1: -1].lower()
    code[j].append(temp)



for b, v in code.items():
    for x, y in enumerate(test.lst):
        if set(v).issubset(y):
            code[b] = x + 1




wbn = copy(test.workbook)
ws = wbn.get_sheet(0)

# 这里选择尺码组的位置
for i, j in enumerate(cols.cols):
    print(cols.code[j])
    ws.write(i + 1, 8, cols.code[j])
wbn.save(test.path)


# for a,b in d.items():
#     print(a,b)


