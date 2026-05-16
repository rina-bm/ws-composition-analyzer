import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from tkinterdnd2 import TkinterDnD, DND_FILES

from core.loader import load_data
from core.dispatcher import run_algorithm
from core.writer import write_results


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
ICON_PATH = os.path.join(BASE_DIR, "ui", "images", "free-icon-font-calculator-3914992.ico")


ALGORITHMS = {
    "jackson": {
        "id": 1,
        "name": "Метод анализа сети Джексона",
        "description": (
            "Аналитический метод для вычисления характеристик "
            "сетей массового обслуживания в условиях экспоненциального распределения."
        ),
    },
    "decomposition": {
        "id": 2,
        "name": "Метод декомпозиции",
        "description": (
            "Приближённый метод, основанный на разбиении сложной сети на независимые "
            "системы массового обслуживания с последующим расчётом характеристик каждой системы отдельно."
        ),
    },
    "diffusion": {
        "id": 3,
        "name": "Метод диффузионной аппроксимации",
        "description": (
            "Метод аппроксимации процессов в сетях массового обслуживания с помощью "
            "диффузионных процессов для получения приближённых решений."
        ),
    },
}

COLORS = {
    "background": "#f5f5f7",
    "foreground": "#1f2937",

    "card": "#ffffff",
    "card_foreground": "#1f2937",

    "primary": "#1e40af",
    "primary_foreground": "#ffffff",

    "secondary": "#e5e7eb",
    "secondary_foreground": "#1f2937",

    "muted": "#f3f4f6",
    "muted_foreground": "#6b7280",

    "accent": "#dbeafe",
    "accent_foreground": "#1e40af",

    "destructive": "#dc2626",
    "destructive_foreground": "#ffffff",

    "border": "#e5e7eb",
    "input_background": "#f9fafb",
    "ring": "#3b82f6",

    "success_background": "#ecfdf5",
    "success_border": "#bbf7d0",
    "success": "#16a34a",
    "success_text": "#047857",

    "warning": "#f59e0b",
    "gray_300": "#d1d5db",
    "gray_400": "#9ca3af",
}


class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.title("КВС – расчёт характеристик СМО")
        self.geometry("900x650")
        self.minsize(850, 620)
        self.configure(bg="#f3f4f6")

        if os.path.exists(ICON_PATH):
            self.iconbitmap(ICON_PATH)

        self.selected_algorithm = tk.StringVar(value="jackson")
        self.status_var = tk.StringVar(value="Готово к расчёту")
        self.result_path = tk.StringVar(value="")

        self.files = {
            "routing": os.path.join(DATA_DIR, "transition_matrix_reliability.txt"),
            "service": os.path.join(DATA_DIR, "data_mu.txt"),
            "arrival": os.path.join(DATA_DIR, "data_lambda.txt"),
            "params": os.path.join(DATA_DIR, "input_data.txt"),
        }

        self.file_entries = {}
        self.file_status_labels = {}

        self.setup_styles()
        self.build_ui()
        self.update_algorithm_description()
        self.update_file_statuses()
        
    def file_input(self, parent, label, key):
        row = ttk.Frame(parent, style="FileInput.TFrame")
        row.pack(fill="x", pady=7, padx=0)

        left = ttk.Frame(row, style="FileInputInner.TFrame")
        left.pack(side="left", fill="x", expand=True, padx=14, pady=12)

        ttk.Label(
            left,
            text=label,
            style="FileInputTitle.TLabel"
        ).pack(anchor="w")

        file_name_label = ttk.Label(
            left,
            text="Файл не выбран",
            style="FileInputName.TLabel"
        )
        file_name_label.pack(anchor="w", pady=(4, 0))

        self.file_entries[key] = file_name_label

        right = ttk.Frame(row, style="FileInputInner.TFrame")
        right.pack(side="right", padx=14, pady=12)

        status_label = ttk.Label(
            right,
            text="Не выбран",
            style="FileStatusMuted.TLabel",
            width=12,
            anchor="center"
        )
        status_label.pack(side="left", padx=(0, 12))

        self.file_status_labels[key] = status_label

        ttk.Button(
            right,
            text="Обзор",
            style="Secondary.TButton",
            command=lambda file_key=key: self.choose_file(file_key)
        ).pack(side="left", ipady=2)

        row.drop_target_register(DND_FILES)
        row.dnd_bind(
            "<<Drop>>",
            lambda event, file_key=key: self.on_drop(event, file_key)
        )

    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        self.configure(bg=COLORS["background"])

        # Базовые фреймы
        style.configure(
            "Root.TFrame",
            background=COLORS["background"]
        )

        style.configure(
            "Card.TFrame",
            background=COLORS["card"],
            relief="solid",
            borderwidth=1
        )

        style.configure(
            "MutedCard.TFrame",
            background=COLORS["muted"],
            relief="solid",
            borderwidth=1
        )

        # Заголовок
        style.configure(
            "HeaderTitle.TLabel",
            background=COLORS["card"],
            foreground=COLORS["primary"],
            font=("Segoe UI", 24, "bold")
        )

        style.configure(
            "HeaderSubtitle.TLabel",
            background=COLORS["card"],
            foreground=COLORS["muted_foreground"],
            font=("Segoe UI", 10)
        )

        # Заголовки секций
        style.configure(
            "SectionTitle.TLabel",
            background=COLORS["card"],
            foreground=COLORS["foreground"],
            font=("Segoe UI", 14, "bold")
        )

        style.configure(
            "Text.TLabel",
            background=COLORS["card"],
            foreground=COLORS["foreground"],
            font=("Segoe UI", 10)
        )

        style.configure(
            "Muted.TLabel",
            background=COLORS["card"],
            foreground=COLORS["muted_foreground"],
            font=("Segoe UI", 9)
        )

        style.configure(
            "Footer.TLabel",
            background=COLORS["background"],
            foreground=COLORS["muted_foreground"],
            font=("Segoe UI", 9)
        )

        # Подсказка
        style.configure(
            "Hint.TLabel",
            background=COLORS["accent"],
            foreground=COLORS["accent_foreground"],
            font=("Segoe UI", 9)
        )

        style.configure(
            "Hint.TFrame",
            background=COLORS["accent"],
            relief="solid",
            borderwidth=1
        )

        # Карточка выбора файла
        style.configure(
            "FileInput.TFrame",
            background=COLORS["input_background"],
            relief="solid",
            borderwidth=1
        )

        style.configure(
            "FileInputInner.TFrame",
            background=COLORS["input_background"]
        )

        style.configure(
            "FileInputTitle.TLabel",
            background=COLORS["input_background"],
            foreground=COLORS["foreground"],
            font=("Segoe UI", 10)
        )

        style.configure(
            "FileInputName.TLabel",
            background=COLORS["input_background"],
            foreground=COLORS["muted_foreground"],
            font=("Segoe UI", 8)
        )

        style.configure(
            "FileStatusMuted.TLabel",
            background=COLORS["input_background"],
            foreground=COLORS["gray_400"],
            font=("Segoe UI", 8)
        )

        style.configure(
            "FileStatusSuccess.TLabel",
            background=COLORS["input_background"],
            foreground=COLORS["success"],
            font=("Segoe UI", 8, "bold")
        )

        style.configure(
            "FileStatusError.TLabel",
            background=COLORS["input_background"],
            foreground=COLORS["destructive"],
            font=("Segoe UI", 8, "bold")
        )

        # Блок результата
        style.configure(
            "Result.TFrame",
            background=COLORS["success_background"],
            relief="solid",
            borderwidth=1
        )

        style.configure(
            "ResultTitle.TLabel",
            background=COLORS["success_background"],
            foreground=COLORS["success_text"],
            font=("Segoe UI", 10, "bold")
        )

        style.configure(
            "ResultText.TLabel",
            background=COLORS["success_background"],
            foreground=COLORS["success_text"],
            font=("Segoe UI", 9)
        )

        # Ошибки
        style.configure(
            "Error.TLabel",
            background=COLORS["card"],
            foreground=COLORS["destructive"],
            font=("Segoe UI", 9, "bold")
        )

        # Combobox
        style.configure(
            "TCombobox",
            fieldbackground=COLORS["input_background"],
            background=COLORS["input_background"],
            foreground=COLORS["foreground"],
            bordercolor=COLORS["border"],
            lightcolor=COLORS["border"],
            darkcolor=COLORS["border"],
            arrowcolor=COLORS["primary"],
            padding=8,
            font=("Segoe UI", 10)
        )

        style.map(
            "TCombobox",
            fieldbackground=[
                ("readonly", COLORS["input_background"])
            ],
            foreground=[
                ("readonly", COLORS["foreground"])
            ]
        )

        # Основная кнопка
        style.configure(
            "Primary.TButton",
            background=COLORS["primary"],
            foreground=COLORS["primary_foreground"],
            borderwidth=0,
            focusthickness=0,
            focuscolor=COLORS["primary"],
            font=("Segoe UI", 11, "bold"),
            padding=10
        )

        style.map(
            "Primary.TButton",
            background=[
                ("disabled", COLORS["gray_300"]),
                ("active", "#1d4ed8"),
                ("pressed", "#1e3a8a")
            ],
            foreground=[
                ("disabled", COLORS["muted_foreground"]),
                ("active", COLORS["primary_foreground"]),
                ("pressed", COLORS["primary_foreground"])
            ]
        )

        # Вторичная кнопка
        style.configure(
            "Secondary.TButton",
            background=COLORS["card"],
            foreground=COLORS["foreground"],
            borderwidth=1,
            focusthickness=0,
            focuscolor=COLORS["border"],
            font=("Segoe UI", 9),
            padding=6
        )

        style.map(
            "Secondary.TButton",
            background=[
                ("active", COLORS["muted"]),
                ("pressed", COLORS["secondary"])
            ],
            foreground=[
                ("active", COLORS["foreground"]),
                ("pressed", COLORS["foreground"])
            ]
        )
        
        style.configure(
            "CardInner.TFrame",
            background=COLORS["card"],
            relief="flat",
            borderwidth=0
        )
        
        style.configure(
            "ResultInner.TFrame",
            background=COLORS["success_background"],
            relief="flat",
            borderwidth=0
        )

    def build_ui(self):
        container = ttk.Frame(self, style="Root.TFrame")
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(
            container,
            bg=COLORS["background"],
            highlightthickness=0
        )
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            container,
            orient="vertical",
            command=canvas.yview
        )
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)

        root = ttk.Frame(canvas, style="Root.TFrame")
        window_id = canvas.create_window(
            (0, 0),
            window=root,
            anchor="nw"
        )

        root.configure(padding=(24, 20, 24, 20))

        self.build_header(root)
        self.build_algorithm_block(root)
        self.build_files_block(root)
        self.build_calculation_block(root)
        self.build_footer(root)

        def update_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def update_canvas_width(event):
            canvas.itemconfig(window_id, width=event.width)

        root.bind("<Configure>", update_scroll_region)
        canvas.bind("<Configure>", update_canvas_width)

        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def on_linux_scroll_up(event):
            canvas.yview_scroll(-1, "units")

        def on_linux_scroll_down(event):
            canvas.yview_scroll(1, "units")

        canvas.bind_all("<MouseWheel>", on_mousewheel)
        canvas.bind_all("<Button-4>", on_linux_scroll_up)
        canvas.bind_all("<Button-5>", on_linux_scroll_down)

    def card(self, parent):
        outer = ttk.Frame(parent, style="Card.TFrame")
        outer.pack(fill="x", pady=9)

        inner = ttk.Frame(outer, style="CardInner.TFrame")
        inner.pack(fill="both", expand=True, padx=22, pady=18)

        return inner

    def build_header(self, parent):
        card = self.card(parent)

        top = ttk.Frame(card, style="CardInner.TFrame")
        top.pack(fill="x")

        left = ttk.Frame(top, style="CardInner.TFrame")
        left.pack(side="left", fill="x", expand=True)

        ttk.Label(
            left,
            text="Композиция веб-сервисов",
            style="HeaderTitle.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            left,
            text="Вычисление основных функциональных характеристик композиции веб-сервисов",
            style="HeaderSubtitle.TLabel"
        ).pack(anchor="w", pady=(4, 0))

        ttk.Label(
            top,
            text="🧮",
            background="#ffffff",
            foreground="#1f3a5f",
            font=("Segoe UI", 28)
        ).pack(side="right", padx=(10, 0))

    def build_algorithm_block(self, parent):
        card = self.card(parent)

        ttk.Label(
            card,
            text="Метод анализа",
            style="SectionTitle.TLabel"
        ).pack(anchor="w", pady=(0, 8))

        values = [data["name"] for data in ALGORITHMS.values()]
        self.algorithm_name_to_key = {
            data["name"]: key for key, data in ALGORITHMS.items()
        }

        self.algorithm_combobox = ttk.Combobox(
            card,
            values=values,
            state="readonly",
            width=70
        )
        self.algorithm_combobox.set(ALGORITHMS[self.selected_algorithm.get()]["name"])
        self.algorithm_combobox.pack(fill="x")
        self.algorithm_combobox.bind("<<ComboboxSelected>>", self.on_algorithm_changed)

        self.algorithm_description = ttk.Label(
            card,
            text="",
            style="Muted.TLabel",
            wraplength=800,
            justify="left"
        )
        self.algorithm_description.pack(anchor="w", pady=(10, 0))

    def build_files_block(self, parent):
        card = self.card(parent)

        ttk.Label(
            card,
            text="Исходные данные",
            style="SectionTitle.TLabel"
        ).pack(anchor="w", pady=(0, 10))

        self.file_input(
            card,
            label="Маршрутная матрица",
            key="routing"
        )

        self.file_input(
            card,
            label="Интенсивности обслуживания",
            key="service"
        )

        self.file_input(
            card,
            label="Интенсивности поступления",
            key="arrival"
        )

        self.file_input(
            card,
            label="Параметры сети",
            key="params"
        )

        hint = ttk.Frame(card, style="Hint.TFrame")
        hint.pack(fill="x", pady=(14, 0))

        ttk.Label(
            hint,
            text="💡 Файлы можно выбрать или перетащить в соответствующее поле",
            style="Hint.TLabel",
            padding=(12, 10)
        ).pack(fill="x")


    def build_calculation_block(self, parent):
        card = self.card(parent)

        ttk.Label(
            card,
            text="Расчёт",
            style="SectionTitle.TLabel"
        ).pack(anchor="w", pady=(0, 12))

        self.calculate_button = ttk.Button(
            card,
            text="Рассчитать показатели",
            style="Primary.TButton",
            command=self.run
        )
        self.calculate_button.pack(fill="x", pady=(4, 10), ipady=4)

        self.status_label = ttk.Label(
            card,
            textvariable=self.status_var,
            style="Muted.TLabel"
        )
        self.status_label.pack(anchor="w", pady=(4, 10))

        self.result_frame = ttk.Frame(card, style="Result.TFrame")

        result_inner = ttk.Frame(self.result_frame, style="ResultInner.TFrame")
        result_inner.pack(fill="x", padx=12, pady=10)

        self.result_title = ttk.Label(
            result_inner,
            text="✓ Расчёт успешно завершён",
            style="ResultTitle.TLabel"
        )
        self.result_title.pack(anchor="w")

        self.result_label = ttk.Label(
            result_inner,
            text="",
            style="ResultText.TLabel",
            wraplength=760
        )
        self.result_label.pack(anchor="w", pady=(6, 10))

        self.open_results_button = ttk.Button(
            result_inner,
            text="Открыть папку с результатами",
            style="Secondary.TButton",
            command=self.open_results_folder
        )
        self.open_results_button.pack(anchor="w")

    def build_footer(self, parent):
        footer = ttk.Frame(parent, style="Root.TFrame")
        footer.pack(fill="x", pady=(8, 0))

        footer_label = ttk.Label(
            footer,
            text=(
                "Поддерживаются следующие методы анализа открытых сетей массового обслуживания: "
                "метод анализа сети Джексона, метод декомпозиции, "
                "метод диффузионной аппроксимации"
            ),
            style="Footer.TLabel",
            anchor="center",
            justify="center"
        )
        footer_label.pack(fill="x", padx=20)

        footer.bind(
            "<Configure>",
            lambda event: footer_label.configure(wraplength=max(event.width - 40, 300))
        )

    def on_algorithm_changed(self, event=None):
        selected_name = self.algorithm_combobox.get()
        selected_key = self.algorithm_name_to_key[selected_name]
        self.selected_algorithm.set(selected_key)
        self.update_algorithm_description()
        self.hide_result()
        
        # убираем фокус
        self.algorithm_combobox.selection_clear()
        self.focus_set()

    def update_algorithm_description(self):
        algorithm_key = self.selected_algorithm.get()
        description = ALGORITHMS[algorithm_key]["description"]
        self.algorithm_description.configure(text=description)

    def choose_file(self, key):
        path = filedialog.askopenfilename(
            title="Выберите файл с исходными данными",
            filetypes=[
                ("Текстовые файлы", "*.txt"),
                ("Все файлы", "*.*")
            ]
        )

        if not path:
            return

        self.files[key] = path
        self.update_file_statuses()
        self.hide_result()

    def on_drop(self, event, key):
        paths = self.tk.splitlist(event.data)

        if not paths:
            return

        self.files[key] = paths[0]
        self.update_file_statuses()
        self.hide_result()

    def update_file_statuses(self):
        for key, label in self.file_entries.items():
            file_path = self.files.get(key)

            if file_path and os.path.exists(file_path):
                label.configure(
                    text=os.path.basename(file_path),
                    style="FileInputName.TLabel"
                )

                self.file_status_labels[key].configure(
                    text="✓ Выбран",
                    style="FileStatusSuccess.TLabel"
                )

            elif file_path:
                label.configure(
                    text=f"{os.path.basename(file_path)} — файл не найден",
                    style="FileInputName.TLabel"
                )

                self.file_status_labels[key].configure(
                    text="Ошибка",
                    style="FileStatusError.TLabel"
                )

            else:
                label.configure(
                    text="Файл не выбран",
                    style="FileInputName.TLabel"
                )

                self.file_status_labels[key].configure(
                    text="Не выбран",
                    style="FileStatusMuted.TLabel"
                )

        self.update_calculate_button_state()
    
    def all_files_selected(self):
        return all(
            self.files.get(key) and os.path.exists(self.files.get(key))
            for key in self.files
        )

    def update_calculate_button_state(self):
        if self.all_files_selected():
            self.calculate_button.configure(state="normal")
            self.status_var.set("Статус: готово к расчёту")
        else:
            self.calculate_button.configure(state="disabled")
            self.status_var.set("Статус: выберите все необходимые файлы")

    def run(self):
        if not self.all_files_selected():
            messagebox.showerror("Ошибка", "Не все файлы выбраны или некоторые файлы не найдены")
            return

        self.status_var.set("Статус: выполняется расчёт...")
        self.update_idletasks()

        try:
            data = load_data(
                self.files["routing"],
                self.files["service"],
                self.files["arrival"],
                self.files["params"]
            )

            algorithm_key = self.selected_algorithm.get()
            algorithm_id = ALGORITHMS[algorithm_key]["id"]
            algorithm_name = ALGORITHMS[algorithm_key]["name"]

            result = run_algorithm(algorithm_id, data)
            path = write_results("results", algorithm_name, data, result)

            self.result_path.set(path)
            self.status_var.set("Статус: расчёт успешно завершён")

            self.show_result(path)

        except Exception as error:
            self.status_var.set("Статус: ошибка расчёта")
            messagebox.showerror("Ошибка расчёта", str(error))

    def show_result(self, path):
        self.result_label.configure(
            text=f"Файл результата: {path}"
        )
        self.result_frame.pack(fill="x", pady=(12, 0))

    def hide_result(self):
        self.result_frame.pack_forget()
        self.result_path.set("")

    def open_results_folder(self):
        os.makedirs(RESULTS_DIR, exist_ok=True)

        if sys.platform.startswith("win"):
            os.startfile(RESULTS_DIR)
        elif sys.platform == "darwin":
            subprocess.run(["open", RESULTS_DIR])
        else:
            subprocess.run(["xdg-open", RESULTS_DIR])


def run_app():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    run_app()