import matplotlib.pyplot as plt
from matplotlib import cm
import pandas as pd

def calculate_pareto_frontier(df, x_col, y_col):
    df_sorted = df.sort_values(by=x_col).dropna(subset=[x_col, y_col])
    pareto_frontier = [df_sorted.iloc[0]]  # Start with the first row

    for _, row in df_sorted.iterrows():
        if row[x_col] != pareto_frontier[-1][x_col]:
            pareto_frontier.append(row)
        if row[y_col] < pareto_frontier[-1][y_col]:  # Minimization on y-axis
            if row[x_col] == pareto_frontier[-1][x_col]:
                pareto_frontier.pop()
            pareto_frontier.append(row)

    pareto_frontier_df = pd.DataFrame(pareto_frontier)
    return pareto_frontier_df[[x_col, y_col]].values

def plot_file(file_path, ax, title):
    df = pd.read_csv(file_path)

    # Identify language types
    df['is_artificial'] = df['language'].str.startswith('artificial_language')
    df['is_optimal'] = df['language'].str.startswith('optimal')

    # Separate data for plotting
    natural_languages = df[~df['is_artificial'] & ~df['is_optimal']]
    artificial_languages = df[df['is_artificial'] & ~df['is_optimal']]
    optimal_languages = df[df['is_optimal']]

    categories = optimal_languages['language'].unique()

    # Generate distinct colors for each category
    colors = cm.get_cmap('tab10', len(categories)).colors
    color_mapping = dict(zip(categories, colors))  # Map each category to a color

    # Map the DataFrame's column to the corresponding colors
    mapped_colors = optimal_languages['language'].map(color_mapping)

    # Scatter plot
    ax.scatter(
        natural_languages['lexicon'], 
        natural_languages['avg_ms_complexity'], 
        color='red', 
        marker='^', 
        label='Natural Languages', 
        alpha=0.8
    )
    ax.scatter(
        artificial_languages['lexicon'], 
        artificial_languages['avg_ms_complexity'], 
        color='black', 
        marker='o', 
        label='Artificial Languages', 
        alpha=0.8
    )
    ax.scatter(
        optimal_languages['lexicon'], 
        optimal_languages['avg_ms_complexity'], 
        color=mapped_colors, 
        marker='*', 
        label='Optimal Languages', 
        s=100,  # Make stars larger
        alpha=0.8
    )

    # Calculate and plot Pareto frontier
    pareto_frontier = calculate_pareto_frontier(df, 'lexicon', 'avg_ms_complexity')
    ax.plot(
        pareto_frontier[:, 0], pareto_frontier[:, 1], 
        color='black', linestyle='-', label='Pareto Frontier'
    )

    for category, color in color_mapping.items():
        ax.scatter([], [], color=color, label=category, marker='*')  # Invisible points for legend
    ax.legend(title="Categories", loc='best')

    # Plot settings
    ax.set_title(title)
    ax.set_xlabel('Lexicon')
    ax.set_ylabel('Avg Morphosyntactic Complexity')
    ax.legend()

 

def main():
    files = [
        ("data/pl_complexity.csv", "PL Complexity"),
        ("data/rev_complexity.csv", "Reversed PL Complexity"),
        ("data/uni_complexity.csv", "Uniform Complexity")
    ]

    fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)

    for ax, (file_path, title) in zip(axes, files):
        plot_file(file_path, ax, title)

    plt.tight_layout()
    plt.savefig('prior_scatterplots.png', dpi=1000)
    plt.show()

if __name__ == "__main__":
    main()
