import __builtin__

for x in dir(__builtin__):
    if x.endswith("Error"):
        print(x)