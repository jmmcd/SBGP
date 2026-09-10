#! /usr/bin/env python

# Taken from PonyGE
# Copyright (c) 2009-2012 Erik Hemberg and James McDermott
# Hereby licensed under the GNU GPL v3.
# http://ponyge.googlecode.com
#
# but improved/changed a bit since then:

# allow eg n_vars=10 kwarg 
# update to Py3
# represent symbol as string s, not tuple (s, "NT") 
# simplify the derivation using iterators

from typing import Dict, List, Set, Tuple, Iterator, Generator, Any, Optional
import re
import math
import itertools
from .exceptions import InvalidIndividualException

# Don't allow space in NTs, and use lookbehind to match "<"
# and ">" only if not preceded by backslash. Group the whole
# thing with capturing parentheses so that split() will return
# all NTs and Ts. TODO does this handle quoted NT symbols?
NON_TERMINAL_PATTERN = re.compile(r"((?<!\\)<\S+?(?<!\\)>)")

# Use lookbehind again to match "|" only if not preceded by
# backslash. Don't group, so split() will return only the
# productions, not the separators.
PRODUCTION_SEPARATOR = re.compile(r"(?<!\\)\|")

class Grammar:
    """Context Free Grammar"""

    def __init__(self, file_name: str, **kwargs: Any) -> None:
        self.rules: Dict[str, List[List[str]]] = {}
        self.non_terminals: Set[str] = set()
        self.terminals: Set[str] = set()
        self.start_rule: Optional[str] = None

        self.read_bnf_file(file_name, **kwargs)
        # TODO check lcm
        self.production_lcm: int = math.lcm(*(len(self.rules[k]) for k in self.non_terminals))
        # print('grammar self.production_lcm', self.production_lcm)

    def read_bnf_file(self, file_name: str, **kwargs: Any) -> None:
        """Read a grammar file in BNF format"""
        rule_separator = "::="

        # Read the grammar file
        with open(file_name, 'r') as f:
            for line in f:
                if not line.startswith("#") and line.strip() != "":
                    # Split rules. Everything must be on one line
                    if rule_separator in line:
                        lhs, productions = line.split(rule_separator, 1) # 1 split
                        lhs = lhs.strip()
                        if not NON_TERMINAL_PATTERN.search(lhs):
                            raise ValueError("lhs is not a NT:", lhs)
                        self.non_terminals.add(lhs)
                        if self.start_rule is None:
                            self.start_rule = lhs
                        # Find terminals and non-terminals
                        tmp_productions = []

                        if productions.strip().startswith("GE_RANGE:"):
                            # Special case: for something like GE_RANGE:nvars, substitute
                            # 0 | 1 | ... | 9 (assuming nvars=10)
                            varname = productions.strip().split(":")[1]
                            assert varname in kwargs
                            n = kwargs[varname]
                            tmp_productions = []
                            for i in range(n):
                                tmp_production = []
                                symbol = str(i)
                                tmp_production.append(symbol)
                                tmp_productions.append(tmp_production)
                                self.terminals.add(symbol)
                        else:
                            # Usual case: iterate through productions on RHS
                            for production in PRODUCTION_SEPARATOR.split(productions):
                                production = production.strip().replace(r"\|", "|")
                                tmp_production = []
                                for symbol in NON_TERMINAL_PATTERN.split(production):
                                    symbol = symbol.replace(r"\<", "<").replace(r"\>", ">")
                                    if len(symbol) == 0:
                                        continue
                                    elif NON_TERMINAL_PATTERN.match(symbol):
                                        tmp_production.append(symbol)
                                    else:
                                        self.terminals.add(symbol)
                                        tmp_production.append(symbol)

                                tmp_productions.append(tmp_production)
                        # Create a rule
                        if lhs not in self.rules:
                            self.rules[lhs] = tmp_productions
                        else:
                            raise ValueError("lhs should be unique", lhs)
                    else:
                        raise ValueError("Each rule must be on one line")

    def __str__(self) -> str:
        return f"{self.terminals} {self.non_terminals} {self.rules} {self.start_rule}"

def derive_string(grammar: Grammar, genome: Iterator[int]) -> Tuple[str, int]:
    """Recursively derive a string given a grammar, genome, and start
    symbol. Track the number of codons used. Don't create the
    derivation tree."""
    s = grammar.start_rule
    if s is None:
        raise ValueError("Grammar start rule is not set")
    used_codons = itertools.count()
    try:
        s = _derive_string(grammar, iter(genome), s, used_codons)
        return s, next(used_codons)
    except StopIteration:
        raise InvalidIndividualException
    
def _derive_string(grammar: Grammar, genome: Iterator[int], s: str, used_codons: Iterator[int]) -> str:
    if s in grammar.terminals:
        return s
    rule = grammar.rules[s]
    if len(rule) > 1:
        codon = next(genome)
        next(used_codons)
        idx = codon % len(rule)
        prod = rule[idx]
        # print "rule", rule, "codon", codon, "prod", prod
    else:
        prod = rule[0]
        # print "rule", rule, "no codon", "prod", prod
    # recurse 
    return "".join([_derive_string(grammar, genome, sym, used_codons)
                   for sym in prod])
    

