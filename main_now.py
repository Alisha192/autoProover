from prover import *
class InvalidInputError(Exception):
  def __init__(self, message):
    self.message = message

def lex(inp):
  # perform a lexical analysis
  tokens = []
  pos = 0
  while pos < len(inp):
    # skip whitespace
    if inp[pos] == ' ':
      pos += 1
      continue

    # identifiers
    identifier = ''
    while pos < len(inp) and inp[pos].isalnum():
      identifier += inp[pos]
      pos += 1
    if len(identifier) > 0:
      tokens.append(identifier)
      continue

    # symbols
    tokens.append(inp[pos])
    pos += 1

  # return the tokens
  return tokens

def parse(tokens):
  # keywords
  keywords = ['!', '>', '|', '*', '+']
  tokens = [(token.lower() if token in keywords else token)
    for token in tokens]

  # empty formula
  if len(tokens) == 0:
    raise InvalidInputError('Empty formula.')

  # XOR
  xor_pos = None
  depth = 0
  for i in range(len(tokens)):
    if tokens[i] == '(':
      depth += 1
      continue
    if tokens[i] == ')':
      depth -= 1
      continue
    if depth == 0 and tokens[i] == '+':  # Символ для XOR
      xor_pos = i
      break
  if xor_pos is not None:
    if xor_pos == 0 or xor_pos == len(tokens) - 1:
      raise InvalidInputError('Missing formula in XOR connective.')
    return XOR(parse(tokens[0:xor_pos]), parse(tokens[xor_pos + 1:])).to_implication()

  # Эквиваленция
  equiv_pos = None
  depth = 0
  for i in range(len(tokens)):
    if tokens[i] == '(':
      depth += 1
      continue
    if tokens[i] == ')':
      depth -= 1
      continue
    if depth == 0 and tokens[i] == '=':  # Символ для Эквиваленции
      equiv_pos = i
      break
  if equiv_pos is not None:
    if equiv_pos == 0 or equiv_pos == len(tokens) - 1:
      raise InvalidInputError('Missing formula in EQUIVALENCE connective.')
    return Equivalence(parse(tokens[0:equiv_pos]), parse(tokens[equiv_pos + 1:])).to_implication()


  # Implies
  implies_pos = None
  depth = 0
  for i in range(len(tokens)):
    if tokens[i] == '(':
      depth += 1
      continue
    if tokens[i] == ')':
      depth -= 1
      continue
    if depth == 0 and tokens[i] == '>':
      implies_pos = i
      break
  if implies_pos is not None:
    quantifier_in_left = False
    depth = 0
    for i in range(implies_pos):
      if tokens[i] == '(':
        depth += 1
        continue
      if tokens[i] == ')':
        depth -= 1
        continue

    if not quantifier_in_left:
      if implies_pos == 0 or implies_pos == len(tokens) - 1:
        raise InvalidInputError('Missing formula in IMPLIES connective.')
      return Implies(parse(tokens[0:implies_pos]),
        parse(tokens[implies_pos+1:]))

  # Or
  or_pos = None
  depth = 0
  for i in range(len(tokens)):
    if tokens[i] == '(':
      depth += 1
      continue
    if tokens[i] == ')':
      depth -= 1
      continue
    if depth == 0 and tokens[i] == '*':
      or_pos = i
      break
  if or_pos is not None:
    quantifier_in_left = False
    depth = 0
    for i in range(or_pos):
      if tokens[i] == '(':
        depth += 1
        continue
      if tokens[i] == ')':
        depth -= 1
        continue
    if not quantifier_in_left:
      if or_pos == 0 or or_pos == len(tokens) - 1:
        raise InvalidInputError('Missing formula in OR connective.')
      return Or(parse(tokens[0:or_pos]), parse(tokens[or_pos+1:]))

  # And
  and_pos = None
  depth = 0
  for i in range(len(tokens)):
    if tokens[i] == '(':
      depth += 1
      continue
    if tokens[i] == ')':
      depth -= 1
      continue
    if depth == 0 and tokens[i] == '|':
      and_pos = i
      break
  if and_pos is not None:
    quantifier_in_left = False
    depth = 0
    for i in range(and_pos):
      if tokens[i] == '(':
        depth += 1
        continue
      if tokens[i] == ')':
        depth -= 1
        continue

    if not quantifier_in_left:
      if and_pos == 0 or and_pos == len(tokens) - 1:
        raise InvalidInputError('Missing formula in AND connective.')
      return And(parse(tokens[0:and_pos]), parse(tokens[and_pos+1:])).to_implication()

  # Not
  if tokens[0] == '!':
    if len(tokens) < 2:
      raise InvalidInputError('Missing formula in NOT connective.')
    return Not(parse(tokens[1:]))

  # Function
  if tokens[0].isalnum() and tokens[0].lower() not in keywords and \
    len(tokens) > 1 and not any([c.isupper() for c in tokens[0]]) and \
    tokens[1] == '(':
    if tokens[-1] != ')':
      raise InvalidInputError('Missing \')\' after function argument list.')
    name = tokens[0]
    args = []
    i = 2
    if i < len(tokens) - 1:
      while i <= len(tokens) - 1:
        end = len(tokens) - 1
        depth = 0
        for j in range(i, len(tokens) - 1):
          if tokens[j] == '(':
            depth += 1
            continue
          if tokens[j] == ')':
            depth -= 1
            continue
          if depth == 0 and tokens[j] == ',':
            end = j
            break
        if i == end:
          raise InvalidInputError('Missing function argument.')
        args.append(parse(tokens[i:end]))
        i = end + 1
    return Function(name, args)

  # Predicate
  if tokens[0].isalnum() and tokens[0].lower() not in keywords and \
    len(tokens) == 1 and any([c.isupper() for c in tokens[0]]):
    return Predicate(tokens[0], [])
  if tokens[0].isalnum() and tokens[0].lower() not in keywords and \
    len(tokens) > 1 and any([c.isupper() for c in tokens[0]]) and \
    tokens[1] == '(':
    if tokens[-1] != ')':
      raise InvalidInputError('Missing \')\' after predicate argument list.')
    name = tokens[0]
    args = []
    i = 2
    if i < len(tokens) - 1:
      while i <= len(tokens) - 1:
        end = len(tokens) - 1
        depth = 0
        for j in range(i, len(tokens) - 1):
          if tokens[j] == '(':
            depth += 1
            continue
          if tokens[j] == ')':
            depth -= 1
            continue
          if depth == 0 and tokens[j] == ',':
            end = j
            break
        if i == end:
          raise InvalidInputError('Missing predicate argument.')
        args.append(parse(tokens[i:end]))
        i = end + 1
    return Predicate(name, args)

  # Variable
  if tokens[0].isalnum() and tokens[0].lower() not in keywords and \
    len(tokens) == 1 and not any([c.isupper() for c in tokens[0]]):
    return Variable(tokens[0])

  if tokens[0] == '(':
    if tokens[-1] != ')':
      raise InvalidInputError('Missing \')\'.')
    if len(tokens) == 2:
      raise InvalidInputError('Missing formula in parenthetical group.')
    return parse(tokens[1:-1])

  raise InvalidInputError('Unable to parse: %s...' % tokens[0])


def typecheck_term(term):
  if isinstance(term, Variable):
    return
  if isinstance(term, Function):
    for subterm in term.terms:
      typecheck_term(subterm)
    return
  raise InvalidInputError('Invalid term: %s.' % term)

def typecheck_formula(formula):
  if isinstance(formula, Predicate):
    for term in formula.terms:
      typecheck_term(term)
    return
  if isinstance(formula, Not):
    typecheck_formula(formula.formula)
    return
  if isinstance(formula, And):
    typecheck_formula(formula.formula_a)
    typecheck_formula(formula.formula_b)
    return
  if isinstance(formula, Or):
    typecheck_formula(formula.formula_a)
    typecheck_formula(formula.formula_b)
    return
  if isinstance(formula, Implies):
    typecheck_formula(formula.formula_a)
    typecheck_formula(formula.formula_b)
    return

  raise InvalidInputError('Invalid formula: %s.' % formula)

def check_formula(formula):
  try:
    typecheck_formula(formula)
  except InvalidInputError as formula_error:
    try:
      typecheck_term(formula)
    except InvalidInputError as term_error:
      raise formula_error
    else:
      raise InvalidInputError('Enter a formula, not a term.')

def main():

  print('  axioms              (list axioms)')
  print('  lemmas              (list lemmas)')
  print('  axiom <formula>     (add an axiom)')
  print('  lemma <formula>     (prove and add a lemma)')
  print('  remove <formula>    (remove an axiom or lemma)')
  print('  reset               (remove all axioms and lemmas)')

  axioms = set()
  lemmas = {}

  while True:
    try:
      inp = input('\n> ')
      commands = ['axiom', 'lemma', 'axioms', 'lemmas', 'remove', 'reset']
      tokens = [(token.lower() if token in commands else token)
        for token in lex(inp)]
      for token in tokens[1:]:
        if token in commands:
          raise InvalidInputError('Unexpected keyword: %s.' % token)
      if len(tokens) > 0 and tokens[0] == 'axioms':
        if len(tokens) > 1:
          raise InvalidInputError('Unexpected: %s.' % tokens[1])
        for axiom in axioms:
          print(axiom)
      elif len(tokens) > 0 and tokens[0] == 'lemmas':
        if len(tokens) > 1:
          raise InvalidInputError('Unexpected: %s.' % tokens[1])
        for lemma in lemmas:
          print(lemma)
      elif len(tokens) > 0 and tokens[0] == 'axiom':
        formula = parse(tokens[1:])
        check_formula(formula)
        axioms.add(formula)
        print('Axiom added: %s.' % formula)
      elif len(tokens) > 0 and tokens[0] == 'lemma':
        formula = parse(tokens[1:])
        check_formula(formula)
        result, time = proveFormula(axioms | set(lemmas.keys()), formula)
        if result:
          lemmas[formula] = axioms.copy()
          print(f'Lemma proven: {formula} for {time}')
        else:
          print('Lemma unprovable: %s.' % formula)
      elif len(tokens) > 0 and tokens[0] == 'remove':
        formula = parse(tokens[1:])
        check_formula(formula)
        if formula in axioms:
          axioms.remove(formula)
          bad_lemmas = []
          for lemma, dependent_axioms in lemmas.items():
            if formula in dependent_axioms:
              bad_lemmas.append(lemma)
          for lemma in bad_lemmas:
            del lemmas[lemma]
          print('Axiom removed: %s.' % formula)
          if len(bad_lemmas) == 1:
            print('This lemma was proven using that ' \
              'axiom and was also removed:')
            for lemma in bad_lemmas:
              print('  %s' % lemma)
          if len(bad_lemmas) > 1:
            print('These lemmas were proven using that ' \
              'axiom and were also removed:')
            for lemma in bad_lemmas:
              print('  %s' % lemma)
        elif formula in lemmas:
          del lemmas[formula]
          print('Lemma removed: %s.' % formula)
        else:
          print('Not an axiom: %s.' % formula)
      elif len(tokens) > 0 and tokens[0] == 'reset':
        if len(tokens) > 1:
          raise InvalidInputError('Unexpected: %s.' % tokens[1])
        axioms = set()
        lemmas = {}
      else:
        formula = parse(tokens)
        check_formula(formula)
        result, time = proveFormula(axioms | set(lemmas.keys()), formula)
        if result:
          print(f'Formula proven: {formula} for {time}')
        else:
          print('Formula unprovable: %s.' % formula)
    except InvalidInputError as e:
      print(e.message)
    except KeyboardInterrupt:
      pass
    except EOFError:
      print('')
      break

if __name__ == '__main__':
  main()
