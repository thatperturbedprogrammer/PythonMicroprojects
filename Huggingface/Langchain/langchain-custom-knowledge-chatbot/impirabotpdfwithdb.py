import os
import sqlite3
import gradio as gr
import PyPDF2
from transformers import pipeline

# Initialize SQLite database
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

# Create users table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT
)
""")
conn.commit()

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
    return response["answer"] if response else "No answer found."

def signup(email, password):
    """User sign-up function"""
    try:
        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        return f"User {email} created successfully!"
    except sqlite3.IntegrityError:
        return "User already exists!"

def login(email, password):
    """User login function"""
    cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
    user = cursor.fetchone()
    if user:
        return f"Welcome back, {email}!"
    return "Invalid email or password!"

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

qa_interface = gr.Interface(
    fn=chatbot,
    inputs=["file", "text"],
    outputs="text",
    title="PDF-Based QA Chatbot",
    description="Upload a PDF document and ask a question about its contents.",
)

# Launch all interfaces
gr.TabbedInterface([signup_interface, login_interface, qa_interface], ["Sign Up", "Login", "Chatbot"]).launch()

# Close database connection when done
conn.close()
