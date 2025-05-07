import random
import pandas as pd
import sys
import copy

# Max number of digits, bases, and monomorphemics for an artificial language
MAX_DIGITS = 20
MAX_NUM_BASES = 5
MAX_MONOMORPHEMICS = 5

# Max number of exceptions for an artificial language
MAX_EXCEPTIONS = 5

# Number of artificial languages to create per generation (1st: 300, others: 50)
FIRST_GEN_NUM_LANGUAGES = 300
NEXT_GEN_NUM_LANGUAGES = 50

OUTPUT_DIR = "data"

# Artificial language files
ARTIFICIAL_LANGUAGE_FILE = f"{OUTPUT_DIR}/artificial_language_grammars.csv"
REV_PL_ART_LANG_FILE = f"{OUTPUT_DIR}/rev_pl_artificial_language_grammars.csv"
UNI_ART_LANG_FILE = f"{OUTPUT_DIR}/uniform_artificial_language_grammars.csv"

# First generation artificial language files
FIRST_GEN_ART_LANG_FILE = f"{OUTPUT_DIR}/first_gen_artificial_language_grammars.csv"
REV_PL_FIRST_GEN_ART_LANG_FILE = f"{OUTPUT_DIR}/rev_pl_first_gen_artificial_language_grammars.csv"
UNI_FIRST_GEN_ART_LANG_FILE = f"{OUTPUT_DIR}/uni_first_gen_artificial_language_grammars.csv"

def generate_digits():
    num = random.randint(1, MAX_DIGITS)
    digits = list(range(1, num + 1))
    return digits

def generate_bases(digits):
    # Must include number after last digit as a base, otherwise, impossible to construct 
    # all numbers in range (without subtraction)
    bases = [digits[-1] + 1]
    numbers = list(range(1, 100))
    numbers = [x for x in numbers if x not in digits]
    num = random.randint(0, MAX_NUM_BASES - 1)
    for i in range(num):
        numbers = [x for x in numbers if x not in bases]
        base = random.choice(numbers)
        bases.append(base)
    return sorted(bases)

def generate_monomorphemics(digits, bases):
    monomorphemics = []
    num = random.randint(0, MAX_MONOMORPHEMICS)
    numbers = list(range(1, 100))
    numbers = [x for x in numbers if x not in digits]
    numbers = [x for x in numbers if x not in bases]
    monomorphemics = random.sample(numbers, num)
    return sorted(monomorphemics)

def generate_multiplication_rule(bases):
    multiplication_rule = []

    for i in range(1, len(bases)):
        multiplication_rule.append([[bases[i-1], bases[i]], bases[i-1]])
    
    multiplication_rule.append([[bases[-1], 100], bases[-1]])    
    return multiplication_rule

def generate_add_sub_rule(digits, bases, addition_rule):
    subtraction_rule = []
    max_sub = random.choice(digits) + 1
    subtraction_rule.append([[bases[0], bases[1]], max_sub])

    max_add = bases[0] - max_sub + 1
    addition_rule[0] = [[bases[0], bases[1]], max_add]

    return addition_rule, subtraction_rule

def update_bases(bases):
    first_base = bases[0]
    new_bases = [first_base, first_base * 2]
    for i in bases:
        if i > first_base * 2:
            new_bases.append(i)
    if len(new_bases) > MAX_NUM_BASES:
        new_bases.pop()
    return new_bases

def generate_exceptions(digits, bases):
    exceptions = []
    num_exceptions = random.randint(1, len(bases))
    for i in range(num_exceptions):
        if i < len(bases) - 1:
            exceptions.append([bases[i], [bases[i], bases[i + 1]], f'(1 * {bases[i]})'])
        else:
            exceptions.append([bases[i], [bases[i], bases[i] + 1], f'(1 * {bases[i]})'])
    return exceptions

def has_rule(probability):
  """Flips a coin that lands on heads 30% of the time."""
  if random.random() < probability:
    return True
  else:
    return False
  
def mutate_digits(digits, bases, number_addition_maxs, number_subtraction_maxs, exceptions):
    """
    Possible mutations:
    1. Delete last digit (if more than 1)
    2. Add a new digit (if less than MAX_DIGITS)
    Must update bases, curr_bases, number_addition_maxs, and potentially number_subtraction_maxs
    """
    
    mutation_subtype = random.randint(0, 1)
    if len(digits) == 1:
        mutation_subtype = 1
    if len(digits) == MAX_DIGITS:
        mutation_subtype = 0
    
    if mutation_subtype == 0:
        removed_digit = digits.pop()
        # replaced_base = bases[0]
        bases[0] = removed_digit
        if number_subtraction_maxs:
            bases[1] = removed_digit * 2
        curr_bases = generate_multiplication_rule(bases) 
        new_number_addition_maxs = copy.deepcopy(curr_bases)
        
        if number_subtraction_maxs:
            if number_subtraction_maxs[0][1] == removed_digit + 1:
                new_number_addition_maxs[0] = [[bases[0], bases[1]], 1]
                number_subtraction_maxs[0] = [[bases[0], bases[1]], removed_digit]
            else:
                new_number_addition_maxs[0] = [[bases[0], bases[1]], number_addition_maxs[0][1]]
                number_subtraction_maxs[0] = [[bases[0], bases[1]], number_subtraction_maxs[0][1] - 1]
        
        if exceptions:
            exceptions = generate_exceptions(digits, bases)
    else:                  
        added_digit = digits[-1] + 1
        digits.append(added_digit)
        # replaced_base = bases[0]
        bases[0] = added_digit + 1
        if len(bases) > 1 and bases[1] == bases[0]:
            bases.pop(1)
        if number_subtraction_maxs:
            bases[1] = bases[0] * 2
            if len(bases) > 2 and bases[2] <= bases[1]:
                bases.pop(2)
        curr_bases = generate_multiplication_rule(bases) 
        new_number_addition_maxs = copy.deepcopy(curr_bases)
        
        if number_subtraction_maxs:
            if number_subtraction_maxs[0][1] == added_digit:
                new_number_addition_maxs[0] = [[bases[0], bases[1]], 1]
                number_subtraction_maxs[0] = [[bases[0], bases[1]], added_digit + 1]
            else:
                new_number_addition_maxs[0] = [[bases[0], bases[1]], number_addition_maxs[0][1] + 1]
                number_subtraction_maxs[0][0] = [bases[0], bases[1]]
        if exceptions:
            exceptions = generate_exceptions(digits, bases)

    return digits, bases, curr_bases, new_number_addition_maxs, number_subtraction_maxs, exceptions
    
def mutate_bases(digits, bases, monomorphemic, curr_bases, number_addition_maxs, number_subtraction_maxs, exceptions):
    """
    Possible mutations:
    1. Delete base (if more than 1)
    2. Change a base
    3. Add a base (if less than MAX_BASES)
    Must update bases, curr_bases, number_addition_maxs, and potentially number_subtraction_maxs
    """
    mutation_subtype = random.randint(0, 2)
    if len(bases) == 1:
        mutation_subtype = 2
    if len(bases) >= MAX_NUM_BASES:
        mutation_subtype = random.randint(0, 1)
    if number_subtraction_maxs and len(bases) == 2:
        mutation_subtype = 2
    if mutation_subtype == 0:
        pop_index = random.randint(1, len(bases) - 1) # randomly remove any base except first (since it is right after last digit)
        if number_subtraction_maxs:
            pop_index = random.randint(2, len(bases) - 1) # randomly remove any base except first two (second one is required if subtraction)
        # popped_base = bases.pop(pop_index)
        curr_bases = generate_multiplication_rule(bases)
        new_number_addition_maxs = copy.deepcopy(curr_bases)
        if number_subtraction_maxs:
            new_number_addition_maxs[0][1] = number_addition_maxs[0][1]
        if exceptions:
            exceptions = generate_exceptions(digits, bases)
  
    elif mutation_subtype == 1:
        numbers = list(range(1, 100))
        numbers = [x for x in numbers if x not in digits]
        numbers = [x for x in numbers if x not in bases]
        numbers = [x for x in numbers if x not in monomorphemic]
        new_base = random.choice(numbers)
        change_index = random.randint(1, len(bases) - 1) # randomly remove any base except first (since it is right after last digit)
        if number_subtraction_maxs:
            change_index = random.randint(2, len(bases) - 1) # randomly remove any base except first two (second one is required for subtraction)
        # replaced_base = bases[change_index]
        bases[change_index] = new_base
        bases.sort()
        curr_bases = generate_multiplication_rule(bases)
        new_number_addition_maxs = copy.deepcopy(curr_bases)
        if number_subtraction_maxs:
            new_number_addition_maxs[0][1] = number_addition_maxs[0][1]
        if exceptions:
            exceptions = generate_exceptions(digits, bases)

    else:
        numbers = list(range(1, 100))
        if number_subtraction_maxs:
            numbers = list(range(bases[1] + 1, 100))
        numbers = [x for x in numbers if x not in digits]
        numbers = [x for x in numbers if x not in bases]
        numbers = [x for x in numbers if x not in monomorphemic]
        new_base = random.choice(numbers)
        bases.append(new_base)
        bases.sort()
        curr_bases = generate_multiplication_rule(bases)
        new_number_addition_maxs = copy.deepcopy(curr_bases)
        if number_subtraction_maxs:
            new_number_addition_maxs[0][1] = number_addition_maxs[0][1]
        if exceptions:
            exceptions = generate_exceptions(digits, bases)
                    
    return digits, bases, monomorphemic, curr_bases, new_number_addition_maxs, number_subtraction_maxs, exceptions

def mutate_monomorphemics(digits, bases, monomorphemic):
    """
    Possible mutations:
    1. Delete monomorphemic (if more than 0)
    2. Change a monomorphemic
    3. Add a monomorphemic (if less than MAX_MONOMORPHEMCIS)
    Must update monomorphemics
    """
    mutation_subtype = random.randint(0, 2)
    if len(monomorphemic) == 0:
        mutation_subtype = 2
    if len(monomorphemic) == MAX_MONOMORPHEMICS:
        mutation_subtype = random.randint(0, 1)
    
    if mutation_subtype == 0:
        remove_value = random.choice(monomorphemic)
        monomorphemic.remove(remove_value)
    elif mutation_subtype == 1:
        change_index = random.randint(0, len(monomorphemic) - 1)
        numbers = list(range(1, 100))
        numbers = [x for x in numbers if x not in digits]
        numbers = [x for x in numbers if x not in bases]
        numbers = [x for x in numbers if x not in monomorphemic]
        new_monomorphemic = random.choice(numbers)
        monomorphemic[change_index] = new_monomorphemic
        monomorphemic.sort()
    else:
        numbers = list(range(1, 100))
        numbers = [x for x in numbers if x not in digits]
        numbers = [x for x in numbers if x not in bases]
        numbers = [x for x in numbers if x not in monomorphemic]
        new_monomorphemic = random.choice(numbers)
        monomorphemic.append(new_monomorphemic)
        monomorphemic.sort()
    return monomorphemic

def mutate_exceptions(bases, exceptions):
    """
    Possible mutations:
    1. Delete an exception (if more than 0)
    2. Add an exception
    Must update exceptions
    """
    mutation_subtype = random.randint(0, 1)
    if len(exceptions) == 0:
        mutation_subtype = 1
    if len(exceptions) == len(bases):
        mutation_subtype = 0
    if mutation_subtype == 0:
        remove_index = random.choice(range(len(exceptions)))
        exceptions.pop(remove_index)
    else:
        exception_bases = [exception[0] for exception in exceptions]
        for base in bases:
            if base not in exception_bases:
                index = bases.index(base)
                if index + 1 < len(bases):
                    exceptions.append([bases[index], [bases[index], bases[index + 1]], f'(1 * {bases[index]})'])
                else:
                    exceptions.append([bases[index], [bases[index], bases[index] + 1], f'(1 * {bases[index]})'])
    
    return exceptions

def mutate(generation, language, language_grammars):
    """Mutate the artificial language.
       Possible mutations:
       1. Editing digits (delete, add)
       2. Editing bases (delete, change, add)
       3. Editing monomorphemics (delete, change, add)
       4. Editing exceptions constraint (delete, change, add)
    """
    mutation_type = random.randint(0, 3)
    name = language['language']
    digits = eval(language['digits'])
    bases = eval(language['bases'])
    monomorphemic = eval(language['monomorphemics'])
    curr_bases = eval(language['curr_bases'])
    number_addition_maxs = eval(language['number_addition_max'])
    number_subtraction_maxs = eval(language['number_subtraction_max'])
    exceptions = eval(language['exceptions'])

    if mutation_type == 0:
        digits, bases, curr_bases, number_addition_maxs, number_subtraction_maxs, exceptions = mutate_digits(digits, bases, number_addition_maxs, number_subtraction_maxs, exceptions)
    elif mutation_type == 1:
        digits, bases, monomorphemic, curr_bases, number_addition_maxs, number_subtraction_maxs, exceptions = mutate_bases(digits, bases, monomorphemic, curr_bases, number_addition_maxs, number_subtraction_maxs, exceptions)
    elif mutation_type == 2:
        monomorphemic = mutate_monomorphemics(digits, bases, monomorphemic)
    elif mutation_type == 3:
        exceptions = mutate_exceptions(bases, exceptions)

    name = f"{name}_m{generation}"
    new_row = pd.DataFrame([[name, digits, bases, monomorphemic, curr_bases,
                             number_addition_maxs, number_subtraction_maxs, [],
                             exceptions]],
                           columns=language_grammars.columns)
    return new_row

def generate_language(idx, generation, language_grammars):
    name = f"artificial_language_g{generation}_{idx}"
    # Generate lexicon
    digits = generate_digits()
    bases = generate_bases(digits)
    monomorphemics = generate_monomorphemics(digits, bases)

    # Generate grammar rules
    has_subtraction = has_rule(0.3)
    if has_subtraction:
        bases = update_bases(bases)

    multiplication_rule = generate_multiplication_rule(bases)
    addition_rule = copy.deepcopy(multiplication_rule)

    num_sub_rule = []
    if has_subtraction:
        addition_rule, num_sub_rule = generate_add_sub_rule(digits, bases, addition_rule)

    phrase_sub_rule = []
    has_exception = has_rule(0.3)
    exceptions = []
    if has_exception:
        exceptions = generate_exceptions(digits, bases)
    
    new_row = pd.DataFrame([[name, digits, bases, monomorphemics, multiplication_rule,
                             addition_rule, num_sub_rule, phrase_sub_rule,
                             exceptions]],
                           columns=language_grammars.columns)
    language_grammars = pd.concat([language_grammars, new_row], ignore_index=True)
    return language_grammars

def main():
    generation = int(sys.argv[1])
    is_first_gen = not generation
    if is_first_gen:
        language_grammars = pd.DataFrame(columns=["language","digits","bases","monomorphemics","curr_bases","number_addition_max",
                                                "number_subtraction_max","phrase_subtraction","exceptions"])
        for i in range(FIRST_GEN_NUM_LANGUAGES):
            language_grammars = generate_language(i, generation, language_grammars)
        language_grammars.to_csv(FIRST_GEN_ART_LANG_FILE, index=False)
    else:
        language_grammars = pd.read_csv(ARTIFICIAL_LANGUAGE_FILE)
        nrows = language_grammars.shape[0]
        for i in range(nrows):
            language = language_grammars.iloc[i]
            mutated_language = mutate(generation, language, language_grammars)
            language_grammars = pd.concat([language_grammars, mutated_language], ignore_index=True)
        for i in range(NEXT_GEN_NUM_LANGUAGES):
            language_grammars = generate_language(i, generation, language_grammars)

    # Write data to csv file
    language_grammars.to_csv(ARTIFICIAL_LANGUAGE_FILE, index=False)

if __name__ == "__main__":
    main()