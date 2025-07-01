import git 
import os
import shutil

# Ensure a temporary directory exists
TEMP_REPO_DIR = "temp_repos"
if not os.path.exists(TEMP_REPO_DIR):
    os.makedirs(TEMP_REPO_DIR)

def clone_repo(repo_url: str, branch: str = "main", local_path: str = None) -> dict:
    """
    Clone a git repository to a temporary directory.
    Args:
        repo_url: The URL of the git repository to clone.
        branch: The branch to clone.
        local_path: The path to clone the repository to.
    Returns:
        A dictionary containing status and message.
    """
    if not local_path:
        # Generate a unique name for the repository
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        unique_id = os.urandom(4).hex()
        target_path = os.path.join(TEMP_REPO_DIR, f"{repo_name}_{unique_id}")
    else:
        target_path = os.path.join(TEMP_REPO_DIR, local_path)

    try:
        print(f"Cloning repository from {repo_url} on branch {branch} to {target_path}...")
        #if directory exists, remove it
        if os.path.exists(target_path):
            shutil.rmtree(target_path)

        repo = git.Repo.clone_from(repo_url, target_path, branch=branch)
        return {
            "status": "success",
            "message": f"Repository cloned successfully to {target_path}",
            "local_path": target_path
        }
    except git.InvalidGitRepositoryError:
        return {
            "status": "error",
            "message": f"Invalid git repository: {repo_url}",
            "local_path": target_path
        }
    except git.GitCommandError as e:
        return {
            "status": "error",
            "message": f"Git command error: {e.stderr}",
            "local_path": target_path
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"An unexpected error occurred: {str(e)}"
        }


def git_repo_status(local_path: str) -> dict:
    """
    Get the status of a git repository.
    Args:
        local_path: The path to the git repository.
    Returns:
        A dictionary containing status and message.
    """
    try:
        repo = git.Repo(local_path)
        # Check for uncommitted changes
        uncommitted_changes = repo.index.diff(None)
        untracked_files = repo.untracked_files
        modified_files = [item.a_path for item in repo.index.diff(None) if item.change_type == "M"]
        deleted_files = [item.a_path for item in repo.index.diff(None) if item.change_type == "D"]

        status_summary = {
            "branch": repo.active_branch.name,
            "is_dirty": repo.is_dirty(untracked_files=True),
            "uncommitted_changes_count": len(uncommitted_changes),
            "untracked_files_count": len(untracked_files),
            "modified_files": modified_files,
            "deleted_files": deleted_files,
            "last_commit_message": repo.head.commit.message.strip() if repo.head.commit else "No commits yet",
        }
        return {
            "status": "success",
            "message": "Repository status retrieved successfully",
            "data": status_summary
        }
    except git.InvalidGitRepositoryError:
        return {
            "status": "error",
            "message": f"Invalid git repository: {local_path}",
            "data": {}
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"An unexpected error occurred: {str(e)}",
            "data": {}
        }

def read_file_content(repo_local_path: str, file_path_in_repo: str) -> dict:
    """
    Read the content of a file in a git repository.
    Args:
        repo_local_path: The path to the git repository.
        file_path: The path to the file to read.
    Returns:
        status: success or error
        message: success or error message
        data: content of the file
    """
    full_repo_path = os.path.join(TEMP_REPO_DIR, repo_local_path)
    full_file_path = os.path.join(full_repo_path, file_path_in_repo)

    if not os.path.exists(full_file_path):
        return {
            "status": "error",
            "message": f"File not found: {full_file_path}",
            "data": {}
        }
    if not os.path.isfile(full_file_path):
        return {
            "status": "error",
            "message": f"Path is not a file: {full_file_path}",
            "data": {}
        }
    try:
        with open(full_file_path, "r", encoding="utf-8") as file:
            content = file.read()
        return {
            "status": "success",
            "content": content
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"An unexpected error occurred: {str(e)}",
            "data": {}
        }

def list_repo_contents(repo_local_path: str, path_in_repo: str = "") -> dict:
    """
    List the contents of a directory in a git repository.
    Args:
        repo_local_path: The path to the git repository.
        path_in_repo: The path to the directory to list.
    Returns:
        status: success or error
        message: success or error message
        data: list of files and directories
    """
    full_path = os.path.join(TEMP_REPO_DIR, repo_local_path, path_in_repo)
    if not os.path.exists(full_path):
        return {
            "status": "error",
            "message": f"Path not found: {path_in_repo} in {repo_local_path}"
        }
    if not os.path.isdir(full_path):   
        return {
            "status": "error",
            "message": f"Path is not a directory: {full_path}"
        }
    try:
        contents = []
        for item in os.listdir(full_path):
            item_path = os.path.join(full_path, item)
            item_type = "directory" if os.path.isdir(item_path) else "file"
            contents.append({
                "name": item,
                "type": item_type
            })
        return {
            "status": "success",
            "contents": contents
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error listing contents: {str(e)}",
            "contents": []
        }
        
result = clone_repo(repo_url="https://github.com/zganjei/dev_assistant_crew", branch="main")
print(result)

result2 = git_repo_status(result["local_path"])
print(result2)

result3 = read_file_content(result["local_path"].split("\\")[-1], "README.md")
print(result3)

result4 = list_repo_contents(result["local_path"].split("\\")[-1], "mcp_tools")
print(result4)
