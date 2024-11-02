from abc import ABC, abstractmethod
from typing import Optional


class Expression(ABC):
    @abstractmethod
    def to_string(self) -> str:
        pass

    @abstractmethod
    def equals(self, other: 'Expression') -> bool:
        pass

    @abstractmethod
    def to_implication_form(self) -> 'Expression':
        pass


class And(Expression):
    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right

    def to_string(self) -> str:
        return f"({self.left.to_string()} ∧ {self.right.to_string()})"

    def equals(self, other: Expression) -> bool:
        return isinstance(other, And) and self.left.equals(other.left) and self.right.equals(other.right)

    def to_implication_form(self) -> Expression:
        return And(self.left.to_implication_form(), self.right.to_implication_form())


class Implication(Expression):
    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right

    def to_string(self) -> str:
        return f"({self.left.to_string()} → {self.right.to_string()})"

    def equals(self, other: Expression) -> bool:
        return isinstance(other, Implication) and self.left.equals(other.left) and self.right.equals(other.right)

    def to_implication_form(self) -> Expression:
        return self  # Already an implication


class Negation(Expression):
    def __init__(self, expr: Expression):
        self.expr = expr

    def to_string(self) -> str:
        return f"¬({self.expr.to_string()})"

    def equals(self, other: Expression) -> bool:
        return isinstance(other, Negation) and self.expr.equals(other.expr)

    def to_implication_form(self) -> Expression:
        return Negation(self.expr.to_implication_form())


class Or(Expression):
    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right

    def to_string(self) -> str:
        return f"({self.left.to_string()} ∨ {self.right.to_string()})"

    def equals(self, other: Expression) -> bool:
        return isinstance(other, Or) and self.left.equals(other.left) and self.right.equals(other.right)

    def to_implication_form(self) -> Expression:
        return Or(self.left.to_implication_form(), self.right.to_implication_form())


class Xor(Expression):
    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right

    def to_string(self) -> str:
        return f"({self.left.to_string()} ⊕ {self.right.to_string()})"

    def equals(self, other: Expression) -> bool:
        return isinstance(other, Xor) and self.left.equals(other.left) and self.right.equals(other.right)

    def to_implication_form(self) -> Expression:
        return Xor(self.left.to_implication_form(), self.right.to_implication_form())


class Variable(Expression):
    def __init__(self, name: str):
        self.name = name

    def to_string(self) -> str:
        return self.name

    def equals(self, other: Expression) -> bool:
        return isinstance(other, Variable) and self.name == other.name

    def to_implication_form(self) -> Expression:
        return self  # Already a variable


class ExpressionCast:
    @staticmethod
    def as_negation(expr: Expression) -> Optional[Negation]:
        return expr if isinstance(expr, Negation) else None

    @staticmethod
    def as_implication(expr: Expression) -> Optional[Implication]:
        return expr if isinstance(expr, Implication) else None

    @staticmethod
    def as_variable(expr: Expression) -> Optional[Variable]:
        return expr if isinstance(expr, Variable) else None

    @staticmethod
    def as_conjunction(expr: Expression) -> Optional[And]:
        return expr if isinstance(expr, And) else None

    @staticmethod
    def as_disjunction(expr: Expression) -> Optional[Or]:
        return expr if isinstance(expr, Or) else None

    @staticmethod
    def as_xor(expr: Expression) -> Optional[Xor]:
        return expr if isinstance(expr, Xor) else None


class ExpressionFactory:
    @staticmethod
    def variable(name: str) -> Expression:
        return Variable(name)

    @staticmethod
    def implication(left: Expression, right: Expression) -> Expression:
        return Implication(left, right)

    @staticmethod
    def negation(expr: Expression) -> Expression:
        return Negation(expr)

    @staticmethod
    def conjunction(left: Expression, right: Expression) -> Expression:
        return And(left, right)

    @staticmethod
    def disjunction(left: Expression, right: Expression) -> Expression:
        return Or(left, right)

    @staticmethod
    def exclusive_or(left: Expression, right: Expression) -> Expression:
        return Xor(left, right)
