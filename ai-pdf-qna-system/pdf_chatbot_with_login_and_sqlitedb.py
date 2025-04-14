import os
import sqlite3
import gradio as gr
import PyPDF2
from transformers import pipeline
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load the environment variables (for securely managing the key)
load_dotenv()

# Get the encryption key from the environment variable (secure location)
def get_encryption_key():
    key = os.getenv("ENCRYPTION_KEY")
    if key is None:
        # If the key doesn't exist, generate it and save it securely
        key = Fernet.generate_key()
        with open("encryption_key.key", "wb") as key_file:
            key_file.write(key)
    return key

# Encrypt password before storing it in the database
def encrypt_password(password, key):
    f = Fernet(key)
    encrypted_password = f.encrypt(password.encode())
    return encrypted_password

# Decrypt password when comparing during login
def decrypt_password(encrypted_password, key):
    f = Fernet(key)
    decrypted_password = f.decrypt(encrypted_password).decode()
    return decrypted_password

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

# Extract Text from PDF
def extract_text_from_pdf(pdf_file):
    """Extracts text from a PDF file."""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

# Process user queries on provided PDF and return AI-generated responses
def chatbot(email, pdf_file, query):
    """Processes user queries on provided PDF and returns AI-generated responses."""
    
    cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
    if not cursor.fetchone():
        return "You must be logged in to use the chatbot."
    
    context = extract_text_from_pdf(pdf_file)

    # Check if the PDF already exists in the database for the user
    cursor.execute("SELECT id FROM pdfs WHERE email = ? AND pdf_name = ?", (email, pdf_file.name))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO pdfs (email, pdf_name, pdf_content) VALUES (?, ?, ?)", (email, pdf_file.name, context))
        conn.commit()
    
    response = nlp(question=query, context=context)
    return response["answer"] if response else "No answer found."

# Sign-up function (with encrypted password)
def signup(email, password):
    """User sign-up function"""
    key = get_encryption_key()  # Get the encryption key from secure storage
    encrypted_password = encrypt_password(password, key)
    
    try:
        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, encrypted_password))
        conn.commit()
        return f"User {email} created successfully!"
    except sqlite3.IntegrityError:
        return "User already exists!"

# Login function (with decrypted password comparison)
def login(email, password):
    """User login function"""
    cursor.execute("SELECT email, password FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    if user:
        # Get the encryption key from secure storage
        key = get_encryption_key()  
        # Decrypt the stored password and compare
        decrypted_password = decrypt_password(user[1], key)
        if decrypted_password == password:
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
    title="AI PDF Q&A System",
    description="Upload a PDF document and ask a question about its contents. You must be logged in to use this feature.",
)

# Launch all interfaces
gr.TabbedInterface([signup_interface, login_interface, logout_interface, qa_interface], ["Sign Up", "Login", "Logout", "Chatbot"]).launch()

# Close the database connection when done
conn.close()
