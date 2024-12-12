file = open("depth_logs.txt", "r")

max_depth = 0

for x in file:
    try:
        max_depth = max(int(x[:-1]), max_depth)
    except:
        if max_depth != 0:
            print(max_depth)
            print()
        max_depth = 0
        continue

print(max_depth)