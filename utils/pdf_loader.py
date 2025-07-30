import os
import json
import fitz  # PyMuPDF

PDF_DIR = "D:/AI&DS/cv_job_assignment/resumes"
OUT_JSON = "data/resumes.json"

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = "\n".join([page.get_text() for page in doc])
    return text

def convert_pdfs_to_json():
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(OUT_JSON)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    resumes = []
    if not os.path.exists(PDF_DIR):
        os.makedirs(PDF_DIR)
    for file in os.listdir(PDF_DIR):
        if file.endswith(".pdf"):
            path = os.path.join(PDF_DIR, file)
            name = os.path.splitext(file)[0]
            text = extract_text_from_pdf(path)
            resumes.append({"name": name, "text": text})

    with open(OUT_JSON, "w") as f:
        json.dump(resumes, f, indent=2)

    print(f"Processed {len(resumes)} resumes into resumes.json")

if __name__ == "__main__":
    convert_pdfs_to_json()
