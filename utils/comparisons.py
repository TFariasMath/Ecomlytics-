"""
Period Comparison Utilities

Calculate and compare metrics between different time periods.
Supports: previous period, year-over-year, historical average.
"""

from datetime import datetime, timedelta
import pandas as pd
from typing import Tuple, Dict


def get_comparison_period(
    start_date: datetime,
    end_date: datetime,
    comparison_type: str = 'previous'
) -> Tuple[datetime, datetime]:
    """
    Calculate the comparison period based on current period
    
    Args:
        start_date: Current period start date
        end_date: Current period end date
        comparison_type: Type of comparison
            - 'previous': Same duration, immediately before
            - 'year_ago': Same period, previous year
            - 'avg_historical': Not implemented yet
    
    Returns:
        Tuple of (comparison_start_date, comparison_end_date)
    
    Example:
        >>> get_comparison_period(
        ...     datetime(2025, 12, 1),
        ...     datetime(2025, 12, 21),
        ...     'previous'
        ... )
        (datetime(2025, 11, 10), datetime(2025, 11, 30))
    """
    # Calculate duration
    duration = end_date - start_date
    days_diff = duration.days
    
    if comparison_type == 'previous':
        # Same duration, just before current period
        comp_end_date = start_date - timedelta(days=1)
        comp_start_date = comp_end_date - timedelta(days=days_diff)
        
    elif comparison_type == 'year_ago':
        # Same period, one year ago
        try:
            comp_start_date = start_date.replace(year=start_date.year - 1)
            comp_end_date = end_date.replace(year=end_date.year - 1)
        except ValueError:
            # Handle Feb 29 edge case
            comp_start_date = start_date - timedelta(days=365)
            comp_end_date = end_date - timedelta(days=365)
    
    else:
        # Default to previous period
        comp_end_date = start_date - timedelta(days=1)
        comp_start_date = comp_end_date - timedelta(days=days_diff)
    
    return comp_start_date, comp_end_date


def calculate_comparison_metrics(
    current_df: pd.DataFrame,
    comparison_df: pd.DataFrame,
    metric_column: str = 'total'
) -> Dict[str, float]:
    """
    Calculate comparison metrics between two dataframes
    
    Args:
        current_df: Current period dataframe
        comparison_df: Comparison period dataframe
        metric_column: Column to compare (default: 'total')
    
    Returns:
        Dictionary with:
            - current_value: Sum for current period
            - comparison_value: Sum for comparison period
            - change_absolute: Absolute change
            - change_percentage: Percentage change
            - current_count: Number of records in current
            - comparison_count: Number of records in comparison
    
    Example:
        >>> metrics = calculate_comparison_metrics(df_current, df_previous)
        >>> print(f"Change: {metrics['change_percentage']:.1f}%")
        Change: +15.3%
    """
    # Calculate totals
    current_value = current_df[metric_column].sum() if not current_df.empty else 0
    comparison_value = comparison_df[metric_column].sum() if not comparison_df.empty else 0
    
    # Calculate change
    change_absolute = current_value - comparison_value
    
    if comparison_value > 0:
        change_percentage = (change_absolute / comparison_value) * 100
    else:
        change_percentage = 100.0 if current_value > 0 else 0.0
    
    # Counts
    current_count = len(current_df)
    comparison_count = len(comparison_df)
    count_change = current_count - comparison_count
    
    if comparison_count > 0:
        count_change_pct = (count_change / comparison_count) * 100
    else:
        count_change_pct = 100.0 if current_count > 0 else 0.0
    
    return {
        'current_value': current_value,
        'comparison_value': comparison_value,
        'change_absolute': change_absolute,
        'change_percentage': change_percentage,
        'current_count': current_count,
        'comparison_count': comparison_count,
        'count_change': count_change,
        'count_change_percentage': count_change_pct
    }


def format_comparison_delta(change_percentage: float) -> str:
    """
    Format percentage change for display
    
    Args:
        change_percentage: Percentage change value
    
    Returns:
        Formatted string with sign and symbol
    
    Example:
        >>> format_comparison_delta(15.3)
        '+15.3% ↑'
        >>> format_comparison_delta(-8.2)
        '-8.2% ↓'
    """
    if change_percentage > 0:
        return f"+{change_percentage:.1f}% ↑"
    elif change_percentage < 0:
        return f"{change_percentage:.1f}% ↓"
    else:
        return "0.0% →"


def get_comparison_color(change_percentage: float) -> str:
    """
    Get color for comparison delta (for metrics display)
    
    Args:
        change_percentage: Percentage change
    
    Returns:
        Color string: 'normal' (green), 'inverse' (red), or 'off'
    """
    if change_percentage > 0:
        return 'normal'  # Green for positive
    elif change_percentage < 0:
        return 'inverse'  # Red for negative
    else:
        return 'off'  # Gray for no change
