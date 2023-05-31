from __future__ import annotations

from abc import ABC, ABCMeta
from dataclasses import dataclass
from typing import Any

# Keyword Structure


@dataclass
class Keyword(ABC):
    key: str
    definition: Value | Block


@dataclass
class KeywordV(Keyword):
    definition: Value


@dataclass
class KeywordB(Keyword):
    definition: Block


@dataclass
class Value(metaclass=ABCMeta):
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


@dataclass
class Integer(Number):
    value: int


@dataclass
class Real(Number):
    value: float


@dataclass
class Physical(Real):
    value: float
    units: str | None


@dataclass
class Vector(Value):
    value: list[Value]


@dataclass
class Line:
    value: list[Value]
    flag: KeywordV


@dataclass
class Block:
    value: list[Line]
    units: str | None
