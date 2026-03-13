import os
from tkinterdnd2 import DND_FILES, TkinterDnD
import tkinter as tk
from tkinter import ttk

from core.loader import load_data
from core.dispatcher import run_algorithm
from core.writer import write_results
from core.utils import short_name



class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.title("КВС – расчет показателей")
        self.geometry("700x500")

        self.files = {
            "matrix": None,
            "mu": None,
            "lamda": None,
            "input": None
        }

        self.algorithm = tk.StringVar(value="Метод анализа сети Джексона")

        self._build_ui()

    def _build_ui(self):
        ttk.Label(self, text="Выбор алгоритма").pack(pady=5)

        ttk.Combobox(
            self,
            textvariable=self.algorithm,
            values=[
                "Метод анализа сети Джексона",
                "Метод декомпозиции",
                "Метод диффузионной аппроксимации"
            ],
            state="readonly"
        ).pack(pady=5)

        self._drop_zone("Маршрутная матрица", "matrix")
        self._drop_zone("Файл data_mu.txt", "mu")
        self._drop_zone("Файл data_lamda.txt", "lamda")
        self._drop_zone("Файл input_data.txt", "input")

        ttk.Button(self, text="Рассчитать", command=self.run).pack(pady=20)

    # def drop_zone(self, text, key):
    #     frame = ttk.Frame(self)
    #     frame.pack(fill="x", padx=30, pady=5)

    #     ttk.Label(frame, text=text, width=30).pack(side="left")

    #     entry = ttk.Entry(frame, width=60)
    #     entry.pack(side="left", padx=5)

    #     # СОХРАНЯЕМ entry
    #     self.entries[key] = entry

    #     # ПОКАЗЫВАЕМ ИМЯ ФАЙЛА ПО УМОЛЧАНИЮ
    #     if self.files.get(key):
    #         entry.insert(0, os.path.basename(self.files[key]))

    #     entry.drop_target_register(DND_FILES)
    #     entry.dnd_bind(
    #         "<<Drop>>",
    #         lambda e, k=key: self.on_drop(e, k)
    #     )




    # def on_drop(self, event, key):
    #     paths = self.tk.splitlist(event.data)
    #     if not paths:
    #         return

    #     path = paths[0]
    #     self.files[key] = path

    #     entry = self.entries[key]
    #     entry.delete(0, tk.END)
    #     entry.insert(0, os.path.basename(path))





    def run(self):
        if None in self.files.values():
            tk.messagebox.showerror("Ошибка", "Не все файлы загружены")
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

        tk.messagebox.showinfo("Готово!", f"Результат сохранён:\n{path}")


if __name__ == "__main__":
    App().mainloop()
