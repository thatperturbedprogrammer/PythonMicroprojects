import os
import sqlite3
import gradio as gr
import PyPDF2
from transformers import pipeline

# Initialize SQLite database
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

# Create tables for users and PDFs
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    password TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS pdfs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    pdf_name TEXT NOT NULL,
    pdf_content TEXT NOT NULL,
    FOREIGN KEY(email) REFERENCES users(email)
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

def chatbot(email, pdf_file, query):
    """Processes user queries on provided PDF and returns AI-generated responses."""
    cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
    if not cursor.fetchone():
        return "You must be logged in to use the chatbot."
    
    context = extract_text_from_pdf(pdf_file)
    cursor.execute("INSERT INTO pdfs (email, pdf_name, pdf_content) VALUES (?, ?, ?)", (email, pdf_file.name, context))
    conn.commit()
    
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
    if cursor.fetchone():
        return f"Welcome back, {email}!"
    return "Invalid email or password!"

def logout(email):
    """User logout function"""
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

# Close the database connection when done
conn.close()
