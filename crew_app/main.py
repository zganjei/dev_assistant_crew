from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from crewai import Agent, Task, Crew, Process
import os

from custom_tools import GitTools

# import openai api key from .env file
load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# --- Define the Crew ---

# Define the agents
git_commander = Agent(
    role="Git Commander",
    goal="Mange local Git repositories, clone, get status, read file content, list repository contents.",
    backstory="""You are a git commander who is responsible for interacting with Git repositories to get information,
    clone, and list repository contents. You are also responsible for reading file content and getting the status of a repository.""",
    llm=llm,
    tools=[GitTools.clone_repo, 
           GitTools.get_repo_status, 
           GitTools.read_file_content, 
           GitTools.list_repo_contents],
    verbose=True,
    allow_delegation=False # this agent performs all tasks itself
)

# Define the tasks
# Task to clone a repository
clone_repo_task = Task(
    description="Clone the repository '{repo_url}' into a local path. Once cloned, store the local path in the variable 'repo_local_path' as it will be used in other tasks.",
    agent=git_commander,
    expected_output="The local path where the repository was cloned to"
)

# Task to get the status of a repository
get_repo_status_task = Task(
    description="Get the status of the repository at '{repo_local_path}'.Report the branch, if there are any uncommitted changes, and the last commit message.",
    agent=git_commander,
    expected_output="A summary of the repository status"
)

# Task to list the contents of a repository
list_repo_contents_task = Task(
    description="List the contents of the repository at '{repo_local_path}'. Report the files and directories in the root directory.",
    agent=git_commander,
    expected_output="A clear list of the files and directories of the root directory"
)

# ---- Assemble the crew ----

developer_asistant_crew = Crew(
    agents=[git_commander],
    tasks=[clone_repo_task, get_repo_status_task, list_repo_contents_task],
    verbose=True, # show more details about agent's thought process
    process=Process.sequential # Agents execute tasks in order
)


# Kick off the crew

if __name__ == "__main__":
    print("Starting the Developer Assistant Crew...")
    test_repo_url = "https://github.com/zganjei/dev_assistant_crew"

    crew_input = {
        "repo_url": test_repo_url,
    }

    print(f"\n-- Cloning repository {test_repo_url} --")
    clone_result = developer_asistant_crew.kickoff(inputs={"repo_url": test_repo_url})
    print(f".............................check {clone_result}")
    cloned_path_info = clone_result.split("local path where the repository was cloned, e.g., '")[1].split("'")[0]
    print(f"Repository cloned to: {cloned_path_info}")

    print(f"\n-- Getting repository status --")
    status_result = developer_asistant_crew.kickoff(inputs={"repo_local_path": cloned_path_info})
    print(status_result)

    print(f"\n-- Listing repository contents --")
    contents_result = developer_asistant_crew.kickoff(inputs={"repo_local_path": cloned_path_info})
    print(contents_result)

    print(f"\n-- Crew completed tasks--")
    





