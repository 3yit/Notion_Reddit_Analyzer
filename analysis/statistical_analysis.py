"""
Statistical utilities for A/B test design and analysis.
Used in the Notion Complaint Analyzer project.
"""

import numpy as np
from scipy import stats
from scipy.stats import norm
import math


def calculate_sample_size(baseline_rate, mde, alpha=0.05, power=0.80, two_tailed=True):
    """
    Calculate required sample size per variant for a conversion rate test.
    
    Parameters:
    -----------
    baseline_rate : float
        Current conversion rate (e.g., 0.15 for 15%)
    mde : float
        Minimum Detectable Effect - the smallest change you want to detect (e.g., 0.02 for 2 percentage points)
    alpha : float
        Significance level (probability of Type I error), default 0.05
    power : float
        Statistical power (1 - probability of Type II error), default 0.80
    two_tailed : bool
        Whether to use a two-tailed test, default True
        
    Returns:
    --------
    dict : Dictionary with sample size calculations and metadata
    """
    # Z-scores for alpha and beta
    z_alpha = norm.ppf(1 - alpha/2) if two_tailed else norm.ppf(1 - alpha)
    z_beta = norm.ppf(power)
    
    # Standard deviations
    p1 = baseline_rate
    p2 = baseline_rate + mde
    
    # Pooled standard deviation
    p_pooled = (p1 + p2) / 2
    sd_pooled = math.sqrt(2 * p_pooled * (1 - p_pooled))
    
    # Sample size calculation
    n = ((z_alpha + z_beta) ** 2 * sd_pooled ** 2) / (mde ** 2)
    n = math.ceil(n)
    
    return {
        'sample_size_per_variant': n,
        'total_sample_size': n * 2,
        'baseline_rate': baseline_rate,
        'expected_treatment_rate': p2,
        'mde': mde,
        'relative_lift': (mde / baseline_rate) * 100,
        'alpha': alpha,
        'power': power,
        'two_tailed': two_tailed
    }


def estimate_test_duration(sample_size_per_variant, daily_users, allocation=0.5):
    """
    Estimate how many days the A/B test needs to run.
    
    Parameters:
    -----------
    sample_size_per_variant : int
        Required sample size for each variant
    daily_users : int
        Average number of eligible users per day
    allocation : float
        Fraction of traffic allocated to the experiment (0.5 = 50%)
        
    Returns:
    --------
    dict : Duration estimate with confidence intervals
    """
    users_per_day = daily_users * allocation / 2  # Split between control and treatment
    
    expected_days = math.ceil(sample_size_per_variant / users_per_day)
    
    # Add buffer for weekday/weekend variation (assume 20% variance)
    lower_bound = math.ceil(expected_days * 0.9)
    upper_bound = math.ceil(expected_days * 1.3)
    
    return {
        'expected_days': expected_days,
        'lower_bound_days': lower_bound,
        'upper_bound_days': upper_bound,
        'expected_weeks': round(expected_days / 7, 1),
        'daily_users_per_variant': int(users_per_day),
        'total_users_needed': sample_size_per_variant * 2
    }


def analyze_ab_test(control_conversions, control_total, treatment_conversions, treatment_total, alpha=0.05):
    """
    Analyze A/B test results using two-proportion z-test.
    
    Parameters:
    -----------
    control_conversions : int
        Number of conversions in control group
    control_total : int
        Total users in control group
    treatment_conversions : int
        Number of conversions in treatment group
    treatment_total : int
        Total users in treatment group
    alpha : float
        Significance level
        
    Returns:
    --------
    dict : Test results with statistical significance
    """
    p_control = control_conversions / control_total
    p_treatment = treatment_conversions / treatment_total
    
    # Pooled proportion
    p_pooled = (control_conversions + treatment_conversions) / (control_total + treatment_total)
    
    # Standard error
    se = math.sqrt(p_pooled * (1 - p_pooled) * (1/control_total + 1/treatment_total))
    
    # Z-score
    z_score = (p_treatment - p_control) / se
    
    # P-value (two-tailed)
    p_value = 2 * (1 - norm.cdf(abs(z_score)))
    
    # Confidence interval for difference
    se_diff = math.sqrt(p_control * (1 - p_control) / control_total + 
                        p_treatment * (1 - p_treatment) / treatment_total)
    ci_margin = norm.ppf(1 - alpha/2) * se_diff
    
    diff = p_treatment - p_control
    ci_lower = diff - ci_margin
    ci_upper = diff + ci_margin
    
    # Relative lift
    relative_lift = ((p_treatment - p_control) / p_control) * 100 if p_control > 0 else 0
    
    return {
        'control_rate': p_control,
        'treatment_rate': p_treatment,
        'absolute_difference': diff,
        'relative_lift_pct': relative_lift,
        'z_score': z_score,
        'p_value': p_value,
        'significant': p_value < alpha,
        'confidence_interval': (ci_lower, ci_upper),
        'confidence_level': (1 - alpha) * 100,
        'sample_sizes': {
            'control': control_total,
            'treatment': treatment_total
        }
    }


def calculate_revenue_impact(user_impact, conversion_rate_lift, avg_revenue_per_user, total_users):
    """
    Calculate estimated revenue impact of a product change.
    
    Parameters:
    -----------
    user_impact : float
        Percentage of users affected (0.0 to 1.0)
    conversion_rate_lift : float
        Expected lift in conversion/retention (0.0 to 1.0)
    avg_revenue_per_user : float
        Average revenue per user per year
    total_users : int
        Total user base
        
    Returns:
    --------
    dict : Revenue impact estimates
    """
    affected_users = int(total_users * user_impact)
    additional_retained_users = int(affected_users * conversion_rate_lift)
    annual_impact = additional_retained_users * avg_revenue_per_user
    
    # Conservative and optimistic scenarios
    conservative_impact = annual_impact * 0.6  # 60% of estimate
    optimistic_impact = annual_impact * 1.4    # 140% of estimate
    
    return {
        'affected_users': affected_users,
        'additional_retained_users': additional_retained_users,
        'expected_annual_impact': annual_impact,
        'conservative_estimate': conservative_impact,
        'optimistic_estimate': optimistic_impact,
        'per_user_value': avg_revenue_per_user
    }


def prioritization_score(impact, effort, impact_weight=0.7):
    """
    Calculate prioritization score for product initiatives.
    Uses weighted RICE-like framework.
    
    Parameters:
    -----------
    impact : float
        Impact score (1-10 scale)
    effort : float
        Effort score (1-10 scale, higher = more effort)
    impact_weight : float
        Weight given to impact vs. efficiency (0.5 = equal weight)
        
    Returns:
    --------
    float : Priority score (higher = more priority)
    """
    # Normalize to 0-1 scale
    impact_norm = impact / 10
    efficiency = (10 - effort) / 10  # Invert effort so higher effort = lower efficiency
    
    # Weighted combination
    score = (impact_norm * impact_weight) + (efficiency * (1 - impact_weight))
    
    return round(score * 100, 2)


# Example usage and test cases
if __name__ == "__main__":
    print("=== A/B Test Sample Size Calculator ===")
    
    # Example: Test to improve activation rate from 15% to 17%
    result = calculate_sample_size(
        baseline_rate=0.15,
        mde=0.02,  # 2 percentage point improvement
        alpha=0.05,
        power=0.80
    )
    
    print(f"\nBaseline Rate: {result['baseline_rate']*100}%")
    print(f"Target Rate: {result['expected_treatment_rate']*100}%")
    print(f"Relative Lift: {result['relative_lift']:.1f}%")
    print(f"Sample Size per Variant: {result['sample_size_per_variant']:,}")
    print(f"Total Sample Size: {result['total_sample_size']:,}")
    
    # Estimate duration
    duration = estimate_test_duration(
        sample_size_per_variant=result['sample_size_per_variant'],
        daily_users=5000,  # Assume 5000 eligible users per day
        allocation=0.5
    )
    
    print(f"\n=== Test Duration Estimate ===")
    print(f"Expected Duration: {duration['expected_days']} days ({duration['expected_weeks']} weeks)")
    print(f"Range: {duration['lower_bound_days']}-{duration['upper_bound_days']} days")
    
    # Example analysis
    print(f"\n=== Example Test Results ===")
    analysis = analyze_ab_test(
        control_conversions=375,
        control_total=2500,
        treatment_conversions=450,
        treatment_total=2500,
        alpha=0.05
    )
    
    print(f"Control Rate: {analysis['control_rate']*100:.2f}%")
    print(f"Treatment Rate: {analysis['treatment_rate']*100:.2f}%")
    print(f"Relative Lift: {analysis['relative_lift_pct']:.2f}%")
    print(f"P-value: {analysis['p_value']:.4f}")
    print(f"Statistically Significant: {analysis['significant']}")
    print(f"95% CI: ({analysis['confidence_interval'][0]*100:.2f}%, {analysis['confidence_interval'][1]*100:.2f}%)")
