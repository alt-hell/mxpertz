import streamlit as st
import requests

st.set_page_config(page_title="AI Resume Screener", page_icon="📄", layout="wide")

st.title("📄 AI Resume Skill Extractor & Analyzer")
st.markdown("Upload resumes (PDF/DOCX) and compare them against a Job Description to accurately extract skills and total experience.")

# Job Description Input
st.subheader("1. Job Description")
job_description = st.text_area("Paste the Job Description here:", height=150, placeholder="e.g., We are looking for a Python developer with FastAPI and PostgreSQL experience...")

# File Uploader
st.subheader("2. Upload Resumes")
uploaded_files = st.file_uploader("Choose PDF or DOCX files", type=['pdf', 'docx'], accept_multiple_files=True)

# Screen Button
if st.button("Screen Resumes", type="primary"):
    if not job_description.strip():
        st.error("Please enter a Job Description.")
    elif not uploaded_files:
        st.error("Please upload at least one resume.")
    else:
        with st.spinner("Analyzing resumes using HF LLM..."):
            # Prepare files for API request
            files_payload = []
            for file in uploaded_files:
                # API expects a tuple: ('field_name', (filename, file_bytes, content_type))
                files_payload.append(
                    ("files", (file.name, file.getvalue(), file.type))
                )
            
            data = {"job_description": job_description}
            
            # Send to FastAPI backend
            try:
                response = requests.post("http://127.0.0.1:8000/match_files", data=data, files=files_payload)
                
                if response.status_code == 200:
                    results = response.json().get("results", [])
                    
                    st.success(f"Successfully analyzed {len(results)} resumes!")
                    
                    # Sort results by score descending
                    results_sorted = sorted(results, key=lambda x: x['match_score'], reverse=True)
                    
                    # Display results nicely using expanders
                    for result in results_sorted:
                        with st.expander(f"Applicant: {result['resume_id']} | Match Score: {result['match_score']}%", expanded=True):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.metric("Match Score", f"{result['match_score']}%")
                                st.markdown("**Matched Skills:**")
                                if result['matched_skills']:
                                    st.success(", ".join(result['matched_skills']))
                                else:
                                    st.warning("None identified")
                                    
                            with col2:
                                st.metric("Total Experience", result['total_experience'])
                                st.markdown("**Missing Skills:**")
                                if result['missing_skills']:
                                    st.error(", ".join(result['missing_skills']))
                                else:
                                    st.success("None! Perfect match.")
                                    
                            st.markdown("---")
                            st.markdown("**All Skills Found in Resume:**")
                            if result.get('extracted_skills'):
                                st.info(", ".join(result['extracted_skills']))
                            else:
                                st.warning("No recognized skills found in resume.")
                                
                            st.markdown(f"**AI Explanation:** {result['explanation']}")
                            
                else:
                    st.error(f"Error from API: {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Failed to connect to the backend API. Please make sure you have started the backend by running `uvicorn main:app --reload` in your terminal.")
