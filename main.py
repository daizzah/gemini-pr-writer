import os
import subprocess
import google.generativeai as genai

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-flash-latest')

def get_git_diff():
    """
    Smart diff retrieval:
    1. Tries to get the diff between current and previous commit.
    2. If that fails (e.g., first commit), falls back to just showing the current commit.
    """
    try:
        subprocess.run(
            ["git", "config", "--global", "--add", "safe.directory", "/github/workspace"],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Warning: Failed to set git config safe.directory: {e}")

    # Try diff against previous commit
    try:
        result = subprocess.run(
            ["git", "diff", "HEAD~1", "HEAD"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout
        
    except subprocess.CalledProcessError:
        print("Could not diff against previous commit (likely first commit). Switching to fallback...")
        
        # If that fails, show the current commit only (first commit case)
        try:
            result = subprocess.run(
                ["git", "show", "--format=", "HEAD"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error running git show fallback: {e}")
            return None

def generate_pr_description(diff_text):
    prompt = f"""
    You are a helpful DevOps assistant. 
    Below is a git diff of a code change. 
    Write a concise PR description in Markdown format.
    
    DIFF:
    {diff_text}
    """
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    print("--- Extracting Git Diff ---")
    diff = get_git_diff()
    
    if diff:
        print("--- Sending Diff to Gemini ---")
        description = generate_pr_description(diff)
        
        with open("pr_description.md", "w") as f:
            f.write(description)
            
        print("Description saved to pr_description.md")
    else:
        print("No diff found or error occurred.")