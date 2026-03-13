from core.loader import load_data
from core.dispatcher import run_algorithm
from core.writer import write_results

def on_run_clicked(algorithm_id):
    data = load_data(...)
    result = run_algorithm(algorithm_id, data)
    write_results("output", "algorithm", data, result)
