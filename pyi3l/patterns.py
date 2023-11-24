from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List
from .util import pcre_quote


class Pattern(ABC):
    @abstractmethod
    def to_pcre(self): pass
    
    @abstractmethod
    def map_chars(self, f): pass
    
    def __add__(self, other: "Pattern"):
        return CompoundPattern([self, other])

@dataclass
class Literal(Pattern):
    s: str
    
    def to_pcre(self):
        return pcre_quote(self.s)
        
    def map_chars(self, f):
        return Literal("".join(map(f, self.s)))

class Anything(Pattern):
    def to_pcre(self):
        return ".*"
    
    def map_chars(self, f):
        return self

@dataclass
class AnyOf(Pattern):
    variants: List[Pattern]

    def to_pcre(self):
        return "(" + "|".join(map(lambda p: p.to_pcre(), self.variants)) + ")"
    
    def map_chars(self, f):
        return AnyOf(
            variants=list(map(lambda p: p.map_chars(f), self.variants)),
        )

@dataclass
class CompoundPattern(Pattern):
    subpatterns: List[Pattern]

    def __add__(self, other: "Pattern"):
        return CompoundPattern([*self.subpatterns, other])

    def to_pcre(self):
        return "".join(map(lambda p: p.to_pcre(), self.subpatterns))
    
    def map_chars(self, f):
        return CompoundPattern(
            subpatterns=list(map(lambda p: p.map_chars(f), self.subpatterns)),
        )

@dataclass
class Raw(Pattern):
    # Please use composable PCRE regexes (without modifiers, without ^ and $)
    # ^ and $ will be added automatically afterwards
    pattern: str
    
    def to_pcre(self):
        return self.pattern
    
    def map_chars(self, f):
        raise Error(f"Cannot map chars of raw pattern {self}")
