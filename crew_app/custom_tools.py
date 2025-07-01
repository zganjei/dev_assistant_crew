import os
import requests
from crewai.tools import tool

MCP_SERVICE_BASE_URL = "http://localhost:8000/mcp"

class GitTools:
    @tool("Clone Git Repository")
    def clone_repo(repo_url: str, branch: str = "main", local_path: str = None) -> str:
        """
        Clones a git repository to a temporary directory.
        Args:
            repo_url: The URL of the git repository to clone
            branch: The branch to clone (default: main)
            local_path: The path to clone the repository to (default: None)
        Returns:
            A string containing the local path where the repository was cloned to
        """
        response = requests.post(f"{MCP_SERVICE_BASE_URL}/git/clone", json={
            "repo_url": repo_url,
            "branch": branch,
            "local_path": local_path
        })
        print(f".............................check {response}")
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
        print(f"222222.........................check ")
        response = requests.post(f"{MCP_SERVICE_BASE_URL}/git/status", json={
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
        print(f"333333.........................check ")
        response = requests.post(f"{MCP_SERVICE_BASE_URL}/git/read_file", json={
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
        Lists the contents of a directory in a git repository.
        Args:
            repo_local_path (str): The path to the git repository
            path_in_repo (str): The path to the directory to list (default: "")
        Returns:
            A string containing the contents of the directory
        """
        print(f"444444.........................check ")
        response = requests.post(f"{MCP_SERVICE_BASE_URL}/git/list_contents", json={
            "repo_local_path": repo_local_path,
            "path_in_repo": path_in_repo
        })
        response.raise_for_status()
        data = response.json()
        if data.get("success"):
            contents = data.get("contents", [])
            formatted_contents = "\n".join([f"- {item['name']} ({item['type']})" for item in contents])
            return f"Contents of {repo_local_path}/{path_in_repo}:\n{formatted_contents}"
        return f"Error listing contents: {data.get('message', 'Unknown error')}"


# Add other tool classes here to implement more MCP services
# class CodeAnalysisTools:
#     @Tool(...)
#     def lint_code(...):
#         pass