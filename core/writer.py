import os
from datetime import datetime
from core.utils import to_python_float


def write_results(output_dir, algorithm_name, input_data, results):
    results = to_python_float(results)
    
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%d.%m-%H:%M")
    filename = f"{algorithm_name}_result.txt"
    filepath = os.path.join(output_dir, filename)

    matrix = input_data["matrix"]
    mu = input_data["mu"]
    lamda = input_data["lamda"]
    kappa = input_data["kappa"]
    lamda_zero = input_data["lamda_zero"]
    
    utilization = results["utilization"]
    node_customers = results["node_customers"]
    response_time_node = results["response_time_node"]

    network_customers = results.get("network_customers")
    response_time_network = results.get("response_time_network")
    extra = results.get("extra", {})

    totalWS = len(mu)

    with open(filepath, "w", encoding="utf-8") as file:
        file.write("\tХарактеристики КВС\n\n")
        file.write(f"\tКоличество веб-сервисов в композиции: {totalWS}\n\n")

        file.write("\tМаршрутная матрица:\n")
        for row in matrix:
            file.write("\t" + " ".join(f"{x:.2f}" for x in row) + "\n")
        file.write("\n")

        file.write("\tИнтенсивность обслуживания требований в системе\n")
        for i, val in enumerate(mu):
            file.write(f"\tИнтенсивность обслуживания требований в системе {i+1}: {val}\n")
        file.write("\n")

        file.write(f"\tИнтенсивность поступления требований из источника: {lamda_zero}\n\n")

        for i, k in enumerate(kappa):
            file.write(f"\tКоличество обслуживающих приборов в системе {i+1}: {k}\n")
        file.write("\n")

        for i, val in enumerate(lamda):
            file.write(f"Интенсивность поступления требований в систему {i+1}: {val:.2f}\n")
        file.write("\n")

        for i, val in enumerate(utilization):
            file.write(f"Коэффициенты использования системы {i+1}: {val:.4f}\n")
        file.write("\n")

        for i, val in enumerate(node_customers):
            file.write(f"Количество требований в системе {i+1}: {val:.4f}\n")
        if network_customers is not None:
            file.write(f"\nКоличество требований в сети {network_customers:.5f}\n\n")

        if response_time_node is not None:
            for i, val in enumerate(response_time_node):
                file.write(f"Длительность пребывания требований в системе {i+1}: {val:.4f}\n")

        if response_time_network is not None:
            file.write(f"\nДлительность пребывания требований в сети " f"{response_time_network:.5f}\n\n")
        file.write("-----"*12)
        if extra:
            
            file.write("\nДополнительные характеристики:\n\n")
            
            if "sq_D" in extra:
                file.write("Квадрат коэффициента вариации интервалов между уходящими требованиями:\n")
                for i, x in enumerate(extra["sq_D"], start=1):
                    file.write(f"  из системы {i}: {x:.4f}\n")

            
            if "sq_A" in extra:
                file.write("Квадрат коэффициента вариации интервалов поступлений требований:\n")
                for i, x in enumerate(extra["sq_A"], start=1):
                    file.write(f"  в систему {i}: {x:.4f}\n")
                

            if "state_probabilities" in extra:
                file.write("\nСтационарные вероятности состояний:\n")
                for i, states in enumerate(extra["state_probabilities"], start=1):
                    states_str = ", ".join(f"{p:.4f}" for p in states)
                    file.write(f"  системы {i}: [{states_str}]\n")

            file.write("\n")



        file.write(f"\nДанные на {timestamp}")

    return filepath
