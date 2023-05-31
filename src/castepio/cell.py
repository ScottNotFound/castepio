"""Context free lexer for the castep cell file."""

from __future__ import annotations

from .parser import Parser
from .lexer import Lexer
from .token import TokenError, TokenType


class CellLexer(Lexer):
    token_map: dict[str, TokenType] = {
        ":": TokenType.COLON,
        "=": TokenType.EQUALS,
        ",": TokenType.COMMA,
        "|": TokenType.PIPE,
        "%": TokenType.PERCENT,
        "@": TokenType.ATSIGN,
        "(": TokenType.PAREN_LEFT,
        ")": TokenType.PAREN_RIGHT,
        "[": TokenType.BRACE_LEFT,
        "]": TokenType.BRACE_RIGHT,
        "{": TokenType.BRACK_LEFT,
        "}": TokenType.BRACK_RIGHT,
        "<": TokenType.CHEVRON_LEFT,
        ">": TokenType.CHEVRON_RIGHT,
    }

    def lex_token(self) -> None:
        c: str = self.advance()
        if c == "\n":
            self.add_token(TokenType.NEWLINE)
            self.line += 1
            self.lastline = self.current
        elif c in [" ", "\r", "\t"]:
            self.consume_whitespace()
            self.add_token(TokenType.WHITESPACE)
        elif c in self.token_map:
            self.add_token(self.token_map[c])
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
                self.add_token(TokenType.STRING)
            else:
                self.lex_error(c)
        return None


class CellParser(Parser):
    pass