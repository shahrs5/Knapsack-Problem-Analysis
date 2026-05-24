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

print("All plots generated successfully!")
