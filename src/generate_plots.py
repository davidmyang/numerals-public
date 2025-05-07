import matplotlib.pyplot as plt
from matplotlib import cm
import pandas as pd

ANALYSIS_PATH = "data/language_analysis.csv"

# Function to calculate Pareto frontier
def calculate_pareto_frontier(df, x_col, y_col):
    df_sorted = df.sort_values(by=x_col).dropna(subset=[x_col, y_col])
    pareto_frontier = [df_sorted.iloc[0]]  # Start with the first row

    # Build the Pareto frontier
    print(df_sorted)
    for _, row in df_sorted.iterrows():
        if row[x_col] != pareto_frontier[-1][x_col]:
            pareto_frontier.append(row)
        if row[y_col] < pareto_frontier[-1][y_col]:  # Minimization on y-axis
            if row[x_col] == pareto_frontier[-1][x_col]:
                pareto_frontier.pop()
            pareto_frontier.append(row)

    # Convert Pareto frontier back to a DataFrame
    pareto_frontier_df = pd.DataFrame(pareto_frontier)

    # Print language names on the Pareto frontier
    print("Languages on the Pareto frontier:")
    print(pareto_frontier_df["language"].tolist())

    # Return Pareto frontier points as a NumPy array
    return pareto_frontier_df[[x_col, y_col]].values

def main():
    df = pd.read_csv(ANALYSIS_PATH)
    
    # Determine categories based on file structure
    natural_languages = df[df['type'] != 'artificial']
    optimal_start_idx = df[df['type'] == 'artificial'].index[0]
    first_gen_indices = df[df['language'] == 'artificial_language_g0_0'].index
    first_gen_start_idx = first_gen_indices[1] if len(first_gen_indices) > 1 else first_gen_indices[0]

    optimal_art_langs = df.iloc[optimal_start_idx:first_gen_start_idx]
    first_gen_art_langs = df.iloc[first_gen_start_idx:]

    # NOTE: Didn't use mapped_color figure in final paper.
    # categories = natural_languages['type'].unique()

    # # Generate distinct colors for each category
    # colors = cm.get_cmap('tab10', len(categories)).colors
    # color_mapping = dict(zip(categories, colors))  # Map each category to a color

    # # Map the DataFrame's column to the corresponding colors
    # mapped_colors = natural_languages['type'].map(color_mapping)
    fig, axes = plt.subplots(1, 1, figsize=(6, 4))

    
    # First plot with specific axes for natural languages
    axes.scatter(
        natural_languages['lexicon'], 
        natural_languages['avg_ms_complexity'], 
        color='red', 
        marker='^', 
        label='Natural Languages', 
        zorder=2,
        alpha=1,
    )
    axes.scatter(
        first_gen_art_langs['lexicon'], 
        first_gen_art_langs['avg_ms_complexity'], 
        facecolors='white',
        edgecolors='black', 
        #color='gray',
        label='First Gen. Artificial Languages', 
        zorder=1,
        alpha=1,
    )
    axes.scatter(
        optimal_art_langs['lexicon'], 
        optimal_art_langs['avg_ms_complexity'], 
        color='black', 
        label='Optimal Artificial Languages', 
        zorder=1,
        alpha=1,
    )

    # Calculate and plot Pareto frontier for first plot
    pareto_frontier1 = calculate_pareto_frontier(
        df, 'lexicon', 'avg_ms_complexity'
    )
    axes.plot(
        pareto_frontier1[:, 0], pareto_frontier1[:, 1], 
        color='black', linestyle='-', label='Pareto Frontier'
    )

    axes.set_xlabel('Lexicon size')
    axes.set_ylabel('Average morphosyntactic complexity')
    axes.legend()
    
    fig.savefig('images/test.png', dpi=1000)
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)  # Adjust top to fit the title
    plt.show()

if __name__ == "__main__":
    main()