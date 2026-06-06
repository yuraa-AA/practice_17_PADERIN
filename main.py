from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from calculations import (
    MATERIAL_FRICTION_RANGES,
    calc_contact_pressure,
    calc_volume_and_areas,
    expansion_alpha_table,
    expansion_temperature_table,
    integral_results,
    interpolation_table,
    mean_friction,
)
from frame_balance import balance_by_transverse_axis
from input_validator import parse_float_list, require_odd, require_positive, to_float, to_int


TASKS = [
    "1 - Расчёт объёма и площадей",
    "2 - Контактное давление",
    "3 - Удлинение стальной заготовки",
    "4 - Таблица удлинений",
    "5 - Балансировка масс рамы",
    "6 - Интерполяция Ньютона и Лагранжа",
    "7 - Интегрирование",
]


class Variant17App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Вариант 17")
        self.geometry("660x455")
        self.configure(bg="white")
        self.resizable(False, False)
        self.show_main_menu()

    def clear(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()

    def make_title(self, text: str) -> None:
        tk.Label(self, text=text, bg="white", fg="black", font=("Arial", 18, "bold"), anchor="w").pack(fill="x", padx=18, pady=(16, 8))

    def make_button(self, parent: tk.Widget, text: str, command) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg="white",
            fg="black",
            activebackground="#eeeeee",
            font=("Arial", 13),
            relief="solid",
            bd=3,
            anchor="w",
            padx=20,
            pady=9,
        )

    def output_box(self, parent: tk.Widget) -> tk.Text:
        box = tk.Text(parent, height=10, bg="white", fg="black", relief="solid", bd=2, font=("Consolas", 12))
        box.pack(fill="both", expand=True, pady=8)
        return box

    def set_output(self, box: tk.Text, text: str) -> None:
        box.delete("1.0", tk.END)
        box.insert(tk.END, text)

    def make_arrow_panel(self, parent: tk.Widget, decrease_command, increase_command, label_var: tk.StringVar) -> None:
        panel = tk.Frame(parent, bg="white", relief="solid", bd=3)
        panel.pack(fill="x", pady=8)
        tk.Button(panel, text="←  -10°C", command=decrease_command, bg="white", fg="black",
                  activebackground="#eeeeee", font=("Arial", 13), relief="flat", padx=20, pady=9).pack(side="left")
        tk.Label(panel, textvariable=label_var, bg="white", fg="black", font=("Arial", 13, "bold"),
                 width=16).pack(side="left", expand=True)
        tk.Button(panel, text="+10°C  →", command=increase_command, bg="white", fg="black",
                  activebackground="#eeeeee", font=("Arial", 13), relief="flat", padx=20, pady=9).pack(side="right")

    def show_error(self, box: tk.Text, error: Exception) -> None:
        self.set_output(box, f"Ошибка: {error}")

    def show_main_menu(self) -> None:
        self.clear()
        self.make_title("Вариант 17")
        container = tk.Frame(self, bg="white")
        container.pack(fill="both", expand=True, padx=18, pady=4)
        for index, task in enumerate(TASKS, start=1):
            btn = self.make_button(container, task, lambda i=index: self.open_task(i))
            btn.pack(fill="x", pady=5)

    def back_button(self, parent: tk.Widget) -> None:
        tk.Button(parent, text="← Назад", command=self.show_main_menu, bg="white", fg="black", relief="solid", bd=2, padx=14).pack(anchor="w", pady=(0, 8))

    def screen_base(self, title: str) -> tuple[tk.Frame, tk.Text]:
        self.clear()
        self.make_title(title)
        container = tk.Frame(self, bg="white")
        container.pack(fill="both", expand=True, padx=18, pady=4)
        self.back_button(container)
        box = self.output_box(container)
        return container, box

    def add_entry(self, parent: tk.Widget, label: str, default: str = "") -> tk.Entry:
        row = tk.Frame(parent, bg="white")
        row.pack(fill="x", pady=3)
        tk.Label(row, text=label, bg="white", fg="black", width=28, anchor="w", font=("Arial", 12)).pack(side="left")
        entry = tk.Entry(row, relief="solid", bd=2, font=("Arial", 12))
        entry.insert(0, default)
        entry.pack(side="left", fill="x", expand=True)
        return entry

    def open_task(self, index: int) -> None:
        getattr(self, f"task_{index}")()

    def task_1(self) -> None:
        container, box = self.screen_base(TASKS[0])
        a_entry = self.add_entry(container, "a", "2")
        h_entry = self.add_entry(container, "h", "5")

        def run() -> None:
            try:
                a = require_positive(to_float(a_entry.get(), "a"), "a")
                h = require_positive(to_float(h_entry.get(), "h"), "h")
                result = calc_volume_and_areas(a, h)
                self.set_output(box, f"V = {result.volume:.6g}\nSб = {result.side_area:.6g}\nSп = {result.full_area:.6g}")
            except Exception as exc:
                self.show_error(box, exc)

        self.make_button(container, "Посчитать", run).pack(fill="x", pady=6)

    def task_2(self) -> None:
        container, box = self.screen_base(TASKS[1])
        material_var = tk.StringVar(value="сталь-алюминий")
        row = tk.Frame(container, bg="white")
        row.pack(fill="x", pady=3)
        tk.Label(row, text="материал", bg="white", width=28, anchor="w", font=("Arial", 12)).pack(side="left")
        ttk.Combobox(row, textvariable=material_var, values=list(MATERIAL_FRICTION_RANGES), state="readonly").pack(side="left", fill="x", expand=True)
        torque = self.add_entry(container, "Mk, Н·м", "100")
        reserve = self.add_entry(container, "K", "1.5")
        diameter = self.add_entry(container, "d, мм", "20")
        length = self.add_entry(container, "l, мм", "50")

        def run() -> None:
            try:
                mu = mean_friction(material_var.get())
                pressure = calc_contact_pressure(
                    require_positive(to_float(torque.get(), "Mk"), "Mk"),
                    require_positive(to_float(reserve.get(), "K"), "K"),
                    mu,
                    require_positive(to_float(diameter.get(), "d"), "d"),
                    require_positive(to_float(length.get(), "l"), "l"),
                )
                low, high = MATERIAL_FRICTION_RANGES[material_var.get()]
                self.set_output(box, f"Материал: {material_var.get()}\nμ диапазон: {low}..{high}\nμ среднее: {mu}\nqm ≥ {pressure:.8g}")
            except Exception as exc:
                self.show_error(box, exc)

        self.make_button(container, "Посчитать", run).pack(fill="x", pady=6)

    def task_3(self) -> None:
        container, box = self.screen_base(TASKS[2])
        current_temp = tk.IntVar(value=20)
        label_var = tk.StringVar()

        def refresh() -> None:
            temp = current_temp.get()
            delta_l = expansion_temperature_table(start_temp=20, end_temp=temp)[-1][1]
            label_var.set(f"T = {temp}°C")
            self.set_output(
                box,
                "T, °C      ΔL, мм\n"
                f"{temp:<10}{delta_l:.6f}"
            )

        def decrease() -> None:
            if current_temp.get() > 20:
                current_temp.set(current_temp.get() - 10)
                refresh()

        def increase() -> None:
            if current_temp.get() < 80:
                current_temp.set(current_temp.get() + 10)
                refresh()

        self.make_arrow_panel(container, decrease, increase, label_var)
        refresh()

    def task_4(self) -> None:
        container, box = self.screen_base(TASKS[3])
        current_dt = tk.IntVar(value=60)
        label_var = tk.StringVar()

        def refresh() -> None:
            dt = current_dt.get()
            rows = expansion_alpha_table(delta_t_values=[dt])
            lines = [f"ΔT = {dt}°C", "", "α             ΔL, мм"]
            lines += [f"{alpha:<14.6g}{dl:.6f}" for _, alpha, dl in rows]
            label_var.set(f"ΔT = {dt}°C")
            self.set_output(box, "\n".join(lines))

        def decrease() -> None:
            if current_dt.get() > 60:
                current_dt.set(current_dt.get() - 10)
                refresh()

        def increase() -> None:
            if current_dt.get() < 100:
                current_dt.set(current_dt.get() + 10)
                refresh()

        self.make_arrow_panel(container, decrease, increase, label_var)
        refresh()

    def task_5(self) -> None:
        container, box = self.screen_base(TASKS[4])
        n_entry = self.add_entry(container, "n, нечётное", "3")
        masses_entry = self.add_entry(container, "массы", "1,2,3,4,5,6,7,8,9")

        def run() -> None:
            try:
                n = require_odd(to_int(n_entry.get(), "n"), "n")
                masses = parse_float_list(masses_entry.get(), n * n)
                result = balance_by_transverse_axis(n, masses)
                lines = ["Матрица масс:"]
                lines += ["  ".join(f"{value:7.2f}" for value in row) for row in result.matrix]
                lines += [
                    "",
                    f"Верхняя часть: {result.upper_sum:.3f}",
                    f"Нижняя часть: {result.lower_sum:.3f}",
                    f"Разница: {result.difference_percent:.2f}%",
                    "Баланс выполнен" if result.is_balanced else "Баланс НЕ выполнен",
                ]
                self.set_output(box, "\n".join(lines))
            except Exception as exc:
                self.show_error(box, exc)

        self.make_button(container, "Сбалансировать", run).pack(fill="x", pady=6)

    def task_6(self) -> None:
        container, box = self.screen_base(TASKS[5])

        def run() -> None:
            rows = interpolation_table()
            lines = ["xTi        Лагранж        Ньютон        разница"]
            for x, lagrange, newton in rows:
                lines.append(f"{x:<11.4f}{lagrange:<15.6f}{newton:<14.6f}{abs(lagrange-newton):.8f}")
            self.set_output(box, "\n".join(lines))

        run()

    def task_7(self) -> None:
        container, box = self.screen_base(TASKS[6])

        def run() -> None:
            rect, trap, simp = integral_results()
            self.set_output(box, f"∫ от 1 до 2: 0.5 * e^(sqrt(1 + 2x)) dx\nh = 0.2\n\nПрямоугольники = {rect:.8f}\nТрапеции      = {trap:.8f}\nСимпсон       = {simp:.8f}")

        run()


if __name__ == "__main__":
    app = Variant17App()
    app.mainloop()
