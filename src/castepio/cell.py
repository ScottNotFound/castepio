"""Context free lexer for the castep cell file."""

from __future__ import annotations

from .lexer import Lexer
from .token import TokenError, TokenType


class CellLexer(Lexer):

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
                raise TokenError(
                    f"Unrecognized character {c} at {self.line}:{self.current - self.lastline}."
                )
        return None
