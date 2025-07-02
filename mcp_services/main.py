# Run this file with `uvicorn mcp_tools.main:app --reload`

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from . import git_operations

app = FastAPI(
    title="MCP Git Service",
    description="Model Context Protocol (MCP)-compatible service for managing git operations",
    version="0.1.0",
    servers=[
        {"url": "http://localhost:8000", "description": "Local development server"},
    ]
)

# --- Pydanid Models for Request Bodies ---

class CloneRepoRequest(BaseModel):
    repo_url: str
    branch: str = "main"
    local_path: Optional[str] = None # Relative path within temp_repos directory

class RepoPathRequest(BaseModel):
    repo_local_path: str # Relative path within temp_repos directory

class FileContentRequest(BaseModel):
    repo_local_path: str # Relative path within temp_repos directory
    file_path_in_repo: str # Relative path within the repository

class ListContentsRequest(BaseModel):
    repo_local_path: str # Relative path within temp_repos directory
    path_in_repo: str  = "" # Relative path within the cloned repository

# --- API Endpoints for MCP Tools ---

@app.post("/mcp/git/clone", summary="Clone a git repository")
def api_clone_repo(request: CloneRepoRequest):
    """
    Clone a git repository to a temporary directory.
    returns the local path where the repository was cloned to
    """
    print(f"Cloning repository from {request.repo_url} on branch {request.branch} to {request.local_path}...")
    result = git_operations.clone_repo(repo_url=request.repo_url, branch=request.branch, local_path=request.local_path)
    if result["status"] == "success":
        return {"success": True, "message": result["message"], "local_path": result["local_path"]}
    raise HTTPException(status_code=500, detail=result["message"])

@app.post("/mcp/git/status", summary="Get the status of a git repository")
def api_get_repo_status(request: RepoPathRequest):
    """
    Get the status of a git repository.
    """
    print(f"Getting status of repository at {request.repo_local_path}...")
    result = git_operations.git_repo_status(local_path=request.repo_local_path)
    if result["status"] == "success":
        return {"success": True, "message": result["message"], "data": result["data"]}
    raise HTTPException(status_code=404, detail=result["message"])


@app.post("/mcp/git/read_file", summary="Read the content of a file in a git repository")
def api_read_file(request: FileContentRequest):
    """
    Reads the content of a file in a git repository.
    """
    print(f"Reading file {request.file_path_in_repo} in repository at {request.repo_local_path}...")
    result = git_operations.read_file_content(
        repo_local_path=request.repo_local_path, 
        file_path_in_repo=request.file_path_in_repo)
    if result["status"] == "success":
        return {"success": True, "content": result["content"]}
    raise HTTPException(status_code=404, detail=result["message"])

@app.post("/mcp/git/list_contents", summary="List the contents of a directory in a git repository")
def api_list_contents(request: ListContentsRequest):
    """
    List the contents of a directory in a git repository.
    """
    print(f"Listing contents of {request.path_in_repo} in repository at {request.repo_local_path}...")
    result = git_operations.list_repo_contents(
        repo_local_path=request.repo_local_path, 
        path_in_repo=request.path_in_repo)
    if result["status"] == "success":
        return {"success": True, "contents": result["contents"]}
    raise HTTPException(status_code=404, detail=result["message"])

# health check endpoint
@app.get("/mcp/git/health", summary="Health check endpoint")
def api_health_check():
    """
    Health check endpoint.
    """
    return {"success": True, "message": "MCP Git Service is running"}
