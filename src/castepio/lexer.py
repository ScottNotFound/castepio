from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import overload

from .token import Comment, Token, TokenError, TokenType


class Lexer(ABC):
    filename: str = ""
    source: str
    tokens: list[Token] = []
    comments: list[Comment] = []
    start: int = 0
    current: int = 0
    line: int = 1
    lastline: int = 0

    FLOAT: re.Pattern = re.compile(r"[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?")
    STRING: re.Pattern = re.compile(r"[\w+./-]+")

    @abstractmethod
    def lex_token(self) -> None:
        ...

    @overload
    def lex(self, source: str) -> list[Token]:
        ...

    @overload
    def lex(self) -> list[Token]:
        ...

    def lex(self, source: str | None = None) -> list[Token]:
        return self.lex_self() if source is None else self.lex_source(source)

    def lex_self(self) -> list[Token]:
        while not self.end():
            self.start = self.current
            self.lex_token()
        self.tokens.append(
            Token(TokenType.EOF, "", None, self.line, 0, self.current + 1)
        )
        return self.tokens

    def lex_source(self, source: str) -> list[Token]:
        self.source = source
        self.tokens = []
        self.comments = []
        self.line = 1
        self.start = 0
        self.current = 0
        return self.lex()

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
        comment = lexeme[len(marker) :]
        self.comments.append(
            Comment(
                comment, marker, self.line, self.start - self.lastline, self.current
            )
        )

    def consume_whitespace(self) -> None:
        match = re.match(r"[ \t\r\f\v]+", self.source[self.current :])
        if match:
            self.current += match.end()

    def get_line(self) -> str:
        endline = self.source[self.lastline :].find("\n") + self.lastline
        return self.source[self.lastline : endline]

    def lex_error(self, c: str) -> None:
        message = f"unrecognized character `{c}`"
        col = self.current - self.lastline
        reference = f" --> {self.filename}:{self.line}:{col}"
        underpoke = f"{'^':>{col}}"
        line = self.get_line()
        spaces = len(str(self.line)) + 1
        empty = " " * spaces
        detail = "\n".join(
            [f"{empty}|", f"{self.line:<{spaces}}|{line}", f"{empty}|{underpoke}"]
        )

        raise TokenError("\n".join([message, reference, detail]))

    @classmethod
    def static_lex(cls, source: str) -> list[Token]:
        lexer = cls()
        return lexer.lex(source)

    @classmethod
    def tokpass(cls, source: str) -> str:
        return "".join(token.lexeme for token in cls.static_lex(source))

    @classmethod
    def lex_file(cls, filename: str) -> list[Token]:
        with open(filename, "r") as f:
            lexer = cls()
            lexer.filename = filename
            return lexer.lex(f.read())
