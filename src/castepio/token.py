from dataclasses import dataclass
from enum import Enum
from typing import Any


class TokenType(Enum):
    EOF = 0
    PIPE = 1
    COLON = 2
    COMMA = 3
    EQUALS = 4
    ATSIGN = 5
    PERCENT = 6
    PAREN_LEFT = 7
    PAREN_RIGHT = 8
    BRACK_LEFT = 9
    BRACK_RIGHT = 10
    BRACE_LEFT = 11
    BRACE_RIGHT = 12
    CHEVRON_LEFT = 13
    CHEVRON_RIGHT = 14
    WHITESPACE = 16
    NEWLINE = 15
    STRING = 17
    FLOAT = 18


@dataclass
class Token:
    token_type: TokenType
    lexeme: str
    literal: Any
    line: int
    col: int
    index: int

    def __str__(self):
        return f"{self.token_type} {self.lexeme} {self.literal}"


@dataclass
class Comment:
    comment: str
    marker: str
    line: int
    col: int
    index: int


class TokenError(Exception):
    ...
