"""
A simple Python implementation of a propositional‐logic theorem prover using the resolution rule of deductive reasoning. 
You represent your knowledge base (KB) as a set of clauses in conjunctive normal form (CNF), 
then ask whether a query follows from the KB by attempting to derive a contradiction when adding the negation of the query.

"""
from typing import Set, FrozenSet, List

Literal = str
Clause  = FrozenSet[Literal]

def negate(literal: Literal) -> Literal:
    """Return the negation of a literal (adds/removes ‘~’)."""
    return literal[1:] if literal.startswith('~') else '~' + literal

def resolve(ci: Clause, cj: Clause) -> List[Clause]:
    """
    Attempt to resolve two clauses.
    For each literal l in ci, if ¬l ∈ cj, produce the resolvent:
      (ci ∪ cj) \ {l, ¬l}
    """
    resolvents = []
    for l in ci:
        nl = negate(l)
        if nl in cj:
            # Remove l and ¬l, then union the rest
            new_clause = (ci.union(cj)) - {l, nl}
            resolvents.append(frozenset(new_clause))
    return resolvents

def resolution_entails(kb: Set[Clause], query: Literal) -> bool:
    """
    Return True if KB ⊨ query, via resolution proof.
    """
    # 1. Add ¬query to KB
    negated_query = frozenset({ negate(query) })
    clauses = set(kb)
    clauses.add(negated_query)

    new = set()
    while True:
        # 2. For each pair of clauses, resolve
        pairs = [(ci, cj) for ci in clauses for cj in clauses if ci != cj]
        for (ci, cj) in pairs:
            for resolvent in resolve(ci, cj):
                # If we’ve derived the empty clause, success!
                if len(resolvent) == 0:
                    return True
                new.add(resolvent)

        # 3. If no new clauses, failure
        if new.issubset(clauses):
            return False

        # 4. Otherwise add new clauses and repeat
        clauses |= new

# Example usage
if __name__ == "__main__":
    # KB: (A ∨ B), (¬A ∨ C), (¬B ∨ C), (¬C ∨ D)
    kb = {
        frozenset({'A', 'B'}),
        frozenset({'~A', 'C'}),
        frozenset({'~B', 'C'}),
        frozenset({'~C', 'D'})
    }

    print(resolution_entails(kb, 'D'))  # Should print True, since D follows
    print(resolution_entails(kb, 'A'))  # Should print False, A is not entailed

"""
How it works
Clause representation
 A clause is a disjunction of literals (e.g. A ∨ ¬B ∨ C), encoded here as a Python frozenset of strings: frozenset({'A','~B','C'}).


Negation helper
 negate(literal) simply adds or removes a leading ~.


Resolving two clauses
 To resolve two clauses CiC_iCi​ and CjC_jCj​, we look for a literal ℓℓℓ in CiC_iCi​ such that ¬ℓ\neg ℓ¬ℓ is in CjC_jCj​. The resolvent is the union of both clauses minus that pair of complementary literals:
 resolvent=(Ci∪Cj)∖{ℓ,¬ℓ}. \mathrm{resolvent} = (C_i ∪ C_j) \setminus \{ℓ, ¬ℓ\}.resolvent=(Ci​∪Cj​)∖{ℓ,¬ℓ}.
Resolution loop


We add the negation of our query to the KB and then repeatedly resolve every pair of clauses.


If at any point we derive the empty clause (i.e. a contradiction), the original KB logically entails the query.


If no new clauses can be generated without producing the empty clause, we conclude the query does not follow.


This algorithm implements a form of refutation‐complete deductive reasoning: if the query truly follows from your KB, resolution will find a proof; otherwise it will terminate without deriving a contradiction.
"""
