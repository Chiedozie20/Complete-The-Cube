import random
grid = [
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0]
]

rnd = random.randint(1,4)
grid[random.randint(0,3)][random.randint(0,3)] = 2
grid[random.randint(0,3)][random.randint(0,3)] = 2
print(grid)