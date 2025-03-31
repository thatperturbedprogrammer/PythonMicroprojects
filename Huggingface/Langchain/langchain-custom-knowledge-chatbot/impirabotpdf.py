import os
from dotenv import load_dotenv
from transformers import pipeline
import gradio as gr
import PyPDF2

load_dotenv()  # Load API key from .env file

# Initialize the question-answering pipeline
nlp = pipeline(
    "question-answering",
    model="distilbert-base-cased-distilled-squad",
)

def extract_text_from_pdf(pdf_file):
    """Extracts text from a PDF file."""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def chatbot(pdf_file, query):
    """Processes user queries on provided PDF and returns AI-generated responses."""
    context = extract_text_from_pdf(pdf_file)
    response = nlp(question=query, context=context)
    print(response)
    return response["answer"] if response else "No answer found."

interface = gr.Interface(
    fn=chatbot,
    inputs=["file", "text"],
    outputs="text",
    title="PDF-Based QA Chatbot",
    description="Upload a PDF document and ask a question about its contents."
)

interface.launch()
