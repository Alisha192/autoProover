from typing import List, Optional, Tuple

class ProofStep:
    def __init__(self, index: int, expression: Expression, reason: str):
        self.index = index
        self.expression = expression
        self.reason = reason

    def __str__(self):
        return f"{self.index}. {self.expression.to_string()}  # {self.reason}"


class ProofEngine:
    def __init__(self):
        self.axioms = [
            lambda A, B: Implication(A, Implication(B, A)),  # Аксиома 1
            lambda A, B, C: Implication(Implication(A, Implication(B, C)), Implication(Implication(A, B), Implication(A, C))),  # Аксиома 2
            lambda A, B: Implication(Implication(Not(A), Not(B)), Implication(B, A))  # Аксиома 3
            # Можно добавить другие аксиомы
        ]
        self.proven_statements = []  # Доказанные утверждения с их индексами и причинами

    def is_axiom(self, expr: Expression) -> Optional[Tuple[int, dict]]:
        for i, axiom in enumerate(self.axioms, start=1):
            substitution = self.match(axiom, expr)
            if substitution is not None:
                return i, substitution
        return None

    def match(self, axiom_template, expr: Expression) -> Optional[dict]:
        # Сопоставляем шаблон аксиомы с выражением
        # Здесь нужен код для сопоставления структуры expr и axiom_template
        return {}  # Заглушка для функции сопоставления

    def apply_modus_ponens(self, known_expressions: List[ProofStep]) -> List[Tuple[Expression, str]]:
        new_expressions = []
        for step1 in known_expressions:
            for step2 in known_expressions:
                if isinstance(step2.expression, Implication) and step2.expression.left.equals(step1.expression):
                    reason = f"{step1.index}, {step2.index}"
                    new_expressions.append((step2.expression.right, reason))
        return new_expressions

    def prove(self, target: Expression, hypotheses: List[Expression]) -> Optional[List[ProofStep]]:
        proof = []
        known_expressions = [ProofStep(index=i+1, expression=hypothesis, reason="Гипотеза") for i, hypothesis in enumerate(hypotheses)]
        proof.extend(known_expressions)
        step_count = len(known_expressions)

        while not any(step.expression.equals(target) for step in known_expressions):
            new_expressions = []

            # Применяем аксиомы
            for axiom_index, axiom in enumerate(self.axioms, start=1):
                for expr in known_expressions:
                    substitution = self.match(axiom, expr.expression)
                    if substitution is not None:
                        step_count += 1
                        reason = f"Аксиома {axiom_index}, {', '.join(f'{k} -> {v.to_string()}' for k, v in substitution.items())}"
                        new_expressions.append(ProofStep(step_count, expr.expression, reason))

            # Применяем modus ponens
            for new_expr, reason in self.apply_modus_ponens(known_expressions):
                step_count += 1
                new_expressions.append(ProofStep(step_count, new_expr, f"Modus Ponens {reason}"))

            # Добавляем только новые выражения
            new_expressions = [expr for expr in new_expressions if not any(expr.expression.equals(e.expression) for e in known_expressions)]
            if not new_expressions:
                print("Целевое выражение недоказуемо с текущими гипотезами.")
                return None  # Доказательство не найдено
            
            proof.extend(new_expressions)
            known_expressions.extend(new_expressions)

            # Проверяем, достигнута ли целевая лемма
            if any(step.expression.equals(target) for step in new_expressions):
                return proof

        return proof

    def display_proof(self, proof: List[ProofStep]):
        for step in proof:
            print(step)
