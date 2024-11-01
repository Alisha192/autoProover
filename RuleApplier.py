class RuleApplier:
    def __init__(self, r, rno):
        temp_hyp = Utils.expandHypothesis(Utils.expandAll(r))
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
            Utils.printHypothesis(hyp2)
            new_hypos.append(hyp2)

        return new_hypos

    def apply_rule(self, hyp, hyp_rhs, ruleexp, hyp_exp):
    lhs_rule_pos = 0
    len_lhs_rule = len(ruleexp)
    len_hyp = len(hyp)
    pos = 0
    variables = {}  # Используется для хранения переменных

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
                    exp = variables.get(rule_char)
                    if exp is None:
                        variables[rule_char] = hyp[pos:pos_end + 1]
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

    variables.clear()
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
    rapp.checkRule(Utils.expand_hypothesis("p->q"))

if __name__ == "__main__":
    main()

