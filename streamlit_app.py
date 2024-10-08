import streamlit as st
from PIL import Image
import fitz  # PyMuPDF
import pytesseract
import io
import time
from docx import Document  # Import Document class
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from streamlit_pdf_viewer import pdf_viewer

st.set_page_config(layout='wide',page_title='Resume Processing | The Round Coder',page_icon=':pencil:')

st.title('CV Processing ')
st.write('This app allows you to do pre-screening of the resumes and job descriptions. You can upload two documents in PDF')
st.write('1st document should be the Job Description and 2nd document should be the Resume. The app will extract the text from the documents and compare them using the Langchain Language Model (LLM).')

openai_api_key = st.text_input('Enter your OPEN API Key here', type='password')

# Initialize the OpenAI embeddings if API key is provided
if openai_api_key:
    llm = OpenAI(api_key=openai_api_key)
    # Define the prompt template for comparison
    prompt_template = PromptTemplate(
        input_variables=["doc1", "doc2"],
        template="""Compare these two documents and provide a detailed analysis:
        {doc1} is the Job Description and {doc2} is the Resume.
        Provide the following information:
        1. How does the candidate's skills align with the job requirements?
        2. What are the candidate's strengths and weaknesses?
        3. Does the candidate have any relevant experience for the job position?
        4. How does the candidate's education and work history align with the job requirements?
        5. Any other relevant information that could help in evaluating the candidate's fit for the role?
        Provide the analysis in bullet point format."""

    )

    ## Initialize the LLM chain with the prompt template
    chain = LLMChain(llm=llm, prompt=prompt_template)


    def extract_text_from_pdf(file):
        text = ""
        pdf_document = fitz.open(stream=file.read(), filetype="pdf")
        num_pages = len(pdf_document)
        progress_bar = st.progress(0)

        for page_num in range(num_pages):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
            progress_bar.progress((page_num + 1) / num_pages)
            time.sleep(0.1)  # Simulate processing time

        return text


    def compare_documents(doc1, doc2):
        return chain.run({"doc1": doc1, "doc2": doc2})





    col1, col2, col3 = st.columns(3)

    with col1:
        uploaded_file_1 = st.file_uploader("Upload the Job Description", type=["pdf", "docx", "txt"], key="file1")
        uploaded_file_2 = st.file_uploader("Upload the Resume", type=["pdf", "docx", "txt"], key="file2")

        if uploaded_file_1:
            if uploaded_file_1.type == "application/pdf":
                st.write("Extracting text from the first PDF...")
                text_1 = extract_text_from_pdf(uploaded_file_1)

        if uploaded_file_2:
            if uploaded_file_2.type == "application/pdf":
                st.write("Extracting text from the second PDF...")
                text_2 = extract_text_from_pdf(uploaded_file_2)

    if uploaded_file_1 and uploaded_file_2:
        st.write("Processing Documents........")
        time.sleep(1)
        comparison_result = compare_documents(text_1, text_2)
        with st.expander("Show Full Comparison Result"):
            st.write(comparison_result)

    with col2:
        if uploaded_file_1:
            if uploaded_file_1.type == "application/pdf":
                st.write("Displaying the first PDF:")
                uploaded_file_1.seek(0)  # Reset file pointer before displaying
                pdf_bytes_1 = uploaded_file_1.read()  # Convert to bytes
                pdf_viewer(pdf_bytes_1, height=600)  # Set height to make it scrollable
    with col3:
        if uploaded_file_2:
            if uploaded_file_2.type == "application/pdf":
                st.write("Displaying the second PDF:")
                uploaded_file_2.seek(0)  # Reset file pointer before displaying
                pdf_bytes_2 = uploaded_file_2.read()  # Convert to bytes
                pdf_viewer(pdf_bytes_2, height=600)



