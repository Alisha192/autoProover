from Architect import *


class Sequent:
    def __init__(self, left: dict, right: dict, siblings, depth: int):
        """
        Инициализация секвента.

        :param left: Левые формулы секвента (обычно предпосылки).
        :param right: Правые формулы секвента (обычно вывод).
        :param siblings: Соседние секванты (доказанные секвенты, которые связаны с этим).
        :param depth: Глубина секвента в дереве доказательства.
        """
        self.left = left  # Хранит формулы слева от знака вывода
        self.right = right  # Хранит формулы справа от знака вывода
        self.siblings = siblings  # Хранит соседние секванты
        self.depth = depth  # Глубина текущего секвента

    def __eq__(self, other):
        """
        Проверяет равенство двух секвентов.

        Сравнивает формулы левой и правой частей текущего и другого секвента.

        :param other: Другой секвент для сравнения.
        :return: True, если секванты равны, иначе False.
        """
        for expression in self.left:
            if expression not in other.left:  # Проверяем, содержится ли формула в другой левой части
                return False
        for expression in other.left:
            if expression not in self.left:  # Проверяем, содержится ли формула в текущей левой части
                return False
        for expression in self.right:
            if expression not in other.right:  # Проверяем, содержится ли формула в другой правой части
                return False
        for expression in other.right:
            if expression not in self.right:  # Проверяем, содержится ли формула в текущей правой части
                return False
        return True  # Все формулы совпадают, секванты равны

    def __str__(self):
        """
        Преобразует секвент в строку для удобного отображения.

        Формат: 'формулы слева ⊢ формулы справа'.
        """
        left_part = ', '.join([str(expression) for expression in self.left])  # Формируем строку для левой части
        right_part = ', '.join([str(expression) for expression in self.right])  # Формируем строку для правой части
        if left_part != '':
            left_part = left_part + ' '  # Добавляем пробел, если левой части нет
        if right_part != '':
            right_part = ' ' + right_part  # Добавляем пробел, если правой части нет
        return left_part + '⊢' + right_part  # Возвращаем строку секвента

    def __hash__(self):
        """
        Возвращает хэш секвента для использования в множествах и словарях.

        Хэш основан на строковом представлении секвента.
        """
        return hash(str(self))  # Возвращаем хэш на основе строкового представления


def deduction(sequent, expression):
    """
    Применение теоремы о дедукции:
    Удаляем импликацию из правой части и добавляем её разложение
    """
    new_sequent = Sequent(
        sequent.left.copy(),
        sequent.right.copy(),
        sequent.siblings,
        sequent.depth + 1
    )
    del new_sequent.right[expression]
    new_sequent.left[expression.left] = sequent.right[expression] + 1
    new_sequent.right[expression.right] = sequent.right[expression] + 1
    return new_sequent


def modus_ponens(sequent, expression):
    """
    Применение правила modus ponens:
    Левую часть импликации добавляем в правую часть секвента - теперь ее нужно доказать
    Правую часть импликации записываем как новое условие в левой части секвента
    """
    new_sequent_a = Sequent(
        sequent.left.copy(),
        sequent.right.copy(),
        sequent.siblings,
        sequent.depth + 1
    )
    new_sequent_b = Sequent(
        sequent.left.copy(),
        sequent.right.copy(),
        sequent.siblings,
        sequent.depth + 1
    )
    del new_sequent_a.left[expression]
    del new_sequent_b.left[expression]
    new_sequent_a.right[expression.left] = sequent.left[expression] + 1
    new_sequent_b.left[expression.right] = sequent.left[expression] + 1

    if new_sequent_a.siblings is not None:
        new_sequent_a.siblings.add(new_sequent_a)
    if new_sequent_b.siblings is not None:
        new_sequent_b.siblings.add(new_sequent_b)

    return [new_sequent_a, new_sequent_b]


def remove_left_negation(sequent, expression):
    """
    Удаляем отрицание из левой части и добавляем его формулу в правую часть
    """
    new_sequent = Sequent(
        sequent.left.copy(),
        sequent.right.copy(),
        sequent.siblings,
        sequent.depth + 1
    )
    del new_sequent.left[expression]
    new_sequent.right[expression.expr] = sequent.left[expression] + 1
    return new_sequent


def remove_right_negation(sequent, expression):
    """
    Удаляем отрицание из правой части и добавляем его формулу в левую часть
    """
    new_sequent = Sequent(
        sequent.left.copy(),
        sequent.right.copy(),
        sequent.siblings,
        sequent.depth + 1
    )
    del new_sequent.right[expression]
    new_sequent.left[expression.expr] = sequent.right[expression] + 1
    return new_sequent


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
    return expression


def unify(expr1: Expression, expr2: Expression, substitutions: dict | None) -> dict | None:
    """
    Унифицирует два выражения, если это возможно.
    :param expr1: Первое выражение.
    :param expr2: Второе выражение.
    :param substitutions: Текущие подстановки.
    :return: Словарь подстановок или None, если унификация невозможна.
    """
    if substitutions is None:
        substitutions = {}

    if isinstance(expr1, Variable):
        return unify_variable(expr1, expr2, substitutions)
    elif isinstance(expr2, Variable):
        return unify_variable(expr2, expr1, substitutions)
    elif isinstance(expr1, Implication) and isinstance(expr2, Implication):
        # Унификация частей импликации
        substitutions = unify(expr1.left, expr2.left, substitutions)
        if substitutions is None:
            return None
        return unify(expr1.right, expr2.right, substitutions)
    elif isinstance(expr1, Negation) and isinstance(expr2, Negation):
        # Унификация отрицаний
        return unify(expr1.expr, expr2.expr, substitutions)
    elif isinstance(expr1, Expression) and isinstance(expr2, Expression):
        # Если оба выражения совпадают
        return substitutions if expr1 == expr2 else None
    else:
        # Если типы не совпадают, унификация невозможна
        return None


def unify_variable(var: Variable, expr: Expression, substitutions: dict):
    """
    Обрабатывает случай унификации переменной с выражением.
    :param var: Переменная.
    :param expr: Выражение.
    :param substitutions: Текущие подстановки.
    :return: Обновленный словарь подстановок или None, если унификация невозможна.
    """
    if var in substitutions:  # Если переменная уже в подстановках
        if substitutions[var] == expr:
            return substitutions  # Подстановка совпадает
        else:
            return None  # Конфликт подстановок

    if isinstance(expr, Variable) or isinstance(expr, Negation):  # Замена переменной на другую переменную или ее отрицание
        for key, value in substitutions.items():
            if value == var:  # Если переменная уже была заменена на другую
                substitutions[key] = expr  # Обновляем замену
        substitutions[var] = expr
        return substitutions

    # Если выражение не переменная, отказываемся от унификации
    return None


def occurs_check(var: Variable, expr: Expression) -> bool:
    """
    Проверяет, встречается ли переменная внутри выражения (для предотвращения циклических подстановок).
    :param var: Переменная.
    :param expr: Выражение.
    :return: True, если переменная встречается в выражении, иначе False.
    """
    if var == expr:
        return True
    elif isinstance(expr, Implication):
        return occurs_check(var, expr.left) or occurs_check(var, expr.right)
    elif isinstance(expr, Negation):
        return occurs_check(var, expr.expr)
    return False


def apply_substitutions(expr: Expression, substitutions: dict) -> Expression:
    """
    Применяет подстановки к выражению.
    :param expr: Выражение, к которому нужно применить подстановки.
    :param substitutions: Словарь подстановок {Variable: Expression}.
    :return: Новое выражение с применёнными подстановками.
    """
    if isinstance(expr, Variable):
        # Если это переменная, заменяем её, если есть подстановка
        return substitutions.get(expr, expr)
    elif isinstance(expr, Implication):
        # Рекурсивно применяем подстановки к левой и правой части импликации
        return Implication(
            apply_substitutions(expr.left, substitutions),
            apply_substitutions(expr.right, substitutions)
        )
    elif isinstance(expr, Negation):
        # Рекурсивно применяем подстановки к выражению в отрицании
        return Negation(apply_substitutions(expr.expr, substitutions))
    else:
        # Если это не переменная, импликация или отрицание, возвращаем как есть
        return expr


if __name__ == "__main__":
    a = Implication(Variable("A"), Implication(Variable("D"),Variable("E")))
    b = Implication(Variable("C"), Variable("B"))
    res = unify(a, b, None)
    for key, value in res.items():
        print(key, value)
    apply_substitutions(a, res)
    print(a)
    print(b)
