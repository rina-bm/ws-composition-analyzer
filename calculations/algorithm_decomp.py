# import calculations.network_characteristics as network_characteristics 
# import calculations.algorithm_jakson as algorithm_jakson
# import calculations.sq_coeff as sq_coeff
# import numpy as np
import math
from calculations.network_characteristics import check_conditions

def run_decomp(data):
    matrix = data["matrix"]
    node = matrix.shape[0] - 1
    mu = data["mu"]
    lamda = data["lamda"]
    kappa = data["kappa"]
    sq_A = data["sq_A"]
    sq_B = data["sq_B"]
    # sq_A = [1.0] * 8
    # sq_B = [1.0] * 8
    w_mmk = data["response_time_node"]
    lamda_zero = data["lamda_zero"]
    
    check_conditions(lamda, mu, kappa)
    
    rho = get_rho(lamda, kappa, mu, node)
    sq_D = get_sq_D(rho, node, sq_A, sq_B, kappa)
    c_cooper = get_c_KRho(kappa, rho)
    
    w_gigk = []

    for i in range(node):
        temp = (1-sq_A[i])/(1 - 4*c_cooper[i])*math.exp(-2/3*(1-rho[i])/rho[i]) + (1 - sq_B[i])/(1 + c_cooper[i]) + sq_A[i] + sq_B[i] - 1
        w_gigk.append((sq_A[i] + sq_B[i])/2 * w_mmk[i] * (1/temp))
    temp = [float(x) for x in w_gigk]
    n = []
    for i in range(node):
        n.append(temp[i]*lamda[i])
    
    response_time_network = (1/lamda_zero)*sum(n)
    
    # result = {
    #     "utilization": rho,
    #     "node_customers": n,
    #     "sq_D": sq_D,
    #     "response_time_node": temp,
    # }
    result = {
    "utilization": rho,
    "node_customers": n,
    "network_customers": sum(n),
    "response_time_node": temp,
    "response_time_network": response_time_network,
    "extra": {
        "sq_D": sq_D
        }
    }
    
    return result

def get_sq_D(rho, node, sq_B, sq_A, kappa):
    sq_D = []
    for i in range(node):
        sq_D.append(1 + (rho[i]*rho[i] * (sq_B[i] - 1))/(math.sqrt(kappa[i])) + (1 - rho[i]*rho[i])*(sq_A[i] - 1))
    # print(f"sq_coeff_D: {sq_coeff_D}")
    return sq_D

def get_rho(lamda, k, mu, node):
    return [lamda[i] / (k[i] * mu[i]) for i in range(node)]

def get_c_KRho(k, rho):
    cooper = []
    for i in range(len(k)):
        cooper.append((1-rho[i])*(k[i] - 1)*((math.sqrt(4+5*k[i]) - 2)/(16*rho[i]*k[i])))
    return cooper
