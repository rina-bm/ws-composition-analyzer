from core.loader import load_data
from core.dispatcher import run_algorithm
from core.writer import write_results
from ui.app import run_app
import os

# def main():
#     data = load_data("transition_matrix_reliability.txt", "data_mu.txt", "data_lamda.txt", "input_data.txt")

#     print("Выберите действие:\n1=Анализ сети Джексона,\n2=Анализ сети общего вида (метод декомпозиции),\n3=Анализ сети общего вида (метод дифф. аппрокс.)")
#     alg = int(input("> "))

#     result = run_algorithm(alg, data)
#     algorithm_names = {
#         1: "Jakson",
#         2: "Decomposition",
#         3: "DA"
#     }
#     algorithm_name = algorithm_names.get(alg, "Unknown")

#     output_dir = os.path.join(os.getcwd(), "output")

#     filepath = write_results(
#         output_dir=output_dir,
#         algorithm_name=algorithm_name,
#         input_data=data,
#         results=result
#     )

#     print(f"\nРезультаты сохранены в файл:\n{filepath}")

if __name__ == "__main__":
    # main()
    run_app()
