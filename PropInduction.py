"""
 a simple Python implementation of a Horn-clause rule learner using the FOIL strategy—a classic example of logical inductive reasoning, 
 where you generalize from positive and negative ground facts into logical rules.
 """
import math
from typing import List, Tuple, Set

# ————— Type aliases —————
# A ground fact or example: predicate applied to a constant
Example = Tuple[str, str]        # e.g. ("Fly", "tweety")
# A candidate literal in the body of a rule: predicate applied to the variable "X"
Literal = Tuple[str, str]        # e.g. ("Bird", "X")

# ————— FOIL information-gain function —————
def foil_gain(p: int, n: int, p1: int, n1: int) -> float:
    """
    Compute FOIL’s information gain for adding a literal:
      p  = # positives covered by current rule
      n  = # negatives covered by current rule
      p1 = # positives covered after adding this literal
      n1 = # negatives covered after adding this literal
    FOIL gain = p1 * ( log2(p1/(p1+n1)) – log2(p/(p+n)) )
    """
    if p == 0 or (p1 + n1) == 0:
        return 0.0
    return p1 * (math.log2(p1 / (p1 + n1)) - math.log2(p / (p + n)))

# ————— The learning loop —————
def learn_rules(
    pos: List[Example],
    neg: List[Example],
    background: Set[Example],
    predicates: Set[str],
) -> List[Tuple[str, str, List[Literal]]]:
    """
    Learn Horn-clause rules for a single target predicate using FOIL.
    Returns a list of rules: (head_predicate, variable, [body_literals]).
    """
    rules: List[Tuple[str, str, List[Literal]]] = []
    pos_examples = pos[:]     # remaining positives to cover
    neg_examples = neg[:]     # all negatives

    while pos_examples:
        # Assume all examples share the same head predicate and variable X
        head_pred = pos_examples[0][0]
        var = "X"
        body: List[Literal] = []

        # Initialize the set of positives/negatives covered by the (empty) rule body
        pos_cover = [e for e in pos_examples if e[0] == head_pred]
        neg_cover = [e for e in neg_examples if e[0] == head_pred]

        # Repeatedly add the literal with highest FOIL gain until no negatives are covered
        while neg_cover:
            best_gain = 0.0
            best_literal = None
            best_pos_cover = []
            best_neg_cover = []

            p, n = len(pos_cover), len(neg_cover)
            # Generate candidate literals: each predicate not yet in the body
            for pred in predicates - {lit[0] for lit in body}:
                # See which examples would still be covered if we added pred(X)
                new_pos = [e for e in pos_cover if (pred, e[1]) in background]
                new_neg = [e for e in neg_cover if (pred, e[1]) in background]
                gain = foil_gain(p, n, len(new_pos), len(new_neg))
                if gain > best_gain:
                    best_gain = gain
                    best_literal = (pred, var)
                    best_pos_cover = new_pos
                    best_neg_cover = new_neg

            # Stop if no literal improves things
            if best_literal is None:
                break

            # Otherwise, add it and narrow down covered sets
            body.append(best_literal)
            pos_cover = best_pos_cover
            neg_cover = best_neg_cover

        # Record the learned rule
        rules.append((head_pred, var, body))

        # Remove all positives now covered by this rule
        covered = [
            e for e in pos_examples
            if e[0] == head_pred and all((pred, e[1]) in background for pred, _ in body)
        ]
        pos_examples = [e for e in pos_examples if e not in covered]

    return rules

# ————— Example usage —————
if __name__ == "__main__":
    # Background facts about which animals belong to which class
    background = {
        ("Bird", "tweety"), ("Bird", "polly"), ("Bird", "tweety2"),
        ("Mammal", "leo"), ("Mammal", "max")
    }
    # Positive examples: which animals can fly
    pos_examples = [("Fly", "tweety"), ("Fly", "polly"), ("Fly", "tweety2")]
    # Negative examples: which animals cannot fly
    neg_examples = [("Fly", "leo"), ("Fly", "max")]

    predicates = {"Bird", "Mammal"}

    rules = learn_rules(pos_examples, neg_examples, background, predicates)
    for head, var, body in rules:
        if body:
            body_str = " ∧ ".join(f"{pred}({var})" for pred, _ in body)
        else:
            body_str = "True"
        print(f"{head}({var}) :- {body_str}")

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
"""
