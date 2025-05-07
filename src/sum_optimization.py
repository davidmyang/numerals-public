import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import minimize

ANALYSIS_FILE = "data/language_analysis.csv"

df = pd.read_csv(ANALYSIS_FILE)

# Determine categories based on file structure
natural_languages = df[df['type'] != 'artificial']

MEAN_MS_COMPLEXITY = sum(natural_languages['avg_ms_complexity']) / len(natural_languages['avg_ms_complexity'])
MEAN_LEXICON = sum(natural_languages['lexicon']) / len(natural_languages['lexicon'])
LAMBDA = MEAN_MS_COMPLEXITY / MEAN_LEXICON

nat_amsc = natural_languages['avg_ms_complexity'].values
nat_lexicon_size = natural_languages['lexicon'].values

# Objective function to minimize
def objective_function(lambda_val):
    global_min = min(df['avg_ms_complexity'] + lambda_val[0] * df['lexicon'])
    sum_min = sum(nat_amsc + lambda_val[0] * nat_lexicon_size - global_min)
    print(sum_min)
    return sum_min

initial_lambda = [0.0]

# Minimize the objective function
result = minimize(objective_function, initial_lambda)

# Extract the optimal lambda and minimum S(L)
LAMBDA = result.x[0]
min_sum = result.fun

print(f'mean ms complexity: {MEAN_MS_COMPLEXITY}, mean lexicon: {MEAN_LEXICON}, lambda: {LAMBDA}, min_sum: {min_sum}')

# Calculate the 'sum' column
df['sum'] = df['avg_ms_complexity'] + LAMBDA * df['lexicon'] 
natural_languages = df[df['type'] != 'artificial']
optimal_start_idx = df[df['type'] == 'artificial'].index[0]
first_gen_indices = df[df['language'] == 'artificial_language_g0_0'].index
first_gen_start_idx = first_gen_indices[1] if len(first_gen_indices) > 1 else first_gen_indices[0]

optimal_art_langs = df.iloc[optimal_start_idx:first_gen_start_idx]
first_gen_art_langs = df.iloc[first_gen_start_idx:]

# Plot histograms
fig, axes = plt.subplots(1, 1, figsize=(6, 3))

sns.histplot(
    natural_languages['sum'], 
    binwidth=.02, 
    color='red', 
    label='Natural Languages', 
    kde=False, 
    alpha=0.7,
    element="step",
    ax=axes
)
sns.histplot(
    first_gen_art_langs['sum'], 
    binwidth=.02, 
    color='grey', 
    label='First Gen. Artificial Languages', 
    kde=False, 
    alpha=0.5,
    element="step",
    ax=axes
)
sns.histplot(
    optimal_art_langs['sum'], 
    binwidth=.02, 
    color='black', 
    label='Optimal Artificial Languages', 
    kde=False, 
    alpha=0.5,
    element="step",
    ax=axes
)
axes.set_xlabel("Sum")
axes.set_ylabel("Frequency")
axes.legend()
plt.tight_layout()

fig.savefig('images/sum_plots.png', dpi=1200)
plt.show()
