import os
from agents.resume_pipeline_agent import root_agent
from utils.pdf_loader import convert_pdfs_to_json

agent = root_agent  

if __name__ == "__main__":
    if not os.path.exists("data/resumes.json") or os.path.getsize("data/resumes.json") == 0:
        print("resumes.json not found or is empty. Running PDF conversion...")
        convert_pdfs_to_json()
        print("PDF conversion complete.")

    while True:
        query = input("Enter resume search query (or type 'exit' to quit): ")
        if query.lower() in ["exit", "quit"]:
            break
        output = root_agent.run(input_data=query)
        print("\nTop Candidates:\n")
        print(output.get('final_output', 'Sorry, something went wrong.'))
        print("\n" + "-"*50 + "\n")
