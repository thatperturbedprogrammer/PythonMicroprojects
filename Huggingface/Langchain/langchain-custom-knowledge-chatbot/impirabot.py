import os
from dotenv import load_dotenv
from transformers import pipeline
import gradio as gr

load_dotenv()  # Load API key from .env file

# Initialize the document-question-answering pipeline
nlp = pipeline(
    "document-question-answering",
    model="impira/layoutlm-document-qa",
)

def chatbot(image_url, query):
    """Processes user queries on document images and returns AI-generated responses."""
    response = nlp(image_url, query)
    print(nlp(image_url, query))
    return response["answer"] if response else "No answer found."

interface = gr.Interface(
    fn=chatbot,
    inputs=["text", "text"],
    outputs="text",
    title="Document QA Chatbot",
    description="Upload an image URL of a document and ask a question about it."
)

interface.launch()
