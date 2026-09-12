import numpy as np

M = 1000000

A = np.array([
    [1, 1, -1, 0, 1],
    [1, 2, 0, 1, 0]
], dtype=float)

b = np.array([4, 6], dtype=float)

c = np.array([3, 2, 0, 0, -M], dtype=float)

tableau = np.zeros((3, 7))
tableau[:2, :5] = A
tableau[:2, 5] = b
tableau[2, :5] = -c

tableau[2] += M * tableau[0]

basis = [4, 3]

while True:
    zj_cj = tableau[2, :5]

    if np.all(zj_cj >= 0):
        break

    entering = np.argmin(zj_cj)

    ratios = []
    for i in range(2):
        if tableau[i, entering] > 0:
            ratios.append(tableau[i, 5] / tableau[i, entering])
        else:
            ratios.append(float('inf'))

    leaving = np.argmin(ratios)

    pivot = tableau[leaving, entering]
    tableau[leaving] /= pivot

    for i in range(3):
        if i != leaving:
            tableau[i] -= tableau[i, entering] * tableau[leaving]

    basis[leaving] = entering

x = np.zeros(5)

for i in range(2):
    x[basis[i]] = tableau[i, 5]

print("x1 =", x[0])
print("x2 =", x[1])
print("Z =", tableau[2, 5])