import os
import textwrap
from datetime import datetime
from core.utils import to_python_float


def _fmt_num(value, digits=3):
    if value is None:
        return "-"
    if isinstance(value, (int, float)):
        return f"{value:.{digits}f}"
    return str(value)


def _wrap_headers(headers, max_width=18):
    wrapped = []
    max_lines = 1

    for header in headers:
        lines = textwrap.wrap(str(header), width=max_width, break_long_words=False)
        if not lines:
            lines = [str(header)]
        wrapped.append(lines)
        max_lines = max(max_lines, len(lines))

    normalized = []
    for lines in wrapped:
        normalized.append(lines + [""] * (max_lines - len(lines)))

    return normalized, max_lines


def _drop_empty_columns(headers, rows):
    if not rows:
        return headers, rows

    keep_indices = []
    for col_idx in range(len(headers)):
        column_values = [row[col_idx] for row in rows]
        has_data = any(str(v).strip() not in {"", "-"} for v in column_values)
        if has_data:
            keep_indices.append(col_idx)

    filtered_headers = [headers[i] for i in keep_indices]
    filtered_rows = [[row[i] for i in keep_indices] for row in rows]
    return filtered_headers, filtered_rows


def _format_table(headers, rows, header_wrap_width=18):
    headers, rows = _drop_empty_columns(headers, rows)

    if not headers:
        return "Нет данных"

    str_rows = [[str(cell) for cell in row] for row in rows]
    wrapped_headers, header_height = _wrap_headers(headers, max_width=header_wrap_width)

    widths = []
    for col_idx in range(len(headers)):
        header_width = max(len(line) for line in wrapped_headers[col_idx])
        cell_width = max((len(row[col_idx]) for row in str_rows), default=0)
        widths.append(max(header_width, cell_width))

    def fmt_line(parts):
        return "  ".join(str(parts[i]).ljust(widths[i]) for i in range(len(parts)))

    lines = []

    for line_idx in range(header_height):
        header_line = [wrapped_headers[col_idx][line_idx] for col_idx in range(len(headers))]
        lines.append(fmt_line(header_line))

    lines.append("  ".join("-" * widths[i] for i in range(len(headers))))

    for row in str_rows:
        lines.append(fmt_line(row))

    return "\n".join(lines)


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

    utilization = results.get("utilization", [])
    node_customers = results.get("node_customers", [])
    response_time_node = results.get("response_time_node", [])

    network_customers = results.get("network_customers")
    response_time_network = results.get("response_time_network")
    extra = results.get("extra", {})

    total_ws = len(mu)

    # ---------- Таблица 1. Входные данные ----------
    input_headers = [
        "Система",
        "Интенсивность поступления lambda",
        "Интенсивность обслуживания mu",
        "Количество приборов k",
    ]

    input_rows = []
    for i in range(total_ws):
        input_rows.append([
            f"ws{i+1}",
            _fmt_num(lamda[i]) if i < len(lamda) else "-",
            _fmt_num(mu[i]) if i < len(mu) else "-",
            str(kappa[i]) if i < len(kappa) else "-",
        ])

    # ---------- Таблица 2. Выходные данные по системам ----------
    output_headers = [
        "Система",
        "Загрузка rho",
        "Количество требований в системе",
        "Длительность пребывания в системе",
    ]

    output_rows = []
    for i in range(total_ws):
        output_rows.append([
            f"ws{i+1}",
            _fmt_num(utilization[i]) if i < len(utilization) else "-",
            _fmt_num(node_customers[i]) if i < len(node_customers) else "-",
            _fmt_num(response_time_node[i]) if i < len(response_time_node) else "-",
        ])

    # ---------- Таблица 3. Характеристики сети ----------
    network_headers = [
        "Количество требований в сети",
        "Длительность пребывания требования в сети",
    ]

    network_rows = [[
        _fmt_num(network_customers) if network_customers is not None else "-",
        _fmt_num(response_time_network) if response_time_network is not None else "-",
    ]]

    # ---------- Таблица 4. Дополнительные характеристики ----------
    extra_headers = [
        "Система",
        "sq_A",
        "sq_D",
        "Вероятности состояний",
    ]

    sq_A = extra.get("sq_A", [])
    sq_D = extra.get("sq_D", [])
    state_probabilities = extra.get("state_probabilities", [])

    extra_rows = []
    for i in range(total_ws):
        sq_a_val = sq_A[i] if i < len(sq_A) else "-"
        sq_d_val = sq_D[i] if i < len(sq_D) else "-"
        states_val = state_probabilities[i] if i < len(state_probabilities) else "-"

        extra_rows.append([
            f"ws{i+1}",
            _fmt_num(sq_a_val) if isinstance(sq_a_val, (int, float)) else "-",
            _fmt_num(sq_d_val) if isinstance(sq_d_val, (int, float)) else "-",
            "[" + ", ".join(_fmt_num(p) for p in states_val) + "]"
            if isinstance(states_val, (list, tuple)) and len(states_val) > 0 else "-",
        ])

    with open(filepath, "w", encoding="utf-8") as file:
        file.write("Характеристики КВС\n\n")
        file.write(f"Количество веб-сервисов в композиции: {total_ws}\n\n")

        file.write("Маршрутная матрица:\n")
        for row in matrix:
            file.write("  " + " ".join(f"{x:.2f}" for x in row) + "\n")
        file.write("\n")

        file.write(f"Интенсивность поступления требований из источника: {_fmt_num(lamda_zero)}\n\n")

        file.write("Входные данные:\n")
        file.write(_format_table(input_headers, input_rows, header_wrap_width=18))
        file.write("\n\n")

        file.write("Выходные данные по системам:\n")
        file.write(_format_table(output_headers, output_rows, header_wrap_width=18))
        file.write("\n\n")

        if network_customers is not None:
            file.write(f"Количество требований в сети: {_fmt_num(network_customers)}\n")
        if response_time_network is not None:
            file.write(
                f"Длительность пребывания требования в сети: "
                f"{_fmt_num(response_time_network)}\n"
            )
        if network_customers is not None or response_time_network is not None:
            file.write("\n")

        extra_table = _format_table(extra_headers, extra_rows, header_wrap_width=18)
        if extra_table != "Нет данных":
            file.write("Дополнительные характеристики:\n")
            file.write(extra_table)
            file.write("\n\n")

        file.write(f"Данные на {timestamp}")

    return filepath