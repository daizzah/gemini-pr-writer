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
    Retrieves the git diff, handling the edge case of the very first commit.
    """
    try:
        subprocess.run(
            ["git", "config", "--global", "--add", "safe.directory", "/github/workspace"],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Warning: Failed to set git config safe.directory: {e}")

    try:
        result = subprocess.run(
            ["git", "diff", "HEAD~1", "HEAD"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        try:
            result = subprocess.run(
                ["git", "show", "--format=", "HEAD"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError:
            return None

def generate_pr_output(diff_text):
    prompt = f"""
    Review this diff. Strict formatting:

    ## 📝 Summary
    - 1-2 bullets on changes.

    ---

    ## 🛡️ Issues
    - Critical bugs/security only. 1 line each.
    - Skip if clean.

    ## 💡 Improvements
    - Top 3 clean code tips (naming, DRY).
    - 1 line each. No code blocks. No lectures.

    DIFF:
    {diff_text}
    """
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    diff = get_git_diff()
    
    if diff:
        output = generate_pr_output(diff)
        
        workspace = "/github/workspace"
        output_path = os.path.join(workspace, "pr_output.md") if os.path.exists(workspace) else "pr_output.md"
        
        with open(output_path, "w") as f:
            f.write(output)
            
        print(f"Output saved to {output_path}")
    else:
        print("No diff found.")