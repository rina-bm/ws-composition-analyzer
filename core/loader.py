import os
import numpy as np
from calculations.sq_coeff import compute_sq_list, compute_mean_values

from calculations.network_characteristics import get_w, get_lamda, check_conditions

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

def load_data(path_matrix, path_service_times, path_arrival_times, path_input_data):
    
    matrix_path = os.path.join(DATA_DIR, path_matrix)
    service_path = os.path.join(DATA_DIR, path_service_times)
    arrival_path = os.path.join(DATA_DIR, path_arrival_times)
    input_path = os.path.join(DATA_DIR, path_input_data)
    
    # общее для алгоритмов
    matrix = parse_transition_matrix(matrix_path)
    matrix_copy = matrix.copy()
    N = matrix.shape[0] - 1
    w = get_w(matrix_copy)
    
    input_data = parse_input_data(input_path)
    lamda_zero = input_data["lamda_zero"]
    lamda = get_lamda(w, lamda_zero, N)
    mu = input_data["mu"]
    kappa = input_data["kappa"]

    # для ND и Decomp
    service_raw = scan_file(service_path)
    sq_B = compute_sq_list(service_raw)
    
    
    arrival_raw = scan_file(arrival_path)
    # lambda_list = [1/x for x in compute_mean_values(arrival_raw)]
    sq_A = compute_sq_list(arrival_raw)

    return {"matrix": matrix, "N": N, "lamda_zero": lamda_zero, "mu": mu, "lamda": lamda, "kappa": kappa, "sq_A": sq_A, "sq_B": sq_B}

def parse_transition_matrix(filename):
    with open(filename, 'r') as f:
        matrix = []
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            line = line.split('#')[0].strip()
            if not line:
                continue
            row = [float(x) for x in line.split()]
            matrix.append(row)
    matrix = np.array(matrix)
    N = matrix.shape[0]
    
    if matrix.shape != (N, N):
        raise ValueError("Матрица должна быть квадратной")
    for i in range(N):
        row_sum = sum(matrix[i])
        if not np.isclose(row_sum, 1.0, atol=1e-10):
            raise ValueError(f"Сумма вероятностей в строке {i} не равна 1: {row_sum}")
    return matrix

def parse_input_data(path):
    data = {}

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line: continue
            if line.startswith("#"): continue

            if ":" in line:
                key, value = line.split(":", 1)
            elif "=" in line:
                key, value = line.split("=", 1)
            else:
                continue

            key = key.strip()
            value = value.strip()

            if key == "kappa":
                data[key] = [int(x) for x in value.split()]
            elif " " in value:
                data[key] = [float(x) for x in value.split()]
            else:
                data[key] = float(value)
    if "mu" not in data or "kappa" not in data:
        raise ValueError("входной файл должен содержать параметры mu и kappa")
    if len(data["mu"]) != len(data["kappa"]):
        raise ValueError(
            f"размерности mu ({len(data['mu'])}) и kappa ({len(data['kappa'])}) не совпадают"
        )
    return data

def scan_file(file_name):
    result_data = {}
    with open(file_name, 'r') as file:
        for line in file:
            if ":" not in line:
                continue
            key, values_str = line.split(':', 1)
            result_data[key.strip()] = [float(x) for x in values_str.split()]
    return result_data
