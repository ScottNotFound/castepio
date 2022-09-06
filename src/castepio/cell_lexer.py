"""Context sensetive lexer for the castep cell file."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import Any, overload

class LexError(Exception):
    ...

TokenType = Enum(
    "TokenType",
    [
        "PAREN_LEFT",
        "PAREN_RIGHT",
        "BRACK_LEFT",
        "BRACK_RIGHT",
        "BRACE_LEFT",
        "BRACE_RIGHT",
        "CHEVRON_LEFT",
        "CHEVRON_RIGHT",
        "ATSIGN",
        "PERCENT",
        "COLON",
        "EQUALS",
        "COMMA",
        "PIPE",
        "STRING",
        "FLOAT",
        "NEWLINE",
        "WHITESPACE",
        "EOF",
    ],
)


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


class Lexer:
    source: str
    tokens: list[Token] = []
    comments: list[Comment] = []
    start: int = 0
    current: int = 0
    line: int = 1
    lastline: int = 0

    FLOAT: re.Pattern = re.compile(r"[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?")
    STRING: re.Pattern = re.compile(r"[\w+-./]+")

    def end(self, n: int = 0) -> bool:
        return self.current + n >= len(self.source)

    def peek(self, n: int = 0) -> str:
        if self.end():
            return "\0"
        return self.source[self.current + n]

    def peek_current(self) -> str:
        return self.peek()

    def peek_next(self) -> str:
        return self.peek(1)

    def advance(self, n: int = 1) -> str:
        current = self.current
        self.current += n
        return self.source[current]

    def match_any(self, text: str) -> bool:
        return self.source[self.current] in text

    def match(self, text: str, case: bool = False) -> bool:
        if self.end():
            return False
        if case:
            if not self.source[self.current :].startswith(text):
                return False
        else:
            if (
                self.source[self.current : self.current + len(text)].lower()
                != text.lower()
            ):
                return False
        self.current += len(text)
        return True

    def add_token(self, tt: TokenType, value: object = None) -> None:
        lexeme = self.source[self.start : self.current]
        self.tokens.append(
            Token(
                tt, lexeme, value, self.line, self.start - self.lastline, self.current
            )
        )
        return None

    def add_comment(self, marker: str) -> None:
        lexeme = self.source[self.start : self.current]
        comment = lexeme[len(marker):]
        self.comments.append(
            Comment(
                comment, marker, self.line, self.start - self.lastline, self.current
            )
        )

    def consume_whitespace(self) -> None:
        match = re.match(r"\s+", self.source[self.current:])
        if match:
            self.current += match.end()

    def lex_token(self) -> None:
        c: str = self.advance()
        if c == "\n":
            self.add_token(TokenType.NEWLINE)
            self.line += 1
            self.lastline = self.current
        elif c in [" ", "\r", "\t"]:
            self.consume_whitespace()
            self.add_token(TokenType.WHITESPACE)
        elif c == ":":
            self.add_token(TokenType.COLON)
        elif c == "=":
            self.add_token(TokenType.EQUALS)
        elif c == ",":
            self.add_token(TokenType.COMMA)
        elif c == "|":
            self.add_token(TokenType.PIPE)
        elif c == "%":
            self.add_token(TokenType.PERCENT)
        elif c == "@":
            self.add_token(TokenType.ATSIGN)
        elif c == "(":
            self.add_token(TokenType.PAREN_LEFT)
        elif c == ")":
            self.add_token(TokenType.PAREN_RIGHT)
        elif c == "[":
            self.add_token(TokenType.BRACE_LEFT)
        elif c == "]":
            self.add_token(TokenType.BRACE_RIGHT)
        elif c == "{":
            self.add_token(TokenType.BRACK_LEFT)
        elif c == "}":
            self.add_token(TokenType.BRACK_RIGHT)
        elif c == "<":
            self.add_token(TokenType.CHEVRON_LEFT)
        elif c == ">":
            self.add_token(TokenType.CHEVRON_RIGHT)
        elif c in ["!", "#", ";"]:
            while self.peek() != "\n" and not self.end():
                self.advance()
            self.add_comment(c)
        else:
            if match := self.FLOAT.match(self.source[self.start :]):
                self.current += match.end() - 1
                self.add_token(TokenType.FLOAT, float(match.group()))
            elif match := self.STRING.match(self.source[self.start :]):
                self.current += match.end() - 1
                if match.group().lower() == "comment":
                    self.add_comment(match.group())
                self.add_token(TokenType.STRING)
            else:
                raise LexError(f"Unrecognized character {c} at {self.line}:{self.current - self.lastline}.")
        return None

    def lex_self(self) -> list[Token]:
        while not self.end():
            self.start = self.current
            self.lex_token()
        self.tokens.append(
            Token(TokenType.EOF, "", None, self.line, self.col, self.current)
        )
        return self.tokens

    def lex_source(self, source: str) -> list[Token]:
        self.source = source
        self.tokens = []
        self.comments = []
        self.line = 1
        self.col = 1
        self.start = 0
        self.current = 0
        return self.lex()

    @overload
    def lex(self, source: str) -> list[Token]:
        ...

    @overload
    def lex(self) -> list[Token]:
        ...

    def lex(self, source: str | None = None) -> list[Token]:
        return self.lex_self() if source is None else self.lex_source(source)

    @classmethod
    def static_lex(cls, source: str) -> list[Token]:
        lexer = cls()
        return lexer.lex(source)

    @classmethod
    def tokpass(cls, source: str) -> str:
        return "".join(token.lexeme for token in cls.static_lex(source))
