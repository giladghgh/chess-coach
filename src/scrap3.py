a = ["1","a","b"]#,"2","c","d","3","e","f","4","g"]

print(a)
print()

print(a[0::3])
print(a[1::3])
print(a[2::3])
print()

b = list(zip(
    a[0::3],
    a[1::3],
    a[2::3]
))
if len(a)%3:
    b.append(tuple(a[-2:]))
print(b)