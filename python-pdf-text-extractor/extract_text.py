import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog
import os

def extract_text_from_pdf(pdf_path):
    """Extracts text from a given PDF file."""
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text("text") + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    
    return text

def select_pdf_and_extract():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    pdf_path = filedialog.askopenfilename(title="Select a PDF file", filetypes=[("PDF Files", "*.pdf")])
    if pdf_path:
        extracted_text = extract_text_from_pdf(pdf_path)
        save_text_to_file(extracted_text, pdf_path)
    else:
        print("No file selected.")

def save_text_to_file(text, pdf_path):
    output_folder = os.path.join(os.getcwd(), "extracted_texts")
    os.makedirs(output_folder, exist_ok=True)
    
    text_file_name = os.path.basename(pdf_path).replace(".pdf", "_extracted.txt")
    text_file_path = os.path.join(output_folder, text_file_name)
    
    with open(text_file_path, "w", encoding="utf-8") as text_file:
        text_file.write(text)
    print(f"Extracted text saved to: {text_file_path}")

if __name__ == "__main__":
    select_pdf_and_extract()
