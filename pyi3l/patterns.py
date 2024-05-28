from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List, Optional
from .util import pcre_quote
from functools import reduce


class Pattern(ABC):
    @abstractmethod
    def to_pcre(self): pass

    @abstractmethod
    def to_python_re(self): pass
    
    @abstractmethod
    def map_chars(self, f): pass
    
    def __add__(self, other: "Pattern"):
        return CompoundPattern([self, other])

    def __or__(self, other: "Pattern"):
        return AnyOf([self, other])

    @staticmethod
    def import_pattern(s):
        if s is None:
            return None
        else:
            if s.startswith("^") and s.endswith("$"):
                return Pattern.import_pattern_part(s[1:-1]).optimize()
            else:
                raise ValueError("Cannot import pattern "+s)

    @staticmethod
    def import_pattern_part(s):
        def unsupported(s):
            raise ValueError(f"Unsupported pattern part: {s}")

        def import_default(s):
            return Literal(s[0]) + Pattern.import_pattern_part(s[1:])

        def import_escaped(s):
            if len(s) < 2:
                raise ValueError("Missing character after escape")
            c = s[1]
            rest = s[2:]
            if c.isalpha():
                raise ValueError(f"Unsupported escape char: {c}")
            return Literal(c) + Pattern.import_pattern_part(rest)

        if s == "":
            return Literal("")
        else:
            return {
                ".": unsupported,
                "^": unsupported,
                "$": unsupported,
                "*": unsupported,
                "+": unsupported,
                "?": unsupported,
                "(": unsupported,
                ")": unsupported,
                "[": unsupported,
                "{": unsupported,
                "\\": import_escaped,
                "|": unsupported,
            }.get(s[0], import_default)(s)

    def optimize(self):
        return self

@dataclass
class Literal(Pattern):
    s: str
    
    def to_pcre(self):
        return pcre_quote(self.s)

    def to_python_re(self):
        return re.escape(self.s)

    def map_chars(self, f):
        return Literal("".join(map(f, self.s)))

    def __add__(self, other: "Pattern"):
        if isinstance(other, Literal):
            return Literal(self.s+other.s)
        else:
            return CompoundPattern([self, other])

class Anything(Pattern):
    def to_pcre(self):
        return ".*"

    def to_python_re(self):
        return ".*"
    
    def map_chars(self, f):
        return self

@dataclass
class AnyOf(Pattern):
    variants: List[Pattern]

    def to_pcre(self):
        return "(" + "|".join(map(lambda p: p.to_pcre(), self.variants)) + ")"

    def to_python_re(self):
        return "(" + "|".join(map(lambda p: p.to_python_re(), self.variants)) + ")"

    def map_chars(self, f):
        return AnyOf(
            variants=list(map(lambda p: p.map_chars(f), self.variants)),
        )

    def optimize(self):
        return AnyOf(
            variants=list(map(lambda c: c.optimize(), self.variants)),
        )

    # just optimized version
    def __or__(self, other: "Pattern"):
        return AnyOf([*self.variants, other])


@dataclass
class CompoundPattern(Pattern):
    subpatterns: List[Pattern]

    def __add__(self, other: "Pattern"):
        return CompoundPattern([*self.subpatterns, other])

    def to_pcre(self):
        return "".join(map(lambda p: p.to_pcre(), self.subpatterns))

    def to_python_re(self):
        return "".join(map(lambda p: p.to_python_re(), self.subpatterns))
    
    def map_chars(self, f):
        return CompoundPattern(
            subpatterns=list(map(lambda p: p.map_chars(f), self.subpatterns)),
        )

    def optimize(self):
        return reduce(
            lambda a, b: a+b,
            map(lambda c: c.optimize(), self.subpatterns)
        )

@dataclass
class Raw(Pattern):
    # Please use composable PCRE regexes (without modifiers, without ^ and $)
    # ^ and $ will be added automatically afterwards
    pattern: str
    python_re: Optional[str]

    def to_pcre(self):
        return self.pattern

    def to_python_re(self):
        if self.python_re is not None:
            return self.python_re
        else:
            raise NotImplementedError(f'No Python regex alternative for {self.pattern}')

    def map_chars(self, f):
        raise Error(f"Cannot map chars of raw pattern {self}")
