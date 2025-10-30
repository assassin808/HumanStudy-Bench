"""
Two One-Sided Tests (TOST) for equivalence testing.

Tests whether an effect size is within an equivalence margin (delta).

H₀: |d| ≥ δ (not equivalent)
H₁: |d| < δ (equivalent)

Lower p-values indicate stronger evidence of equivalence.
"""

import numpy as np
from scipy import stats
from typing import Dict, Any


# Global default equivalence margin
GLOBAL_DELTA = 0.2  # "Small effect" boundary (Cohen 1988)


def tost_test(
    d: float,
    se: float,
    n1: int,
    n2: int,
    delta: float = GLOBAL_DELTA
) -> Dict[str, Any]:
    """
    Perform Two One-Sided Tests (TOST) for equivalence.
    
    Args:
        d: Observed standardized effect size
        se: Standard error of d
        n1: Sample size (agent)
        n2: Sample size (human)
        delta: Equivalence margin (standardized units)
        
    Returns:
        Dictionary with:
            - p_tost: TOST p-value (lower = more equivalent)
            - t_upper: t-statistic for upper test
            - t_lower: t-statistic for lower test
            - df: degrees of freedom
            - delta: equivalence margin used
            - interpretation: verbal interpretation
    """
    # Degrees of freedom
    df = n1 + n2 - 2
    
    # Two one-sided t-tests
    # Test 1: d - delta < 0  (d < delta)
    t_upper = (d - delta) / se
    p_upper = stats.t.cdf(t_upper, df)
    
    # Test 2: d + delta > 0  (-d < delta, or d > -delta)
    t_lower = (-d - delta) / se
    p_lower = stats.t.cdf(t_lower, df)
    
    # TOST p-value is the maximum of the two
    p_tost = max(p_upper, p_lower)
    
    # Interpretation
    interpretation = interpret_tost_p(p_tost, d, delta)
    
    return {
        "p_tost": float(p_tost),
        "t_upper": float(t_upper),
        "t_lower": float(t_lower),
        "p_upper": float(p_upper),
        "p_lower": float(p_lower),
        "df": int(df),
        "delta": float(delta),
        "d_observed": float(d),
        "interpretation": interpretation
    }


def interpret_tost_p(p: float, d: float, delta: float) -> str:
    """
    Interpret TOST p-value.
    
    Args:
        p: TOST p-value
        d: Observed effect size
        delta: Equivalence margin
        
    Returns:
        Verbal interpretation
    """
    if p < 0.001:
        strength = "very strong"
    elif p < 0.01:
        strength = "strong"
    elif p < 0.05:
        strength = "moderate"
    elif p < 0.10:
        strength = "weak"
    else:
        strength = "insufficient"
    
    if d < delta * 0.5:
        distance = "very close"
    elif d < delta:
        distance = "within margin"
    else:
        distance = "outside margin"
    
    return f"{strength} equivalence ({distance}, d={d:.3f} vs δ={delta})"


def tost_from_proportions(
    p_agent: float,
    n_agent: int,
    p_human: float,
    n_human: int,
    delta: float = GLOBAL_DELTA
) -> Dict[str, Any]:
    """
    Convenience function for TOST on proportions.
    
    Performs Freeman-Tukey transformation and TOST in one step.
    """
    # Freeman-Tukey transformation
    theta_agent = np.arcsin(np.sqrt(p_agent))
    theta_human = np.arcsin(np.sqrt(p_human))
    
    # Standard errors
    se_agent = 1.0 / (2.0 * np.sqrt(n_agent))
    se_human = 1.0 / (2.0 * np.sqrt(n_human))
    se_pooled = np.sqrt(se_agent**2 + se_human**2)
    
    # Standardized effect size
    d = abs(theta_agent - theta_human) / se_pooled
    
    # TOST
    result = tost_test(d, se_pooled, n_agent, n_human, delta)
    
    # Add proportion-specific details
    result.update({
        "p_agent": float(p_agent),
        "p_human": float(p_human),
        "theta_agent": float(theta_agent),
        "theta_human": float(theta_human),
        "method": "Freeman-Tukey + TOST"
    })
    
    return result


def tost_from_means(
    m_agent: float,
    sd_agent: float,
    n_agent: int,
    m_human: float,
    sd_human: float,
    n_human: int,
    delta: float = GLOBAL_DELTA
) -> Dict[str, Any]:
    """
    Convenience function for TOST on means (ratings/scales).
    
    Uses Cohen's d and TOST.
    """
    # Pooled standard deviation
    sd_pooled = np.sqrt(
        ((n_agent - 1) * sd_agent**2 + (n_human - 1) * sd_human**2) /
        (n_agent + n_human - 2)
    )
    
    # Cohen's d
    d = abs(m_agent - m_human) / sd_pooled
    
    # Standard error of d
    se_d = np.sqrt((n_agent + n_human) / (n_agent * n_human))
    
    # TOST
    result = tost_test(d, se_d, n_agent, n_human, delta)
    
    # Add mean-specific details
    result.update({
        "m_agent": float(m_agent),
        "m_human": float(m_human),
        "sd_agent": float(sd_agent),
        "sd_human": float(sd_human),
        "sd_pooled": float(sd_pooled),
        "method": "Cohen's d + TOST"
    })
    
    return result


def set_global_delta(delta: float):
    """
    Set the global equivalence margin.
    
    Args:
        delta: New equivalence margin (standardized units)
    """
    global GLOBAL_DELTA
    GLOBAL_DELTA = delta
    print(f"✓ Global equivalence margin set to δ = {delta}")


def get_global_delta() -> float:
    """Get the current global equivalence margin."""
    return GLOBAL_DELTA
