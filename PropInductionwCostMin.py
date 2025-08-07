"""
an extension of the Horn‐clause abducer that lets you assign a numeric cost to each abducible and then returns only those explanations whose total cost is minimal.
"""
from typing import List, Set, Tuple, Dict
from itertools import product

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
