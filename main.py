import os 
from PIL import Image
import streamlit as st
from streamlit_option_menu import option_menu
from utills import (
    gemini_pro_vision_response,
    read_pdf_or_docx,
    markdown_to_pdf,
    create_download_link
)
from io import StringIO
from streamlit_pdf_viewer import pdf_viewer
import os
import streamlit as st
import tempfile
from pathlib import Path
import base64


# Set page config to wide mode
st.set_page_config(layout="wide")

working_dir = os.path.dirname(os.path.abspath(__file__))

print(working_dir)
    
# Streamlit page title with custom styling
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .main > div {
            padding: 2rem 1rem;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🎞️ Resume Analyser")
uploaded_file = st.file_uploader("Upload an Resume...", type=['pdf', 'docx', 'doc'])

if st.button("Analyse Resume"):
    pdf_bytes = uploaded_file.read()
    
    # Create full-width columns
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        # Check if the uploaded file is pdf or docx
        if uploaded_file.type in ['application/pdf', 'application/docx', 'application/doc']:
            text = read_pdf_or_docx(uploaded_file)
            pdf_viewer(pdf_bytes)
        else:
            text = "Please upload a valid pdf or docx file"

    default_prompt = """Please convert the resume into json format with following keys:
    1. name
    2. summary
    3. contact:[email, phone, location, linkedin]
    4. work_experience:[role, company, dates, responsibilities]
    5. education:[degree, institution, graduation_year]
    6. awards:[award1, award2, ...]
    7. skills:[]
    8. projects:[]
    9. certifications:[cert1, cert2, ...]
    10. languages:[lang1, lang2, ...]
    11. interests:[interest1, interest2, ...]
    12. references:[ref1, ref2, ...]
    13. hobbies:[hobby1, hobby2, ...]
    14. publications:[pub1, pub2, ...]
    15. patents:[pat1, pat2, ...]
    16. volunteer_experience:[vol1, vol2, ...]
    17. courses:[course1, course2, ...]

    Please produce the resume in the above format json with following key names.
    """
    default_prompt2 = """Question1: Does Resume Has all Mandatory Sections like 
    name, summary, contact, work_experience, education, skills, certifications?
    Question2: Does Resume has followed the order of sections correctly? Ex: Name, Summary, Contact, Work Experience, Education, Skills, Certifications
    Question3: Does Resume has all the required information in each section? if not mention the missing information.
    Question4: Does Resume has followed reverse chronological order for work experience and education?
    Question5: Does Candidate has any gaps in work experience? if yes, mention the gaps.
    Question6: Does Candidate has any gaps in education? if yes, mention the gaps.
    Question7: Does Candidate has done career transition? if yes, then mention the transition in summary section.
    Question8: Does Resume has any spelling mistakes? if yes, mention the mistakes.
    Question9: Does Resume has any grammatical mistakes? if yes, mention the mistakes.
    """

    # Getting response from gemini-1.5-flash model
    json_resume = gemini_pro_vision_response(default_prompt, text)

    # Check problems in the resume
    caption2 = gemini_pro_vision_response(default_prompt2, json_resume)
    
    caption3 = gemini_pro_vision_response(
        "Please make changes suggested to the resume and produce resume in markdown format",
        json_resume + caption2
    )
    
    with col2:
        st.markdown("""
            <style>
                .stInfo {
                    white-space: pre-wrap;
                    word-wrap: break-word;
                }
            </style>
        """, unsafe_allow_html=True)
        st.info(caption2)
    st.info(caption3)
    
    # Convert markdown to PDF
    if caption3:  # If we have the markdown content
        pdf_content = markdown_to_pdf(caption3)
        if pdf_content:
            # Create download button
            st.markdown("### Download Modified Resume")
            download_link = create_download_link(pdf_content, "modified_resume.pdf")
            st.markdown(download_link, unsafe_allow_html=True)

