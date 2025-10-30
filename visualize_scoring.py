"""
Visualization: Old vs New Scoring Systems

This script demonstrates the difference between discrete tier scoring
and continuous linear scoring for data-level tests.
"""

import numpy as np
import matplotlib.pyplot as plt

def old_scoring(h):
    """Old discrete tier scoring."""
    if h < 0.20:
        return 1.0
    elif h < 0.50:
        return 0.9
    elif h < 0.80:
        return 0.8
    else:
        return 0.7

def new_scoring(h, max_h=0.80):
    """New continuous linear scoring."""
    return max(0.0, 1.0 - h / max_h)

# Generate Cohen's h values
h_values = np.linspace(0, 1.2, 500)

# Calculate scores
old_scores = [old_scoring(h) for h in h_values]
new_scores = [new_scoring(h) for h in h_values]

# Create comparison plot
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: Old scoring (discrete)
ax1 = axes[0]
ax1.plot(h_values, old_scores, linewidth=3, color='blue', label='Old Scoring')
ax1.axvline(x=0.20, color='gray', linestyle='--', alpha=0.5, label='Thresholds')
ax1.axvline(x=0.50, color='gray', linestyle='--', alpha=0.5)
ax1.axvline(x=0.80, color='gray', linestyle='--', alpha=0.5)
ax1.axhline(y=0.70, color='red', linestyle=':', alpha=0.5, label='Minimum (0.7)')
ax1.set_xlabel("Cohen's h", fontsize=12)
ax1.set_ylabel("Score", fontsize=12)
ax1.set_title("Old System: Discrete Tier Scoring", fontsize=14, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.legend()
ax1.set_ylim([0, 1.1])
ax1.set_xlim([0, 1.2])

# Annotate tiers
ax1.text(0.10, 1.05, 'Excellent\n(1.0)', ha='center', fontsize=10, color='green')
ax1.text(0.35, 0.95, 'Good\n(0.9)', ha='center', fontsize=10, color='blue')
ax1.text(0.65, 0.85, 'Acceptable\n(0.8)', ha='center', fontsize=10, color='orange')
ax1.text(1.00, 0.75, 'Poor\n(0.7)', ha='center', fontsize=10, color='red')

# Plot 2: New scoring (continuous)
ax2 = axes[1]
ax2.plot(h_values, new_scores, linewidth=3, color='green', label='New Scoring')
ax2.axvline(x=0.80, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Zero threshold (h=0.8)')
ax2.axhline(y=0.0, color='red', linestyle=':', alpha=0.5)
ax2.fill_between(h_values, 0, new_scores, alpha=0.2, color='green')
ax2.set_xlabel("Cohen's h", fontsize=12)
ax2.set_ylabel("Score", fontsize=12)
ax2.set_title("New System: Continuous Linear Scoring", fontsize=14, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.legend()
ax2.set_ylim([0, 1.1])
ax2.set_xlim([0, 1.2])

# Annotate key points
ax2.text(0.0, 1.05, 'h=0.0\nscore=1.0', ha='center', fontsize=9, color='green')
ax2.text(0.4, 0.55, 'h=0.4\nscore=0.5', ha='center', fontsize=9, color='blue')
ax2.text(0.8, 0.05, 'h=0.8\nscore=0.0', ha='center', fontsize=9, color='red')
ax2.text(1.0, 0.05, 'h≥0.8\nscore=0.0', ha='center', fontsize=9, color='red')

plt.tight_layout()
plt.savefig('scoring_comparison.png', dpi=300, bbox_inches='tight')
print("✅ Visualization saved as 'scoring_comparison.png'")

# Print comparison table
print("\n" + "="*70)
print("COMPARISON TABLE: Old vs New Scoring")
print("="*70)
print(f"{'Cohen\'s h':<12} {'Old Score':<12} {'New Score':<12} {'Difference':<12}")
print("-"*70)

test_h_values = [0.00, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]
for h in test_h_values:
    old = old_scoring(h)
    new = new_scoring(h)
    diff = new - old
    symbol = "✅" if new <= old else "⚠️"
    print(f"{h:<12.2f} {old:<12.2f} {new:<12.3f} {diff:<12.3f} {symbol}")

print("="*70)
print("\nKey insights:")
print("  • Old system: Scores stay at 0.7 even for very large h")
print("  • New system: Scores reach 0.0 when h ≥ 0.8 ✅")
print("  • New system: Continuous rewards for similarity")
print("  • New system: More discriminating for moderate differences")
