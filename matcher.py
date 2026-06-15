import os
import json
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize the Groq client
if GROQ_API_KEY and GROQ_API_KEY != "your_groq_api_key_here":
    client = Groq(api_key=GROQ_API_KEY)
else:
    client = None

def calculate_similarity_and_match(jd_text: str, resume_text: str):
    """Uses a lightning-fast Groq LLM (Llama 3) to extract skills, score the match, and explain."""
    
    if not client:
        raise ValueError("Groq API Key not found. Please add GROQ_API_KEY to your .env file.")
        
    prompt = f"""
You are an expert Technical IT Recruiter. You are given a Job Description (JD) and a Candidate's Resume.
Your task is to analyze them and output a strict JSON object with your findings. Do NOT output any markdown formatting, conversational text, or explanations outside the JSON object.

Job Description:
{jd_text}

Resume:
{resume_text}

Analyze the resume against the JD. First, identify the core role/domain of the candidate (e.g. 'MERN Stack Developer', 'Frontend Engineer') and the core role of the JD (e.g. 'AI/ML Engineer'). 
If the candidate's core expertise is completely different from the job role, your 'explanation' MUST explicitly state: "You are a [Candidate Role], but we are searching for a [JD Role]." followed by a brief elaboration.

Return ONLY a JSON object with this exact structure:
{{
  "match_score": <int between 0 and 100 based on how well the candidate fits the JD skills and experience>,
  "matched_skills": [<list of strings of skills present in BOTH JD and Resume>],
  "missing_skills": [<list of strings of skills required by JD but missing in Resume>],
  "extracted_skills": [<list of strings of ALL technical skills found in the Resume>],
  "total_experience": "<string, e.g., '5 years', or 'Unable to fetch total experience'>",
  "explanation": "<2-3 sentences explaining the score. If there is a major role mismatch, use the 'You are a X, but we are searching for a Y' format as instructed.>"
}}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        output_text = response.choices[0].message.content
        
        # Robust JSON parsing
        json_str = output_text.strip()
        
        # Find the first { and last } in case the LLM outputs markdown wrapper ```json ... ```
        start_idx = json_str.find('{')
        end_idx = json_str.rfind('}')
        if start_idx != -1 and end_idx != -1:
            json_str = json_str[start_idx:end_idx+1]
            
        result = json.loads(json_str)
        
        # Ensure we have all required fields (provide fallbacks)
        return {
            "match_score": result.get("match_score", 0),
            "matched_skills": result.get("matched_skills", []),
            "missing_skills": result.get("missing_skills", []),
            "extracted_skills": result.get("extracted_skills", []),
            "total_experience": result.get("total_experience", "Unable to fetch total experience"),
            "explanation": result.get("explanation", "The model successfully processed the text.")
        }
    except json.JSONDecodeError:
        raise ValueError(f"LLM failed to output valid JSON. Raw output: {output_text}")
    except Exception as e:
        raise ValueError(f"LLM Processing failed. Error: {str(e)}")
