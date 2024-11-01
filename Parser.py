from collections import defaultdict

class ThmParser:
    def __init__(self):
        # Основные структуры данных для хранения гипотез
        self.hypothesis = {}  # HashMap<String, Hypothesis>
        self.lhs_hypo = defaultdict(set)  # HashMap<String, HashSet<String>>
        self.rhs_hypo = defaultdict(set)  # HashMap<String, HashSet<String>>
        self.new_lhs_hypo = defaultdict(set)  # HashMap<String, HashSet<Hypothesis>>

        # Набор символов, встречающихся в гипотезах
        self.charsinhypo = set()  # HashSet<String>

        # Инициализация правил и аксиом
        Utils.rules.extend([
            "A->(B->A)",  # аксиома 0
            "(A->(B->C))->((A->B)->(A->C))",  # аксиома 1
            "((A->F)->F)->A",  # аксиома 2
            "A->((A->F)->F)",  # аксиома 3
            "(A->B)->(~B->~A)",  # аксиома 4
            "(~B->~A)->(A->B)",  # аксиома 5
            "(~B->A)->(~A->B)",  # аксиома 6
            "(B->~A)->(A->~B)",  # аксиома 7
            "~(A&B)->(~A|~B)",  # аксиома 8
            "~(A|B)->(~A&~B)"  # аксиома 9
        ])

        Utils.ruleappliers.extend([
            RuleApplier("A->(B->A)", 0),
            RuleApplier("(A->(B->C))->((A->B)->(A->C))", 1),
            RuleApplier("((A->F)->F)->A", 2),
            RuleApplier("A->((A->F)->F)", 3),
            RuleApplier("(A->B)->(~B->~A)", 4),
            RuleApplier("(~B->~A)->(A->B)", 5),
            RuleApplier("(~B->A)->(~A->B)", 6),
            RuleApplier("(B->~A)->(A->~B)", 7),
            RuleApplier("~(A&B)->(~A|~B)", 8),
            RuleApplier("~(A|B)->(~A&~B)", 9)
        ])

    def rhstolhs(self, thm: str):
        count = 0
        pos = 0

        # Если выражение состоит из одного символа
        if len(thm) == 1:
            if thm[0] == 'F':  # Если это "ложь", возвращаемся
                return
            else:
                # Преобразование выражения в вид (~A->F)->F для модуля
                self.rhstolhs(f"({thm[0]}->F)->F")
                return

        # Разделяем строку на левую (lhs) и правую (rhs) части
        while pos < len(thm):
            c = thm[pos]
            if c == '(':
                count += 1
            elif c == ')':
                count -= 1
            elif c == '-' and count == 0:
                # Разделение на lhs и rhs
                if thm[0] == '(':
                    lhs = thm[1:pos - 1]  # левая часть с оберткой скобками
                else:
                    lhs = thm[:pos]

                if thm[pos + 2] == '(':
                    rhs = thm[pos + 3:len(thm) - 1]  # правая часть с оберткой скобками
                else:
                    rhs = thm[pos + 2:]

                # Создаем гипотезу для lhs и добавляем в структуры для модуля
                temp_hypo = self.make_hypothesis(lhs, 0, -1, None, None)
                self.insert_new_hypo_mp_dirty(temp_hypo)

                # Рекурсивно обрабатываем правую часть
                self.rhstolhs(rhs)
                return

            pos += 1

        # Обрабатываем выражения вида (p->q)
        self.rhstolhs(thm[1:-1])

    @staticmethod
    def make_hypothesis(hyp, how, ruleno, Ei, Ej):
        # Если гипотеза пуста, возвращаем None
        if len(hyp) == 0:
            return None
        
        # Расширяем гипотезу, используя существующий метод expandHypothesis
        newhypo = Utils.expand_hypothesis(hyp)
        newhypo.how = how  # Устанавливаем значение "how"
        newhypo.ruleno = ruleno  # Устанавливаем номер правила
        newhypo.Ei = Ei  # Устанавливаем значение Ei
        newhypo.Ej = Ej  # Устанавливаем значение Ej
        return newhypo

    def insert_hypothesis(self, newhypo):
        # Проверка на наличие пустой гипотезы
        if newhypo is None or len(newhypo.expression) == 0:
            return False

        expression = newhypo.expression

        # Проверяем, существует ли уже гипотеза с таким выражением
        if expression in self.hypothesis:
            return False  # Если существует, ничего не добавляем

        # Добавляем новую гипотезу в self.hypothesis
        self.hypothesis[expression] = newhypo
        Utils.println(f"Adding hypo {expression}")

        lhs = newhypo.lhs
        rhs = newhypo.rhs

        # Обновляем lhs_hypo, добавляя правую часть выражения к множеству левых
        if lhs not in self.lhs_hypo:
            self.lhs_hypo[lhs] = {rhs}
        else:
            self.lhs_hypo[lhs].add(rhs)

        # Обновляем rhs_hypo, добавляя левую часть выражения к множеству правых
        if rhs not in self.rhs_hypo:
            self.rhs_hypo[rhs] = {lhs}
        else:
            self.rhs_hypo[rhs].add(lhs)

        return True

  def insert_new_hypo_mp_dirty(self, newhypo):
    # Вставляем новую гипотезу и проверяем, была ли она добавлена успешно
    in_hypo = self.insert_hypothesis(newhypo)
    
    if in_hypo:
        # Если новая гипотеза добавлена, выводим сообщение об этом (отладка)
        # Ищем множество гипотез для левой части выражения
        hypo_set = self.new_lhs_hypo.get(newhypo.lhs)
        
        if hypo_set is None:
            # Если множества нет, создаем новое и добавляем гипотезу
            hypo_set = {newhypo}
            self.new_lhs_hypo[newhypo.lhs] = hypo_set
        else:
            # Если множество существует, просто добавляем гипотезу в него
            hypo_set.add(newhypo)
    else:
        # Если гипотеза уже существовала, можно вывести сообщение (отладка)
        pass

    # Возвращаем флаг, указывающий, была ли гипотеза добавлена как новая
    return in_hypo


  def modusponens(self):
    # Временная таблица для гипотез и множество новых гипотез
    temp_lhs_hypo = {}
    new_hypos = set()

    # Итерация по всем существующим гипотезам
    for A, _ in self.hypothesis.items():
        # Получаем все гипотезы для A (если существуют)
        A_B = self.new_lhs_hypo.get(A)
        if A_B is None:
            continue  # Если нет совпадений, переходим к следующей гипотезе
        
        # Проходим по гипотезам в A_B
        for A_B_hypo in A_B:
            # Создаем новую гипотезу для правой части выражения
            mp_hypo = self.make_hypothesis(A_B_hypo.rhs, 1, -1, A, A_B_hypo.expression)
            if mp_hypo is not None:
                new_hypos.add(mp_hypo)
                if mp_hypo.expression in self.hypothesis:
                    # Если гипотеза уже существует, пропускаем
                    continue
                # В случае новой гипотезы - обрабатываем её

    # Обработка новых гипотез для modus ponens
    for A, hypos in self.new_lhs_hypo.items():
        for A_hypo in hypos:
            # Получаем множество B для данной гипотезы A
            B_set = self.lhs_hypo.get(A)
            if B_set is None:
                continue  # Если нет совпадений, переходим к следующей гипотезе
            
            # Проходим по каждому элементу множества B
            for B_str in B_set:
                A_B_exp = Utils.expression(A, B_str)
                # Создаем гипотезу для B_str
                mp_hypo = self.make_hypothesis(B_str, 1, -1, A, A_B_exp)
                if mp_hypo is not None:
                    new_hypos.add(mp_hypo)
                    if mp_hypo.expression in self.hypothesis:
                        # Если гипотеза уже существует, пропускаем
                        continue
                    # В случае новой гипотезы - обрабатываем её

    # Вставка новых гипотез в глобальный список
    for mp_hypo in new_hypos:
        if self.insert_hypothesis(mp_hypo):
            # Добавляем новую гипотезу в temp_lhs_hypo
            temp_hypos = temp_lhs_hypo.get(mp_hypo.lhs, set())
            temp_hypos.add(mp_hypo)
            temp_lhs_hypo[mp_hypo.lhs] = temp_hypos

    # Обновляем список гипотез
    self.new_lhs_hypo.clear()
    self.new_lhs_hypo = temp_lhs_hypo
    
    # Если были добавлены новые гипотезы, вызываем modusponens рекурсивно
    if len(self.new_lhs_hypo) != 0:
        self.modusponens()

  def axiom1(self, A, B):
    print("Axiom 1 on single non-terminals : ")
    new_hypos = set()

    # Итерация по всем элементам A и B
    for sA in A:
        for sB in B:
            rhs = Utils.expression(sB, sA)
            hyp = Utils.expression(sA, rhs)
            axiom1_hypo = self.make_hypothesis(hyp, 2, 1, Utils.rules[0], f"{sA} & {sB}")
            axiom1_hypo.appliedrules.add(0)
            new_hypos.add(axiom1_hypo)

    # Вставка новых гипотез
    for mp_hypo in new_hypos:
        self.insert_new_hypo_mp_dirty(mp_hypo)

    print("modus ponens: ")
    self.modusponens()

    # Проверка на наличие гипотезы "F"
    if self.checkF():
        self.proofPath("F")
        return

def checkF(self):
    return "F" in self.hypothesis

def proofPath(self, h):
    hyp = self.hypothesis[h]
    if hyp.how == 0:
        Utils.print_hypothesis(hyp)
    elif hyp.how == 1:
        self.proofPath(hyp.Ei)
        self.proofPath(hyp.Ej)
        Utils.print_hypothesis(hyp)
    elif hyp.how == 2:
        self.proofPath(hyp.Ej)
        Utils.print_hypothesis(hyp)

  def run_parser(self, hyp):
    self.charsinhypo = Utils.distinctChars(hyp)
    print("rhstolhs: ")
    self.rhstolhs(Utils.expandAll(hyp))

    i = 1
    while True:
        i = 1
        itr = 0
        while i != 0 and itr < 1:
            i = 0
            print("modus ponens: ")
            self.modusponens()
            h1 = len(self.hypothesis)

            for rulenum in range(len(Utils.rules)):
                print(f"Applying rule {rulenum} {Utils.ruleappliers[rulenum].rule} : ")
                new_hypos = set()
                for exp, hypo in self.hypothesis.items():
                    if rulenum in hypo.appliedrules:
                        continue
                    else:
                        print(f"on : {exp}")
                        hypo.appliedrules.add(rulenum)

                    hypos = Utils.ruleappliers[rulenum].checkRule(hypo)
                    new_hypos.update(hypos)

                for mp_hypo in new_hypos:
                    self.insert_new_hypo_mp_dirty(mp_hypo)

                print("modus ponens: ")
                self.modusponens()

                if self.checkF():
                    self.proofPath("F")
                    return

            h2 = len(self.hypothesis)
            if h1 != h2:
                i = 1
                itr += 1
            if self.checkF():
                self.proofPath("F")
                return

        while True:
            inp = input("hint : ")
            Utils.printRules()
            if inp == "continue":
                break
            elif inp == "axiom1":
                self.axiom1(self.charsinhypo, self.charsinhypo)
                continue
            else:
                try:
                    newrulenum = int(input("rule number : ")) if inp == "rule" else len(Utils.rules)
                    if inp != "rule":
                        Utils.rules.append(inp)
                        Utils.ruleappliers.append(RuleApplier(inp, newrulenum))
                except ValueError:
                    print("Invalid input for rule number. Please enter a valid integer.")
                    continue

            print("")

            print("modus ponens: ")
            self.modusponens()

            print(f"Applying rule {newrulenum} {Utils.ruleappliers[newrulenum].rule} : ")
            new_hypos = set()
            for exp, hypo in self.hypothesis.items():
                if newrulenum in hypo.appliedrules:
                    continue
                else:
                    print(f"on : {exp}")
                    hypo.appliedrules.add(newrulenum)

                hypos = Utils.ruleappliers[newrulenum].checkRule(hypo)
                new_hypos.update(hypos)

            for mp_hypo in new_hypos:
                self.insert_new_hypo_mp_dirty(mp_hypo)

            print("modus ponens: ")
            self.modusponens()

            if self.checkF():
                self.proofPath("F")
                return


