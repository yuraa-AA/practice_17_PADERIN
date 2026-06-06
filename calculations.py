from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable


MATERIAL_FRICTION_RANGES: dict[str, tuple[float, float]] = {
    "сталь-алюминий": (0.02, 0.06),
    "сталь-латунь": (0.05, 0.10),
    "сталь-пластмасса": (0.40, 0.50),
}


@dataclass(frozen=True)
class AreasResult:
    volume: float
    side_area: float
    full_area: float


def calc_volume_and_areas(a: float, h: float) -> AreasResult:
    """Задача 1: V = a²h, Sб = 4ah, Sп = 4ah + 2a²."""
    if a <= 0 or h <= 0:
        raise ValueError("a и h должны быть больше 0")
    volume = a**2 * h
    side_area = 4 * a * h
    full_area = side_area + 2 * a**2
    return AreasResult(volume, side_area, full_area)


def calc_contact_pressure(torque: float, reserve_factor: float, friction: float, diameter: float, length: float) -> float:
    """Задача 2: qm >= 2*Mk*K / (mu*pi*d²*l)."""
    for name, value in {
        "крутящий момент": torque,
        "коэффициент запаса": reserve_factor,
        "коэффициент трения": friction,
        "диаметр": diameter,
        "длина": length,
    }.items():
        if value <= 0:
            raise ValueError(f"{name} должен быть больше 0")
    return (2 * torque * reserve_factor) / (friction * math.pi * diameter**2 * length)


def mean_friction(material_key: str) -> float:
    if material_key not in MATERIAL_FRICTION_RANGES:
        raise ValueError("Неизвестное сочетание материалов")
    low, high = MATERIAL_FRICTION_RANGES[material_key]
    return (low + high) / 2


def expansion(length: float, alpha: float, delta_t: float) -> float:
    """Задачи 3-4: ΔL = L * alpha * ΔT."""
    if length <= 0:
        raise ValueError("длина должна быть больше 0")
    if alpha <= 0:
        raise ValueError("коэффициент расширения должен быть больше 0")
    return length * alpha * delta_t


def expansion_temperature_table(start_temp: int = 20, end_temp: int = 80, step: int = 10,
                                length: float = 250, alpha: float = 12e-6) -> list[tuple[int, float]]:
    """Задача 3: нагрев от 20 до 80 °C, ΔT считается относительно 20 °C."""
    return [(temp, expansion(length, alpha, temp - start_temp))
            for temp in range(start_temp, end_temp + 1, step)]


def expansion_alpha_table(length: float = 100,
                          delta_t_values: list[int] | None = None,
                          alpha_values: list[float] | None = None) -> list[tuple[int, float, float]]:
    """Задача 4: ΔT 60..100 °C, alpha 12e-6..16e-6."""
    delta_t_values = delta_t_values or list(range(60, 101, 10))
    alpha_values = alpha_values or [value * 1e-6 for value in range(12, 17)]
    return [(dt, alpha, expansion(length, alpha, dt)) for dt in delta_t_values for alpha in alpha_values]


def variant17_nodes() -> tuple[list[float], list[float]]:
    """Узлы табличной функции для задачи 6."""
    b = 10.8
    x = [0, b / 4, b / 2, 0.75 * b, b]
    y = [-9.4, -12.8, -8.7, -0.4, 1.1]
    return x, y


def lagrange_value(x_nodes: list[float], y_nodes: list[float], x: float) -> float:
    """Задача 6: значение интерполяционного многочлена Лагранжа."""
    if len(x_nodes) != len(y_nodes):
        raise ValueError("Количество x и y должно совпадать")
    total = 0.0
    for i, xi in enumerate(x_nodes):
        term = y_nodes[i]
        for j, xj in enumerate(x_nodes):
            if i != j:
                term *= (x - xj) / (xi - xj)
        total += term
    return total


def divided_differences(x_nodes: list[float], y_nodes: list[float]) -> list[float]:
    """Задача 6: коэффициенты для многочлена Ньютона."""
    if len(x_nodes) != len(y_nodes):
        raise ValueError("Количество x и y должно совпадать")
    coef = y_nodes[:]
    n = len(x_nodes)
    for j in range(1, n):
        for i in range(n - 1, j - 1, -1):
            coef[i] = (coef[i] - coef[i - 1]) / (x_nodes[i] - x_nodes[i - j])
    return coef


def newton_value(x_nodes: list[float], coefficients: list[float], x: float) -> float:
    """Задача 6: значение интерполяционного многочлена Ньютона."""
    result = coefficients[-1]
    for i in range(len(coefficients) - 2, -1, -1):
        result = result * (x - x_nodes[i]) + coefficients[i]
    return result


def interpolation_table() -> list[tuple[float, float, float]]:
    """Задача 6: значения в точках xTi = xi + b/8 для i=0..3."""
    x_nodes, y_nodes = variant17_nodes()
    b = 10.8
    points = [x + b / 8 for x in x_nodes[:-1]]
    coef = divided_differences(x_nodes, y_nodes)
    return [(x, lagrange_value(x_nodes, y_nodes, x), newton_value(x_nodes, coef, x)) for x in points]


def task7_function(x: float) -> float:
    """Подынтегральная функция задачи 7: 0.5 * e^(sqrt(1 + 2x))."""
    return 0.5 * math.exp(math.sqrt(1 + 2 * x))


def rectangle_integral(func: Callable[[float], float], a: float, b: float, h: float) -> float:
    """Задача 7: метод средних прямоугольников."""
    n = round((b - a) / h)
    return sum(func(a + (i + 0.5) * h) for i in range(n)) * h


def trapezoid_integral(func: Callable[[float], float], a: float, b: float, h: float) -> float:
    """Задача 7: метод трапеций."""
    n = round((b - a) / h)
    total = 0.5 * (func(a) + func(b))
    total += sum(func(a + i * h) for i in range(1, n))
    return total * h


def simpson_integral(func: Callable[[float], float], a: float, b: float, h: float) -> float:
    """Задача 7: композитный метод Симпсона."""
    n = round((b - a) / h)
    if n < 2:
        raise ValueError("Для метода Симпсона нужно минимум 2 интервала")
    if n % 2 == 0:
        total = func(a) + func(b)
        total += 4 * sum(func(a + i * h) for i in range(1, n, 2))
        total += 2 * sum(func(a + i * h) for i in range(2, n, 2))
        return total * h / 3

    split = b - 3 * h
    result = 0.0
    even_n = n - 3
    if even_n > 0:
        result += simpson_integral(func, a, split, h)
    result += 3 * h / 8 * (func(split) + 3 * func(split + h) + 3 * func(split + 2 * h) + func(b))
    return result


def integral_results() -> tuple[float, float, float]:
    """Задача 7: интеграл на отрезке [1; 2] с шагом h = 0.2."""
    a, b, h = 1.0, 2.0, 0.2
    return (
        rectangle_integral(task7_function, a, b, h),
        trapezoid_integral(task7_function, a, b, h),
        simpson_integral(task7_function, a, b, h),
    )
