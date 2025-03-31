import os
import gradio as gr
import PyPDF2
from transformers import pipeline

# Simple user database (for testing purposes)
users = {}
logged_in_users = set()

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

def chatbot(email, pdf_file, query):
    """Processes user queries on provided PDF and returns AI-generated responses."""
    if email not in logged_in_users:
        return "You must be logged in to use the chatbot."
    context = extract_text_from_pdf(pdf_file)
    response = nlp(question=query, context=context)
    return response["answer"] if response else "No answer found."

def signup(email, password):
    """User sign-up function"""
    if email in users:
        return "User already exists!"
    users[email] = password
    return f"User {email} created successfully!"

def login(email, password):
    """User login function"""
    if users.get(email) == password:
        logged_in_users.add(email)
        return f"Welcome back, {email}!"
    return "Invalid email or password!"

def logout(email):
    """User logout function"""
    logged_in_users.discard(email)
    return f"User {email} has been logged out."

# Gradio Interface
signup_interface = gr.Interface(
    fn=signup,
    inputs=["text", "text"],
    outputs="text",
    title="Sign Up",
    description="Create a new account.",
)

login_interface = gr.Interface(
    fn=login,
    inputs=["text", "text"],
    outputs="text",
    title="Login",
    description="Enter your email and password to log in.",
)

logout_interface = gr.Interface(
    fn=logout,
    inputs=["text"],
    outputs="text",
    title="Logout",
    description="Log out from your account.",
)

qa_interface = gr.Interface(
    fn=chatbot,
    inputs=["text", "file", "text"],
    outputs="text",
    title="PDF-Based QA Chatbot",
    description="Upload a PDF document and ask a question about its contents. You must be logged in to use this feature.",
)

# Launch all interfaces
gr.TabbedInterface([signup_interface, login_interface, logout_interface, qa_interface], ["Sign Up", "Login", "Logout", "Chatbot"]).launch()
