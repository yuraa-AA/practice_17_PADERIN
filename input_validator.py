from __future__ import annotations


def to_float(value: str, field_name: str = "значение") -> float:
    """Преобразование строки в число. Запятая допускается как десятичный разделитель."""
    try:
        return float(str(value).strip().replace(",", "."))
    except ValueError as exc:
        raise ValueError(f"Поле '{field_name}' должно быть числом") from exc


def to_int(value: str, field_name: str = "значение") -> int:
    """Преобразование строки в целое число."""
    try:
        return int(str(value).strip())
    except ValueError as exc:
        raise ValueError(f"Поле '{field_name}' должно быть целым числом") from exc


def require_positive(value: float, field_name: str = "значение") -> float:
    if value <= 0:
        raise ValueError(f"Поле '{field_name}' должно быть больше 0")
    return value


def require_odd(value: int, field_name: str = "n") -> int:
    if value <= 0:
        raise ValueError(f"Поле '{field_name}' должно быть больше 0")
    if value % 2 == 0:
        raise ValueError(f"Поле '{field_name}' должно быть нечётным числом")
    return value


def parse_float_list(text: str, expected_count: int | None = None) -> list[float]:
    """Преобразование списка масс, введённых через пробел, запятую или точку с запятой."""
    if not text.strip():
        raise ValueError("Нужно ввести массы через пробел или запятую")
    raw = text.replace(";", ",").replace("\n", ",").split(",")
    if len(raw) == 1:
        raw = text.split()
    values = [to_float(item, "масса") for item in raw if item.strip()]
    if expected_count is not None and len(values) != expected_count:
        raise ValueError(f"Нужно ввести ровно {expected_count} значений масс")
    for value in values:
        require_positive(value, "масса")
    return values
