class Data_test():
    day = 0
    month = 0
    year = 0

    def __init__(self, year=0, month=0, day=0):
        self.year = year
        self.day = day
        self.month = month

    @classmethod
    def get_date(cls, string_date):
        year, month, day=map(int, string_date('-'))
        date1 = cls(year, month, day)
        return date1

    def out_date(self):
        print('year:' + str(self.year) + ' month:' + str(self.month) + ' day:' + str(self.day))

r = Data_test()
print(r.get_date())

