from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BalanceResult:
    matrix: list[list[float]]
    upper_sum: float
    lower_sum: float
    difference_percent: float
    is_balanced: bool


def balance_by_transverse_axis(n: int, masses: list[float], allowed_percent: float = 15.0) -> BalanceResult:
    """Задача 5: балансировка масс рамы относительно поперечной оси.

    Матрица имеет размер n×n. Средняя строка лежит на поперечной оси и
    не участвует в сравнении верхней и нижней частей.
    """
    if n <= 0 or n % 2 == 0:
        raise ValueError("n должно быть положительным нечётным числом")
    if len(masses) != n * n:
        raise ValueError(f"Нужно {n * n} масс для матрицы {n}×{n}")
    if any(m <= 0 for m in masses):
        raise ValueError("Все массы должны быть больше 0")

    matrix = [[0.0 for _ in range(n)] for _ in range(n)]
    sorted_masses = sorted(masses, reverse=True)

    upper_positions = [(r, c) for r in range(n // 2) for c in range(n)]
    lower_positions = [(r, c) for r in range(n // 2 + 1, n) for c in range(n)]
    axis_positions = [(n // 2, c) for c in range(n)]

    upper_sum = 0.0
    lower_sum = 0.0
    upper_i = 0
    lower_i = 0

    for mass in sorted_masses:
        if upper_i < len(upper_positions) and (upper_sum <= lower_sum or lower_i >= len(lower_positions)):
            r, c = upper_positions[upper_i]
            upper_i += 1
            upper_sum += mass
        elif lower_i < len(lower_positions):
            r, c = lower_positions[lower_i]
            lower_i += 1
            lower_sum += mass
        else:
            r, c = axis_positions.pop(0)
        matrix[r][c] = mass

    denominator = max(upper_sum, lower_sum, 1.0)
    difference_percent = abs(upper_sum - lower_sum) / denominator * 100
    return BalanceResult(matrix, upper_sum, lower_sum, difference_percent, difference_percent <= allowed_percent)
