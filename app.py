from dotenv import load_dotenv
import base64
import streamlit as st
import os
import pdfplumber
import google.generativeai as genai

# -------------------
# Load API key
# -------------------
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# -------------------
# Helper Functions
# -------------------
def extract_pdf_text(pdf_path):
    """Extract text from PDF using pdfplumber."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text.strip()

def input_pdf_setup(uploaded_file):
    """Save uploaded PDF and extract its text."""
    pdf_path = "uploaded_resume.pdf"
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.read())
    
    resume_text = extract_pdf_text(pdf_path)
    
    if not resume_text:
        raise ValueError("Could not extract text from the uploaded PDF. It might be a scanned image.")
    
    return resume_text

def get_gemini_response(input_text, resume_text, prompt):
    """Send job description + resume text + prompt to Gemini."""
    model = genai.GenerativeModel("gemini-1.5-flash")  

    if not resume_text:
        return "Could not extract text from the uploaded resume. Please upload a text-based PDF."

    full_input = f"Job Description:\n{input_text}\n\nResume:\n{resume_text}\n\n{prompt}"

    response = model.generate_content([full_input])
    return response.text

# -------------------
# Streamlit App
# -------------------
st.set_page_config(page_title="ATS Resume Expert")
st.header("ResumeRanker - ATS Tracking System")

# Input
input_text = st.text_area("Job Description:", key="input")
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

if uploaded_file is not None:
    st.write("✅ PDF Uploaded Successfully")

# Buttons
submit1 = st.button("Resume Report")
submit3 = st.button("Resume Match Score")

# Prompts
input_prompt1 = """
You are an experienced Technical Human Resource Manager.
Review the provided resume against the job description.
Highlight strengths and weaknesses of the applicant in relation to the job requirements.
"""

input_prompt3 = """
You are a skilled ATS scanner.
Evaluate the resume against the provided job description.
Give me the percentage match first, then missing keywords, then final thoughts.
"""

# -------------------
# Button Actions
# -------------------
if submit1:
    if uploaded_file is not None:
        resume_text = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_text, resume_text, input_prompt1)
        st.subheader("Report:")
        st.write(response)
    else:
        st.write("⚠️ Please upload the resume.")

elif submit3:
    if uploaded_file is not None:
        resume_text = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_text, resume_text, input_prompt3)
        st.subheader("Report:")
        st.write(response)
    else:
        st.write("⚠️ Please upload the resume.")
