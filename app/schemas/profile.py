from pydantic import BaseModel
from typing import List, Optional, Any

class DatasetSummary(BaseModel):
    total_rows: int
    total_columns: int
    file_size_kb: float
    duplicate_rows: int
    memory_usage_kb: float

class ColumnProfile(BaseModel):
    name: str
    dtype: str
    missing_count: int
    unique_count: int
    mean: Optional[float] = None
    min: Optional[Any] = None
    max: Optional[Any] = None
    
    # --- NEW FIELDS FOR v1.1 ---
    outliers_count: Optional[int] = 0
    skewness: Optional[str] = None
    variability_cv: Optional[str] = None
    # ---------------------------

class Alert(BaseModel):
    type: str
    message: str
    severity: str  # low, medium, high

class ProfileReport(BaseModel):
    filename: str
    summary: DatasetSummary
    columns: List[ColumnProfile]
    alerts: List[str]
    ai_analysis: Optional[str] = None