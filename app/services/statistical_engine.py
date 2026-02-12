import pandas as pd
import numpy as np
from typing import Dict, List, Any

def detect_outliers_iqr(series: pd.Series) -> Dict[str, Any]:
    """
    Calculates outliers using the Interquartile Range (IQR) method.
    Returns count, percentage, and bounds.
    """
    if series.empty or not pd.api.types.is_numeric_dtype(series):
        return {"count": 0, "percentage": 0.0, "lower_bound": None, "upper_bound": None}

    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = series[(series < lower_bound) | (series > upper_bound)]
    count = len(outliers)
    percentage = round((count / len(series)) * 100, 2)
    
    return {
        "count": count,
        "percentage": percentage,
        "lower_bound": float(lower_bound),
        "upper_bound": float(upper_bound)
    }

def analyze_skewness(series: pd.Series) -> Dict[str, Any]:
    """
    Calculates skewness and classifies the distribution shape.
    Why it matters: Highly skewed data can break machine learning models
    and distort average values (mean vs median).
    """
    if series.empty or not pd.api.types.is_numeric_dtype(series):
        return {"value": None, "classification": "Unknown"}

    skew_val = series.skew()
    
    if pd.isna(skew_val):
        return {"value": None, "classification": "Unknown"}
        
    classification = "Symmetric"
    if skew_val > 1:
        classification = "Highly Right-Skewed (Long Tail)"
    elif skew_val > 0.5:
        classification = "Moderately Right-Skewed"
    elif skew_val < -1:
        classification = "Highly Left-Skewed"
    elif skew_val < -0.5:
        classification = "Moderately Left-Skewed"
        
    return {"value": round(skew_val, 2), "classification": classification}

def analyze_variability(series: pd.Series) -> Dict[str, Any]:
    """
    Calculates Coefficient of Variation (CV) to interpret volatility.
    Why it matters: High variability means higher risk or instability in business data.
    """
    if series.empty or not pd.api.types.is_numeric_dtype(series):
        return {"std_dev": None, "cv": None, "classification": "Unknown"}

    mean_val = series.mean()
    std_dev = series.std()
    
    if mean_val == 0:
        return {"std_dev": round(std_dev, 2), "cv": None, "classification": "Unknown (Mean is 0)"}
        
    cv = std_dev / abs(mean_val)
    
    classification = "Moderate Variability"
    if cv < 0.1:
        classification = "Low Variability (Stable)"
    elif cv > 1.0:
        classification = "High Variability (Volatile)"
        
    return {
        "std_dev": round(std_dev, 2),
        "cv": round(cv, 2),
        "classification": classification
    }

def compute_correlations(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Identifies strong relationships between variables.
    Correlation != Causation: Just because ice cream sales and shark attacks
    both go up in summer doesn't mean ice cream causes shark attacks.
    """
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.shape[1] < 2:
        return []

    corr_matrix = numeric_df.corr()
    strong_corrs = []

    # Iterate over the correlation matrix
    for i in range(len(corr_matrix.columns)):
        for j in range(i):
            col1 = corr_matrix.columns[i]
            col2 = corr_matrix.columns[j]
            r_value = corr_matrix.iloc[i, j]
            
            # Detect strong correlation (|r| > 0.7)
            if abs(r_value) > 0.7:
                strong_corrs.append({
                    "col_1": col1,
                    "col_2": col2,
                    "correlation": round(r_value, 2),
                    "strength": "Very Strong" if abs(r_value) > 0.9 else "Strong"
                })
                
    return strong_corrs

def run_statistical_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Master function to run all statistical checks on the dataframe.
    """
    stats_profile = {
        "numeric_columns": {},
        "correlations": compute_correlations(df)
    }
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    for col in numeric_cols:
        series = df[col]
        stats_profile["numeric_columns"][col] = {
            "outliers": detect_outliers_iqr(series),
            "skewness": analyze_skewness(series),
            "variability": analyze_variability(series)
        }
        
    return stats_profile