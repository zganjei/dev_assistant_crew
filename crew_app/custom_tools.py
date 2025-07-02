import os
import requests
from crewai.tools import tool
import datetime

# Base URL for your Git MCP Service (should be running on port 8000)
MCP_GIT_SERVICE_URL = os.getenv("MCP_GIT_SERVICE_URL", "http://localhost:8000/mcp")

# Base URL for your Code Analysis MCP Service (running on port 8001)
MCP_CODE_ANALYSIS_SERVICE_URL = os.getenv("MCP_CODE_ANALYSIS_SERVICE_URL", "http://localhost:8001/mcp")


class GitTools:
    @tool("Clone Git Repository")
    def clone_repo(repo_url: str, branch: str = "main") -> str:
        """
        Clones a git repository to a temporary directory.
        Args:
            repo_url: The URL of the git repository to clone
            branch: The branch to clone (default: main)
            local_path: The path to clone the repository to (default: None)
        Returns:
            A string containing the local path where the repository was cloned to
        """
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        # Create a mock local path, in a real scenario this would be a real directory
        local_path = os.path.join("temp_repos", f"{repo_name}_{timestamp}")
        response = requests.post(f"{MCP_GIT_SERVICE_URL}/git/clone", json={
            "repo_url": repo_url,
            "branch": branch,
            "local_path": local_path
        })
        
        response.raise_for_status()
        data = response.json()
        if data.get("success"):
            return data.get("local_path", "")
        
        return f"Error cloning repository: {data.get('message', 'Unknown error')}"
        
    @tool("Get Repository Status")
    def get_repo_status(repo_local_path: str) -> str:
        """
        Gets the status of a git repository.
        Args:
            repo_local_path (str): The path to the git repository
        Returns:
            A string containing the status of the repository
        """
        response = requests.post(f"{MCP_GIT_SERVICE_URL}/git/status", json={
            "repo_local_path": repo_local_path
        })
        response.raise_for_status()
        data = response.json()
        if data.get("success"):
            status_data = data.get("data", {})
            return f"Repository status for {repo_local_path}:\n" \
                 f"Branch: {status_data.get('branch', 'Unknown branch')}\n" \
                 f"Is dirty: {status_data.get('is_dirty', False)}\n" \
                 f"Uncommitted changes: {status_data.get('uncommitted_changes_count')}\n" \
                 f"Untracked files: {status_data.get('untracked_files_count')}\n" \
                 f"Modified files: {status_data.get('modified_files')}\n" \
                 f"Deleted files: {status_data.get('deleted_files')}\n" \
                 f"Last commit message: {status_data.get('last_commit_message')}"

        return f"Error getting repository status: {data.get('message', 'Unknown error')}"
    
    @tool("Read File Content")
    def read_file_content(repo_local_path: str, file_path_in_repo: str) -> str:
        """
        Reads the content of a file in a git repository.
        Args:
            repo_local_path (str): The path to the git repository
            file_path_in_repo (str): The path to the file to read
        Returns:
            A string containing the content of the file
        """
        response = requests.post(f"{MCP_GIT_SERVICE_URL}/git/read_file", json={
            "repo_local_path": repo_local_path,
            "file_path_in_repo": file_path_in_repo
        })
        response.raise_for_status()
        data = response.json()
        if data.get("success"):
            return data.get("content")
        return f"Error reading file: {data.get('message', 'Unknown error')}"
    
    @tool("List Repository Contents")
    def list_repo_contents(repo_local_path: str, path_in_repo: str = "") -> str:
        """
        Lists files and directories at a specified path within a cloned repository
        via the MCP Git Service.
        Args:
            repo_local_path (str): The local path of the cloned repository.
            path_in_repo (str, optional): The path within the repo to list. Defaults to root "".
        Returns:
            str: A string representation of the directory contents (name (type) for each item), or an error message.
                 The LLM will need to parse this string.
        """
        payload = {"repo_local_path": repo_local_path, "path_in_repo": path_in_repo}
        response = requests.post(f"{MCP_GIT_SERVICE_URL}/git/list_contents", json=payload)
        response.raise_for_status()
        data = response.json()
        if data.get("success"):
            contents = data.get("contents", [])
            if contents:
                # Format for LLM consumption: "filename (type), another_file (type)"
                formatted_contents = ", ".join([f"{item['name']} ({item['type']})" for item in contents])
                return f"Contents of '{path_in_repo}' in '{repo_local_path}': {formatted_contents}"
            return f"No contents found in '{path_in_repo}' within '{repo_local_path}'."
        return f"Error listing contents: {data.get('detail', 'Unknown error')}"



# --- Code Analysis Tools ---
class CodeAnalysisTools:
    @tool("Analyze Python Code Style")
    def analyze_code_style(code_content: str) -> str:
        """
        Analyzes Python code style with Flake8 and provides feedback.
        """
        payload = {
            "code_content": code_content
        }
       
        response = requests.post(f"{MCP_CODE_ANALYSIS_SERVICE_URL}/code/analyse_style", json=payload)
        response.raise_for_status()
        data = response.json()
        if data.get("success"):
            feedback = data.get("feedback")
            if feedback:
                # Format the feedback nicely for the LLM
                return "Python code style analysis feedback:\n" + "\n".join([f"- {item}" for item in feedback])
            return data.get("message", "No style issues found")
        return f"Error analyzing code style: {data.get('message', 'Unknown error')}"
    
    # @tool("Analyze Python Code Security")
    # def analyze_code_security(code_content: str) -> str:
    #     """