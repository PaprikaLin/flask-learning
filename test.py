import xlrd

path = u'C:\\Users\\49931\Desktop\\21852.xls'
workbook = xlrd.open_workbook(path)
sheet_names = workbook.sheet_names()
sheetname = workbook.sheet_by_name(sheet_names[0])
#row = sheetname.row_values(1)
# = sheetname.col_values(6)


path1 = u'C:\\Users\\49931\Desktop\\size.xls'
workbook1 = xlrd.open_workbook(path1)
sheet_names1 = workbook1.sheet_names()
sheetname1 = workbook1.sheet_by_name(sheet_names1[0])
# row1 = sheetname1.row_values(0, start_colx=1)
# print(row1, len(row1))
# for i in row1:
#     if '' in row1:
#         row1.remove('')
# s1 = row1
lst = []
for i in range(19):
    a = sheetname1.row_values(i, start_colx=1)
    for j,k in enumerate(a):
        a[j] = str(k).lower()
        if '' in a:
            a.remove('')
    lst.append(a)

for m in lst:
    for n in range(m.count('')):
        m.remove('')






