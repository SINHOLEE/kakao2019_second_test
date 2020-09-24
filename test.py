arr = []

for i in range(3):
    for j in range(4):
        arr.append((i,j))

arr2 = [(i, j) for i in range(3) for j in range(4)]
print(arr)
print(arr2)