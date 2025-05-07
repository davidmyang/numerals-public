import subprocess
import pandas as pd

# Paths to the other scripts
GENERATION_SCRIPT = "src/artificial_language_generation.py"
HURFORD_GRAMMAR_SCRIPT = "src/hurford_grammar.py"
COMPLEXITY_ANALYSIS_SCRIPT = "src/complexity_analysis.py"

# Number of generations (100)
NUM_GENERATIONS = 100

# Artificial language files
OUTPUT_DIR = "data"
ARTIFICIAL_LANGUAGE_FILE = f"{OUTPUT_DIR}/artificial_language_grammars.csv"
REV_PL_ART_LANG_FILE = f"{OUTPUT_DIR}/rev_pl_artificial_language_grammars.csv"
UNI_ART_LANG_FILE = f"{OUTPUT_DIR}/uniform_artificial_language_grammars.csv"

HURFORD_OUTPUT_FILE = f"{OUTPUT_DIR}/language_specific_constructions.csv"
COMPLEXITY_OUTPUT_FILE = f"{OUTPUT_DIR}/language_analysis.csv"

def run_script(script, *args):
    """Run a Python script with optional arguments."""
    command = ["python", script] + list(args)
    subprocess.run(command, check=True)

def is_more_optimal(lang1, lang2):
    """Determine if lang1 is more optimal than lang2 based on defined criteria."""
    size1, size2 = lang1['lexicon'], lang2['lexicon']
    complexity1, complexity2 = lang1['avg_ms_complexity'], lang2['avg_ms_complexity']
    grammar1, grammar2 = lang1['grammar'], lang2['grammar']

    # Grammar dimension is not used in final paper.
    # if grammar1 != grammar2:
    #     return False
    if complexity1 < complexity2 and size1 == size2:
        return True
    if size1 < size2 and complexity1 == complexity2:
        return True
    return False

def select_optimal_languages(languages_df):
    """Select the most optimal languages from the population using a DataFrame."""
    optimal_languages = []
    seen_criteria = set()

    for index, lang in languages_df.iterrows():
        # Skip if already seen this combination
        # criteria = (lang['lexicon'], lang['avg_ms_complexity'], lang['grammar'])
        criteria = (lang['lexicon'], lang['avg_ms_complexity'])
        if criteria in seen_criteria:
            continue

        # Check if the language is optimal
        if all(
            other_index == index or not is_more_optimal(other, lang)  # Skip self-comparison
            for other_index, other in languages_df.iterrows()
        ):
            optimal_languages.append(lang['language'])
            seen_criteria.add(criteria)

    print(optimal_languages)
    return optimal_languages

def keep_optimal_artificial(artificial_grammars, optimal_languages):
    """Filter the artificial grammars to retain only optimal ones."""
    filtered_df = artificial_grammars[artificial_grammars['language'].isin(optimal_languages)]
    return filtered_df

def evolve_population():
    """Perform evolutionary optimization across multiple generations."""
    for generation in range(0, NUM_GENERATIONS):
        print(f"Starting generation {generation}...")

        # Step 1: Generate artificial languages
        run_script(GENERATION_SCRIPT, str(generation))
        print(f"Generated artificial languages for generation {generation}.")

        # Step 2: Generate Hurford number constructions
        is_last_gen = generation == NUM_GENERATIONS - 1
        run_script(HURFORD_GRAMMAR_SCRIPT, str(is_last_gen))
        print(f"Generated Hurford number constructions for generation {generation}.")

        # Step 3: Perform complexity analysis and select optimal languages
        run_script(COMPLEXITY_ANALYSIS_SCRIPT)
        print(f"Performed complexity analysis for generation {generation}.")

        # Read optimal languages from the output file
        language_complexities = pd.read_csv(COMPLEXITY_OUTPUT_FILE)
        language_complexities['is_artificial'] = language_complexities['language'].str.startswith('artificial_language')

        # Separate data for plotting
        artificial_languages = language_complexities[language_complexities['is_artificial']]
        optimal_languages = select_optimal_languages(artificial_languages)
        artificial_language_grammars = pd.read_csv(ARTIFICIAL_LANGUAGE_FILE)

        artificial_language_grammars = keep_optimal_artificial(artificial_language_grammars, optimal_languages)
        print(artificial_language_grammars)
        artificial_language_grammars.to_csv(ARTIFICIAL_LANGUAGE_FILE, index=False)
        

def main():
    evolve_population()

if __name__ == "__main__":
    main()
