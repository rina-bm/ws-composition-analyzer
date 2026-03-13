import math
from calculations.network_characteristics import check_conditions


def run_jakson(data):
        
    matrix = data["matrix"]
    totalWS = matrix.shape[0] - 1
    arrivalRateSource = data["lamda_zero"]
    serviceTime = data["mu"]
    arrivalRate = data["lamda"]
    service_units = data["kappa"]
    
    check_conditions(arrivalRate, serviceTime, service_units)
    
    val_UR = get_UR(arrivalRate, serviceTime, service_units, totalWS)
    val_NCN = get_mean_NCN(serviceTime, val_UR, service_units, arrivalRate, totalWS)

    response_time_node, network_bandwidth = get_mean_RTN(serviceTime, val_UR, service_units, arrivalRate, arrivalRateSource, totalWS)

    result = {
    "utilization": val_UR,
    "node_customers": val_NCN,
    "network_customers": sum(val_NCN),
    "response_time_node": response_time_node,
    "response_time_network": network_bandwidth,
    "extra": {}
    }
    

    return result

def get_UR(lamda, mu, k, totalWS):
    return [lamda[i] / (k[i] * mu[i]) for i in range(totalWS)]

def get_Prob_and_mean_NRQ(kappa, psi, totalWS):
    p_results = []
    b_results = []
    
    for i in range(totalWS):
        summ = 0.0
        k = kappa[i]
        rho = psi[i]
        for n in range(0, k):
            summ += (pow(k * rho, n)) / math.factorial(n)
        denominator = summ + (pow(k * rho, k)) / (math.factorial(k) * (1 - rho))
        p = 1 / denominator
        numerator = p * pow(k * rho, k) * rho
        denominator_b = math.factorial(k) * pow(1 - rho, 2)
        b = numerator / denominator_b
        p_results.append(p)
        b_results.append(b)
    return p_results, b_results

def get_mean_NCN(mu, psi, kappa, lamda, totalWS):
    _, b = get_Prob_and_mean_NRQ(kappa, get_UR(lamda, mu, kappa, totalWS), totalWS)
    n = [(b[i]+psi[i]*kappa[i]) for i in range(totalWS)]
    return n

def get_mean_RTN(mu, psi, kappa, lamda, lamda_sourse, totalWS):
    _, b = get_Prob_and_mean_NRQ(kappa, get_UR(lamda, mu, kappa, totalWS), totalWS)
    n = get_mean_NCN(mu, psi, kappa, lamda, totalWS)
    u = [((b[i]+psi[i]*kappa[i])/lamda[i]) for i in range(totalWS)]
    tau = (1/lamda_sourse)*sum(n)
    return u, tau

def list_comprehension(parameter):
    result = [float(x) for x in parameter]
    return result

def get_newline(totalWS):
    newline = '\n\n' if totalWS > 1 else '\n'
    return newline

# м переписать: работает только для 3 ненадежных систем?
def write_file_line(serviceTime, unrel_WS, type_system):
    system_num = []
    if type_system == 'unreliability':
        for i in range(len(serviceTime)):
            system_num.append(f"F{i - (len(unrel_WS) + 1)}" if i in unrel_WS else f"{i + 1}")
    else:
        for i in range(len(serviceTime)):
            system_num.append(i+1)
    return system_num

