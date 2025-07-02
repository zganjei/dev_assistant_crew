import os, tempfile, subprocess
import io
import sys
from contextlib import redirect_stdout, redirect_stderr
from flake8.main.cli import main as flake8_main

def analyze_python_code_style(code_content: str) -> dict:
    """
    Analyzes Python code style and provides feedback.
    It writes the code to a temporary file and runs flake8 on it, captures the output, and returns it,
    and then cleans up the temporary file.
    Args:
        code_content: The content of the Python code to analyze.
    Returns:
        A dictionary containing the analysis results.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
        temp_file.write(code_content)
        temp_file_path = temp_file.name
    #2. redirect stdout and stderr to capture Flake8 output
    try:
        # Run flake8 using subprocess
        result = subprocess.run(
            ["flake8", "--isolated", temp_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        feedback = []
        if result.stdout:
            # Parse Flake8 output: "filename:line:col: E/W code message"
            for line in result.stdout.splitlines():
                parts = line.split(":", 3) # Split only 3 times to get filename, line, col, and code
                if len(parts) == 4:
                    feedback.append(parts[3].strip()) # Extracts only the message part
                else:
                    feedback.append(line.strip()) # Fallback for unexpected format

        if not feedback:
            return {"status": "success", "feedback": "Code looks good! No style issues found!"}
        
        return {"status": "success", "message": "Flake8 found style issues", "feedback": feedback}
    
    except Exception as e:
        return {"status": "error", "message": f"Error analyzing code with Flake8: {str(e)}"}
    finally:
        # 5. Clean up the temporary file and directory
        os.remove(temp_file_path)

# Example Usage (for testing)
if __name__ == "__main__":
    good_code = """
def hello_world():
    print("Hello, world!")
"""

    bad_code_indentation = """
def hello_world():
  print("Hello, world!")
"""

    bad_code_long_line = """
def very_long_function_name_that_exceeds_the_typical_line_length_limit_of_seventy_nine_characters_for_pep8_compliance():
    print("This line is way too long and will trigger a style warning or error.")
"""

    print("--- Analyzing Good Code ---")
    result_good = analyze_python_code_style(good_code)
    print(result_good)
    print("\n--- Analyzing Bad Indentation Code ---")
    result_bad_indent = analyze_python_code_style(bad_code_indentation)
    print(result_bad_indent)
    print("\n--- Analyzing Bad Long Line Code ---")
    result_bad_long_line = analyze_python_code_style(bad_code_long_line)
    print(result_bad_long_line)
    print("\n--- Analyzing Code with Syntax Error (Flake8 might catch this or crash) ---")
    result_syntax_error = analyze_python_code_style("def test_func:\n    pass")
    print(result_syntax_error)

