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

st.set_page_config(layout='wide')

openai_api_key = st.text_input('Enter your OPEN API Key here', type='password')

# Initialize the OpenAI embeddings if API key is provided
if openai_api_key:
    llm = OpenAI(api_key=openai_api_key)
    # Define the prompt template for comparison
    prompt_template = PromptTemplate(
        input_variables=["doc1", "doc2"],
        template="""Compare these two documents and provide a detailed analysis:

        Document 1:
        {doc1}

        Document 2:
        {doc2}

        **Candidate Fit Analysis**
        1. Assess if the candidate is a good fit for the position based on the Job Description and Resume.
        2. Describe how the candidate's skills align with the job requirements."""

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





    col1, col2 = st.columns(2)

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
            st.write("Comparing documents using Langchain LLM...")
            time.sleep(1)
            comparison_result = compare_documents(text_1, text_2)
            # Display the full comparison result in an expander
            with st.expander("Show Full Comparison Result"):
                st.write(comparison_result)

    with col2:
        if uploaded_file_1:
            if uploaded_file_1.type == "application/pdf":
                st.write("Displaying the first PDF:")
                uploaded_file_1.seek(0)  # Reset file pointer before displaying
                pdf_bytes_1 = uploaded_file_1.read()  # Convert to bytes
                pdf_viewer(pdf_bytes_1, height=600)  # Set height to make it scrollable

        if uploaded_file_2:
            if uploaded_file_2.type == "application/pdf":
                st.write("Displaying the second PDF:")
                uploaded_file_2.seek(0)  # Reset file pointer before displaying
                pdf_bytes_2 = uploaded_file_2.read()  # Convert to bytes
                pdf_viewer(pdf_bytes_2, height=600)

