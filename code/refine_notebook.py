
import nbformat
import os

notebook_path = '/home/bhavik/Dropbox/edu/smu/winter/data_mining/a3_association/5580-dm-a3-association/code/03_apriori_session.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = nbformat.read(f, as_version=4)

# Define the new code for the elite rules cell
refined_code = """# 1. Apply the stricter Tier 1 Filter (Elite Zone)
elite_20_df = df_session_rules[
    (df_session_rules['support'] >= 0.045) & 
    (df_session_rules['confidence'] >= 0.90)
].sort_values(by='lift', ascending=False).head(20)

# 2. Add Length info for complexity analysis
elite_20_df['len_ant'] = elite_20_df['antecedents'].apply(len)
elite_20_df['len_con'] = elite_20_df['consequents'].apply(len)
elite_20_df['total_len'] = elite_20_df['len_ant'] + elite_20_df['len_con']

# 3. Final display and export
display(elite_20_df[['antecedents', 'consequents', 'support', 'confidence', 'lift', 'total_len']])
elite_20_df.to_csv(results_dir / "apriori_session_elite_rules.csv", index=False)

# 4. Advanced Visualization for Report Chapters
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid", context="talk")

# Plot A: Top 20 Elite Rules by Lift
plt.figure(figsize=(14, 10))
plot_df = elite_20_df.copy().sort_values('lift', ascending=True)
plot_df['rule_label'] = plot_df['antecedents'].apply(lambda x: ', '.join(list(x))) + " \\n→ " + plot_df['consequents'].apply(lambda x: ', '.join(list(x)))

ax = sns.barplot(data=plot_df, x='lift', y='rule_label', palette='mako', hue='rule_label', legend=False)
plt.title('Top 20 Session-Level "Elite" Rules by Lift Strength', fontsize=18, fontweight='bold', pad=20)
plt.xlabel('Lift (Association Strength)', fontsize=14)
plt.ylabel('Association Rule', fontsize=14)

for p in ax.patches:
    ax.annotate(f"{p.get_width():.2f}", (p.get_width() + 0.1, p.get_y() + p.get_height()/2), va='center', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig(results_dir / "apriori_session_elite_lift_bar.pdf", bbox_inches='tight')
plt.show()

# Plot B: Elite Rule Performance Zone (Scatter Plot)
plt.figure(figsize=(10, 7))
sns.scatterplot(data=elite_20_df, x='support', y='confidence', size='lift', hue='lift', sizes=(150, 1000), palette='viridis', alpha=0.7)
plt.title('Session-Level Elite Rules: Support vs Confidence Zone', fontsize=16, fontweight='bold')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, title='Lift')
plt.tight_layout()
plt.savefig(results_dir / "apriori_session_elite_precision_scatter.pdf")
plt.show()"""

# Define the new markdown for personas
refined_personas = """## 10. Tactical Persona Mapping: Session-Level Insights

---

While User-Level Personas focus on long-term strategy, **Session-Level Personas** provide tactical insights into the immediate objectives of a user in a single sitting. Based on the refined "Elite 20" session-level mining, we identify three distinct behavioral archetypes:

1.  🚀 **The 'Quick-Fire' Messenger**: Characterized by session-level rules focusing on the `SendNow` → `ReportsTab` sequence. These sessions are short, transactional, and goal-oriented. Rules in this category often show exceptionally high confidence (>0.98).
2.  🎨 **The Content Editor**: Engaged in prolonged sessions involving `AddImage` and `TxtFontSizeColor`. This indicates complex asset manipulation and multi-element layout adjustments within a single date window. 
3.  🔍 **The Audit Investigator**: Sessions dominated by `OpenReportList`, `OpenData`, and `ManageTab`. Items like `OpensAndBounces` often follow, representing a tactical 'deep dive' into campaign performance immediately after launch.

**Key Insight**: Comparison between levels reveals that \"strategic mastery\" (User level) is built upon the consistent execution of these \"tactical bursts\" (Session level). Understanding the transition from a 'Quick-Fire' session to a 'Content Editor' session is key to predicting user maturity."""

# Find and update cells
for cell in nb.cells:
    if cell.cell_type == 'code' and 'elite_20_df = df_session_rules[' in cell.source:
        cell.source = refined_code
    if cell.cell_type == 'markdown' and '## 10. Tactical Persona Mapping' in cell.source:
        cell.source = refined_personas

with open(notebook_path, 'w', encoding='utf-8') as f:
    nbformat.write(nb, f)

print("Notebook updated successfully.")
