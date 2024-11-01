class Hypothesis:
    def __init__(self, expression: str, lhs: str = "", rhs: str = "", how: int = 0, ruleno: int = -1, Ei: str = "", Ej: str = ""):
        self.expression = expression  # Выражение гипотезы
        self.lhs = lhs  # Левая часть выражения
        self.rhs = rhs  # Правая часть выражения
        self.how = how  # Способ получения гипотезы: 0 - гипотеза, 1 - результат модуса поненса, 2 - результат аксиомы
        self.ruleno = ruleno  # Номер правила в случае аксиомы
        self.Ei = Ei  # Содержит (1) A или (2) правило (номер правила)
        self.Ej = Ej  # Содержит (1) A->B или (2) A
        self.appliedrules = set()  # Множество применённых правил

    def __eq__(self, other):
        # Проверка на равенство гипотез по полю expression
        if isinstance(other, Hypothesis):
            return self.expression == other.expression
        return False

    def __hash__(self):
        # Хеш-код объекта на основе поля expression, для использования в хэш-структурах
        return hash(self.expression)
