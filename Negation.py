from expression import Expression

class Negation(Expression):
    def __init__(self, expr: Expression):
        self.expr = expr

    def to_string(self) -> str:
        return f"¬{self.expr.to_string()}"

    def equals(self, other: 'Expression') -> bool:
        if not isinstance(other, Negation):
            return False
        return self.expr.equals(other.expr)
