from language import *

class Unification:
    @staticmethod
    def unify(term_a, term_b):
        """
        Выполняет унификацию двух термов.
        """
        if isinstance(term_a, UnificationTerm):
            if term_b.occurs(term_a) or term_b.time > term_a.time:
                return None
            return {term_a: term_b}
        if isinstance(term_b, UnificationTerm):
            if term_a.occurs(term_b) or term_a.time > term_b.time:
                return None
            return {term_b: term_a}
        if isinstance(term_a, Variable) and isinstance(term_b, Variable):
            if term_a == term_b:
                return {}
            return None
        if (isinstance(term_a, Function) and isinstance(term_b, Function)) or \
           (isinstance(term_a, Predicate) and isinstance(term_b, Predicate)):
            if term_a.name != term_b.name or len(term_a.terms) != len(term_b.terms):
                return None
            substitution = {}
            for a, b in zip(term_a.terms, term_b.terms):
                for k, v in substitution.items():
                    a = a.replace(k, v)
                    b = b.replace(k, v)
                sub = Unification.unify(a, b)
                if sub is None:
                    return None
                substitution.update(sub)
            return substitution
        return None

    @staticmethod
    def unify_list(pairs):
        substitution = {}
        for term_a, term_b in pairs:
            a, b = term_a, term_b
            for k, v in substitution.items():
                a = a.replace(k, v)
                b = b.replace(k, v)
            sub = Unification.unify(a, b)
            if sub is None:
                return None
            substitution.update(sub)
        return substitution

class ProofSearch:
    @staticmethod
    def applyModusPonens(old_sequent, left_formula):
        print(f"Используется modus ponens {old_sequent} и {left_formula}")
        new_sequent_a = Sequent(old_sequent.left.copy(), old_sequent.right.copy(), old_sequent.siblings, old_sequent.depth + 1)
        new_sequent_b = Sequent(old_sequent.left.copy(), old_sequent.right.copy(), old_sequent.siblings, old_sequent.depth + 1)
        new_sequent_a.left.pop(left_formula)
        new_sequent_b.left.pop(left_formula)
        new_sequent_a.right[left_formula.formula_a] = old_sequent.left[left_formula] + 1
        new_sequent_b.left[left_formula.formula_b] = old_sequent.left[left_formula] + 1
        if new_sequent_a.siblings is not None:
            new_sequent_a.siblings.add(new_sequent_a)
        if new_sequent_b.siblings is not None:
            new_sequent_b.siblings.add(new_sequent_b)
        return [new_sequent_a, new_sequent_b]

    @staticmethod
    def applyNotLeft(old_sequent, left_formula):
        print(f"используется правило для {old_sequent} и {left_formula}: Когда формула ¬A находится в левой части секвента.")
        new_sequent = Sequent(old_sequent.left.copy(), old_sequent.right.copy(), old_sequent.siblings, old_sequent.depth + 1)
        new_sequent.left.pop(left_formula)
        new_sequent.right[left_formula.formula] = old_sequent.left[left_formula] + 1
        return new_sequent

    @staticmethod
    def applyNotRight(old_sequent, right_formula):
        print(f"используется правило для {old_sequent} и {right_formula}: Когда формула ¬A находится в правой части секвента.")
        new_sequent = Sequent(old_sequent.left.copy(), old_sequent.right.copy(), old_sequent.siblings, old_sequent.depth + 1)
        new_sequent.right.pop(right_formula)
        new_sequent.left[right_formula.formula] = old_sequent.right[right_formula] + 1
        return new_sequent

    @staticmethod
    def applyImpliesRight(old_sequent, right_formula):
        print(f"используется правило для {old_sequent} и {right_formula}: Когда формула A → B находится в правой части секвента.")
        new_sequent = Sequent(old_sequent.left.copy(), old_sequent.right.copy(), old_sequent.siblings, old_sequent.depth + 1)
        new_sequent.right.pop(right_formula)
        new_sequent.left[right_formula.formula_a] = old_sequent.right[right_formula] + 1
        new_sequent.right[right_formula.formula_b] = old_sequent.right[right_formula] + 1
        return new_sequent

    @staticmethod
    def proveSequent(sequent):
        for formula in sequent.left:
            formula.setInstantiationTime(0)
        for formula in sequent.right:
            formula.setInstantiationTime(0)

        frontier, proven = [sequent], {sequent}
        while True:
            old_sequent = None
            while frontier and (old_sequent is None or old_sequent in proven):
                old_sequent = frontier.pop(0)
            if old_sequent is None:
                break
            print(f'Глубина: {old_sequent.depth}. Секвент: {old_sequent}')
            if len(set(old_sequent.left.keys()) & set(old_sequent.right.keys())) > 0:
                proven.add(old_sequent)
                continue
            if old_sequent.siblings:
                sibling_pair_lists = [sequent.getUnifiablePairs() for sequent in old_sequent.siblings]
                if all(sibling_pair_lists):
                    substitution, index = None, [0] * len(sibling_pair_lists)
                    while True:
                        substitution = Unification.unify_list([sibling_pair_lists[i][index[i]] for i in range(len(sibling_pair_lists))])
                        if substitution:
                            break
                        pos = len(sibling_pair_lists) - 1
                        while pos >= 0:
                            index[pos] += 1
                            if index[pos] < len(sibling_pair_lists[pos]):
                                break
                            index[pos] = 0
                            pos -= 1
                        if pos < 0:
                            break
                    if substitution:
                        for k, v in substitution.items():
                            print(f'  Замена: {k} = {v}')
                        proven |= old_sequent.siblings
                        frontier = [sequent for sequent in frontier if sequent not in old_sequent.siblings]
                        continue
                else:
                    old_sequent.siblings.remove(old_sequent)
            left_formula, right_formula, left_depth, right_depth = None, None, None, None
            for formula, depth in old_sequent.left.items():
                if left_depth is None or left_depth > depth:
                    if not isinstance(formula, Predicate):
                        left_formula, left_depth = formula, depth
            for formula, depth in old_sequent.right.items():
                if right_depth is None or right_depth > depth:
                    if not isinstance(formula, Predicate):
                        right_formula, right_depth = formula, depth
            if left_formula and not right_formula:
                if isinstance(left_formula, Not):
                    frontier.append(ProofSearch.applyNotLeft(old_sequent, left_formula))
                    break
                if isinstance(left_formula, Implies):
                    frontier.extend(ProofSearch.applyModusPonens(old_sequent, left_formula))
                    break
            elif right_formula and not left_formula:
                if isinstance(right_formula, Not):
                    frontier.append(ProofSearch.applyNotRight(old_sequent, right_formula))
                    break
                if isinstance(right_formula, Implies):
                    frontier.append(ProofSearch.applyImpliesRight(old_sequent, right_formula))
                    break
            else:
                return False
        return True

    @staticmethod
    def proveFormula(axioms, formula):
        return ProofSearch.proveSequent(Sequent({axiom: 0 for axiom in axioms}, {formula: 0}, None, 0))
