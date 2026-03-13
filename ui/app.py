import os
from tkinterdnd2 import TkinterDnD, DND_FILES
import tkinter as tk
from tkinter import ttk, messagebox

from core.loader import load_data
from core.dispatcher import run_algorithm
from core.writer import write_results



BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ICON_PATH = os.path.join(BASE_DIR, "ui", "images", "free-icon-font-calculator-3914992.ico")




class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        
        style = ttk.Style(self)
        style.theme_use("default")

        style.configure(
            "TLabel",
            font=("Segoe UI", 10)
        )

        style.configure(
            "Header.TLabel",
            font=("Segoe UI", 10, "bold")
        )

        style.configure(
            "Card.TFrame",
            background="#f5f6f7",
            relief="solid",
            borderwidth=1
        )

        style.configure(
            "Accent.TButton",
            font=("Segoe UI", 12, "bold"),
            padding=8
        )


        self.title("КВС – расчет показателей производительности")
        self.iconbitmap(ICON_PATH)
        self.geometry("800x550")

        self.files = {
            "matrix": os.path.join(DATA_DIR, "transition_matrix_reliability.txt"),
            "mu": os.path.join(DATA_DIR, "data_mu.txt"),
            "lamda": os.path.join(DATA_DIR, "data_lamda.txt"),
            "input": os.path.join(DATA_DIR, "input_data.txt"),
        }


        self.algorithm = tk.StringVar(value="Метод анализа сети Джексона")
        self.entries = {}


        self.build_ui()

    def build_ui(self):
        header = ttk.Label(
            self,
            text="КВС – расчет показателей производительности",
            style="Header.TLabel"
        )
        header.pack(pady=(20, 10))


        ttk.Combobox(
            self,
            textvariable=self.algorithm,
            state="readonly",
            values=[
                "Метод анализа сети Джексона",
                "Метод декомпозиции",
                "Метод диффузионной аппроксимации"
            ],
            width=30
        ).pack(pady=5)

        self.drop_zone("Маршрутная матрица", "matrix")
        self.drop_zone("Файл data_mu.txt", "mu")
        self.drop_zone("Файл data_lamda.txt", "lamda")
        self.drop_zone("Файл input_data.txt", "input")

        ttk.Button(
            self,
            text="Рассчитать",
            command=self.run,
            style="Accent.TButton",
            width=25
        ).pack(pady=25)


    def on_drop(self, event, key):
        paths = self.tk.splitlist(event.data)
        if not paths:
            return

        path = paths[0]
        self.files[key] = path

        entry = self.entries[key]
        entry.delete(0, tk.END)
        entry.insert(0, os.path.basename(path))


    def drop_zone(self, text, key):
        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=30, pady=5)

        ttk.Label(frame, text=text, width=30).pack(side="left")

        entry = ttk.Entry(frame, width=60)
        entry.pack(side="left", padx=5)

        self.entries[key] = entry

        # показываем имя файла по умолчанию
        if self.files.get(key):
            entry.insert(0, os.path.basename(self.files[key]))

        entry.drop_target_register(DND_FILES)
        entry.dnd_bind(
            "<<Drop>>",
            lambda e, k=key: self.on_drop(e, k)
        )


    def run(self):
        if None in self.files.values():
            messagebox.showerror("Ошибка", "Не все файлы загружены")
            return

        data = load_data(
            self.files["matrix"],
            self.files["mu"],
            self.files["lamda"],
            self.files["input"]
        )

        alg_map = {
        "Метод анализа сети Джексона": 1,
        "Метод декомпозиции": 2,
        "Метод диффузионной аппроксимации": 3
        }

        result = run_algorithm(alg_map[self.algorithm.get()], data)

        path = write_results("results", self.algorithm.get(), data, result)

        messagebox.showinfo("готово!", f"результат сохранён:\n{path}")

def run_app():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    App().mainloop()
