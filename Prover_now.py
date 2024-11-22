from datetime import datetime

from language import *


def unify(term_a, term_b):
    """
  Выполняет унификацию двух термов.

  :param term_a: Первый терм для унификации.
  :param term_b: Второй терм для унификации.
  :return: Словарь с заменами, если унификация возможна; иначе None.
  """
    # Если первый терм - унификационный терм
    if isinstance(term_a, UnificationTerm):
        # Проверяем, не возникает ли конфликт (цикличность) и не превышает ли время замены
        if term_b.occurs(term_a) or term_b.time > term_a.time:
            return None  # Невозможно унифицировать
        return {term_a: term_b}  # Возвращаем замену терма

    # Если второй терм - унификационный терм
    if isinstance(term_b, UnificationTerm):
        # Проверяем на цикличность и время
        if term_a.occurs(term_b) or term_a.time > term_b.time:
            return None  # Невозможно унифицировать
        return {term_b: term_a}  # Возвращаем замену терма

    # Если оба терма - переменные
    if isinstance(term_a, Variable) and isinstance(term_b, Variable):
        if term_a == term_b:
            return {}  # Они идентичны, ничего не меняем
        return None  # Две разные переменные не могут быть унифицированы

    # Если оба терма - функции или предикаты
    if (isinstance(term_a, Function) and isinstance(term_b, Function)) or \
            (isinstance(term_a, Predicate) and isinstance(term_b, Predicate)):
        # Проверяем, совпадают ли имена
        if term_a.name != term_b.name:
            return None  # Разные имена не могут быть унифицированы
        if len(term_a.terms) != len(term_b.terms):
            return None  # Разное количество аргументов

        substitution = {}  # Словарь для хранения замен
        for i in range(len(term_a.terms)):
            a = term_a.terms[i]
            b = term_b.terms[i]

            # Применяем существующие замены к термам
            for k, v in substitution.items():
                a = a.replace(k, v)
                b = b.replace(k, v)

            sub = unify(a, b)  # Рекурсивно унифицируем термы
            if sub is None:
                return None  # Если унификация невозможна

            # Добавляем новые замены
            for k, v in sub.items():
                substitution[k] = v

        return substitution  # Возвращаем найденные замены

    return None  # Невозможна унификация других типов термов


def unify_list(pairs):
    """
  Решает список уравнений, выполняя унификацию для каждой пары термов.

  :param pairs: Список пар термов для унификации.
  :return: Словарь с заменами для всех термов, если унификация возможна; иначе None.
  """
    substitution = {}  # Словарь для хранения замен
    for term_a, term_b in pairs:
        a = term_a
        b = term_b

        # Применяем существующие замены к термам
        for k, v in substitution.items():
            a = a.replace(k, v)
            b = b.replace(k, v)

        sub = unify(a, b)  # Пытаемся унифицировать текущую пару термов
        if sub is None:
            return None  # Если унификация невозможна, возвращаем None

        # Добавляем новые замены
        for k, v in sub.items():
            substitution[k] = v

    return substitution  # Возвращаем найденные замены


##############################################################################
# Sequents
##############################################################################

class Sequent:
    def __init__(self, left, right, siblings, depth):
        """
    Инициализация секвента.

    :param left: Левые формулы секвента (обычно предпосылки).
    :param right: Правые формулы секвента (обычно вывод).
    :param siblings: Соседние секванты (доказанные секванты, которые связаны с этим).
    :param depth: Глубина секвента в дереве доказательства.
    """
        self.left = left  # Хранит формулы слева от знака вывода
        self.right = right  # Хранит формулы справа от знака вывода
        self.siblings = siblings  # Хранит соседние секванты
        self.depth = depth  # Глубина текущего секвента

    def freeVariables(self):
        """
    Возвращает множество свободных переменных в секвенте.

    Обходит все формулы в левой и правой части секвента и собирает свободные переменные.
    """
        result = set()
        for formula in self.left:
            result |= formula.freeVariables()  # Собираем свободные переменные из левых формул
        for formula in self.right:
            result |= formula.freeVariables()  # Собираем свободные переменные из правых формул
        return result  # Возвращаем все найденные свободные переменные

    def freeUnificationTerms(self):
        """
    Возвращает множество свободных унификационных термов в секвенте.

    Обходит все формулы в левой и правой части секвента и собирает свободные унификационные термы.
    """
        result = set()
        for formula in self.left:
            result |= formula.freeUnificationTerms()  # Собираем свободные унификационные термы из левых формул
        for formula in self.right:
            result |= formula.freeUnificationTerms()  # Собираем свободные унификационные термы из правых формул
        return result  # Возвращаем все найденные свободные унификационные термы

    def getVariableName(self, prefix):
        """
    Генерирует уникальное имя переменной на основе заданного префикса.

    Проверяет, существует ли переменная с таким именем, и при необходимости добавляет индекс.

    :param prefix: Префикс для имени переменной.
    :return: Уникальное имя переменной.
    """
        fv = self.freeVariables() | self.freeUnificationTerms()  # Собираем все свободные переменные и унификационные термы
        index = 1
        name = prefix + str(index)
        while Variable(name) in fv or UnificationTerm(name) in fv:  # Проверяем, существует ли уже такая переменная
            index += 1
            name = prefix + str(index)  # Увеличиваем индекс и генерируем новое имя
        return name  # Возвращаем уникальное имя переменной

    def getUnifiablePairs(self):
        """
    Возвращает список пар формул, которые могут быть унифицированы.

    Проходит по всем формульным комбинациям в левой и правой части секвента и использует функцию унификации.
    """
        pairs = []
        for formula_left in self.left:
            for formula_right in self.right:
                if unify(formula_left, formula_right) is not None:  # Проверяем, могут ли формулы быть унифицированы
                    pairs.append((formula_left, formula_right))  # Добавляем пару, если унификация успешна
        return pairs  # Возвращаем список унифицируемых пар

    def __eq__(self, other):
        """
    Проверяет равенство двух секвентов.

    Сравнивает формулы левой и правой частей текущего и другого секвента.

    :param other: Другой секвент для сравнения.
    :return: True, если секванты равны, иначе False.
    """
        for formula in self.left:
            if formula not in other.left:  # Проверяем, содержится ли формула в другой левой части
                return False
        for formula in other.left:
            if formula not in self.left:  # Проверяем, содержится ли формула в текущей левой части
                return False
        for formula in self.right:
            if formula not in other.right:  # Проверяем, содержится ли формула в другой правой части
                return False
        for formula in other.right:
            if formula not in self.right:  # Проверяем, содержится ли формула в текущей правой части
                return False
        return True  # Все формулы совпадают, секванты равны

    def __str__(self):
        """
    Преобразует секвент в строку для удобного отображения.

    Формат: 'формулы слева ⊢ формулы справа'.
    """
        left_part = ', '.join([str(formula) for formula in self.left])  # Формируем строку для левой части
        right_part = ', '.join([str(formula) for formula in self.right])  # Формируем строку для правой части
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


##############################################################################
# Proof search
##############################################################################

# returns True if the sequent is provable
# returns False or loops forever if the sequent is not provable
def applyModusPonens(old_sequent, left_formula):
    print(f"Используется modus ponens {old_sequent} и {left_formula}")
    new_sequent_a = Sequent(
        old_sequent.left.copy(),
        old_sequent.right.copy(),
        old_sequent.siblings,
        old_sequent.depth + 1
    )
    new_sequent_b = Sequent(
        old_sequent.left.copy(),
        old_sequent.right.copy(),
        old_sequent.siblings,
        old_sequent.depth + 1
    )
    del new_sequent_a.left[left_formula]
    del new_sequent_b.left[left_formula]
    new_sequent_a.right[left_formula.formula_a] = old_sequent.left[left_formula] + 1
    new_sequent_b.left[left_formula.formula_b] = old_sequent.left[left_formula] + 1

    if new_sequent_a.siblings is not None:
        new_sequent_a.siblings.add(new_sequent_a)
    if new_sequent_b.siblings is not None:
        new_sequent_b.siblings.add(new_sequent_b)

    return [new_sequent_a, new_sequent_b]


def applyNotLeft(old_sequent, left_formula):
    print(
        f"используется правило для {old_sequent} и {left_formula}: Когда формула ¬A находится в левой части секвента, это означает, что в этом контексте мы утверждаем, что формула A ложна. Чтобы изменить это представление, мы перемещаем A в правую часть секвента, так как теперь A должна быть доказана как ложная в рамках вывода.")
    # Создаем новый секвент с копиями текущих частей
    new_sequent = Sequent(
        old_sequent.left.copy(),
        old_sequent.right.copy(),
        old_sequent.siblings,
        old_sequent.depth + 1
    )
    # Удаляем отрицание из левой части и добавляем его формулу в правую часть
    del new_sequent.left[left_formula]
    new_sequent.right[left_formula.formula] = old_sequent.left[left_formula] + 1
    return new_sequent


def applyNotRight(old_sequent, right_formula):
    print(
        f"используеся правило для {old_sequent} и {right_formula}: Когда формула ¬A находится в правой части секвента, это указывает на то, что A в левой части должно быть истинным. Чтобы это выразить, мы перемещаем A в левую часть секвента, где оно должно быть доказано как истинное.")
    # Создаем новый секвент с копиями текущих частей
    new_sequent = Sequent(
        old_sequent.left.copy(),
        old_sequent.right.copy(),
        old_sequent.siblings,
        old_sequent.depth + 1
    )
    # Удаляем отрицание из правой части и добавляем его формулу в левую часть
    del new_sequent.right[right_formula]
    new_sequent.left[right_formula.formula] = old_sequent.right[right_formula] + 1
    return new_sequent


def applyImpliesRight(old_sequent, right_formula):
    print(
        f"используется правило для {old_sequent} и {right_formula}: Когда формула A → B находится в правой части секвента, это означает, что если A истинно, то должно быть истинно и B. Логически это эквивалентно утверждению, что либо A ложна, либо B истинно, то есть ¬A ∨ B.")
    # Создаем новый секвент с копиями текущих частей
    new_sequent = Sequent(
        old_sequent.left.copy(),
        old_sequent.right.copy(),
        old_sequent.siblings,
        old_sequent.depth + 1
    )
    # Удаляем импликацию из правой части и добавляем её разложение
    del new_sequent.right[right_formula]
    new_sequent.left[right_formula.formula_a] = old_sequent.right[right_formula] + 1
    new_sequent.right[right_formula.formula_b] = old_sequent.right[right_formula] + 1
    return new_sequent


def proveSequent(sequent):
    # Сбрасываем время инстанциации для каждой формулы в секвенте
    for formula in sequent.left:
        formula.setInstantiationTime(0)
    for formula in sequent.right:
        formula.setInstantiationTime(0)

    # Списки для хранения секвентов, которые нужно проверить и которые уже доказаны
    frontier = [sequent]  # Секвенты для проверки
    proven = {sequent}  # Секвенты, которые уже доказаны

    while True:
        # Получаем следующий секвент из списка для проверки
        old_sequent = None
        while len(frontier) > 0 and (old_sequent is None or old_sequent in proven):
            old_sequent = frontier.pop(0)  # Извлекаем первый секвент
        if old_sequent is None:
            break  # Если больше нет секвентов для проверки, выходим из цикла

        # Выводим информацию о текущем секвенте
        print(f'Глубина: {old_sequent.depth}. Секвент: {old_sequent}')

        # Проверяем, является ли секвент аксиоматически истинным без унификации
        if len(set(old_sequent.left.keys()) & set(old_sequent.right.keys())) > 0:
            proven.add(old_sequent)  # Добавляем секвент в доказанные
            continue  # Переходим к следующему секвенту

        # Проверяем наличие унифицируемых пар для каждого соседа
        if old_sequent.siblings is not None:
            sibling_pair_lists = [sequent.getUnifiablePairs() for sequent in old_sequent.siblings]

            # Проверяем, есть ли унифицируемая пара для каждого соседа
            if all([len(pair_list) > 0 for pair_list in sibling_pair_lists]):
                # Перебираем все возможные комбинации унифицируемых пар
                substitution = None
                index = [0] * len(sibling_pair_lists)
                while True:
                    # Пытаемся унифицировать формулы
                    substitution = unify_list([sibling_pair_lists[i][index[i]] for i in range(len(sibling_pair_lists))])
                    if substitution is not None:
                        break  # Если унификация удалась, выходим из цикла

                    # Увеличиваем индекс для следующей попытки унификации
                    pos = len(sibling_pair_lists) - 1
                    while pos >= 0:
                        index[pos] += 1
                        if index[pos] < len(sibling_pair_lists[pos]):
                            break
                        index[pos] = 0
                        pos -= 1
                    if pos < 0:
                        break  # Если перебрали все возможные комбинации, выходим

                # Если унификация успешна, выводим замену и обновляем списки
                if substitution is not None:
                    for k, v in substitution.items():
                        print(f'  Замена: {k} = {v}')  # Выводим замену
                    proven |= old_sequent.siblings  # Добавляем всех соседей в доказанные
                    frontier = [sequent for sequent in frontier if sequent not in old_sequent.siblings]
                    continue

            else:
                # Если не удалось найти унифицируемые пары, удаляем соседа
                old_sequent.siblings.remove(old_sequent)

        while True:
            # Определяем, какую формулу будем расширять
            left_formula = None
            left_depth = None
            for formula, depth in old_sequent.left.items():
                if left_depth is None or left_depth > depth:
                    if not isinstance(formula, Predicate):
                        left_formula = formula
                        left_depth = depth

            right_formula = None
            right_depth = None
            for formula, depth in old_sequent.right.items():
                if right_depth is None or right_depth > depth:
                    if not isinstance(formula, Predicate):
                        right_formula = formula
                        right_depth = depth

            # Определяем, будем ли применять левое или правое правило
            apply_left = False
            apply_right = False
            if left_formula is not None and right_formula is None:
                apply_left = True
            if left_formula is None and right_formula is not None:
                apply_right = True
            if left_formula is not None and right_formula is not None:
                if left_depth < right_depth:
                    apply_left = True
                else:
                    apply_right = True
            if left_formula is None and right_formula is None:
                return False  # Если формул нет, не можем доказать

            # Применение левого правила
            if apply_left:
                if isinstance(left_formula, Not):
                    new_sequent = applyNotLeft(old_sequent, left_formula)
                    frontier.append(new_sequent)  # Добавляем новый секвент в frontier
                    break
                if isinstance(left_formula, Implies):
                    new_sequents = applyModusPonens(old_sequent, left_formula)
                    frontier.extend(new_sequents)  # Добавляем новые секвенты в frontier
                    break

            # Применение правого правила
            if apply_right:
                if isinstance(right_formula, Not):
                    new_sequent = applyNotRight(old_sequent, right_formula)
                    frontier.append(new_sequent)  # Добавляем новый секвент в frontier
                    break
                if isinstance(right_formula, Implies):
                    new_sequent = applyImpliesRight(old_sequent, right_formula)
                    frontier.append(new_sequent)  # Добавляем новый секвент в frontier
                    break

    # Если больше нет секвентов для доказательства, возвращаем True
    return True


def proveFormula(axioms, formula):
    start = datetime.now()
    result = proveSequent(Sequent(
        {axiom: 0 for axiom in axioms},
        {formula.to_implication(): 0},
        None,
        0
    ))
    end = datetime.now()
    time = end - start
    return result, time
