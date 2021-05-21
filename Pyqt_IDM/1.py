import numpy as np

def mse(x):
    sum = 0
    for i in range(3):
        sum+=(x[i]-x.mean())**2
    return sum/3


x1 = np.array([40, 50, 55])
x2 = np.array([60, 70, 74])
print(mse(x1)+mse(x2))
