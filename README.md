# AI-Powered Code & Repository Manager with MCP Integration

## Features:
 - Checking style of Python code in a repo using Flake8


Code structure 

dev_assistant_crew/
├── venv/
├── crew_app/
│   ├── main.py            # Your CrewAI application logic
│   └── custom_tools.py    # Definitions of CrewAI Tools for MCP interaction
└── mcp_services/          # Contains your FastAPI/Lambda code for MCP tools
    ├── git_service/
    │   ├── main.py        # FastAPI app for Git operations
    │   ├── git_operations.py # Python functions using gitpython
    │   └── requirements.txt
    ├── code_analysis_service/ # (Future)
    │   ├── main.py
    │   └── requirements.txt
    └── ...

To run the tool, first activate a virtual environment
python -m venv venv
.\venv\Scripts\activate

Install dependencies

pip install -r mcp_services/git_service/requirements.txt
pip install -r crew_app/requirements.txt

Local Testing of MCP Service:
cd dev_assistant_crew/mcp_services/git_service
uvicorn main:app --reload --port 8000

uvicorn mcp_services.code_analysis_service.main:app --reload --port 8001

Sample results for style check
image.png
image.png
