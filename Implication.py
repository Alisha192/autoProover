from expression import Expression
from typing import Optional

class Implication(Expression):
    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right

    def to_string(self) -> str:
        return f"({self.left.to_string()} -> {self.right.to_string()})"

    def equals(self, other: 'Expression') -> bool:
        if not isinstance(other, Implication):
            return False
        return self.left.equals(other.left) and self.right.equals(other.right)
