import sys
sys.path.append('/opt/homebrew/lib/python3.12/site-packages')
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set design aesthetics
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.titlesize': 14,
    'font.family': 'sans-serif'
})

# Load the dataset
df = pd.read_csv('results/all_results.csv')

# 1. Plot Runtime for Shared Sizes (n=5 to 20, Log Scale)
shared = df[df['source'] == 'synthetic-shared'].copy()
plt.figure(figsize=(8, 5))
plt.plot(shared['n'], shared['bf_time'], marker='o', color='#de2d26', linewidth=2, label='Brute Force (O(2^n))')
plt.plot(shared['n'], shared['dp_time'], marker='s', color='#3182bd', linewidth=2, label='Dynamic Programming (O(nW))')
plt.plot(shared['n'], shared['gr_time'], marker='^', color='#31a354', linewidth=2, label='Greedy (O(n log n))')

plt.yscale('log')
plt.xlabel('Number of Items (n)')
plt.ylabel('Runtime (Seconds) - Log Scale')
plt.title('Figure 1: Runtime Comparison for Small Sizes (n = 5 to 20)')
plt.xticks(shared['n'])
plt.legend(frameon=True, facecolor='white', edgecolor='lightgray')
plt.tight_layout()
plt.savefig('results/plot_shared_runtime.png', dpi=300)
plt.close()

# 2. Plot Runtime for Large Sizes (n=50 to 1000, Linear Scale)
large = df[df['source'] == 'synthetic-large'].copy()
plt.figure(figsize=(8, 5))
plt.plot(large['n'], large['dp_time'], marker='s', color='#3182bd', linewidth=2, label='Dynamic Programming (O(nW))')
plt.plot(large['n'], large['gr_time'], marker='^', color='#31a354', linewidth=2, label='Greedy (O(n log n))')

plt.xlabel('Number of Items (n)')
plt.ylabel('Runtime (Seconds)')
plt.title('Figure 2: Runtime Comparison for Large Sizes (n = 50 to 1000)')
plt.xticks([50, 100, 200, 300, 500, 750, 1000])
plt.legend(frameon=True, facecolor='white', edgecolor='lightgray')
plt.tight_layout()
plt.savefig('results/plot_large_runtime.png', dpi=300)
plt.close()

# 3. Plot Greedy Approximation Ratio on kplib by correlation type
kplib = df[df['source'] == 'kplib'].copy()
kplib['cat'] = kplib['name'].apply(lambda x: x.split('/')[1] if len(x.split('/')) > 1 else 'unknown')

# Mapping category names for better display
cat_map = {
    '00Uncorrelated': 'Uncorrelated\n(00Uncorrelated)',
    '01WeaklyCorrelated': 'Weakly Correlated\n(01WeaklyCorrelated)',
    '02StronglyCorrelated': 'Strongly Correlated\n(02StronglyCorrelated)'
}
kplib['cat_display'] = kplib['cat'].map(cat_map)

plt.figure(figsize=(8, 5))
# Calculate mean, min, max for error bars manually
grouped = kplib.groupby('cat_display')['gr_ratio'].agg(['mean', 'min', 'max']).reset_index()

# Plot bars with error range
yerr = [grouped['mean'] - grouped['min'], grouped['max'] - grouped['mean']]
bars = plt.bar(grouped['cat_display'], grouped['mean'] * 100, yerr=np.array(yerr)*100, 
               color=['#9ecae1', '#6baed6', '#3182bd'], edgecolor='gray', capsize=8, width=0.5)

plt.ylim(90, 101)
plt.ylabel('Greedy Approximation Ratio (%)')
plt.xlabel('Dataset Correlation Category')
plt.title('Figure 3: Greedy Solution Quality (Approximation Ratio) by Correlation Family')

# Add labels above the bars
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.2, f'{height:.3f}%',
             ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('results/plot_kplib_ratios.png', dpi=300)
plt.close()

# 4. Figure 4: DP Feasibility Boundary on Jooken Instances (N vs Capacity)
jooken = df[df['source'] == 'jooken'].copy()
jooken['Status'] = jooken['dp_time'].apply(lambda t: 'Solved' if pd.notna(t) else 'Skipped (OOM Limit)')

plt.figure(figsize=(8, 5))
# Using a categorical color palette matching the existing figures
sns.scatterplot(
    data=jooken, 
    x='n', 
    y='capacity', 
    hue='Status', 
    palette={'Solved': '#3182bd', 'Skipped (OOM Limit)': '#de2d26'},
    style='Status',
    s=100,
    alpha=0.8
)
plt.yscale('log')
plt.xlabel('Number of Items (n)')
plt.ylabel('Knapsack Capacity (W) - Log Scale')
plt.title('Figure 4: Feasibility Boundary of Dynamic Programming on Jooken Hard Instances')
plt.legend(frameon=True, facecolor='white', edgecolor='lightgray', title='DP Status')
plt.tight_layout()
plt.savefig('results/plot_dp_feasibility.png', dpi=300)
plt.close()

# 5. Figure 5: Greedy Runtime Scalability on Jooken Instances
jooken['gr_time_us'] = jooken['gr_time'] * 1e6
plt.figure(figsize=(8, 5))
sns.lineplot(
    data=jooken,
    x='n',
    y='gr_time_us',
    hue='capacity',
    palette='viridis',
    marker='o',
    linewidth=2,
    legend='full'
)
# Format legend labels to be human-readable, e.g., W = 1e+06, W = 1e+08, W = 1e+10
handles, labels = plt.gca().get_legend_handles_labels()
new_labels = []
for l in labels:
    try:
        val = float(l)
        new_labels.append(f'W = {val:.0e}')
    except ValueError:
        new_labels.append(l)
plt.legend(handles, new_labels, frameon=True, facecolor='white', edgecolor='lightgray', title='Capacity')

plt.xlabel('Number of Items (n)')
plt.ylabel('Greedy Runtime (Microseconds)')
plt.title('Figure 5: Greedy Runtime Scalability on Jooken Hard Instances')
plt.tight_layout()
plt.savefig('results/plot_greedy_jooken_runtime.png', dpi=300)
plt.close()

# 6. Figure 6: Distribution of Greedy Approximation Ratios (Jooken vs kplib)
k_df = df[df['source'] == 'kplib'].copy()
k_df['cat'] = k_df['name'].apply(lambda x: x.split('/')[1] if len(x.split('/')) > 1 else 'unknown')
cat_map = {
    '00Uncorrelated': 'kplib - Uncorrelated',
    '01WeaklyCorrelated': 'kplib - Weakly Correlated',
    '02StronglyCorrelated': 'kplib - Strongly Correlated'
}
k_df['group'] = k_df['cat'].map(cat_map)

j_df = df[(df['source'] == 'jooken') & df['gr_ratio'].notna()].copy()
j_df['group'] = 'jooken - Hard Instances'

combined = pd.concat([k_df[['group', 'gr_ratio']], j_df[['group', 'gr_ratio']]])
combined['gr_ratio_pct'] = combined['gr_ratio'] * 100

plt.figure(figsize=(9, 6))
sns.boxplot(
    data=combined,
    x='group',
    y='gr_ratio_pct',
    palette='Set2',
    width=0.5,
    showfliers=False
)
sns.stripplot(
    data=combined,
    x='group',
    y='gr_ratio_pct',
    color='black',
    alpha=0.5,
    size=5,
    jitter=0.2
)

plt.ylabel('Greedy Approximation Ratio (%)')
plt.xlabel('Dataset Category')
plt.title('Figure 6: Distribution of Greedy Approximation Ratios')
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig('results/plot_greedy_ratios_distribution.png', dpi=300)
plt.close()

print("All plots generated successfully!")
