from Utils import *
from typing import List


class Prover:
    def __init__(self, axioms: List[Expression], target: Expression):
        self.axioms = [simplify(axiom) for axiom in axioms]  # Список для хранения аксиом
        self.conditions = self.axioms.copy()  # Условия
        self.target = simplify(target)  # Цель доказательства
        self.to_prove = self.target.copy()  # Цель доказательства для обработки

    def preprocessing(self):
        # Применяем теорему о дедукции
        new_conditions, self.to_prove = deduction(self.to_prove)
        # Добавляем новые условия
        for new_condition in new_conditions:
            if new_condition in self.conditions:
                self.conditions.append(new_condition)
        # Применяем modus ponens
        self.conditions = modus_ponens(self.conditions)
        # TODO: unify()

    def unify(self):
        pass

    def prove(self):
        self.preprocessing()
        if self.to_prove in self.conditions:
            print(f"Доказано: {self.target}")
            return True

