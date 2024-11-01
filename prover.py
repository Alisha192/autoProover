from language import *

def unify(term_a, term_b):
  if isinstance(term_a, UnificationTerm):
    if term_b.occurs(term_a) or term_b.time > term_a.time:
      return None
    return { term_a: term_b }
  if isinstance(term_b, UnificationTerm):
    if term_a.occurs(term_b) or term_a.time > term_b.time:
      return None
    return { term_b: term_a }
  if isinstance(term_a, Variable) and isinstance(term_b, Variable):
    if term_a == term_b:
      return { }
    return None
  if (isinstance(term_a, Function) and isinstance(term_b, Function)) or \
     (isinstance(term_a, Predicate) and isinstance(term_b, Predicate)):
    if term_a.name != term_b.name:
      return None
    if len(term_a.terms) != len(term_b.terms):
      return None
    substitution = { }
    for i in range(len(term_a.terms)):
      a = term_a.terms[i]
      b = term_b.terms[i]
      for k, v in substitution.items():
        a = a.replace(k, v)
        b = b.replace(k, v)
      sub = unify(a, b)
      if sub == None:
        return None
      for k, v in sub.items():
        substitution[k] = v
    return substitution
  return None

# solve a list of equations
def unify_list(pairs):
  substitution = { }
  for term_a, term_b in pairs:
    a = term_a
    b = term_b
    for k, v in substitution.items():
      a = a.replace(k, v)
      b = b.replace(k, v)
    sub = unify(a, b)
    if sub == None:
      return None
    for k, v in sub.items():
      substitution[k] = v
  return substitution

##############################################################################
# Sequents
##############################################################################

class Sequent:
  def __init__(self, left, right, siblings, depth):
    self.left = left
    self.right = right
    self.siblings = siblings
    self.depth = depth

  def freeVariables(self):
    result = set()
    for formula in self.left:
      result |= formula.freeVariables()
    for formula in self.right:
      result |= formula.freeVariables()
    return result

  def freeUnificationTerms(self):
    result = set()
    for formula in self.left:
      result |= formula.freeUnificationTerms()
    for formula in self.right:
      result |= formula.freeUnificationTerms()
    return result

  def getVariableName(self, prefix):
    fv = self.freeVariables() | self.freeUnificationTerms()
    index = 1
    name = prefix + str(index)
    while Variable(name) in fv or UnificationTerm(name) in fv:
      index += 1
      name = prefix + str(index)
    return name

  def getUnifiablePairs(self):
    pairs = []
    for formula_left in self.left:
      for formula_right in self.right:
        if unify(formula_left, formula_right) is not None:
          pairs.append((formula_left, formula_right))
    return pairs

  def __eq__(self, other):
    for formula in self.left:
      if formula not in other.left:
        return False
    for formula in other.left:
      if formula not in self.left:
        return False
    for formula in self.right:
      if formula not in other.right:
        return False
    for formula in other.right:
      if formula not in self.right:
        return False
    return True

  def __str__(self):
    left_part = ', '.join([str(formula) for formula in self.left])
    right_part = ', '.join([str(formula) for formula in self.right])
    if left_part != '':
      left_part = left_part + ' '
    if right_part != '':
      right_part = ' ' + right_part
    return left_part + '⊢' + right_part

  def __hash__(self):
    return hash(str(self))


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
  print(f"используется правило для {old_sequent} и {left_formula}: Когда формула ¬A находится в левой части секвента, это означает, что в этом контексте мы утверждаем, что формула A ложна. Чтобы изменить это представление, мы перемещаем A в правую часть секвента, так как теперь A должна быть доказана как ложная в рамках вывода.")
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
  print(f"используеся правило для {old_sequent} и {right_formula}: Когда формула ¬A находится в правой части секвента, это указывает на то, что A в левой части должно быть истинным. Чтобы это выразить, мы перемещаем A в левую часть секвента, где оно должно быть доказано как истинное.")
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
  print(f"используется правило для {old_sequent} и {right_formula}: Когда формула A → B находится в правой части секвента, это означает, что если A истинно, то должно быть истинно и B. Логически это эквивалентно утверждению, что либо A ложна, либо B истинно, то есть ¬A ∨ B.")
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
    proven = { sequent }  # Секвенты, которые уже доказаны

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

# returns True if the formula is provable
# returns False or loops forever if the formula is not provable
def proveFormula(axioms, formula):
  return proveSequent(Sequent(
    { axiom: 0 for axiom in axioms },
    { formula: 0 },
    None,
    0
  ))
