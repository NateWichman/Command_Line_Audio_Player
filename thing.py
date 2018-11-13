class Thing:
    def __init__(self, num):
        self.num = num
    def __add__(self, othernum):
        return self.num + othernum.num

a=Thing(42)
b=Thing(24)
c = a+b
print("a+b = ", c)
