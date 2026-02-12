import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Load Config
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY not found.")

genai.configure(api_key=api_key)

# --- FIX: Using the model that worked in Phase 1 ---
model = genai.GenerativeModel('gemini-flash-latest')

def calculate_data_confidence(profile: dict) -> dict:
    """
    Determines how trustworthy the dataset is based on size and missing data.
    """
    stats = {
        "score": "LOW",
        "completeness": 0.0,
        "sample_size": profile['summary']['total_rows'],
        "warnings": []
    }

    # 1. Calculate Completeness (How much data is missing?)
    total_cells = profile['summary']['total_rows'] * profile['summary']['total_columns']
    total_missing = sum(c['missing_count'] for c in profile['columns'])
    
    if total_cells > 0:
        stats['completeness'] = round(((total_cells - total_missing) / total_cells) * 100, 1)
    else:
        stats['completeness'] = 0

    # 2. Determine Confidence Score
    # Rule A: Sample Size
    if stats['sample_size'] < 50:
        stats['score'] = "LOW (Insufficient Data)"
        stats['warnings'].append("Sample size is too small for statistical significance.")
    elif stats['sample_size'] < 200:
        stats['score'] = "MEDIUM"
    else:
        stats['score'] = "HIGH"

    # Rule B: Missing Data Penalty
    if stats['completeness'] < 80:
        stats['score'] = "LOW (Poor Data Quality)"
        stats['warnings'].append(f"Data is only {stats['completeness']}% complete.")

    return stats

def generate_data_story(profile_dict: dict) -> str:
    """
    Sends metadata to Gemini with a calculated Confidence Score and Statistical Context.
    """
    # 1. Get the Confidence Metrics first
    confidence = calculate_data_confidence(profile_dict)
    
    # 2. Convert profile to JSON string for the AI to read
    profile_text = json.dumps(profile_dict, indent=2)

    # 3. Inject Confidence & Stats into the Prompt
    prompt = f"""
    You are a Senior Data Scientist. Write an executive summary for this dataset.
    
    DATA PROFILE:
    {profile_text}

    SYSTEM METRICS (DO NOT IGNORE):
    - Reliability Score: {confidence['score']}
    - Data Completeness: {confidence['completeness']}%
    - Critical Warnings: {', '.join(confidence['warnings'])}

    NEW STATISTICAL INTELLIGENCE INSTRUCTIONS:
    1. **Outliers:** Look at the 'outliers_count' in the column data. If high (>5%), flag potential anomalies or fraud.
    2. **Skewness:** Look at 'skewness'. If 'Highly Skewed', mention that averages (mean) might be misleading compared to the median.
    3. **Variability:** Look at 'variability_cv'. High variability means instability/risk.
    4. **Correlations:** Check the 'alerts' list for any "Strong Correlation" warnings. Explain what they might mean (e.g., "A correlates with B").

    REPORT STRUCTURE:
    1. Start with the **Reliability Score** in bold.
    2. **Executive Overview:** What is this dataset about?
    3. **Statistical Deep Dive:** Discuss the distribution shapes (skewness), outliers, and stability.
    4. **Data Quality & Correlations:** Mention missing values and any strong relationships found.
    5. **Strategic Recommendations:** Suggest 3 analytical questions based on these findings.

    Tone: Professional, Objective, Cautious (if Low reliability).
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Analysis failed: {str(e)}"

def ask_data_question(profile_dict: dict, user_question: str) -> str:
    """
    Answers user questions with context about data limitations.
    """
    confidence = calculate_data_confidence(profile_dict)
    profile_text = json.dumps(profile_dict, indent=2)
    
    prompt = f"""
    You are a Data Analyst. Answer the user question based on this profile.
    
    DATA PROFILE:
    {profile_text}
    
    CONTEXT:
    - The data reliability is: {confidence['score']}
    - If the user asks for predictions or trends and reliability is LOW, add a disclaimer: "Caution: Sample size is small."
    - Use the 'skewness', 'outliers_count', and 'variability_cv' fields to give smarter answers (e.g., "The average is X, but the data is skewed, so the median is better").

    USER QUESTION:
    "{user_question}"
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"