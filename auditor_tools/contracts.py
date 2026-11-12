"""Shared validation for explicitly supplied offline evidence."""

import json
import math
from pathlib import Path
import re


def mapping(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ValueError(f"{label} must be an object with string keys")
    return {key: item for key, item in value.items()}


def sequence(value: object, label: str) -> list[object]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be an array")
    return list(value)


def identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", value):
        raise ValueError(f"{label} must be a non-sensitive identifier of at most 64 ASCII characters")
    return value


def number(value: object, label: str) -> float:
    if type(value) not in (int, float):
        raise ValueError(f"{label} must be a finite nonnegative number")
    try:
        result = float(value)
    except OverflowError as error:
        raise ValueError(f"{label} is outside the supported numeric range") from error
    if not math.isfinite(result) or result < 0:
        raise ValueError(f"{label} must be a finite nonnegative number")
    return result


def integer(value: object, label: str, *, strings: bool = False) -> int:
    if strings and isinstance(value, str) and re.fullmatch(r"[0-9]{1,20}", value):
        value = int(value)
    if type(value) is not int or not 0 <= value <= 2**64 - 1:
        raise ValueError(f"{label} must be an unsigned 64-bit integer")
    return value


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _invalid_constant(value: str) -> object:
    raise ValueError("non-finite JSON numbers are not supported")


def load_json(path: Path) -> object:
    with path.open("rb") as stream:
        content = stream.read(64 * 1024 * 1024 + 1)
    if len(content) > 64 * 1024 * 1024:
        raise ValueError("input exceeds the 64 MiB offline limit")
    return json.loads(
        content.decode("utf-8-sig"), object_pairs_hook=_unique_object,
        parse_constant=_invalid_constant,
    )
