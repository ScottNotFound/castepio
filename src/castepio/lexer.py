from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import overload

from .token import Comment, Token, TokenError, TokenType


class Lexer(ABC):
    """
    This is the base lexer class. Provides tools to lex files or source strings.
    An implementing class only needs to implement `lex_token` to define how the 
    lexer should handle its current state. The state should generally be handled
    by reading one or many characters from the source and adding a token. The state
    may alternatively be handled by adding comments, doing nothing, or raising an error.
    It is up to the implementing class to decide how to lex, whether it should be 
    context aware, how far to look ahead, exception handling, etc.

    The lexing is iterated by `lex_self` where the lexer checks for the end, then 
    resets the start index, then calls `lex_token`.
    """
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
        """Check n characters ahead to find the end of the source. Default is 0."""
        return self.current + n >= len(self.source)

    def peek(self, n: int = 0) -> str:
        """Peek n characters ahead. Defualt is 0, the current character. Does not consume."""
        if self.end():
            return "\0"
        return self.source[self.current + n]

    def peek_current(self) -> str:
        """Peek the current character. Does not consume."""
        return self.peek()

    def peek_next(self) -> str:
        """Peek up to the next character. Does not consume."""
        return self.peek(1)

    def advance(self, n: int = 1) -> str:
        """Advance the lexer n characters ahead. Consumes."""
        current = self.current
        self.current += n
        return self.source[current]

    def match_any(self, text: str) -> bool:
        """Checks if `text` contains the current character."""
        return self.source[self.current] in text

    def match(self, text: str, case: bool = False) -> bool:
        """
        Checks source from current character for match with `text`.
        Case sensitive if `case` is True, default is False. 
        Consumes and returns True if match.
        """
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
        """Add a token with a type. Include `value` if token is a literal or should hold a value."""
        lexeme = self.source[self.start : self.current]
        self.tokens.append(
            Token(
                tt, lexeme, value, self.line, self.start - self.lastline, self.current
            )
        )
        return None

    def add_comment(self, marker: str) -> None:
        """Add a comment with `marker` as the character that marks the comment."""
        lexeme = self.source[self.start : self.current]
        comment = lexeme[len(marker) :]
        self.comments.append(
            Comment(
                comment, marker, self.line, self.start - self.lastline, self.current
            )
        )

    def consume_whitespace(self) -> None:
        """Consumes whitespace greedily."""
        match = re.match(r"[ \t\r\f\v]+", self.source[self.current :])
        if match:
            self.current += match.end()

    def get_line(self) -> str:
        """Return the entire line the lexer is currently reading."""
        endline = self.source[self.lastline :].find("\n") + self.lastline
        return self.source[self.lastline : endline]

    def lex_error(self, c: str) -> None:
        """Raise a TokenError on the given character."""
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
        """Lexes the source."""
        lexer = cls()
        return lexer.lex(source)

    @classmethod
    def tokpass(cls, source: str) -> str:
        """
        Lexes the source and joines the token lexems together.
        Essentially shows the source as the lexer sees it in token land.
        """
        return "".join(token.lexeme for token in cls.static_lex(source))

    @classmethod
    def lex_file(cls, filename: str) -> list[Token]:
        """Lexes the file."""
        with open(filename, "r") as f:
            lexer = cls()
            lexer.filename = filename
            return lexer.lex(f.read())
