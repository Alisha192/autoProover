from collections import defaultdict


class Utils:

    rules = []
    ruleappliers = []

    @staticmethod
    def println(s: str):
        print(s)

    @staticmethod
    def print(s: str):
        print(s, end="")

    @staticmethod
    def print_rules():
        for i, rule_applier in enumerate(Utils.ruleappliers):
            print(f"{i}: {rule_applier.rule}")

    @staticmethod
    def expression(lhs: str, rhs: str) -> str:
        if len(rhs) == 0:
            return lhs

        lhs1 = f"({lhs})" if len(lhs) != 1 else lhs
        rhs1 = f"({rhs})" if len(rhs) != 1 else rhs
        return f"{lhs1}->{rhs1}"

    @staticmethod
    def remove_unwanted_brac(s: str) -> str:
        if len(s) == 1:
            return s

        count = 0
        pos = 0

        while pos != len(s):
            c = s[pos]
            if c == '(':
                count += 1
            elif c == ')':
                count -= 1
            elif c == '-' and count == 0:
                lhs = s[1:pos - 1] if s[0] == '(' else s[:pos]
                rhs = s[pos + 3:len(s) - 1] if s[pos + 2] == '(' else s[pos + 2:]
                lhs = Utils.remove_unwanted_brac(lhs)
                rhs = Utils.remove_unwanted_brac(rhs)
                return Utils.expression(lhs, rhs)
            pos += 1

        return Utils.remove_unwanted_brac(s[1:-1])

    @staticmethod
    def expand_not(thm: str) -> str:
        notpos = 0
        # Searching for ~
        while notpos < len(thm):
            if thm[notpos] == '~':
                break
            notpos += 1
        if notpos == len(thm):
            return thm  # no more ~

        count = 0
        pos = notpos + 1
        while pos < len(thm):
            c = thm[pos]
            if c == '(':
                count += 1
            elif c == ')':
                count -= 1

            if count == 0:
                # Found the expression
                newthm = thm[:notpos] + f"({thm[notpos + 1:pos + 1]}->F)" + thm[pos + 1:]
                return Utils.expand_not(newthm)
            pos += 1

        return thm

    @staticmethod
    def expand_and(thm: str) -> str:
        andpos = 0
        # Searching for &
        while andpos < len(thm):
            if thm[andpos] == '&':
                break
            andpos += 1
        if andpos == len(thm):
            return thm  # no more &

        count = 0
        rhspos = andpos + 1
        rhs = ""
        while rhspos < len(thm):
            c = thm[rhspos]
            if c == '(':
                count += 1
            elif c == ')':
                count -= 1

            if count == 0:
                # Found RHS expression
                rhs = f"({thm[andpos + 1:rhspos + 1]}->F)"
                break
            rhspos += 1

        count = 0
        lhspos = andpos - 1
        lhs = ""
        while lhspos > -1:
            c = thm[lhspos]
            if c == '(':
                count += 1
            elif c == ')':
                count -= 1

            if count == 0:
                # Found LHS expression
                lhs = thm[lhspos:andpos]
                break
            lhspos -= 1

        if lhspos - 1 >= 0 and thm[lhspos - 1] == '(' and rhspos + 1 < len(thm) and thm[rhspos + 1] == ')':
            lhspos -= 1
            rhspos += 1

        newthm = thm[:lhspos] + f"(({lhs}->{rhs})->F)" + thm[rhspos + 1:]
        return Utils.expand_and(newthm)

    @staticmethod
    def expand_or(thm: str) -> str:
        orpos = 0
        # Searching for |
        while orpos < len(thm):
            if thm[orpos] == '|':
                break
            orpos += 1
        if orpos == len(thm):
            return thm  # no more |

        count = 0
        rhspos = orpos + 1
        rhs = ""
        while rhspos < len(thm):
            c = thm[rhspos]
            if c == '(':
                count += 1
            elif c == ')':
                count -= 1

            if count == 0:
                # Found RHS expression
                rhs = thm[orpos + 1:rhspos + 1]
                break
            rhspos += 1

        count = 0
        lhspos = orpos - 1
        lhs = ""
        while lhspos > -1:
            c = thm[lhspos]
            if c == '(':
                count += 1
            elif c == ')':
                count -= 1

            if count == 0:
                # Found LHS expression
                lhs = f"({thm[lhspos:orpos]}->F)"
                break
            lhspos -= 1

        if lhspos - 1 >= 0 and thm[lhspos - 1] == '(' and rhspos + 1 < len(thm) and thm[rhspos + 1] == ')':
            lhspos -= 1
            rhspos += 1

        newthm = thm[:lhspos] + f"({lhs}->{rhs})" + thm[rhspos + 1:]
        return Utils.expand_or(newthm)

    @staticmethod
    def expand_all(thm: str) -> str:
        # Remove all whitespace, then apply expandNot, expandAnd, and expandOr in sequence
        thm = thm.replace(" ", "")
        return Utils.remove_unwanted_brac(Utils.expand_or(Utils.expand_and(Utils.expand_not(thm))))

    @staticmethod
    def expand_hypothesis(hyp: str) -> "Hypothesis":
        count = 0
        pos = 0

        newhypo = Hypothesis(expression="", lhs="", rhs="")

        # Если выражение состоит из одного символа
        if len(hyp) == 1:
            exp = hyp[0]
            newhypo.expression = exp
            newhypo.lhs = exp
            newhypo.rhs = ""
            return newhypo

        # Обход строки для нахождения основного разделителя
        while pos < len(hyp):
            c = hyp[pos]
            if c == '(':
                count += 1
            elif c == ')':
                count -= 1
            elif c == '-' and count == 0:
                # Разделение на lhs и rhs
                if hyp[0] == '(':
                    # lhs в скобках
                    lhs = hyp[1:pos - 1]
                else:
                    lhs = hyp[:pos]

                if hyp[pos + 2] == '(':
                    # rhs в скобках
                    rhs = hyp[pos + 3:len(hyp) - 1]
                else:
                    rhs = hyp[pos + 2:]

                # Формирование новой гипотезы
                newhypo.lhs = lhs
                newhypo.rhs = rhs
                newhypo.expression = Utils.expression(lhs, rhs)
                return newhypo

            pos += 1

        # Обработка выражения вида (p->q)
        return Utils.expand_hypothesis(hyp[1:-1])

    @staticmethod
    def print_thm_parser(thmp):
        # Печать гипотез
        print("Hypothesis:")
        for key, hyp in thmp.hypothesis.items():
            print(f"{key} {hyp.expression} lhs: {hyp.lhs} rhs: {hyp.rhs}")

        # Печать левой части гипотез
        print("LHS:")
        for key, rhs_set in thmp.lhs_hypo.items():
            print(f"{key} : ", end="")
            print(", ".join(rhs_set))  # Печать всех элементов через запятую
            print()  # Для новой строки

        # Печать правой части гипотез
        print("RHS:")
        for key, lhs_set in thmp.rhs_hypo.items():
            print(f"{key} : ", end="")
            print(", ".join(lhs_set))  # Печать всех элементов через запятую
            print()  # Для новой строки

        # Печать уникальных символов
        print("Distinct Chars:")
        print(", ".join(thmp.charsinhypo))  # Печать всех символов через запятую
        print()  # Для новой строки

    def print_hypothesis(hyp):
        footer = ""
        if hyp.how == 0:
            footer = "    Basic Hypothesis"
        elif hyp.how == 1:
            footer = f"    Modus Ponens ( {hyp.Ei} on {hyp.Ej} )"
        elif hyp.how == 2:
            footer = f"    rule: {hyp.ruleno}    Axiom/Theorem ( {hyp.Ei} on {hyp.Ej} )"

        print(f"{hyp.expression}, lhs: {hyp.lhs}, rhs: {hyp.rhs}{footer}")

    @staticmethod
    def distinct_chars(s):
        chars = set()  # Используем множество для уникальных символов
        chars.add("F")
        for c in s:
            if c not in "()->~&|":
                chars.add(c)
        return chars



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

class RuleApplier:

    variables = {}

    def __init__(self, r, rno):
        temp_hyp = Utils.expand_hypothesis(Utils.expand_all(r))
        self.rule = temp_hyp.expression
        self.rule_lhs = temp_hyp.lhs
        self.rule_rhs = temp_hyp.rhs
        self.ruleno = rno
        print(f"{self.rule_lhs} : {self.rule_rhs}")

    def check_rule(self, hyp):
        new_hypos = []
        hyp1 = self.apply_rule(hyp.lhs, hyp.rhs, self.rule, hyp.expression)
        hyp2 = self.apply_rule(hyp.expression, "", self.rule_lhs, hyp.expression)

        if hyp1 is not None:
            Utils.printHypothesis(hyp1)
            new_hypos.append(hyp1)

            hypo = ThmParser.makeHypothesis(hyp.lhs, 2, self.ruleno, Utils.rules[self.ruleno], hyp.expression)
            Utils.printHypothesis(hypo)
            new_hypos.append(hypo)

        if hyp2 is not None:
            Utils.print_hypothesis(hyp2)
            new_hypos.append(hyp2)

        return new_hypos

    def apply_rule(self, hyp, hyp_rhs, ruleexp, hyp_exp):
        lhs_rule_pos = 0

        len_lhs_rule = len(ruleexp)
        len_hyp = len(hyp)
        pos = 0

        while pos < len_hyp and lhs_rule_pos < len_lhs_rule:
            rule_char = ruleexp[lhs_rule_pos]

            if rule_char in "()->F":
                if hyp[pos] == rule_char:
                    # Совпадение
                    lhs_rule_pos += 1
                    pos += 1
                else:
                    break
            elif hyp[pos] == '>':
                break
            else:
                count = 0
                pos_end = pos
                valid = True

                while pos_end < len_hyp:
                    c = hyp[pos_end]
                    if c == '(':
                        count += 1
                    elif c == ')':
                        count -= 1

                    if count < 0:
                        valid = False
                        break
                    elif count == 0:
                        # Найдено выражение
                        exp = self.variables.get(rule_char)
                        if exp is None:
                            self.variables[rule_char] = hyp[pos:pos_end + 1]
                            lhs_rule_pos += 1
                            pos = pos_end + 1
                        else:
                            if exp == hyp[pos:pos_end + 1]:
                                # Действительно
                                lhs_rule_pos += 1
                                pos = pos_end + 1
                            else:
                                valid = False
                                break
                        break
                    pos_end += 1

                if not valid:
                    break

        if lhs_rule_pos == len_lhs_rule and pos == len_hyp:
            # Это конец правила
            if len(hyp_rhs) == 0:
                hypo = self.transform_hypothesis(hyp, 0, pos)
                if hypo is None:
                    return None
                hypo.how = 2
                hypo.ruleno = self.ruleno
                hypo.Ei = Utils.rules[self.ruleno]
                hypo.Ej = hyp_exp
            else:
                hypo = ThmParser.makeHypothesis(hyp_rhs, 2, self.ruleno, Utils.rules[self.ruleno], hyp_exp)
            return hypo
        else:
            # Гипотеза закончилась раньше, чем правило
            # Правило закончилось раньше, чем гипотеза завершилась
            pass  # Тут можно добавить дополнительную обработку, если нужно

        self.variables.clear()
        return None


    def transform_hypothesis(self, hyp, hyp_pos, hyp_end):
        rhs = self.rule_rhs
        pos = 0
        new_rhs = ""

        while pos != len(rhs):
            c = rhs[pos]
            if c in "()->F":
                new_rhs += c
            else:
                t = self.variables.get(c)
                if t is not None:
                    new_rhs += t
                else:
                    return None
            pos += 1

        if len(new_rhs) != 1 and not (hyp_pos == 0 and hyp_end == len(hyp)):
            new_rhs = f"({new_rhs})"

        new_hyp = hyp[:hyp_pos] + new_rhs + hyp[hyp_end:]
        new_hypo = Utils.expand_hypothesis(new_hyp)
        self.variables.clear()
        return new_hypo


    @staticmethod
    def is_axiom_1(h):
        # Проверка аксиомы 1: A -> (B -> A)
        lhs = h.lhs
        rhs = h.rhs
        if rhs == "":
            return False

        temp_hyp = Utils.expand_hypothesis(rhs)
        return temp_hyp.rhs == lhs


    @staticmethod
    def is_axiom_2(h):
        # Проверка аксиомы 2: (A -> (B -> C)) -> ((A -> B) -> (A -> C))
        lhs1 = h.lhs
        rhs1 = h.rhs
        if rhs1 == "":
            return False

        temp_hyp_l1 = Utils.expand_hypothesis(lhs1)
        temp_hyp_r1 = Utils.expand_hypothesis(rhs1)

        a = temp_hyp_l1.lhs
        btoc = temp_hyp_l1.rhs
        if btoc == "":
            return False

        temp_hyp_btoc = Utils.expand_hypothesis(btoc)
        b = temp_hyp_btoc.lhs
        c = temp_hyp_btoc.rhs
        if c == "":
            return False

        atob = temp_hyp_r1.lhs
        atoc = temp_hyp_r1.rhs
        if atoc == "":
            return False

        temp_hyp_atob = Utils.expand_hypothesis(atob)
        temp_hyp_atoc = Utils.expand_hypothesis(atoc)

        a2 = temp_hyp_atob.lhs
        b2 = temp_hyp_atob.rhs
        a3 = temp_hyp_atoc.lhs
        c2 = temp_hyp_atoc.rhs

        if b2 == "" or c2 == "":
            return False

        return a == a2 and a == a3 and b == b2 and c == c2


    @staticmethod
    def is_axiom_3(h):
        # Проверка аксиомы 3: ((A -> F) -> F) -> A
        l = h.lhs
        r = h.rhs
        if r == "":
            return False

        temp_hyp_l = Utils.expand_hypothesis(l)
        atoF = temp_hyp_l.lhs
        f = temp_hyp_l.rhs
        if f != "F":
            return False

        temp_hyp_atoF = Utils.expand_hypothesis(atoF)
        a = temp_hyp_atoF.lhs
        f = temp_hyp_atoF.rhs
        if f != "F":
            return False

        return a == r


    @staticmethod
    def is_axiom_4(h):
        # Проверка аксиомы 4: A -> ((A -> F) -> F)
        l = h.lhs
        r = h.rhs
        if r == "":
            return False

        temp_hyp_r = Utils.expand_hypothesis(r)
        atoF = temp_hyp_r.lhs
        f = temp_hyp_r.rhs
        if f != "F":
            return False

        temp_hyp_atoF = Utils.expand_hypothesis(atoF)
        a = temp_hyp_atoF.lhs
        f = temp_hyp_atoF.rhs
        if f != "F":
            return False

        return a == l



def main():
    thmp = ThmParser()
    rapp = RuleApplier("(A->B)->(~B->~A)", 0)
    print('-------------------------------------')
    rapp.check_rule(Utils.expand_hypothesis("p->(q->p)"))

if __name__ == "__main__":
    main()
