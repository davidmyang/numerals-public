import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import ttest_rel, binomtest

# Load data
pl_data = pd.read_csv("data/pl_complexity.csv")
uni_data = pd.read_csv("data/uni_complexity.csv")
rev_data = pd.read_csv("data/rev_complexity.csv")

# Function to calculate distances for a single file
def calculate_distances(df):
    # Separate natural and artificial languages
    natural_langs = df[df['type'] != 'artificial']
    artificial_langs = df[df['type'] == 'artificial']
    
    # Find the optimal artificial language (smallest avg_ms_complexity) for each lexicon size
    optimal_artificial = (
        artificial_langs
        .groupby('lexicon', as_index=False)['avg_ms_complexity']
        .min()
        .rename(columns={'avg_ms_complexity': 'optimal_avg_ms_complexity'})
    )
    
    # Merge the optimal artificial data with natural languages on lexicon size
    merged = natural_langs.merge(optimal_artificial, on='lexicon', how='left')
    
    # Calculate the distance
    merged['distance_to_optimal'] = abs(merged['avg_ms_complexity'] - merged['optimal_avg_ms_complexity'])
    
    # Return the merged DataFrame with distances
    return merged[['language', 'lexicon', 'avg_ms_complexity', 'optimal_avg_ms_complexity', 'distance_to_optimal']]

# Process all files and store results
pl_result = calculate_distances(pl_data)
rev_result = calculate_distances(rev_data)
uni_result = calculate_distances(uni_data)

merged_power_reverse = pl_result.merge(
    rev_result,
    on="language",
    suffixes=("_power", "_reverse")
)

# Perform the t-test
test_power_reverse = ttest_rel(
    merged_power_reverse["distance_to_optimal_power"],
    merged_power_reverse["distance_to_optimal_reverse"], alternative='less'
)

print("Paired t-test: Power-law vs Reverse Power-law")
print(f"t-statistic: {test_power_reverse.statistic:.4f}, p-value: {test_power_reverse.pvalue:.4e}")

# Merge for paired t-test: Power-law vs Uniform
merged_power_uniform = pl_result.merge(
    uni_result,
    on="language",
    suffixes=("_power", "_uniform")
)

# Perform the t-test
test_power_uniform = ttest_rel(
    merged_power_uniform["distance_to_optimal_power"],
    merged_power_uniform["distance_to_optimal_uniform"], alternative='less'
)

print("\nPaired t-test: Power-law vs Uniform")
print(f"t-statistic: {test_power_uniform.statistic:.4f}, p-value: {test_power_uniform.pvalue:.4e}")

# Calculate the signs of the differences
merged_power_uniform['sign'] = (
    merged_power_uniform['distance_to_optimal_power'] < 
    merged_power_uniform['distance_to_optimal_uniform']
)

# Count positives and negatives
uni_positive_signs = merged_power_uniform['sign'].sum()  # Count where Power < Uniform
uni_total_nonzero = merged_power_uniform['sign'].notna().sum()  # Ignore zero differences

# Run a one-sided sign test (testing if positives are more frequent)
uni_sign_test_result = binomtest(uni_positive_signs, uni_total_nonzero, p=0.5, alternative='greater')

print("\n\nNon-parametric Sign Test: Power-law vs Uniform (Power < Uniform)")
print(f"Number of positive signs: {uni_positive_signs}/{uni_total_nonzero}")
print(f"p-value: {uni_sign_test_result.pvalue:.4e}")

# Calculate the signs of the differences
merged_power_reverse['sign'] = (
    merged_power_reverse['distance_to_optimal_power'] < 
    merged_power_reverse['distance_to_optimal_reverse']
)

# Count positives and negatives
rev_positive_signs = merged_power_reverse['sign'].sum()  # Count where Power < Reverese
rev_total_nonzero = merged_power_reverse['sign'].notna().sum()  # Ignore zero differences

# Run a one-sided sign test (testing if positives are more frequent)
rev_sign_test_result = binomtest(rev_positive_signs, rev_total_nonzero, p=0.5, alternative='greater')

print("\nNon-parametric Sign Test: Power-law vs Reverse (Power < Reverse)")
print(f"Number of positive signs: {rev_positive_signs}/{rev_total_nonzero}")
print(f"p-value: {rev_sign_test_result.pvalue:.4e}")

# Set priors
pl_result['prior'] = 'Power-law'
uni_result['prior'] = 'Uniform'
rev_result['prior'] = 'Reverse power-law'

# Loop through each dataset and create a plot
fig, axes = plt.subplots(1, 1, figsize=(6, 4))

combined = pd.concat([pl_result, uni_result, rev_result], axis=0)

# Make Mandarin different color
combined['color'] = combined['language'].apply(lambda x: 'red' if x == 'mandarin' else 'blue')
palette = {'red': 'red', 'blue': '#1f77b4'}

sns.swarmplot(x='prior', y='distance_to_optimal', data=combined, ax=axes, hue='color', palette=palette, size=7, edgecolor='gray', linewidth=1, legend=False)
axes.set_xlabel(None)
axes.set_ylabel('Deviation from optimality (log scale)')
axes.set_ylim(0, 20)
axes.set_yscale('symlog', linthresh=1e-3)

plt.savefig('images/priors_comparison.png', dpi=1000)
plt.show()
