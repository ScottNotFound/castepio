from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import overload

from .keyword import Keyword
from .lexer import Lexer
from .token import Token, TokenType


class ParseError(Exception):
    ...


class Parser(ABC):
    """
    This is the base parser class. Provides tools to parse lists
    of Tokens. It is up to the implementing class to define how
    a Keyword should be constructed from Tokens.
    """

    tokens: list[Token]
    keywords: list[Keyword] = []
    current: int = 0

    @abstractmethod
    def parse_keyword(self) -> Keyword:
        ...

    @overload
    def parse(self) -> list[Keyword]:
        ...

    @overload
    def parse(self, tokens: list[Token]) -> list[Keyword]:
        ...

    def parse(self, tokens: list[Token] | None = None) -> list[Keyword]:
        return self.parse_self() if tokens is None else self.parse_tokens(tokens)

    def parse_self(self) -> list[Keyword]:
        try:
            while not self.end():
                self.keywords.append(self.parse_keyword())
            return self.keywords
        except ParseError:
            return []

    def parse_tokens(self, tokens: list[Token]) -> list[Keyword]:
        self.tokens = tokens
        self.keywords = []
        self.current = 0
        return self.parse()

    def end(self, n: int = 0) -> bool:
        """Checks n tokens ahead to find the EOF token. Default is 0."""
        if n == 0:
            return self.tokens[self.current].token_type == TokenType.EOF
        else:
            for token in self.tokens[self.current : self.current + n + 1]:
                if token.token_type == TokenType.EOF:
                    return True
            return False

    def peek(self, n: int = 0) -> Token:
        """Peeks ahead to get the nth token. Default is current."""
        return self.tokens[self.current + n]

    def peek_current(self) -> Token:
        return self.peek()

    def peek_next(self) -> Token:
        return self.peek(1)

    def peek_previous(self) -> Token:
        return self.peek(-1)

    def advance(self) -> Token:
        if not self.end():
            self.current += 1
        return self.peek_previous()

    def check_current_s(self, tokentype: TokenType) -> bool:
        return not self.end() and self.peek_current().token_type == tokentype

    def check_current(self, *args: TokenType) -> bool:
        for tokentype in args:
            if self.check_current_s(tokentype):
                return True
        return False

    def match_current(self, *args: TokenType) -> bool:
        for tokentype in args:
            if self.check_current_s(tokentype):
                self.advance()
                return True
        return False

    def error(self, token: Token, message: str | None = None) -> ParseError:
        if not message:
            message = f"Error parsing token {token.lexeme}"
        reference = f" --> <filename>:{token.line}:{token.col}"
        underpoke = f"{'^':>{token.col}}"
        spaces = len(str(token.line)) + 1
        empty = " " * spaces
        detail = "\n".join(
            [
                f"{empty}|",
                f"{token.line:<{spaces}}|{token.line}",
                f"{empty}|{underpoke}",
            ]
        )
        return ParseError("\n".join([message, reference, detail]))

    def require_token(self, tokentype: TokenType, message: str | None = None) -> Token:
        if self.check_current_s(tokentype):
            return self.advance()
        raise self.error(self.peek_current(), message)

    @classmethod
    def static_parse(cls, tokens: list[Token]) -> list[Keyword]:
        parser = cls()
        return parser.parse(tokens)
