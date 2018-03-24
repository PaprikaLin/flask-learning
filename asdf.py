import os

for i, j in os.environ.items():
    print(i, j)

print(os.environ.get("AAA"))