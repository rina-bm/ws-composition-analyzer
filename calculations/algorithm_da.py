import numpy as np
import math
from calculations.network_characteristics import check_conditions


def get_visit_rates(P):
    N = P.shape[0] - 1
    p0 = P[0, 1:]
    P_sub = P[1:, 1:]

    A = np.eye(N) - P_sub.T

    if np.linalg.matrix_rank(A) < N:
        raise ValueError(f"Система вырождена{P}")

    return np.linalg.solve(A, p0)


def compute_rho(lambda_zero, e, mu):
    return [lambda_zero * e[i + 1] / mu[i] for i in range(len(mu))]


def compute_sq_coeff_A(matrix, e, sq_B):
    node = len(e) - 1
    sq_A = []

    for i in range(1, node + 1):
        s = 0.0
        for j in range(node + 1):
            s += (sq_B[j] - 1) * matrix[j][i]**2 * e[j] / e[i]
        sq_A.append(1 + s)

    return sq_A


def compute_rho_hat(rho, sq_A, sq_B):
    return [
        math.exp(-2 * (1 - rho[i]) / (sq_A[i] * rho[i] + sq_B[i + 1]))
        for i in range(len(rho))
    ]


def compute_k(rho, rho_hat):
    return [rho[i] / (1 - rho_hat[i]) for i in range(len(rho))]


def compute_state_probabilities(rho, rho_hat, k):
    pi = []
    for i in range(len(rho)):
        states = [1 - rho[i]]
        max_k = int(np.ceil(k[i]))

        for m in range(1, max_k + 1):
            prob = rho[i] * (1 - rho_hat[i]) * (rho_hat[i] ** (m - 1))
            states.append(prob)

        pi.append(states)

    return pi

def list_comprehension(parameter):
    result = [float(x) for x in parameter]
    return result

def round_nested(lst, digits=4):
    return [[round(x, digits) for x in row] for row in lst]


def run_da(data):
    matrix = data["matrix"]
    mu = data["mu"]
    lamda_zero = data["lamda_zero"]
    lamda = data["lamda"]
    sq_B_d = data["sq_B"]

    sq_A0 = 1.0
    sq_B = [sq_A0] + sq_B_d
    e = get_visit_rates(matrix)
    e = np.insert(e, 0, 1.0)
    rho = compute_rho(lamda_zero, e, mu)

    check_conditions(rho, mu, [1] * len(mu))


    sq_A = compute_sq_coeff_A(matrix, e, sq_B)
    rho_hat = compute_rho_hat(rho, sq_A, sq_B)
    n = compute_k(rho, rho_hat)
    pi = compute_state_probabilities(rho, rho_hat, n)
    
    u = []
    for i in range(len(mu)):
        u.append(n[i]/lamda[i])
        
    response_time_network = (1/lamda_zero)*sum(n)
    
    result = {
    "utilization": rho,
    "node_customers": n,
    "network_customers": sum(n),
    "response_time_node": u,
    "response_time_network": response_time_network,
    "extra": {
        "sq_A": sq_A,
        "state_probabilities": pi,
        }
    }
    
    return result
