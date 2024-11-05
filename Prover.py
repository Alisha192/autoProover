from typing import List, Optional
from Architect import *


class ProofStep:
    def __init__(self, index, expr: Expression, comment: str):
        self.expr = expr
        self.comment = comment
        self.index = index

    def __str__(self):
        return f"{self.index} - {self.expr.to_string()} - {self.comment}"


class Prover:
    def __init__(self, axioms: List[Expression], target: Expression):
        self.axioms = axioms
        self.target = target
        self.step_index = 0
        self.proof_steps = []  # Список шагов доказательства
        self.hypotheses = []  # Список гипотез для текущего доказательства

    def reverse_deduction(self):
        new_target = self.target
        while not isinstance(new_target, Variable):
            self.hypotheses.append(new_target.left)
            new_target = new_target.right
        self.target = new_target

    def find_modus_ponens(self) -> List[Expression]:
        #не забыть увеличивать step_index
        pass

    def aply_modus_ponens(self, axiom: Expression, formula: Expression) -> Expression:
        pass

    def unify(self, formula: Expression) -> Expression:
        pass
    def prove(self):
        if(self.target in self.axioms):
            print(f"{self.target} это аксиома") #предусмотреть что это может быть акиома с заменой
            return
        steps = []
        self.reverse_deduction()
        print("новые посылки в результате приминения теоремы дедукции")
        for hyp in self.hypotheses:
            print(hyp.to_string())
        print(f"цель, после применения обратной теоремы дедукции: {self.target.to_string()}")
        while True:
            if self.target in self.hypotheses:
                print("Доказано")
                break
            self.step_index += 1
            modus = self.find_modus_ponens()
            if modus is None:
                print("Не удалось доказать")
                break
            step = ProofStep(self.step_index, modus[0], "аксиома номер с заменой") #этот момент должен быть в самой функции find_modus_ponens
            new_exp = self.aply_modus_ponens(modus[0], modus[1])
            step = ProofStep(self.step_index, new_exp, f"MP строка строка")

