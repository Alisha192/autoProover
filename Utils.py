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
class Utils:

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
                newthm = thm[:notpos] + f"({thm[notpos+1:pos+1]}->F)" + thm[pos+1:]
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
                rhs = f"({thm[andpos+1:rhspos+1]}->F)"
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

        newthm = thm[:lhspos] + f"(({lhs}->{rhs})->F)" + thm[rhspos+1:]
        return Utils.expand_and(newthm)
class Utils:

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

    class Utils:

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

    

