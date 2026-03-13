from calculations.algorithm_jakson import run_jakson   # M/M/k
from calculations.algorithm_decomp import run_decomp
from calculations.algorithm_da import run_da


def run_algorithm(choice, full_data):
    if choice == 1:
        data = {
            "matrix": full_data["matrix"],
            "lamda_zero": full_data["lamda_zero"],
            "mu": full_data["mu"],
            "lamda": full_data["lamda"],
            "kappa": full_data["kappa"],
        }
        return run_jakson(data)

    if choice == 2:

        # cначала считаем Jakson,
        #    потому что Decomp зависит от его response_time_node
        jakson_input = {
            "matrix": full_data["matrix"],
            "lamda_zero": full_data["lamda_zero"],
            "mu": full_data["mu"],
            "lamda": full_data["lamda"],
            "kappa": full_data["kappa"],
        }
        jakson_output = run_jakson(jakson_input)

        # cобираем входные данные для Decomp
        decomp_data = {
            "matrix": full_data["matrix"],
            "mu": full_data["mu"],
            "lamda": full_data["lamda"],
            "kappa": full_data["kappa"],
            "sq_A": full_data["sq_A"],
            "sq_B": full_data["sq_B"],
            # "node_customers": jakson_output["val_NCN"],
            "response_time_node": jakson_output["response_time_node"],
            "lamda_zero": full_data["lamda_zero"],
        }

        return run_decomp(decomp_data)

    if choice == 3:
        data = {
            "matrix": full_data["matrix"],
            "mu": full_data["mu"],
            "lamda": full_data["lamda"],
            "lamda_zero": full_data["lamda_zero"],
            # "sq_A": full_data["sq_A"],
            "sq_B": full_data["sq_B"],
        }
        
        return run_da(data)
    
    raise ValueError("error - ошибка в выборе алгоритма")
