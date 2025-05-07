import pandas as pd

OUTPUT_DIR = "data"
NATURAL_GRAMMAR_PATH = f"{OUTPUT_DIR}/natural_language_grammars.csv"
ARTIFICIAL_LANGUAGE_FILE = f"{OUTPUT_DIR}/artificial_language_grammars.csv"
REV_PL_ART_LANG_FILE = f"{OUTPUT_DIR}/rev_pl_artificial_language_grammars.csv"
UNI_ART_LANG_FILE = f"{OUTPUT_DIR}/uniform_artificial_language_grammars.csv"

REV_PL_FIRST_GEN_ART_LANG_FILE = f"{OUTPUT_DIR}/rev_pl_first_gen_artificial_language_grammars.csv"
UNI_FIRST_GEN_ART_LANG_FILE = f"{OUTPUT_DIR}/uni_first_gen_artificial_language_grammars.csv"
FIRST_GEN_ART_LANG_FILE = f"{OUTPUT_DIR}/first_gen_artificial_language_grammars.csv"

CONSTRUCTION_PATH = f"{OUTPUT_DIR}/language_specific_constructions.csv"

# Change this to whichever file you want the complexity calculations to go
COMPLEXITY_OUTPUT_FILE = f"{OUTPUT_DIR}/language_analysis.csv" 

prior_power_sum = 0
for i in range(1,100):
  prior_power_sum += i**(-2)

def calculate_lexicon(digits, bases, monomorphemics):
    lexicon_size = len(digits) + len(bases) + len(monomorphemics)
    return lexicon_size

# NOTE: The grammar size calculation is not finalized or used in the final paper.
def calculate_grammar(curr_bases, num_addition, num_subtraction, phrase_subtraction, exceptions):
    def base_addition_diff():
        diff = 0
        n = min(len(curr_bases), len(num_addition))
        for i in range(n):
            if curr_bases[i] != num_addition[i]:
                diff += 1
        diff += abs(len(curr_bases) - len(num_addition))
        return diff
    
    grammar_size = 0
    #grammar_size += len(num_subtraction)
    grammar_size += len(exceptions)
    #grammar_size += 1 if len(curr_bases) > 0 else 0
    #grammar_size += 1 if len(num_addition) > 0 else 0
    grammar_size += 1 if len(num_subtraction) > 0 else 0

    grammar_size += base_addition_diff()

    # for exception in exceptions:
    #     #if "[1, 100]" not in str(exception):
    #         grammar_size += 1
    return grammar_size

# Function to calculate the average morphosyntactic complexity
def calculate_avg_ms_complexity(constructions):
    def probaf(number):
        return (number**(-2)) / prior_power_sum
    def rev_probaf(number):
        return ((100 - number)**(-2)) / prior_power_sum
    def uni_probaf(number):
        return 1.0 / 99.0
    
    constructions_list = constructions.tolist()
    total = 0
    for i in range(len(constructions_list)):
        total += len(str(constructions_list[i]).split()) * probaf(i + 1)
        #total += len(str(constructions_list[i]).split()) * rev_probaf(i + 1)
        #total += len(str(constructions_list[i]).split()) * uni_probaf(i + 1)
    return total

def main():
    # Read language-specifics from file
    natural_language_grammars = pd.read_csv(NATURAL_GRAMMAR_PATH)
    artificial_language_grammars = pd.read_csv(ARTIFICIAL_LANGUAGE_FILE)
    first_gen_language_grammars = pd.read_csv(FIRST_GEN_ART_LANG_FILE)
    all_language_constructions = pd.read_csv(CONSTRUCTION_PATH)

    language_analysis = pd.DataFrame(columns=['language', 'type', 'lexicon', 'grammar', 'lexicon_grammar', 'avg_ms_complexity'])

    
    nrows = natural_language_grammars.shape[0]
    for i in range(nrows):
        language = natural_language_grammars.iloc[i]
        
        # Read each column
        name = language['language']
        type = language['type']

        # Lexicon
        digits = set(eval(language['digits']))
        bases = set(eval(language['bases']))
        monomorphemics = set(eval(language['monomorphemics']))

        # Grammar
        curr_bases = eval(language['curr_bases'])
        num_addition = eval(language['number_addition_max'])
        num_subtraction = eval(language['number_subtraction_max'])
        phrase_subtraction = eval(language['phrase_subtraction'])
        exceptions = eval(language['exceptions'])

        lexicon_size = calculate_lexicon(digits, bases, monomorphemics)
        grammar_size = calculate_grammar(curr_bases, num_addition, num_subtraction, phrase_subtraction, exceptions)
        language_analysis = pd.concat([language_analysis, pd.DataFrame([[name, type, lexicon_size, grammar_size, lexicon_size + grammar_size, 0]], 
                                                columns=language_analysis.columns)], ignore_index=True)
    
    nrows = artificial_language_grammars.shape[0]
    for i in range(nrows):
        language = artificial_language_grammars.iloc[i]
        
        # Read each column
        name = language['language']

        # Lexicon
        digits = set(eval(language['digits']))
        bases = set(eval(language['bases']))
        monomorphemics = set(eval(language['monomorphemics']))

        # Grammar
        curr_bases = eval(language['curr_bases'])
        num_addition = eval(language['number_addition_max'])
        num_subtraction = eval(language['number_subtraction_max'])
        phrase_subtraction = eval(language['phrase_subtraction'])
        exceptions = eval(language['exceptions'])

        lexicon_size = calculate_lexicon(digits, bases, monomorphemics)
        grammar_size = calculate_grammar(curr_bases, num_addition, num_subtraction, phrase_subtraction, exceptions)
        language_analysis = pd.concat([language_analysis, pd.DataFrame([[name, 'artificial', lexicon_size, grammar_size, lexicon_size + grammar_size, 0]], 
                                                columns=language_analysis.columns)], ignore_index=True)
    
    nrows = first_gen_language_grammars.shape[0]
    for i in range(nrows):
        language = first_gen_language_grammars.iloc[i]
        
        # Read each column
        name = language['language']
        
        # Lexicon
        digits = set(eval(language['digits']))
        bases = set(eval(language['bases']))
        monomorphemics = set(eval(language['monomorphemics']))

        # Grammar
        curr_bases = eval(language['curr_bases'])
        num_addition = eval(language['number_addition_max'])
        num_subtraction = eval(language['number_subtraction_max'])
        phrase_subtraction = eval(language['phrase_subtraction'])
        exceptions = eval(language['exceptions'])

        lexicon_size = calculate_lexicon(digits, bases, monomorphemics)
        grammar_size = calculate_grammar(curr_bases, num_addition, num_subtraction, phrase_subtraction, exceptions)
        language_analysis = pd.concat([language_analysis, pd.DataFrame([[name, 'artificial', lexicon_size, grammar_size, lexicon_size + grammar_size, 0]], 
                                                columns=language_analysis.columns)], ignore_index=True)
    
    for language, group in all_language_constructions.groupby('language'):
    # Split the group into chunks of 99 rows
        for i in range(0, len(group), 99):
            chunk = group.iloc[i:i + 99]
            avg_ms_complexity = calculate_avg_ms_complexity(chunk['constructions'])
            language_analysis.loc[language_analysis['language'] == language, 'avg_ms_complexity'] = avg_ms_complexity
    
    language_analysis.to_csv(COMPLEXITY_OUTPUT_FILE, index=False)

if __name__ == "__main__":
    main()