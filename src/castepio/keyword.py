from __future__ import annotations

from abc import ABC, ABCMeta
from dataclasses import dataclass
from typing import Any

# Keyword Structure


@dataclass
class Keyword(ABC):
    key: str


@dataclass
class Value(Keyword, metaclass=ABCMeta):
    value: Any


@dataclass
class String(Value):
    value: str


@dataclass
class Logical(Value):
    value: bool


@dataclass
class Number(Value, metaclass=ABCMeta):
    value: int | float
    units: str


@dataclass
class Integer(Number):
    value: int


@dataclass
class Real(Number):
    value: float


@dataclass
class Line:
    value: list[Value]


@dataclass
class Block(Keyword):
    value: list[Line]
    units: str
