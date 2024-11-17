from mimetypes import knownfiles
from msilib.schema import File
from Architect import *
from queue import Queue
from time import time as current_time


class Prover:
    def __init__(self, axioms: [Expression], target: Expression):
        self.known_axioms = []
        self.conclusions = {}
        self.axioms = axioms
        self.produced = []
        self.time_limit = 0
        self.targets = [target]
        self.ss = None
        self.dump = 'prove.txt'
        self.dep = []
        self.depends = []
        self.axioms.reverse = 10000
        self.dep.reverse = 10000
        self.depends.reverse = 10000
        self.known_axioms.reverse = 10000
        self.conclusions.reverse = 10000

        axiom1 = Implication(Variable("A"), Implication(Variable("B"), Variable("A")))
        axiom2 = Implication(Implication(Variable("A"), Implication(Variable("B"), Variable("C"))), Implication(Implication(Variable("A"), Variable("B")), Implication(Variable("A"), Variable("C"))))
        axiom3 = Implication(Implication(Negation(Variable("A")), Negation(Variable("B"))), Implication(Implication(Negation(Variable("A")), Variable("B")), Variable("A")))
        ax = [axiom1, axiom2, axiom3]
        ax.append(modus_ponens(ax[0], ax[0]))  #TODO modus_ponens
        ax.append(modus_ponens(ax[1], ax[0]))
        ax.append(modus_ponens(ax[3], ax[1]))
        ax.append(modus_ponens(ax[4], ax[1]))
        ax.append(modus_ponens(ax[2], ax[5]))
        ax.append(modus_ponens(ax[6], ax[6]))
        ax.append(modus_ponens(ax[7], ax[8]))
        ax.append(modus_ponens(ax[3], ax[9]))
        self.add_conclusion(axiom1, [])
        self.add_conclusion(axiom2, [])
        self.add_conclusion(axiom3, [])
        self.add_conclusion(axiom3, [ax[0], ax[0]])
        self.add_conclusion(ax[3], [ax[0], ax[0]])
        self.add_conclusion(ax[4], [ax[1], ax[0]])
        self.add_conclusion(ax[5], [ax[3], ax[1]])
        self.add_conclusion(ax[6], [ax[4], ax[1]])
        self.add_conclusion(ax[7], [ax[2], ax[5]])
        self.add_conclusion(ax[8], [ax[6], ax[6]])
        self.add_conclusion(ax[9], [ax[7], ax[8]])
        self.add_conclusion(ax[10], [ax[3], ax[9]])

        self.axioms.append(ax[-1])

    def deduction(self, expression: Expression):
        if expression is None:
            return False
        left = expression.left
        right = expression.right
        self.axioms.append(left)
        self.targets.append(right)
        return True

    def is_target_proved_by(self, expression:Expression):
        if expression is None:
            return False
        for target in self.targets:
            if target == expression:
                return True
        return False

    def add_expression(self, expression: Expression):
        expression.normalize()  #TODO normalize
        if self.known_axioms.__contains__(expression):
            return False
        try:
            with open(self.dump, 'a', encoding='utf-8') as file:
                file.write(f"{len(self.axioms)}. {expression}\n")
        except Exception as e:
            print(f"Ошибка при записи в файл {self.dump}: {e}")
            return False

    def add_produced(self, expression: Expression):
        if expression is None:
            return False
        if self.known_axioms.__contains__(expression):
            return False
        self.produced.append(expression)

    def add_conclusion(self, source: Expression, expressions: [Expression]):
        source_key = source.to_string()
        if source_key in self.conclusions:
            self.conclusions[source_key].clear()
        self.conclusions[source_key] = [exp.to_string() for exp in expressions]

    def produce(self):
        if not self.produced:
            return

        iteration_size = len(self.produced)
        print(f"iter: {iteration_size}")

        for _ in range(iteration_size):

            expression = self.produced.pop(0)  # Получаем и удаляем первый элемент

            # Ранние проверки
            if self.is_target_proved_by(expression):
                self.add_expression(expression)
                break

            for axiom in self.axioms:
                # modus_ponens: axiom -> expression
                expr = modus_ponens(axiom, expression)
                if self.is_target_proved_by(expr):
                    self.add_conclusion(expr, [axiom, expression])
                    self.add_expression(expr)
                    return

                if self.add_produced(expr):
                    self.add_conclusion(expr, [axiom, expression])

                # modus_ponens: expression -> axiom (обратный порядок)
                expr = modus_ponens(expression, axiom)
                if self.is_target_proved_by(expr):
                    self.add_conclusion(expr, [expression, axiom])
                    self.add_expression(expr)
                    return

                if self.add_produced(expr):
                    self.add_conclusion(expr, [expression, axiom])

            self.add_expression(expression)

            # Обработка последнего элемента в axioms
            expr = modus_ponens(self.axioms[-1], self.axioms[-1])
            if self.add_produced(expr):
                self.add_conclusion(expr, [self.axioms[-1], self.axioms[-1]])

        print(f"newly produced: {len(self.produced)}")

    def prove(self):
        self.ss.clear()

        # Simplify target if possible
        while self.deduction(self.targets[-1]):
            prev = self.targets[-2]
            curr = self.targets[-1]
            axiom = self.axioms[-1]

            self.ss.append(f"deduction theorem: Γ ⊢ {prev} <=> Γ U {{{axiom}}} ⊢ {curr}\n")

        # Write all axioms to the produced array
        for axiom in self.axioms:
            axiom.normalize()
            self.produced.append(axiom)
        self.axioms.clear()

        # Calculate stopping criterion
        current_time_ms = int(current_time() * 1000)
        if current_time_ms > (2 ** 64 - 1) - self.time_limit:
            self.time_limit = 2 ** 64 - 1
        else:
            self.time_limit += current_time_ms

        # Set a limit for the number of operations

        # Start producing expressions
        while int(current_time() * 1000) < self.time_limit:
            self.produce()

            if self.is_target_proved_by(self.axioms[-1]):
                break

        # Check if any target is proved
        if not any(self.is_target_proved_by(expr) for expr in self.axioms):
            self.ss.append("No proof was found in the time allotted\n")
            return

        # Find which target was proved
        proof = None
        for axiom in self.axioms:
            if proof:
                break
            for target in self.targets:
                if target == axiom:
                    proof = axiom
                    break

        # Build proof chain
        q = Queue()
        chain = set()
        q.put(proof.to_string())

        while not q.empty():
            node = q.get()
            chain.add(node)

            if node not in self.conclusions:
                continue

            for new_node in self.conclusions[node]:
                q.put(new_node)

        # Print thought chain in a pretty format
        for step in chain:
            print(step, end="")
            if step not in self.conclusions:
                print(" axiom")
                continue

            print(" deps: ", end="")
            for dep in self.conclusions[step]:
                print(dep, end=" ")
            print()

    def thought_chain(self) -> str:
        return "".join(self.ss)

