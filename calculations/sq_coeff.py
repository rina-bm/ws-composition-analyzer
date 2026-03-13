
def compute_sq(values):
    x1 = sum(values)/len(values)
    x2 = sum(v*v for v in values)/len(values)
    return x2/(x1*x1)


def compute_sq_list(data_dict):
    return [compute_sq(values) for values in data_dict.values()]


def compute_mean_values(data_dict):
    return [sum(v)/len(v) for v in data_dict.values()]


# import math
# import pandas as pd
# import numpy as np

# PATH_SD = r"D:\Program Files\VSCode project\Python\CWS_project\data\data_mu.txt"
# PATH_AD = r"D:\Program Files\VSCode project\Python\CWS_project\data\data_l.txt"

# def scan_file(file_name):
#     result_data = {}
#     with open(file_name, 'r') as file:
#         for line in file:
#             part = line.split()
#             if not line or ':' not in line:
#                     continue
                    
#             key, values_str = line.split(':', 1)
#             key = key.strip()
            
#             values = [float(x) for x in values_str.split()]
#             result_data[key] = values
#     return result_data


# def get_sq_result(result_data):
#     result_sq = []
#     for key, values in result_data.items():
#         x1 = sum(values)/len(values)
#         x2 = sum(values[i]*values[i] for i in range(len(values)))/len(values)
#         result_sq.append(x2/(x1*x1))
#         # print(f"{key} - {len(values)}")
#     return result_sq

# sq_B =[]
# sq_A = []

# service_data = scan_file(PATH_SD)
# sq_B = get_sq_result(service_data)
# print(f"sq_B: {[f'{x:.2f}' for x in sq_B]}")

# arrival_data = scan_file(PATH_AD)
# sq_A = get_sq_result(arrival_data)
# print(f"sq_A: {[f'{x:.2f}' for x in sq_A]}")

# result_mu = []
# for key, values in service_data.items():
#     x1 = sum(values)/len(values)
#     result_mu.append(1/x1)