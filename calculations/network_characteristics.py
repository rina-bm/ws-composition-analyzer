import numpy as np
import math

def check_conditions(lamda, mu, k):
    if not (len(lamda) == len(mu) == len(k)):
        raise ValueError("Размерности lamda, mu и k не совпадают")
    for i in range(len(lamda)):
        if lamda[i] < 0:
            raise ValueError(f"Отрицательная интенсивность потока в системе {i+1}: {lamda[i]}")
        if lamda[i] >= (k[i]*mu[i]):
            raise ValueError(f"Нарушено условие стационарности для системы {i+1}")    
    return True

def get_w(matrix):
    N = matrix.shape[0]
    T_matrix = matrix.transpose()
    for i in range(N):
        T_matrix[i, i] -= 1
    T_matrix[-1] = np.ones(N)
    v1 = np.zeros(N)
    v1[-1] = 1.0
    w = np.linalg.solve(T_matrix, v1)
    return w

def get_lamda(w, lamda_zero, N):
    lamda = []
    for i in range(1, N+1):
        value = w[i] * lamda_zero / w[0]
        if value < 0:
            raise ValueError(f"Отрицательная интенсивность потока в системе {i+1}: lamda[{i}] = {lamda[i]}")
        lamda.append(value)
    return lamda

