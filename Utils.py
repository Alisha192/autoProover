from Architect import *


def deduction(target: Expression):
    """Применение теоремы о дедукции"""
    if target is None:
        return None, None
    new_conditions = []
    while isinstance(target, Implication):
        new_conditions.append(simplify(target.left))
        target = simplify(target.right)
    return new_conditions, target


def modus_ponens(conditions):
    """Применение правила modus ponens"""
    if conditions is None:
        return None
    for condition in conditions:
        if isinstance(condition, Implication) and condition.left in conditions:
            conditions.append(condition.right)
            conditions = modus_ponens(conditions)
    return [simplify(condition) for condition in conditions]


def simplify(expression: Expression):
    """Упрощение логических высказываний"""
    if expression is None:
        return None
    if isinstance(expression, Variable):
        return expression
    # Убираем двойные отрицания
    if isinstance(expression, Negation):
        if isinstance(expression.expr, Negation):
            return expression.expr.expr
    if isinstance(expression, (Equivalence, Xor, Or, Implication, And)):
        current_class = type(expression)
        return current_class(simplify(expression.left), simplify(expression.right))
    return None
