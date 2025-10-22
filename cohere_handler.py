# cohere_handler.py

import streamlit as st
import cohere

# Initialize Cohere client with API key from Streamlit secrets
co = cohere.Client(st.secrets["general"]["COHERE_API_KEY"])

def explain_code(code: str, language: str = "python") -> str:
    """
    Explains the given code in simple, step-by-step terms using Cohere API.
    """
    prompt = f"Explain the following {language} code in simple terms:\n\n{code}"

    response = co.chat(
        model="command-a-03-2025",  # Updated model name to supported one
        message=prompt,
        temperature=0.5
    )

    return response.text.strip()

def analyze_code(code: str, language: str = "python", advanced: bool = False) -> dict:
    """
    Analyzes code using Cohere API.
    Returns feedback, warnings, and errors.
    """
    prompt = f"""You are a {language} code reviewer. Analyze this code and:
    - Identify potential bugs with line numbers
    - Provide improvement suggestions (mark as [SUGGESTION])
    - Recommend best practices
    { '[Include detailed technical analysis]' if advanced else '' }

    Code:
    {code}"""

    response = co.chat(
    model="command-a-03-2025",  # Use the current main supported model
    message=prompt,
    temperature=0.5
)

    

    return {
        "feedback": response.text.strip(),
        "warnings": [],  # Placeholder for structured parsing later
        "errors": []
    }
