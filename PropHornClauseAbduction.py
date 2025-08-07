"""
A Python framework for propositional‐Horn‐clause abduction. 

You supply:
a knowledge base of definite clauses


a set of abducible atoms (literals you’re allowed to assume)


an observation you wish to explain


The abduce function will return all (minimal) sets of abducibles that, together with your KB, can entail the observation.
from typing import List, Set, Tuple
from itertools import product
"""
# ————— Data structures —————

class HornClause:
    """A definite clause of the form head :- body1, body2, ..."""
    def __init__(self, head: str, body: List[str]):
        self.head = head
        self.body = body

    def __repr__(self):
        if self.body:
            return f"{self.head} :- " + ", ".join(self.body)
        else:
            return f"{self.head}."

# ————— Abductive reasoning —————

def abduce(
    goal: str,
    kb: List[HornClause],
    abducibles: Set[str],
    seen: Set[str]=None
) -> List[Set[str]]:
    """
    Return a list of sets of abducibles that explain `goal`.
    Each explanation is a set of atoms ⊆ abducibles.
    """
    if seen is None:
        seen = set()
    # avoid infinite loops on recursive rules
    if goal in seen:
        return []
    seen = seen | {goal}

    # 1) If goal itself is abducible, one explanation is to assume it directly:
    explanations: List[Set[str]] = []
    if goal in abducibles:
        explanations.append({goal})

    # 2) Otherwise, look for clauses that can derive goal
    for clause in kb:
        if clause.head == goal:
            # for each body literal, get its explanations
            sub_expls = [ abduce(b, kb, abducibles, seen) for b in clause.body ]
            # if any body literal has no explanation, this clause won't fire
            if any(len(exs) == 0 for exs in sub_expls):
                continue
            # take one choice of explanation per body literal (cartesian product)
            for combo in product(*sub_expls):
                # combo is a tuple of sets; union them
                merged = set().union(*combo)
                explanations.append(merged)

    # 3) remove non‐minimal explanations (prune supersets)
    minimal: List[Set[str]] = []
    for e in explanations:
        if not any((e2 < e) for e2 in explanations):
            minimal.append(e)
    return minimal

# ————— Example usage —————
if __name__ == "__main__":
    # KB:
    #   r :- p, q.
    #   r :- s.
    #   p :- t.
    #   q.
    kb = [
        HornClause("r", ["p", "q"]),
        HornClause("r", ["s"]),
        HornClause("p", ["t"]),
        HornClause("q", []),
    ]

    # We allow {s, t} to be hypothesized
    abducibles = {"s", "t"}

    # Observation: 'r'
    exps = abduce("r", kb, abducibles)
    print("Explanations for r:")
    for e in exps:
        print("  ", e)
    # Expected output:
    #   {'s'}
    #   {'t'}     (since p :- t, q is a fact)
"""
How it works
Direct abduction
 If the goal is in your set of abducibles, you can always “explain” it by assuming it.


Backward‐chaining
 For each clause with head = goal, recursively abduct each literal in the body.


If any body literal has no explanation, that clause can’t derive the goal.


Otherwise, take the Cartesian product of explanations for each sub‐goal and union them into candidate explanations.


Minimality pruning
 Once all candidates are collected, we discard any explanation that strictly contains another: only minimal sets of assumptions remain.


This simple abductive solver works for propositional Horn theories. You can extend it by adding weights or preferences over abducibles, or by integrating a cost‐minimization step to pick the “best” explanation.
========================================================================

Here’s an extension of the Horn‐clause abducer that lets you assign a numeric cost to each abducible and then returns only those explanations whose total cost is minimal.

from typing import List, Set, Tuple, Dict
from itertools import product
"""
# ————— Data structures —————

class HornClause:
    """A definite clause of the form head :- body1, body2, ..."""
    def __init__(self, head: str, body: List[str]):
        self.head = head
        self.body = body

    def __repr__(self):
        if self.body:
            return f"{self.head} :- " + ", ".join(self.body)
        else:
            return f"{self.head}."

# ————— Abductive reasoning with minimality by inclusion —————

def abduce(
    goal: str,
    kb: List[HornClause],
    abducibles: Set[str],
    seen: Set[str]=None
) -> List[Set[str]]:
    """
    Return all (inclusion-)minimal sets of abducibles that explain `goal`.
    """
    if seen is None:
        seen = set()
    if goal in seen:
        return []
    seen = seen | {goal}

    explanations: List[Set[str]] = []
    # 1) Direct assumption
    if goal in abducibles:
        explanations.append({goal})

    # 2) Derivation via clauses
    for clause in kb:
        if clause.head == goal:
            # recursively get explanations for each body literal
            sub_expls = [abduce(b, kb, abducibles, seen) for b in clause.body]
            # if any body literal fails to explain, skip this clause
            if any(len(exs) == 0 for exs in sub_expls):
                continue
            # combine one explanation per literal
            for combo in product(*sub_expls):
                merged = set().union(*combo)
                explanations.append(merged)

    # 3) Prune non‐minimal (by set‐inclusion)
    minimal: List[Set[str]] = []
    for e in explanations:
        if not any((other < e) for other in explanations):
            minimal.append(e)
    return minimal

# ————— Cost‐minimizing wrapper —————

def abduce_min_cost(
    goal: str,
    kb: List[HornClause],
    abducibles: Set[str],
    cost: Dict[str, float]
) -> List[Set[str]]:
    """
    Return those explanations whose total cost is the lowest.
    `cost` maps each abducible atom → nonnegative numeric cost.
    """
    all_expls = abduce(goal, kb, abducibles)
    # annotate with total cost
    scored = []
    for expl in all_expls:
        total = sum(cost.get(a, float('inf')) for a in expl)
        scored.append((total, expl))
    if not scored:
        return []
    # find minimal total cost
    min_cost = min(score for score, _ in scored)
    # return all explanations achieving that cost
    return [expl for score, expl in scored if score == min_cost]

# ————— Example usage —————
if __name__ == "__main__":
    # Knowledge base:
    #   r :- p, q.
    #   r :- s.
    #   p :- t.
    #   q.
    kb = [
        HornClause("r", ["p", "q"]),
        HornClause("r", ["s"]),
        HornClause("p", ["t"]),
        HornClause("q", []),
    ]

    abducibles = {"s", "t"}
    # assign costs: assuming s is expensive to hypothesize
    cost_map = {"s": 5.0, "t": 1.0}

    best_explanations = abduce_min_cost("r", kb, abducibles, cost_map)
    print("Cheapest explanations for r:")
    for e in best_explanations:
        total = sum(cost_map[a] for a in e)
        print(f"  {e}  (cost = {total})")
    # Output:
    #   {'t'}  (cost = 1.0)
"""
What changed?
Cost map
 You provide cost: Dict[str, float] mapping each abducible to its numeric “penalty.”


Wrapper function


abduce_min_cost first calls the original abduce to get all inclusion-minimal explanations.


It then computes each explanation’s total cost by summing its abducibles’ costs.


Finally, it filters out only those explanations whose total cost equals the global minimum.


Result
 You still get logically sound (minimal) explanations, but now you also ensure they’re the least “expensive” under whatever cost model makes sense for your domain.
"""
