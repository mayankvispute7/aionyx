# app/services/validator.py
from typing import List, Dict, Any

def validate_analysis_intent(profile: Dict[str, Any], question: str) -> Dict[str, Any]:
    """
    Analyzes the user's question and the dataset profile to determine
    if the request is mathematically valid.
    """
    
    # 1. Extract potential target columns from the question
    # (Simple keyword matching against column names in the profile)
    found_columns = []
    columns_info = {col['name']: col for col in profile['columns']}
    
    for col_name in columns_info.keys():
        # Case-insensitive check if column name is in question
        if col_name.lower() in question.lower():
            found_columns.append(columns_info[col_name])

    # 2. Heuristic: Detect Intent (Simplified)
    intent = "general_query"
    question_lower = question.lower()
    
    if any(word in question_lower for word in ["average", "mean", "sum", "median", "max", "min"]):
        intent = "aggregation"
    elif any(word in question_lower for word in ["correlation", "relationship", "trend", "predict"]):
        intent = "correlation"
    elif any(word in question_lower for word in ["distribution", "histogram", "breakdown", "count"]):
        intent = "distribution"

    # 3. Validation Logic (The Guardrail)
    validation_result = {
        "is_valid": True,
        "intent": intent,
        "found_columns": [c['name'] for c in found_columns],
        "suggestion": "Proceed with analysis.",
        "warning": None
    }

    # RULE 1: Aggregation requires Numeric columns
    if intent == "aggregation":
        for col in found_columns:
            # If the user asks for "Average Name", we reject it.
            if col['dtype'] not in ['int64', 'float64', 'int', 'float']:
                validation_result["is_valid"] = False
                validation_result["warning"] = f"Cannot calculate {intent} on text column '{col['name']}'."
                validation_result["suggestion"] = "Try counting unique values instead."

    # RULE 2: Correlation requires at least 2 columns
    if intent == "correlation":
        if len(found_columns) < 2 and len(profile['columns']) > 1:
             # This is a soft warning, not a hard reject
             validation_result["warning"] = "Correlation usually requires two specific variables."
             
    return validation_result