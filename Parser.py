from typing import List
from Architect import *


class Parser:
    def __init__(self, expression: str, keywords: List):
        self.keywords = keywords
        self.tokens = self.tokenize(expression)
        self.pos = 0

    def tokenize(self, expression: str) -> List[str]:
        tokens = []
        i = 0
        while i < len(expression):
            if expression[i].isspace():
                i += 1
                continue
            if expression[i] in '()|*!>+=!':
                tokens.append(expression[i])
                i += 1
            elif expression[i].isalpha():  # Переменные
                start = i
                while i < len(expression) and expression[i].isalnum():
                    i += 1
                tokens.append(expression[start:i])
            else:
                raise ValueError(f"Недопустимый символ: {expression[i]}")
        return tokens

    def parse(self) -> Expression:
        result = self.parse_equivalence()
        if self.pos < len(self.tokens):
            raise ValueError("Введено некорректное выражение")
        return result

    def parse_variable(self) -> Expression:
        token = self.tokens[self.pos]
        self.pos += 1
        if token.isalnum() and token.lower() not in self.keywords and len(token) == 1:
            return ExpressionFactory.variable(token)
        else:
            raise ValueError("Недопустимое имя переменной")

    def parse_parenthesized(self) -> Expression:
        if self.tokens[self.pos] == '(':
            self.pos += 1
            expr = self.parse_equivalence()  # Начинаем с самого низкого приоритета
            if self.pos < len(self.tokens) and self.tokens[self.pos] == ')':
                self.pos += 1
                return expr
            else:
                raise ValueError("Пропущена закрывающая скобка")
        else:
            return self.parse_variable()

    def parse_negation(self) -> Expression:
        if self.tokens[self.pos] == '!':
            self.pos += 1
            return ExpressionFactory.negation(self.parse_negation())
        else:
            return self.parse_parenthesized()

    def parse_conjunction(self) -> Expression:
        left = self.parse_negation()
        while self.pos < len(self.tokens) and self.tokens[self.pos] == '*':
            self.pos += 1
            right = self.parse_negation()
            left = ExpressionFactory.conjunction(left, right)
        return left

    def parse_disjunction(self) -> Expression:
        left = self.parse_conjunction()
        while self.pos < len(self.tokens) and self.tokens[self.pos] == '|':
            self.pos += 1
            right = self.parse_conjunction()
            left = ExpressionFactory.disjunction(left, right)
        return left

    def parse_xor(self) -> Expression:
        left = self.parse_disjunction()
        while self.pos < len(self.tokens) and self.tokens[self.pos] == '+':
            self.pos += 1
            right = self.parse_disjunction()
            left = ExpressionFactory.exclusive_or(left, right)
        return left

    def parse_implication(self) -> Expression:
        left = self.parse_xor()
        while self.pos < len(self.tokens) and self.tokens[self.pos] == '>':
            self.pos += 1
            right = self.parse_xor()
            left = ExpressionFactory.implication(left, right)
        return left

    def parse_equivalence(self) -> Expression:
        left = self.parse_implication()
        while self.pos < len(self.tokens) and self.tokens[self.pos] == '=':
            self.pos += 1
            right = self.parse_implication()
            left = ExpressionFactory.equivalence(left, right)
        return left


if __name__ == "__main__":
    # Пример использования
    # parser = Parser("(A > C) > ((B > C) > ((A | B) > C))")
    parser = Parser("A = C > (B = C)")
    expression_tree = parser.parse()
    print(expression_tree.to_string())  # Для проверки парсера
