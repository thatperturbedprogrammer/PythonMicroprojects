import os
from dotenv import load_dotenv
from transformers import pipeline
import gradio as gr

load_dotenv()  # Load API key from .env file

# Initialize the question-answering pipeline
nlp = pipeline(
    "question-answering",
    model="distilbert-base-cased-distilled-squad",
)

def chatbot(context, query):
    """Processes user queries on provided text and returns AI-generated responses."""
    response = nlp(question=query, context=context)
    print(response)
    return response["answer"] if response else "No answer found."

interface = gr.Interface(
    fn=chatbot,
    inputs=["text", "text"],
    outputs="text",
    title="Text-Based QA Chatbot",
    description="Enter a passage of text and ask a question about it."
)

interface.launch()
