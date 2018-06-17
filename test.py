import xlrd
from xlutils.copy import copy
# 打开目标文件
path = u'C:\\Users\\49931\Desktop\\13852.xls'
workbook = xlrd.open_workbook(path)
sheet_names = workbook.sheet_names()
sheetname = workbook.sheet_by_name(sheet_names[0])


# 打开尺码组编号文件
path1 = u'C:\\Users\\49931\Desktop\\size.xls'
workbook1 = xlrd.open_workbook(path1)
sheet_names1 = workbook1.sheet_names()
sheetname1 = workbook1.sheet_by_name(sheet_names1[0])

# 获取尺码组编号，存在lst 列表里面
lst = []
for i in range(19):
    a = sheetname1.row_values(i, start_colx=1)
    for j,k in enumerate(a):
        a[j] = str(k).lower()
        if '' in a:
            a.remove('')
    lst.append(a)

# 列表去重
for m in lst:
    for n in range(m.count('')):
        m.remove('')

d = {}
for num in range(1,20):
    d[str(num)] = lst[num - 1]
for key,value in d.items():
    print(key, value)



# 获取款式编号,选择款式编号所在的行
cols = sheetname.col_values(1)
cols = cols[1:]

code = {}
for m in cols:
    if m not in code:
        code[m] = []

# 添加尺码到字典的值，这里选尺码的位置
for i, j in enumerate(cols):
    temp = str(sheetname.cell(i + 1, 6))
    temp = temp[temp.index("'") + 1: -1].lower()
    code[j].append(temp)

for b, v in code.items():
    for x, y in enumerate(lst):
        if set(v).issubset(y):
            code[b] = x + 1

wbn = copy(workbook)
ws = wbn.get_sheet(0)

# 这里选择尺码组的位置
for i, j in enumerate(cols):
    print(code[j])
    ws.write(i + 1, 7, code[j])
wbn.save(path)








