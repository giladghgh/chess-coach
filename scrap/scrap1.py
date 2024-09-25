class Line(list):
    def __init__(self , *args):
        super().__init__()
        for arg in args:
            try:
                for item in arg:
                    super().append(item)
            except TypeError:
                super().append(arg)

        self.eval = None


    def __add__(self , this):
        return Line(self,this)


    def __repr__(self):
        return "L" + super().__repr__()





a = Line(1,2,3)
print("a:",type(a),a)

a.append(2)
print("a:",type(a),a)

a.append(Line(3))
a.append([5,6])
print("a:",type(a),a)
for aa in a:
    print("\t",type(aa),aa)



print()
print()



b = Line()
print("b:",type(b),b)

b.append(Line(0) + [0])
print("b:",type(b),b)

b += Line([1,2,3])
print("b:",type(b),b)

b.append(Line(4))
print("b:",type(b),b)

c = b + 8
print("c:", type(c), c)

c = b + [8]
print("c:",type(c),c)

c = b + Line(8)
print("c:",type(c),c)

c = b + Line([8])
print("c:",type(c),c)



print()
print()



d = Line(5)
print("d:",type(d),d)

e = d + [8]
print("e:",type(e),e)