import pandas as pd
import numpy as np
import io
from app.schemas.profile import ProfileReport, DatasetSummary, ColumnProfile, Alert
from app.services.statistical_engine import run_statistical_analysis  # <--- NEW IMPORT

def analyze_dataset(df: pd.DataFrame, filename: str) -> ProfileReport:
    """
    Analyzes a pandas DataFrame and returns a structured ProfileReport.
    Now enhanced with Statistical Intelligence (v1.1).
    """
    # 1. Basic Summary
    total_rows, total_cols = df.shape
    memory_usage = df.memory_usage(deep=True).sum() / 1024  # KB
    duplicate_rows = df.duplicated().sum()
    
    # 2. Detailed Column Analysis
    columns_profile = []
    alerts = []
    
    # --- NEW: Run Statistical Engine ---
    stats_results = run_statistical_analysis(df)
    # -----------------------------------

    for col in df.columns:
        dtype = str(df[col].dtype)
        missing = df[col].isnull().sum()
        unique = df[col].nunique()
        
        # Basic Stats
        col_stats = {
            "name": col,
            "dtype": dtype,
            "missing_count": int(missing),
            "unique_count": int(unique),
            "mean": None,
            "min": None,
            "max": None,
            # Placeholder for new stats (merged below)
            "outliers_count": 0,
            "skewness": None,
            "variability_cv": None
        }
        
        # Numeric logic
        if pd.api.types.is_numeric_dtype(df[col]):
            col_stats["mean"] = float(df[col].mean()) if not df[col].isnull().all() else None
            col_stats["min"] = float(df[col].min()) if not df[col].isnull().all() else None
            col_stats["max"] = float(df[col].max()) if not df[col].isnull().all() else None
            
            # --- MERGE STATISTICAL INTELLIGENCE ---
            if col in stats_results["numeric_columns"]:
                stat_data = stats_results["numeric_columns"][col]
                col_stats["outliers_count"] = stat_data["outliers"]["count"]
                col_stats["skewness"] = stat_data["skewness"]["classification"]
                col_stats["variability_cv"] = stat_data["variability"]["classification"]
                
                # Add Smart Alerts
                if stat_data["outliers"]["percentage"] > 5.0:
                    alerts.append(f"Column '{col}' has {stat_data['outliers']['percentage']}% outliers.")
                
                if "High" in stat_data["variability"]["classification"]:
                    alerts.append(f"Column '{col}' is highly volatile (High Variability).")
            # --------------------------------------

        columns_profile.append(ColumnProfile(**col_stats))

    # Add Correlation Alerts
    for corr in stats_results["correlations"]:
        alerts.append(f"Strong Correlation ({corr['correlation']}) between '{corr['col_1']}' and '{corr['col_2']}'. Check for multicollinearity.")

    summary = DatasetSummary(
        total_rows=total_rows,
        total_columns=total_cols,
        file_size_kb=round(memory_usage, 2),
        duplicate_rows=int(duplicate_rows),
        memory_usage_kb=round(memory_usage, 2)
    )

    return ProfileReport(
        filename=filename,
        summary=summary,
        columns=columns_profile,
        alerts=alerts,
        ai_analysis=None 
    )