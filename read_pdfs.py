import os
from pypdf import PdfReader

def read_pdf(filename):
    print(f"--- Reading {filename} ---")
    try:
        reader = PdfReader(filename)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        print(text)
    except Exception as e:
        print(f"Error reading {filename}: {e}")
    print(f"--- End of {filename} ---")

if __name__ == "__main__":
    read_pdf("project_description.pdf")
    read_pdf("stage1_report.pdf")
