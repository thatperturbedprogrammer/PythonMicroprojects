import sqlite3
import tkinter as tk
from tkinter import ttk

# Function to fetch and display data
def fetch_data():
    # Clear existing data
    for row in user_table.get_children():
        user_table.delete(row)
    for row in pdf_table.get_children():
        pdf_table.delete(row)

    # Connect to the database
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Fetch users
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    for user in users:
        user_table.insert("", "end", values=user)

    # Fetch PDFs
    cursor.execute("SELECT * FROM pdfs")
    pdfs = cursor.fetchall()
    for pdf in pdfs:
        pdf_table.insert("", "end", values=pdf)

    # Close connection
    conn.close()

# Create GUI window
root = tk.Tk()
root.title("Admin Database Viewer")
root.geometry("600x400")

# Label for Users
tk.Label(root, text="User Records", font=("Arial", 12, "bold")).pack()

# User Table
user_table = ttk.Treeview(root, columns=("Email", "Password"), show="headings")

user_table.heading("Email", text="Email")
user_table.heading("Password", text="Password")
user_table.pack(fill="x", padx=10, pady=5)

# Label for PDFs
tk.Label(root, text="Uploaded PDFs", font=("Arial", 12, "bold")).pack()

# PDF Table
pdf_table = ttk.Treeview(root, columns=("ID", "User Email", "File Name"), show="headings")
pdf_table.heading("ID", text="ID")
pdf_table.heading("User Email", text="User Email")
pdf_table.heading("File Name", text="File Name")
pdf_table.pack(fill="x", padx=10, pady=5)

# Refresh Button
refresh_btn = tk.Button(root, text="Refresh Data", command=fetch_data)
refresh_btn.pack(pady=10)

# Load data initially
fetch_data()

# Run GUI
root.mainloop()
