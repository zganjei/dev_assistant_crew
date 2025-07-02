from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
from . import analysis_operations

app = FastAPI(title="Code Analysis Service", 
              description="MCP-compatible service for code analysis",
              version="0.1.0",
              servers=[{"url": "http://localhost:8001"}])

# Pydantic models for request body
class CodeContentRequest(BaseModel):
    code_content: str # The Python code to analyze

class CodeAnalysisResponse(BaseModel):
    success: bool
    message: str
    feedback: List[str]

@app.post("/mcp/code/analyse_style", summary="Analyze Python code style")
def api_analyze_code_style(request: CodeContentRequest) -> CodeAnalysisResponse:
    """
    Analyzes Python code style with Flake8 and provides feedback.
    """
    print(f"Analyzing code style for: {request.code_content[:100]}...")
    result = analysis_operations.analyze_python_code_style(request.code_content)
    if result["status"] == "success":
        return CodeAnalysisResponse(success=True, message=result["message"], feedback=result["feedback"])
    raise HTTPException(status_code=500, detail=result["message"])


# Health check endpoint
@app.get("/health", summary="Health check endpoint")
def health_check():
    return {"status": "ok", "service": "MCP code_analysis_service"}