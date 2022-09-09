from __future__ import annotations

import re
from abc import ABC, abstractmethod

from .lexer import Lexer


class Parser(ABC):
    lexer: Lexer
    