import xlrd
import test

# path = u'C:\\Users\\49931\Desktop\\test.xls'
# workbook = xlrd.open_workbook(path)
# sheet_names = workbook.sheet_names()
# sheetname = workbook.sheet_by_name(sheet_names[0])

# 获取款式编号,选择款式编号所在的行
cols = test.sheetname.col_values(2)
cols = cols[2:]

d = {}
for m in cols:
    if m not in d:
        d[m] = []

# 添加尺码到字典的值，这里选尺码的位置
for i, j in enumerate(cols):
    temp = str(test.sheetname.cell(i + 2, 5))
    temp = temp[temp.index("'") + 1: -1].lower()
    d[j].append(temp)



for b, v in d.items():
    for x, y in enumerate(test.lst):
        if set(v).issubset(y):
            d[b] = x + 1


# for a,b in d.items():
#     print(a,b)


