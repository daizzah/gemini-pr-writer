import os
import google.generativeai as genai

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Please set it in your environment.")

genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-flash-latest')

def generate_pr_description(diff_text):
    """
    Sends the diff text to Gemini and returns a PR description.
    """
    prompt = f"""
    You are a helpful DevOps assistant. 
    Below is a git diff of a code change. 
    Please write a concise Pull Request description explaining what changed.
    
    DIFF:
    {diff_text}
    """
    
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    try:
        with open("dummy_diff.txt", "r") as f:
            diff_content = f.read()
            
        print("--- Sending Diff to Gemini ---")
        description = generate_pr_description(diff_content)
        
        print("\n--- Generated Description ---")
        print(description)
        
    except FileNotFoundError:
        print("Error: dummy_diff.txt not found.")
    except Exception as e:
        print(f"An error occurred: {e}")